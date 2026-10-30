from __future__ import annotations

import unittest
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from order_service import confirm_order, create_order
from shared_platform import SessionLocal, current_user


class AdminRefundOrderTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.customer_id = UUID("698cc9c6-1238-4088-8fc4-104eec02af88")
        self.customer_user = {
            "id": self.customer_id,
            "phone": "0912345678",
            "full_name": "Nguyen Van A",
            "is_active": True,
            "role": "customer",
        }

        self.admin_id = UUID("2bd11c09-67ef-49c6-8fba-7fa52086f658")
        self.admin_user = {
            "id": self.admin_id,
            "phone": "0909999999",
            "full_name": "Admin System",
            "is_active": True,
            "role": "admin",
        }

        # Override với quyền admin mặc định
        app.dependency_overrides[current_user] = lambda: self.admin_user

        # Seeded variant: stock = 5, reserved = 0, price = 189000
        self.variant_id = UUID("30000000-0000-4000-8000-000000000001")
        self.db.execute(
            text("UPDATE product_variants SET stock_on_hand = 5, reserved_quantity = 0 WHERE id = :v"),
            {"v": self.variant_id}
        )
        self.db.execute(
            text("UPDATE products SET is_active = true WHERE id = (SELECT product_id FROM product_variants WHERE id = :v)"),
            {"v": self.variant_id}
        )
        self.db.commit()

        self.created_order_ids: list[UUID] = []

    def tearDown(self):
        for oid in self.created_order_ids:
            self.db.execute(text("DELETE FROM inventory_adjustments WHERE reason LIKE :r"), {"r": f"%{oid}%"})
            self.db.execute(text("DELETE FROM orders WHERE id = :id"), {"id": oid})
        self.db.execute(
            text("UPDATE product_variants SET stock_on_hand = 5, reserved_quantity = 0 WHERE id = :v"),
            {"v": self.variant_id}
        )
        self.db.commit()
        self.db.close()
        app.dependency_overrides.clear()

    def _create_paid_order(self, quantity: int = 2) -> UUID:
        """Tạo đơn hàng online đã xác nhận và đã thanh toán (payment_status = 'paid')."""
        order_id = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": quantity}],
            address_snapshot={"fullName": "Nguyen Van A", "phone": "0912345678", "city": "TP.HCM"},
        )
        self.created_order_ids.append(order_id)
        # Xác nhận đơn và chuyển payment_status = 'paid'
        confirm_order(self.db, order_id, self.admin_id)
        self.db.execute(
            text("UPDATE orders SET payment_status = 'paid' WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()
        return order_id

    def test_admin_refund_paid_order_success(self):
        """Admin hoàn tiền hợp lệ cho đơn đã thanh toán -> payment_status='refunded', status='cancelled'."""
        order_id = self._create_paid_order(quantity=1)

        payload = {
            "reason": "Khách hàng yêu cầu hủy đơn do đặt nhầm size",
            "refund_amount": 189000,
        }
        response = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()

        self.assertEqual(data["order_id"], str(order_id))
        self.assertEqual(data["status"], "cancelled")
        self.assertEqual(data["payment_status"], "refunded")
        self.assertEqual(data["refund_amount"], 189000)
        self.assertEqual(data["refund_reason"], payload["reason"])
        self.assertEqual(len(data["restocked_items"]), 1)
        self.assertEqual(data["restocked_items"][0]["quantity_restocked"], 1)

        # Kiểm tra database state
        order_row = self.db.execute(
            text("SELECT status, payment_status, cancelled_at FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(order_row["status"], "cancelled")
        self.assertEqual(order_row["payment_status"], "refunded")
        self.assertIsNotNone(order_row["cancelled_at"])

        # Kiểm tra order_status_history
        history = self.db.execute(
            text("SELECT note FROM order_status_history WHERE order_id = :id AND to_status = 'cancelled'"),
            {"id": order_id}
        ).scalars().all()
        self.assertTrue(any("Hoàn tiền" in n for n in history))

    def test_restock_inventory_restored(self):
        """Kiểm tra tồn kho product_variants.stock_on_hand tăng lại chính xác bằng số lượng hoàn."""
        # Variant ban đầu có stock = 5
        # Tạo đơn mua 2 cái -> confirm_order trừ stock xuống 3
        order_id = self._create_paid_order(quantity=2)

        stock_after_confirm = self.db.execute(
            text("SELECT stock_on_hand FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).scalar_one()
        self.assertEqual(stock_after_confirm, 3)

        # Thực hiện hoàn tiền
        payload = {"reason": "Sản phẩm lỗi đóng gói"}
        response = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["restocked_items"][0]["quantity_restocked"], 2)
        self.assertEqual(data["restocked_items"][0]["stock_before"], 3)
        self.assertEqual(data["restocked_items"][0]["stock_after"], 5)

        # Verify tồn kho DB được hồi phục về 5
        stock_restored = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(stock_restored["stock_on_hand"], 5)
        self.assertEqual(stock_restored["reserved_quantity"], 0)

        # Verify ghi nhận vào inventory_adjustments
        adj = self.db.execute(
            text("SELECT delta, quantity_before, quantity_after, reason FROM inventory_adjustments WHERE variant_id = :v ORDER BY created_at DESC LIMIT 1"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(adj["delta"], 2)
        self.assertEqual(adj["quantity_before"], 3)
        self.assertEqual(adj["quantity_after"], 5)
        self.assertIn("refunded & restocked by Admin", adj["reason"])

    def test_refund_unpaid_order_fails(self):
        """Hoàn tiền cho đơn chưa thanh toán (payment_status='unpaid') -> 400 Bad Request."""
        order_id = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": 1}],
            address_snapshot={"fullName": "Nguyen Van A", "phone": "0912345678", "city": "TP.HCM"},
        )
        self.created_order_ids.append(order_id)
        self.db.commit()

        # payment_status mặc định là 'unpaid'
        payload = {"reason": "Test hoàn đơn chưa trả tiền"}
        response = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "ORDER_NOT_PAID")

    def test_refund_already_refunded_order_fails(self):
        """Cố tình hoàn tiền lần thứ 2 cho đơn đã hoàn tiền -> 409 Conflict."""
        order_id = self._create_paid_order(quantity=1)

        payload = {"reason": "Hoàn tiền lần đầu"}
        res1 = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json=payload)
        self.assertEqual(res1.status_code, 200)

        # Lần 2 -> 409 Conflict
        res2 = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json={"reason": "Hoàn tiền lần hai"})
        self.assertEqual(res2.status_code, 409)
        self.assertEqual(res2.json()["error"]["code"], "ORDER_ALREADY_REFUNDED")

    def test_non_admin_cannot_refund(self):
        """User không có quyền admin (ví dụ customer) gọi API hoàn tiền -> 403 Forbidden."""
        order_id = self._create_paid_order(quantity=1)

        app.dependency_overrides[current_user] = lambda: self.customer_user
        payload = {"reason": "Customer tự yêu cầu hoàn tiền trực tiếp"}
        response = self.client.post(f"/api/v1/admin/orders/{order_id}/refund", json=payload)
        self.assertEqual(response.status_code, 403)


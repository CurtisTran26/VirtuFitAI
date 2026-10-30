from __future__ import annotations

import unittest
from datetime import timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.services.orders.expiration import run_expiration_batch
from order_service import confirm_order, create_order
from shared_platform import SessionLocal, current_user, now


class OrderExpirationTestCase(unittest.TestCase):
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

    def test_01_stale_order_auto_expired(self):
        """Đơn hàng VNPay quá hạn 15 phút -> Tự động chuyển sang trạng thái expired."""
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
        # Giả lập đơn đã quá hạn giữ chỗ 15 phút
        past_time = now() - timedelta(minutes=1)
        self.db.execute(
            text("UPDATE orders SET hold_expires_at = :t WHERE id = :id"),
            {"t": past_time, "id": order_id}
        )
        self.db.commit()

        # Chạy batch hủy đơn quá hạn
        result = run_expiration_batch(self.db)
        self.assertGreaterEqual(result["expired_count"], 1)

        # Kiểm tra order state
        order_row = self.db.execute(
            text("SELECT status, hold_expires_at FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(order_row["status"], "expired")
        self.assertIsNone(order_row["hold_expires_at"])

        # Kiểm tra order_status_history
        history = self.db.execute(
            text("SELECT note FROM order_status_history WHERE order_id = :id AND to_status = 'expired'"),
            {"id": order_id}
        ).scalars().all()
        self.assertTrue(any("expired" in n.lower() for n in history))

    def test_02_inventory_reservation_released(self):
        """Kiểm tra giải phóng giữ chỗ: reserved_quantity quay về 0, tồn khả dụng hồi phục."""
        # Variant có stock = 5, reserved = 0
        order_id = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": 2}],
            address_snapshot={"fullName": "Nguyen Van A", "phone": "0912345678", "city": "TP.HCM"},
        )
        self.created_order_ids.append(order_id)
        self.db.commit()

        # Kiểm tra reserved_quantity tăng lên 2
        variant_before = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant_before["reserved_quantity"], 2)
        self.assertEqual(variant_before["stock_on_hand"], 5)
        available_before = variant_before["stock_on_hand"] - variant_before["reserved_quantity"]
        self.assertEqual(available_before, 3)

        # Giả lập hết hạn giữ chỗ và chạy worker
        self.db.execute(
            text("UPDATE orders SET hold_expires_at = :t WHERE id = :id"),
            {"t": now() - timedelta(minutes=5), "id": order_id}
        )
        self.db.commit()

        run_expiration_batch(self.db)

        # Kiểm tra reserved_quantity đã được giải phóng về 0
        variant_after = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant_after["reserved_quantity"], 0)
        self.assertEqual(variant_after["stock_on_hand"], 5)
        # Tồn khả dụng hồi phục về 5
        self.assertEqual(variant_after["stock_on_hand"] - variant_after["reserved_quantity"], 5)

        # Kiểm tra inventory_reservations status = 'released'
        reservation_status = self.db.execute(
            text("SELECT status FROM inventory_reservations WHERE order_id = :id"),
            {"id": order_id}
        ).scalar_one()
        self.assertEqual(reservation_status, "released")

    def test_03_active_unexpired_order_not_cancelled(self):
        """Đơn hàng còn hạn giữ chỗ (hold_expires_at > now()) không bị hủy nhầm."""
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
        # Đặt hạn giữ chỗ còn 10 phút nữa
        self.db.execute(
            text("UPDATE orders SET hold_expires_at = :t WHERE id = :id"),
            {"t": now() + timedelta(minutes=10), "id": order_id}
        )
        self.db.commit()

        run_expiration_batch(self.db)

        # Kiểm tra đơn vẫn giữ nguyên status = 'pending_confirmation'
        order_row = self.db.execute(
            text("SELECT status FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(order_row["status"], "pending_confirmation")

        # Giữ chỗ vẫn là active
        res_status = self.db.execute(
            text("SELECT status FROM inventory_reservations WHERE order_id = :id"),
            {"id": order_id}
        ).scalar_one()
        self.assertEqual(res_status, "active")

    def test_04_confirmed_and_cod_orders_not_cancelled(self):
        """Đơn hàng đã thanh toán hoặc đơn COD không bị hủy nhầm bởi expiration worker."""
        # Đơn 1: VNPay đã xác nhận (confirmed)
        order_confirmed = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": 1}],
            address_snapshot={"fullName": "Nguyen Van A", "phone": "0912345678", "city": "TP.HCM"},
        )
        self.created_order_ids.append(order_confirmed)
        confirm_order(self.db, order_confirmed, self.admin_id)

        # Đơn 2: COD (duyệt xác nhận ngay lập tức khi tạo)
        order_cod = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="cod",
            lines=[{"variant_id": self.variant_id, "quantity": 1}],
            address_snapshot={"fullName": "Nguyen Van A", "phone": "0912345678", "city": "TP.HCM"},
            confirm_immediately=True,
        )
        self.created_order_ids.append(order_cod)
        self.db.commit()

        # Chạy expiration worker
        result = run_expiration_batch(self.db)

        # Cả 2 đơn vẫn giữ nguyên status = 'confirmed'
        for oid in (order_confirmed, order_cod):
            status = self.db.execute(
                text("SELECT status FROM orders WHERE id = :id"),
                {"id": oid}
            ).scalar_one()
            self.assertEqual(status, "confirmed")

    def test_05_admin_expire_stale_api_endpoint(self):
        """Test API POST /api/v1/admin/orders/expire-stale kích hoạt worker."""
        # Tạo đơn quá hạn
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
        self.db.execute(
            text("UPDATE orders SET hold_expires_at = :t WHERE id = :id"),
            {"t": now() - timedelta(minutes=2), "id": order_id}
        )
        self.db.commit()

        # 1. Admin gọi endpoint -> 200 OK
        response = self.client.post("/api/v1/admin/orders/expire-stale")
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["expired_orders"], 1)

        # 2. Customer gọi endpoint -> 403 Forbidden
        app.dependency_overrides[current_user] = lambda: self.customer_user
        res_forbidden = self.client.post("/api/v1/admin/orders/expire-stale")
        self.assertEqual(res_forbidden.status_code, 403)


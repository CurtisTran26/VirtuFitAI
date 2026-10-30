from __future__ import annotations

import unittest
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from shared_platform import SessionLocal, current_user, now


class CodOrderTestCase(unittest.TestCase):
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

        self.warehouse_staff_id = UUID("7d5308b7-0c4c-4024-b177-fa29c72e1f46")
        self.warehouse_staff_user = {
            "id": self.warehouse_staff_id,
            "phone": "0908888888",
            "full_name": "Tran Van Kho",
            "is_active": True,
            "role": "warehouse_staff",
        }

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

    def test_01_create_cod_order_success(self):
        """1. Test tạo đơn hàng COD hợp lệ -> Trạng thái ban đầu: status='confirmed', payment_status='unpaid'."""
        app.dependency_overrides[current_user] = lambda: self.customer_user

        payload = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cod",
            "shipping_address": {
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "address": "456 Nguyen Trai, Phuong 7, Quan 5",
                "ward": "Phuong 7",
                "district": "Quan 5",
                "province": "TP. Ho Chi Minh"
            }
        }

        res = self.client.post("/api/v1/orders", json=payload)
        self.assertEqual(res.status_code, 201, res.text)
        data = res.json()

        order_id = UUID(data["id"])
        self.created_order_ids.append(order_id)

        self.assertEqual(data["payment_method"], "cod")
        self.assertEqual(data["payment_status"], "unpaid")
        self.assertEqual(data["status"], "confirmed")  # Đã duyệt đơn giao
        self.assertEqual(data["total_vnd"], 189000)

        # Kiểm tra kho: stock_on_hand bị trừ trực tiếp (5 - 1 = 4), reserved = 0
        variant = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant["stock_on_hand"], 4)
        self.assertEqual(variant["reserved_quantity"], 0)

    def test_02_cod_collect_when_processing_fails_400(self):
        """2. Test xác nhận thu COD khi đơn hàng mới đang đóng gói (processing) -> Báo lỗi 400 Bad Request."""
        # Tạo đơn COD trước
        app.dependency_overrides[current_user] = lambda: self.customer_user
        payload = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cod",
            "shipping_address": {
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "address": "456 Nguyen Trai, Phuong 7, Quan 5",
            }
        }
        res_create = self.client.post("/api/v1/orders", json=payload)
        self.assertEqual(res_create.status_code, 201)
        order_id = UUID(res_create.json()["id"])
        self.created_order_ids.append(order_id)

        # Cập nhật trạng thái đơn sang 'processing'
        self.db.execute(
            text("UPDATE orders SET status = 'processing', updated_at = now() WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()

        # Đổi quyền sang warehouse_staff để gọi thu COD
        app.dependency_overrides[current_user] = lambda: self.warehouse_staff_user

        res_collect = self.client.post(f"/api/v1/orders/{order_id}/cod-collect")
        self.assertEqual(res_collect.status_code, 400, res_collect.text)
        data = res_collect.json()
        self.assertEqual(data["error"]["code"], "INVALID_ORDER_STATE")

        # payment_status vẫn là unpaid
        order = self.db.execute(text("SELECT payment_status FROM orders WHERE id = :id"), {"id": order_id}).mappings().first()
        self.assertEqual(order["payment_status"], "unpaid")

    def test_03_cod_collect_when_completed_success(self):
        """3. Test xác nhận thu COD khi đơn đã giao (completed) -> Cập nhật thành công sang paid."""
        # Tạo đơn COD
        app.dependency_overrides[current_user] = lambda: self.customer_user
        payload = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cod",
            "shipping_address": {
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "address": "456 Nguyen Trai, Phuong 7, Quan 5",
            }
        }
        res_create = self.client.post("/api/v1/orders", json=payload)
        self.assertEqual(res_create.status_code, 201)
        order_id = UUID(res_create.json()["id"])
        self.created_order_ids.append(order_id)

        # Cập nhật trạng thái đơn sang 'completed' (đã giao thành công)
        self.db.execute(
            text("UPDATE orders SET status = 'completed', updated_at = now() WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()

        # Nhân viên kho xác nhận thu COD
        app.dependency_overrides[current_user] = lambda: self.warehouse_staff_user
        res_collect = self.client.post(f"/api/v1/orders/{order_id}/cod-collect")
        self.assertEqual(res_collect.status_code, 200, res_collect.text)
        data = res_collect.json()

        self.assertEqual(data["order_id"], str(order_id))
        self.assertEqual(data["payment_status"], "paid")
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["collector_id"], str(self.warehouse_staff_id))
        self.assertIn("thành công", data["message"].lower())

        # DB đã cập nhật payment_status = 'paid'
        order = self.db.execute(text("SELECT payment_status FROM orders WHERE id = :id"), {"id": order_id}).mappings().first()
        self.assertEqual(order["payment_status"], "paid")

    def test_04_cod_collect_duplicate_fails_409(self):
        """4. Test cố tình xác nhận thu COD lần thứ 2 cho cùng 1 đơn -> Báo lỗi 409 Conflict."""
        # Tạo đơn COD
        app.dependency_overrides[current_user] = lambda: self.customer_user
        payload = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cod",
            "shipping_address": {
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "address": "456 Nguyen Trai, Phuong 7, Quan 5",
            }
        }
        res_create = self.client.post("/api/v1/orders", json=payload)
        self.assertEqual(res_create.status_code, 201)
        order_id = UUID(res_create.json()["id"])
        self.created_order_ids.append(order_id)

        # Cập nhật sang shipped (đang giao)
        self.db.execute(
            text("UPDATE orders SET status = 'shipped', updated_at = now() WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()

        app.dependency_overrides[current_user] = lambda: self.warehouse_staff_user

        # Lần 1: Thu COD thành công
        res1 = self.client.post(f"/api/v1/orders/{order_id}/cod-collect")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["payment_status"], "paid")

        # Lần 2: Cố tình gọi lại
        res2 = self.client.post(f"/api/v1/orders/{order_id}/cod-collect")
        self.assertEqual(res2.status_code, 409, res2.text)
        self.assertEqual(res2.json()["error"]["code"], "ORDER_ALREADY_PAID")

    def test_05_customer_forbidden_from_cod_collect(self):
        """Test khách hàng customer cố tình gọi API đối soát COD -> Chặn 403 Forbidden."""
        # Tạo đơn COD và chuyển sang completed
        app.dependency_overrides[current_user] = lambda: self.customer_user
        payload = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cod",
            "shipping_address": {
                "name": "Nguyen Van A",
                "phone": "0912345678",
                "address": "456 Nguyen Trai, Phuong 7, Quan 5",
            }
        }
        res_create = self.client.post("/api/v1/orders", json=payload)
        order_id = UUID(res_create.json()["id"])
        self.created_order_ids.append(order_id)

        self.db.execute(
            text("UPDATE orders SET status = 'completed', updated_at = now() WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()

        # Customer gọi cod-collect -> 403 Forbidden
        res = self.client.post(f"/api/v1/orders/{order_id}/cod-collect")
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()["error"]["code"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()


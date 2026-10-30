from __future__ import annotations

import unittest
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from order_service import create_order
from shared_platform import SessionLocal, current_user, now


class WarehouseFulfillmentTestCase(unittest.TestCase):
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

        # Override với quyền nhân viên kho mặc định
        app.dependency_overrides[current_user] = lambda: self.warehouse_staff_user

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

    def _create_confirmed_order(self, quantity: int = 1) -> tuple[UUID, str]:
        """Tạo đơn hàng online đã duyệt (confirmed) sẵn sàng cho kho soạn hàng."""
        order_id = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="cod",
            lines=[{"variant_id": self.variant_id, "quantity": quantity}],
            address_snapshot={"name": "Nguyen Van A", "phone": "0912345678", "address": "789 Tran Hung Dao, Q5"},
            idempotency_key=f"test-wh-{now().timestamp()}",
            confirm_immediately=True,
        )
        self.db.commit()
        self.created_order_ids.append(order_id)

        order_number = self.db.execute(
            text("SELECT order_number FROM orders WHERE id = :id"),
            {"id": order_id}
        ).scalar_one()
        return order_id, order_number

    def test_01_get_warehouse_orders_list(self):
        """1. Test lấy danh sách đơn cần soạn hàng (status='confirmed') cho nhân viên kho."""
        order_id, order_number = self._create_confirmed_order(quantity=1)

        res = self.client.get("/api/v1/warehouse/orders", params={"status": "confirmed"})
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertGreaterEqual(data["total"], 1)
        found = any(item["id"] == str(order_id) for item in data["items"])
        self.assertTrue(found, f"Order {order_id} không tìm thấy trong danh sách soạn hàng!")

        item = next(i for i in data["items"] if i["id"] == str(order_id))
        self.assertEqual(item["order_number"], order_number)
        self.assertEqual(item["status"], "confirmed")
        self.assertEqual(len(item["items"]), 1)
        self.assertEqual(item["items"][0]["variant_id"], str(self.variant_id))

    def test_02_fulfillment_step_by_step_transitions(self):
        """2. Test chuyển tuần tự trạng thái: confirmed -> processing -> ready_to_ship -> shipped -> completed."""
        order_id, order_number = self._create_confirmed_order(quantity=1)

        # Bước 1: confirmed -> processing (Bắt đầu soạn hàng)
        res1 = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "processing", "note": "Bắt đầu soạn hàng tại kệ A3"}
        )
        self.assertEqual(res1.status_code, 200, res1.text)
        data1 = res1.json()
        self.assertEqual(data1["from_status"], "confirmed")
        self.assertEqual(data1["to_status"], "processing")

        # Bước 2: processing -> ready_to_ship (Đóng gói xong, chờ ship)
        res2 = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "ready_to_ship", "note": "Đã đóng gói vào thùng tiêu chuẩn"}
        )
        self.assertEqual(res2.status_code, 200, res2.text)
        data2 = res2.json()
        self.assertEqual(data2["from_status"], "processing")
        self.assertEqual(data2["to_status"], "ready_to_ship")

        # Bước 3: ready_to_ship -> shipped (Bàn giao vận chuyển với mã vận đơn)
        res3 = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={
                "next_status": "shipped",
                "carrier_name": "Giao Hàng Nhanh (GHN)",
                "tracking_code": "GHN-VF-998877",
                "note": "Đã bàn giao shipper GHN"
            }
        )
        self.assertEqual(res3.status_code, 200, res3.text)
        data3 = res3.json()
        self.assertEqual(data3["from_status"], "ready_to_ship")
        self.assertEqual(data3["to_status"], "shipped")
        self.assertEqual(data3["carrier_name"], "Giao Hàng Nhanh (GHN)")
        self.assertEqual(data3["tracking_code"], "GHN-VF-998877")

        # Kiểm tra address_snapshot đã lưu carrier và tracking_code
        order_row = self.db.execute(
            text("SELECT address_snapshot FROM orders WHERE id = :id"),
            {"id": order_id}
        ).scalar_one()
        self.assertEqual(order_row.get("carrier_name"), "Giao Hàng Nhanh (GHN)")
        self.assertEqual(order_row.get("tracking_code"), "GHN-VF-998877")

        # Bước 4: shipped -> completed (Giao thành công)
        res4 = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "completed", "note": "Khách đã nhận hàng và ký nhận"}
        )
        self.assertEqual(res4.status_code, 200, res4.text)
        data4 = res4.json()
        self.assertEqual(data4["from_status"], "shipped")
        self.assertEqual(data4["to_status"], "completed")

    def test_03_jump_state_fails_409_state_conflict(self):
        """3. Test nhảy cóc trạng thái (từ confirmed nhảy thẳng lên completed) -> Báo lỗi 409 State Conflict."""
        order_id, _ = self._create_confirmed_order(quantity=1)

        # Cố tình chuyển từ confirmed nhảy cóc thẳng lên completed
        res = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "completed"}
        )
        self.assertEqual(res.status_code, 409, res.text)
        data = res.json()
        self.assertEqual(data["error"]["code"], "ORDER_STATE_CONFLICT")

        # Thử nhảy từ confirmed sang ready_to_ship
        res_skip = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "ready_to_ship"}
        )
        self.assertEqual(res_skip.status_code, 409)

    def test_04_shipped_missing_tracking_code_fails_422(self):
        """4. Test chuyển sang shipped nhưng không truyền mã vận đơn tracking_code -> Báo lỗi 422 Unprocessable Entity."""
        order_id, _ = self._create_confirmed_order(quantity=1)

        # Chuyển tuần tự đến ready_to_ship
        self.client.patch(f"/api/v1/warehouse/orders/{order_id}/status", json={"next_status": "processing"})
        self.client.patch(f"/api/v1/warehouse/orders/{order_id}/status", json={"next_status": "ready_to_ship"})

        # Chuyển sang shipped nhưng thiếu tracking_code
        res_missing_tracking = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={
                "next_status": "shipped",
                "carrier_name": "GHTK",
                "tracking_code": None  # Thiếu tracking code
            }
        )
        self.assertEqual(res_missing_tracking.status_code, 422, res_missing_tracking.text)

        # Chuyển sang shipped nhưng thiếu carrier_name
        res_missing_carrier = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={
                "next_status": "shipped",
                "carrier_name": "",
                "tracking_code": "TRACK-123456"
            }
        )
        self.assertEqual(res_missing_carrier.status_code, 422, res_missing_carrier.text)

    def test_05_customer_forbidden_from_warehouse_api(self):
        """5. Test tài khoản customer cố gọi API chuyển trạng thái kho -> Chặn 403 Forbidden."""
        order_id, _ = self._create_confirmed_order(quantity=1)

        # Chuyển user thành customer
        app.dependency_overrides[current_user] = lambda: self.customer_user

        # Thử lấy danh sách đơn kho
        res_get = self.client.get("/api/v1/warehouse/orders")
        self.assertEqual(res_get.status_code, 403, res_get.text)
        self.assertEqual(res_get.json()["error"]["code"], "FORBIDDEN")

        # Thử cập nhật trạng thái kho
        res_patch = self.client.patch(
            f"/api/v1/warehouse/orders/{order_id}/status",
            json={"next_status": "processing"}
        )
        self.assertEqual(res_patch.status_code, 403, res_patch.text)
        self.assertEqual(res_patch.json()["error"]["code"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()


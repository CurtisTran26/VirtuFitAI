from __future__ import annotations

import unittest
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.services.sales.service import (
    VIETQR_BANK_ID,
    VIETQR_ACCOUNT_NO,
    create_counter_order,
)
from app.schemas.sales.sales import CounterOrderCreate, OrderItemInput
from shared_platform import SessionLocal, current_user


class SalesOrderTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.staff_id = UUID("be346270-0bef-4c1b-89f3-26251105b98c")
        self.staff_user = {
            "id": self.staff_id,
            "phone": "0988776655",
            "full_name": "Nguyen Van Sales",
            "is_active": True,
            "role": "sales_staff",
        }

        self.customer_id = UUID("698cc9c6-1238-4088-8fc4-104eec02af88")
        self.customer_user = {
            "id": self.customer_id,
            "phone": "0912345678",
            "full_name": "Customer A",
            "is_active": True,
            "role": "customer",
        }

        # Mặc định override với vai trò sales_staff
        app.dependency_overrides[current_user] = lambda: self.staff_user

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

    def _create_counter_order(self, quantity: int = 1) -> tuple[UUID, str, int]:
        """Tạo đơn hàng quầy mẫu với trạng thái pending_confirmation."""
        payload = CounterOrderCreate(
            items=[OrderItemInput(variant_id=self.variant_id, quantity=quantity)],
            payment_method="cash"
        )
        order = create_counter_order(self.db, staff_id=self.staff_id, payload=payload)
        order_id = order["id"]
        self.created_order_ids.append(order_id)
        return order_id, order["order_number"], order["total_vnd"]

    def test_01_create_counter_order_success(self):
        """Test tạo đơn hàng tại quầy -> Trả về 201 Created và order_type = 'counter'."""
        body = {
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
            "payment_method": "cash",
            "note": "Khách mua tại cửa hàng Nguyễn Trãi"
        }
        res = self.client.post("/api/v1/sales/orders", json=body)
        self.assertEqual(res.status_code, 201, res.text)
        data = res.json()
        self.assertEqual(data["order_type"], "counter")
        self.assertEqual(data["status"], "pending_confirmation")
        self.assertEqual(data["total_vnd"], 189000)
        self.created_order_ids.append(UUID(data["id"]))

    def test_02_pay_cash_success_and_correct_change(self):
        """1. Test nhân viên sales thanh toán tiền mặt đủ -> Đơn chuyển completed, trả về tiền thừa chính xác."""
        order_id, order_number, total_vnd = self._create_counter_order(quantity=2)
        # total_vnd = 189000 * 2 = 378000 VND
        self.assertEqual(total_vnd, 378000)

        # Khách đưa 500,000 VND
        cash_received = 500000
        expected_change = 500000 - 378000  # 122,000 VND

        res = self.client.post(
            f"/api/v1/sales/orders/{order_id}/pay-cash",
            json={"cash_received": cash_received}
        )
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["order_id"], str(order_id))
        self.assertEqual(data["order_number"], order_number)
        self.assertEqual(data["total_vnd"], total_vnd)
        self.assertEqual(data["cash_received"], cash_received)
        self.assertEqual(data["cash_change"], expected_change)
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["payment_status"], "paid")

        # Kiểm tra tồn kho đã bị trừ thực tế: 5 - 2 = 3, reserved = 0
        variant = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant["stock_on_hand"], 3)
        self.assertEqual(variant["reserved_quantity"], 0)

    def test_03_pay_cash_insufficient_fails_400(self):
        """2. Test khách đưa thiếu tiền mặt -> Báo lỗi 400 Bad Request."""
        order_id, order_number, total_vnd = self._create_counter_order(quantity=1)
        # total_vnd = 189000 VND. Khách đưa thiếu: 100,000 VND
        cash_received = 100000

        res = self.client.post(
            f"/api/v1/sales/orders/{order_id}/pay-cash",
            json={"cash_received": cash_received}
        )
        self.assertEqual(res.status_code, 400, res.text)
        data = res.json()
        self.assertEqual(data["error"]["code"], "INVALID_CASH_AMOUNT")

        # Kiểm tra đơn vẫn pending, kho chưa bị trừ
        order = self.db.execute(text("SELECT status FROM orders WHERE id = :id"), {"id": order_id}).mappings().first()
        self.assertEqual(order["status"], "pending_confirmation")

    def test_04_vietqr_payload_matches_order(self):
        """3. Test sinh payload VietQR khớp chính xác mã đơn và số tiền cần thanh toán."""
        order_id, order_number, total_vnd = self._create_counter_order(quantity=1)

        res = self.client.post(f"/api/v1/sales/orders/{order_id}/vietqr")
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["order_id"], str(order_id))
        self.assertEqual(data["order_number"], order_number)
        self.assertEqual(data["amount_vnd"], total_vnd)
        self.assertEqual(data["transfer_content"], order_number)
        self.assertEqual(data["bank_id"], VIETQR_BANK_ID)
        self.assertEqual(data["account_no"], VIETQR_ACCOUNT_NO)

        # Kiểm tra QR Image URL chứa đúng các thông số
        qr_url = data["qr_image_url"]
        self.assertIn(f"amount={total_vnd}", qr_url)
        self.assertIn(f"addInfo={order_number}", qr_url)

        # Kiểm tra chuỗi EMVCo payload chuẩn
        emvco = data["emvco_payload"]
        self.assertTrue(emvco.startswith("000201010212"))
        self.assertIn(str(total_vnd), emvco)
        self.assertIn(order_number, emvco)

    def test_05_confirm_bank_transfer_success(self):
        """Test nhân viên xác nhận chuyển khoản thành công -> Đơn chuyển completed, payment_method = bank_transfer."""
        order_id, order_number, total_vnd = self._create_counter_order(quantity=1)

        res = self.client.post(f"/api/v1/sales/orders/{order_id}/confirm-transfer")
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["payment_status"], "paid")
        self.assertEqual(data["payment_method"], "bank_transfer")

        # Kiểm tra kho thực tế đã bị trừ
        variant = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant["stock_on_hand"], 4)
        self.assertEqual(variant["reserved_quantity"], 0)

    def test_06_customer_forbidden_from_sales_api(self):
        """4. Test tài khoản vai trò customer cố tình gọi API thanh toán quầy -> Chặn 403 Forbidden."""
        order_id, order_number, total_vnd = self._create_counter_order(quantity=1)

        # Chuyển user hiện tại thành customer
        app.dependency_overrides[current_user] = lambda: self.customer_user

        # Thử gọi thanh toán tiền mặt
        res_cash = self.client.post(
            f"/api/v1/sales/orders/{order_id}/pay-cash",
            json={"cash_received": total_vnd}
        )
        self.assertEqual(res_cash.status_code, 403, res_cash.text)
        self.assertEqual(res_cash.json()["error"]["code"], "FORBIDDEN")

        # Thử gọi sinh VietQR
        res_qr = self.client.post(f"/api/v1/sales/orders/{order_id}/vietqr")
        self.assertEqual(res_qr.status_code, 403, res_qr.text)

        # Thử gọi confirm transfer
        res_transfer = self.client.post(f"/api/v1/sales/orders/{order_id}/confirm-transfer")
        self.assertEqual(res_transfer.status_code, 403, res_transfer.text)


if __name__ == "__main__":
    unittest.main()


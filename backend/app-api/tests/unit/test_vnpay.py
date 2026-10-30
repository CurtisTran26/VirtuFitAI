from __future__ import annotations

import unittest
from datetime import timedelta
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.services.payments.vnpay import (
    VNPAY_HASH_SECRET,
    VNPAY_TMN_CODE,
    generate_vnpay_signature,
    verify_vnpay_signature,
)
from order_service import create_order
from shared_platform import SessionLocal, current_user, now


class VNPayPaymentTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.user_id = UUID("698cc9c6-1238-4088-8fc4-104eec02af88")
        self.test_user = {
            "id": self.user_id,
            "phone": "0912345678",
            "full_name": "Nguyen Van A",
            "is_active": True,
            "role": "customer",
        }
        app.dependency_overrides[current_user] = lambda: self.test_user

        # Seeded variant: stock = 5, reserved = 0, price = 189000
        self.variant_id = UUID("30000000-0000-4000-8000-000000000001")
        # Ensure initial stock is reset
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
            # Delete reservations, items, status history, and order
            self.db.execute(text("DELETE FROM inventory_adjustments WHERE reason LIKE :r"), {"r": f"%{oid}%"})
            self.db.execute(text("DELETE FROM orders WHERE id = :id"), {"id": oid})
        # Reset stock to 5 and reserved to 0
        self.db.execute(
            text("UPDATE product_variants SET stock_on_hand = 5, reserved_quantity = 0 WHERE id = :v"),
            {"v": self.variant_id}
        )
        self.db.commit()
        self.db.close()
        app.dependency_overrides.clear()

    def _create_test_order(self, quantity: int = 1) -> tuple[UUID, str, int]:
        """Tạo đơn hàng test với phương thức thanh toán VNPay."""
        order_id = create_order(
            self.db,
            customer_id=self.user_id,
            actor_id=self.user_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": quantity}],
            address_snapshot={"name": "Nguyen Van A", "phone": "0912345678", "address": "123 Le Loi, Q1, TP.HCM"},
            idempotency_key=f"test-vnpay-{now().timestamp()}",
        )
        self.db.commit()
        self.created_order_ids.append(order_id)

        row = self.db.execute(
            text("SELECT order_number, total_vnd FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        return order_id, row["order_number"], row["total_vnd"]

    def test_01_create_vnpay_url_success(self):
        """1. Test sinh URL thanh toán VNPay có đầy đủ tham số và chữ ký HMAC-SHA512 chuẩn."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=2)

        payload = {"order_id": str(order_id)}
        res = self.client.post("/api/v1/payments/vnpay/create-url", json=payload)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["order_id"], str(order_id))
        self.assertEqual(data["order_number"], order_number)
        self.assertEqual(data["amount_vnd"], total_vnd)

        payment_url = data["payment_url"]
        self.assertTrue(payment_url.startswith("https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?"))

        # Parse query params from generated URL
        parsed = urlparse(payment_url)
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        self.assertEqual(params.get("vnp_Version"), "2.1.0")
        self.assertEqual(params.get("vnp_Command"), "pay")
        self.assertEqual(params.get("vnp_TmnCode"), VNPAY_TMN_CODE)
        self.assertEqual(params.get("vnp_Amount"), str(total_vnd * 100))
        self.assertEqual(params.get("vnp_CurrCode"), "VND")
        self.assertEqual(params.get("vnp_TxnRef"), order_number)
        self.assertIn("vnp_SecureHash", params)

        # Verify signature
        secure_hash = params["vnp_SecureHash"]
        is_valid = verify_vnpay_signature(VNPAY_HASH_SECRET, params, secure_hash)
        self.assertTrue(is_valid, "Chữ ký HMAC-SHA512 trên URL thanh toán không khớp!")

    def test_02_ipn_success_confirm_order_and_deduct_stock(self):
        """2. Test IPN thành công (vnp_ResponseCode = '00') -> Đơn đổi sang confirmed, kho thực tế được khấu trừ."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=2)

        # Kiểm tra tồn kho trước khi thanh toán: stock_on_hand = 5, reserved_quantity = 2
        variant_before = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant_before["stock_on_hand"], 5)
        self.assertEqual(variant_before["reserved_quantity"], 2)

        # Giả lập tham số callback IPN từ máy chủ VNPay
        ipn_params = {
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": str(total_vnd * 100),
            "vnp_BankCode": "NCB",
            "vnp_BankTranNo": "VNP12345678",
            "vnp_CardType": "ATM",
            "vnp_PayDate": "20261030220000",
            "vnp_OrderInfo": f"Thanh toan don hang {order_number}",
            "vnp_TransactionNo": "14567890",
            "vnp_ResponseCode": "00",
            "vnp_TransactionStatus": "00",
            "vnp_TxnRef": order_number,
            "vnp_SecureHashType": "HMACSHA512",
        }
        ipn_params["vnp_SecureHash"] = generate_vnpay_signature(VNPAY_HASH_SECRET, ipn_params)

        res = self.client.get("/api/v1/payments/vnpay/ipn", params=ipn_params)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"RspCode": "00", "Message": "Confirm Success"})

        # Kiểm tra trạng thái đơn hàng sau IPN
        order_after = self.db.execute(
            text("SELECT status, payment_status, hold_expires_at FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(order_after["status"], "confirmed")
        self.assertEqual(order_after["payment_status"], "paid")
        self.assertIsNone(order_after["hold_expires_at"])

        # Kiểm tra kho sau khi trừ: stock_on_hand = 5 - 2 = 3, reserved_quantity = 2 - 2 = 0
        variant_after = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant_after["stock_on_hand"], 3)
        self.assertEqual(variant_after["reserved_quantity"], 0)

        # Kiểm tra trạng thái reservation chuyển sang 'consumed'
        res_row = self.db.execute(
            text("SELECT status FROM inventory_reservations WHERE order_id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(res_row["status"], "consumed")

    def test_03_ipn_invalid_signature_returns_97(self):
        """3. Test IPN sai chữ ký (vnp_SecureHash giả) -> Trả về RspCode: '97'."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=1)

        ipn_params = {
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": str(total_vnd * 100),
            "vnp_ResponseCode": "00",
            "vnp_TxnRef": order_number,
            "vnp_SecureHash": "fake_invalid_checksum_hash_12345",
        }

        res = self.client.get("/api/v1/payments/vnpay/ipn", params=ipn_params)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"RspCode": "97", "Message": "Invalid Checksum"})

        # Đơn hàng vẫn ở trạng thái pending_confirmation
        order = self.db.execute(text("SELECT status FROM orders WHERE id = :id"), {"id": order_id}).mappings().first()
        self.assertEqual(order["status"], "pending_confirmation")

    def test_04_ipn_invalid_amount_returns_04(self):
        """4. Test IPN sai lệch số tiền -> Trả về RspCode: '04'."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=1)

        # Giả lập VNPay gửi số tiền khác với tổng đơn
        tampered_amount = str((total_vnd + 50000) * 100)
        ipn_params = {
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": tampered_amount,
            "vnp_ResponseCode": "00",
            "vnp_TxnRef": order_number,
        }
        ipn_params["vnp_SecureHash"] = generate_vnpay_signature(VNPAY_HASH_SECRET, ipn_params)

        res = self.client.get("/api/v1/payments/vnpay/ipn", params=ipn_params)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"RspCode": "04", "Message": "Invalid Amount"})

        # Đơn hàng không bị confirm
        order = self.db.execute(text("SELECT status FROM orders WHERE id = :id"), {"id": order_id}).mappings().first()
        self.assertEqual(order["status"], "pending_confirmation")

    def test_05_ipn_idempotency_returns_02_and_no_double_deduction(self):
        """5. Test gọi IPN 2 lần liên tiếp cho cùng 1 đơn -> Lần 2 trả RspCode: '02' và không trừ kho 2 lần."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=1)

        ipn_params = {
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": str(total_vnd * 100),
            "vnp_ResponseCode": "00",
            "vnp_TxnRef": order_number,
        }
        ipn_params["vnp_SecureHash"] = generate_vnpay_signature(VNPAY_HASH_SECRET, ipn_params)

        # Lần 1: Thành công
        res1 = self.client.get("/api/v1/payments/vnpay/ipn", params=ipn_params)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json(), {"RspCode": "00", "Message": "Confirm Success"})

        # Kiểm tra tồn kho sau lần 1: 5 - 1 = 4
        stock_after_1 = self.db.execute(
            text("SELECT stock_on_hand FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).scalar_one()
        self.assertEqual(stock_after_1, 4)

        # Lần 2: Gọi lại IPN lần 2 cho cùng 1 đơn đã confirmed
        res2 = self.client.get("/api/v1/payments/vnpay/ipn", params=ipn_params)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json(), {"RspCode": "02", "Message": "Order already confirmed"})

        # Tồn kho vẫn giữ nguyên là 4 (không bị trừ lần 2)
        stock_after_2 = self.db.execute(
            text("SELECT stock_on_hand FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).scalar_one()
        self.assertEqual(stock_after_2, 4)

    def test_06_vnpay_return_endpoint(self):
        """6. Test endpoint Return URL trả về thông tin tóm tắt và xác thực chữ ký cho khách."""
        order_id, order_number, total_vnd = self._create_test_order(quantity=1)

        return_params = {
            "vnp_TmnCode": VNPAY_TMN_CODE,
            "vnp_Amount": str(total_vnd * 100),
            "vnp_ResponseCode": "00",
            "vnp_TransactionNo": "99988877",
            "vnp_TxnRef": order_number,
        }
        return_params["vnp_SecureHash"] = generate_vnpay_signature(VNPAY_HASH_SECRET, return_params)

        res = self.client.get("/api/v1/payments/vnpay/return", params=return_params)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_success"])
        self.assertEqual(data["order_number"], order_number)
        self.assertEqual(data["amount_vnd"], total_vnd)
        self.assertEqual(data["response_code"], "00")
        self.assertIn("thành công", data["message"].lower())


if __name__ == "__main__":
    unittest.main()


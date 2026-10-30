from __future__ import annotations

import unittest
from datetime import timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.services.payments.reconciliation import (
    build_querydr_payload,
    run_reconciliation_batch,
)
from order_service import create_order
from shared_platform import SessionLocal, current_user, now


class VNPayReconciliationTestCase(unittest.TestCase):
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

    def _create_vnpay_order(self, age_minutes: int = 15, quantity: int = 1) -> tuple[UUID, str]:
        """Tạo đơn hàng VNPay pending_confirmation với thời gian created_at giả lập trong quá khứ."""
        order_id = create_order(
            self.db,
            customer_id=self.customer_id,
            actor_id=self.customer_id,
            order_type="online",
            payment_method="vnpay",
            lines=[{"variant_id": self.variant_id, "quantity": quantity}],
            address_snapshot={"name": "Nguyen Van A", "phone": "0912345678", "address": "123 Le Loi, TP.HCM"},
            idempotency_key=f"test-rec-{now().timestamp()}-{age_minutes}",
        )
        # Giả lập lùi thời gian created_at để qua ngưỡng quét 10 phút
        # Đồng thời đảm bảo hold_expires_at vẫn còn hạn (30 phút nữa) để confirm_order không bị expired
        past_time = now() - timedelta(minutes=age_minutes)
        future_hold = now() + timedelta(minutes=20)
        self.db.execute(
            text("UPDATE orders SET created_at = :created, hold_expires_at = :hold WHERE id = :id"),
            {"created": past_time, "hold": future_hold, "id": order_id}
        )
        self.db.commit()
        self.created_order_ids.append(order_id)

        order_number = self.db.execute(
            text("SELECT order_number FROM orders WHERE id = :id"),
            {"id": order_id}
        ).scalar_one()
        return order_id, order_number

    def test_01_worker_scans_only_orders_older_than_10_minutes(self):
        """1. Test worker quét đúng các đơn VNPay treo quá 10 phút và bỏ qua đơn mới tạo."""
        # Đơn 1: Mới tạo 2 phút trước (< 10 phút)
        id_fresh, _ = self._create_vnpay_order(age_minutes=2)
        # Đơn 2: Đã tạo 12 phút trước (> 10 phút)
        id_stale, _ = self._create_vnpay_order(age_minutes=12)

        # Mock caller trả về mã lỗi (chưa thanh toán) để kiểm tra việc quét
        def mock_caller(payload):
            return {"vnp_ResponseCode": "01", "vnp_TransactionStatus": "01"}

        result = run_reconciliation_batch(self.db, lookback_minutes=10, querydr_caller=mock_caller)
        self.assertEqual(result["scanned_orders"], 1)
        self.assertEqual(result["processed_orders"], 1)
        self.assertEqual(result["confirmed_orders"], 0)

        # Kiểm tra đơn 12 phút đã được đối soát 1 lần
        order_stale = self.db.execute(text("SELECT address_snapshot FROM orders WHERE id = :id"), {"id": id_stale}).scalar_one()
        self.assertEqual(order_stale.get("reconciliation_attempts"), 1)

        # Kiểm tra đơn 2 phút không bị quét
        order_fresh = self.db.execute(text("SELECT address_snapshot FROM orders WHERE id = :id"), {"id": id_fresh}).scalar_one()
        self.assertNotIn("reconciliation_attempts", order_fresh)

    def test_02_querydr_success_confirms_order_and_deducts_stock(self):
        """2. Test mock API VNPay QueryDR trả về '00' -> Đơn hàng tự động được xác nhận và khấu trừ kho."""
        order_id, order_number = self._create_vnpay_order(age_minutes=15, quantity=2)

        # Mock VNPay QueryDR phản hồi đã thanh toán thành công
        def mock_caller_success(payload):
            self.assertEqual(payload["vnp_TxnRef"], order_number)
            self.assertEqual(payload["vnp_Command"], "querydr")
            return {
                "vnp_ResponseCode": "00",
                "vnp_TransactionStatus": "00",
                "vnp_Amount": "37800000",
                "vnp_BankCode": "NCB",
            }

        result = run_reconciliation_batch(self.db, lookback_minutes=10, querydr_caller=mock_caller_success)
        self.assertEqual(result["confirmed_orders"], 1)

        # Kiểm tra trạng thái đơn hàng sau đối soát
        order = self.db.execute(
            text("SELECT status, payment_status FROM orders WHERE id = :id"),
            {"id": order_id}
        ).mappings().first()
        self.assertEqual(order["status"], "confirmed")
        self.assertEqual(order["payment_status"], "paid")

        # Kiểm tra tồn kho thực tế bị khấu trừ: 5 - 2 = 3
        variant = self.db.execute(
            text("SELECT stock_on_hand, reserved_quantity FROM product_variants WHERE id = :v"),
            {"v": self.variant_id}
        ).mappings().first()
        self.assertEqual(variant["stock_on_hand"], 3)
        self.assertEqual(variant["reserved_quantity"], 0)

        # Kiểm tra nhật ký lịch sử đơn
        notes = self.db.execute(
            text("SELECT note FROM order_status_history WHERE order_id = :id"),
            {"id": order_id}
        ).scalars().all()
        self.assertTrue(any("QueryDR" in n for n in notes), f"Không tìm thấy note QueryDR trong lịch sử: {notes}")

    def test_03_already_paid_order_not_scanned_again(self):
        """3. Test đơn hàng đã thanh toán (payment_status='paid') không bị worker quét lại."""
        order_id, _ = self._create_vnpay_order(age_minutes=15)

        # Cập nhật đơn này thành 'paid' và 'confirmed'
        self.db.execute(
            text("UPDATE orders SET status = 'confirmed', payment_status = 'paid', updated_at = now() WHERE id = :id"),
            {"id": order_id}
        )
        self.db.commit()

        call_count = 0

        def mock_caller(payload):
            nonlocal call_count
            call_count += 1
            return {"vnp_ResponseCode": "00", "vnp_TransactionStatus": "00"}

        result = run_reconciliation_batch(self.db, lookback_minutes=10, querydr_caller=mock_caller)
        self.assertEqual(result["scanned_orders"], 0)
        self.assertEqual(call_count, 0)

    def test_04_concurrency_skip_locked(self):
        """4. Test cơ chế khóa chống xung đột giữa QueryDR worker và Webhook IPN (FOR UPDATE SKIP LOCKED)."""
        order_id, _ = self._create_vnpay_order(age_minutes=15)

        # Mở một session độc lập và giữ khóa FOR UPDATE trên đơn hàng (giả lập webhook IPN đang xử lý)
        session2 = SessionLocal()
        session2.execute(text("SELECT id FROM orders WHERE id = :id FOR UPDATE"), {"id": order_id})

        # Worker chạy ở session chính sẽ SKIP LOCKED đơn hàng này
        result = run_reconciliation_batch(self.db, lookback_minutes=10)
        self.assertEqual(result["scanned_orders"], 0, "Worker không được đụng độ với row đang bị IPN khóa!")

        session2.rollback()
        session2.close()

    def test_05_reconciliation_api_endpoint_rbac(self):
        """5. Test endpoint kích hoạt đối soát /api/v1/payments/vnpay/reconcile."""
        # 1. Gọi bằng quyền Admin -> Thành công 200
        app.dependency_overrides[current_user] = lambda: self.admin_user
        res_admin = self.client.post("/api/v1/payments/vnpay/reconcile")
        self.assertEqual(res_admin.status_code, 200, res_admin.text)
        data = res_admin.json()
        self.assertIn("scanned_orders", data)
        self.assertIn("confirmed_orders", data)

        # 2. Gọi bằng quyền Customer -> Chặn 403 Forbidden
        app.dependency_overrides[current_user] = lambda: self.customer_user
        res_cust = self.client.post("/api/v1/payments/vnpay/reconcile")
        self.assertEqual(res_cust.status_code, 403)
        self.assertEqual(res_cust.json()["error"]["code"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()

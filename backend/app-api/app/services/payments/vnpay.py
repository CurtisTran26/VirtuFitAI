from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote_plus
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail
from order_service import confirm_order
from shared_platform import now

# Configuration from environment with standard VNPay sandbox defaults
VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE", "2QXUI4J4")
VNPAY_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET", "RAIQUND2GHRLKTUTZLPHXD2XFXA53MNN")
VNPAY_URL = os.getenv("VNPAY_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL", "http://localhost:8000/api/v1/payments/vnpay/return")


def get_vnpay_hash_data(params: dict[str, Any]) -> str:
    """Xây dựng chuỗi ký tự hash_data theo chuẩn VNPay 2.1.0 (sắp xếp alphabet, quote_plus)."""
    filtered = {
        k: str(v)
        for k, v in params.items()
        if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType") and v is not None and str(v) != ""
    }
    sorted_items = sorted(filtered.items())
    return "&".join(f"{quote_plus(k)}={quote_plus(str(v))}" for k, v in sorted_items)


def generate_vnpay_signature(secret: str, params: dict[str, Any]) -> str:
    """Tạo chữ ký HMAC-SHA512 từ các tham số VNPay."""
    hash_data = get_vnpay_hash_data(params)
    return hmac.new(secret.encode("utf-8"), hash_data.encode("utf-8"), hashlib.sha512).hexdigest()


def verify_vnpay_signature(secret: str, params: dict[str, Any], received_hash: str) -> bool:
    """Xác minh tính hợp lệ của chữ ký VNPay (chống giả mạo request)."""
    if not received_hash:
        return False
    expected = generate_vnpay_signature(secret, params)
    return hmac.compare_digest(expected.lower(), received_hash.lower())


def create_vnpay_payment_url(
    db: Session,
    order_id: UUID,
    customer_id: UUID | None = None,
    client_ip: str = "127.0.0.1",
    bank_code: str | None = None,
) -> dict[str, Any]:
    """Sinh URL thanh toán VNPay chuẩn version 2.1.0."""
    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_method, hold_expires_at, customer_id
               FROM orders WHERE id = :id"""),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    if customer_id and order["customer_id"] and order["customer_id"] != customer_id:
        fail(403, "FORBIDDEN", "Bạn không có quyền truy cập đơn hàng này.")

    if order["payment_method"] != "vnpay":
        fail(400, "INVALID_PAYMENT_METHOD", "Phương thức thanh toán của đơn hàng không phải VNPay.")

    if order["status"] != "pending_confirmation":
        fail(409, "ORDER_STATE_CONFLICT", f"Đơn hàng đang ở trạng thái '{order['status']}', không thể thanh toán.")

    if order["hold_expires_at"] and order["hold_expires_at"] <= now():
        fail(409, "HOLD_EXPIRED", "Thời gian giữ chỗ cho đơn hàng đã hết hạn. Vui lòng tạo đơn mới.")

    vn_tz = timezone(timedelta(hours=7))
    current_time = datetime.now(vn_tz)
    create_date = current_time.strftime("%Y%m%d%H%M%S")
    expire_date = (current_time + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S")

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNPAY_TMN_CODE,
        "vnp_Amount": str(order["total_vnd"] * 100),
        "vnp_CreateDate": create_date,
        "vnp_CurrCode": "VND",
        "vnp_IpAddr": client_ip,
        "vnp_Locale": "vn",
        "vnp_OrderInfo": f"Thanh toan don hang {order['order_number']}",
        "vnp_OrderType": "other",
        "vnp_ReturnUrl": VNPAY_RETURN_URL,
        "vnp_TxnRef": order["order_number"],
        "vnp_ExpireDate": expire_date,
    }

    if bank_code:
        params["vnp_BankCode"] = bank_code

    hash_data = get_vnpay_hash_data(params)
    signature = generate_vnpay_signature(VNPAY_HASH_SECRET, params)
    payment_url = f"{VNPAY_URL}?{hash_data}&vnp_SecureHash={signature}"

    return {
        "payment_url": payment_url,
        "order_id": order["id"],
        "order_number": order["order_number"],
        "amount_vnd": order["total_vnd"],
    }


def process_vnpay_ipn(db: Session, params: dict[str, Any]) -> dict[str, str]:
    """Tiếp nhận và xử lý Webhook Server-to-Server từ máy chủ VNPay."""
    received_hash = params.get("vnp_SecureHash", "")
    if not received_hash or not verify_vnpay_signature(VNPAY_HASH_SECRET, params, received_hash):
        return {"RspCode": "97", "Message": "Invalid Checksum"}

    order_number = params.get("vnp_TxnRef")
    if not order_number:
        return {"RspCode": "01", "Message": "Order Not Found"}

    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_status, hold_expires_at, created_by
               FROM orders WHERE order_number = :num FOR UPDATE"""),
        {"num": order_number}
    ).mappings().first()

    if not order:
        return {"RspCode": "01", "Message": "Order Not Found"}

    raw_amount = params.get("vnp_Amount")
    try:
        amount_vnd = int(raw_amount) // 100
    except (ValueError, TypeError):
        return {"RspCode": "04", "Message": "Invalid Amount"}

    if amount_vnd != order["total_vnd"]:
        return {"RspCode": "04", "Message": "Invalid Amount"}

    # Chống xử lý trùng lặp (Idempotent)
    if order["status"] == "confirmed" or order["payment_status"] == "paid":
        return {"RspCode": "02", "Message": "Order already confirmed"}

    response_code = params.get("vnp_ResponseCode")
    if response_code == "00":
        confirm_result = confirm_order(db, order["id"], actor_id=order["created_by"])
        if confirm_result == "confirmed":
            db.execute(
                text("UPDATE orders SET payment_status = 'paid', updated_at = now() WHERE id = :id"),
                {"id": order["id"]}
            )
            db.commit()
            return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            # Đơn hàng đã hết hạn giữ chỗ trước khi thanh toán
            db.commit()
            return {"RspCode": "00", "Message": "Confirm Success"}
    else:
        # Thanh toán thất bại hoặc khách hủy trên cổng VNPay
        db.commit()
        return {"RspCode": "00", "Message": "Confirm Success"}


def process_vnpay_return(params: dict[str, Any]) -> dict[str, Any]:
    """Xử lý redirect trình duyệt của khách hàng sau khi thanh toán trên VNPay."""
    received_hash = params.get("vnp_SecureHash", "")
    is_valid_hash = verify_vnpay_signature(VNPAY_HASH_SECRET, params, received_hash)
    response_code = params.get("vnp_ResponseCode", "")
    is_success = bool(is_valid_hash and response_code == "00")

    raw_amount = params.get("vnp_Amount", 0)
    try:
        amount_vnd = int(raw_amount) // 100
    except (ValueError, TypeError):
        amount_vnd = 0

    message = "Thanh toán giao dịch thành công."
    if not is_valid_hash:
        message = "Chữ ký bảo mật không hợp lệ (Invalid Checksum)."
    elif response_code == "24":
        message = "Giao dịch đã bị khách hàng hủy bỏ."
    elif response_code != "00":
        message = f"Thanh toán không thành công (Mã phản hồi VNPay: {response_code})."

    return {
        "is_success": is_success,
        "order_number": params.get("vnp_TxnRef", ""),
        "amount_vnd": amount_vnd,
        "transaction_no": params.get("vnp_TransactionNo"),
        "response_code": response_code,
        "message": message,
    }


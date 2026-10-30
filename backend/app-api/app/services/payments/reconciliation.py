from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.payments.vnpay import (
    VNPAY_HASH_SECRET,
    VNPAY_TMN_CODE,
)
from order_service import confirm_order
from shared_platform import SessionLocal, now

logger = logging.getLogger(__name__)

# URL API QueryDR của VNPay Sandbox
VNPAY_QUERYDR_URL = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"

_reconciliation_task: asyncio.Task | None = None


def build_querydr_payload(order: dict[str, Any], client_ip: str = "127.0.0.1") -> dict[str, Any]:
    """Sinh payload truy vấn giao dịch VNPay QueryDR chuẩn version 2.1.0."""
    vn_tz = timezone(timedelta(hours=7))
    current_time = datetime.now(vn_tz)
    create_date = current_time.strftime("%Y%m%d%H%M%S")

    order_created_at = order.get("created_at")
    if isinstance(order_created_at, datetime):
        txn_date = order_created_at.astimezone(vn_tz).strftime("%Y%m%d%H%M%S")
    else:
        txn_date = create_date

    request_id = f"QDR-{order['order_number']}-{current_time.strftime('%H%M%S%f')[:10]}"
    order_info = f"Truy van giao dich don hang {order['order_number']}"

    # Định dạng chuỗi hash QueryDR v2.1.0:
    # requestId|version|command|tmnCode|txnRef|txnDate|createDate|ipAddr|orderInfo
    hash_data = (
        f"{request_id}|2.1.0|querydr|{VNPAY_TMN_CODE}|{order['order_number']}|"
        f"{txn_date}|{create_date}|{client_ip}|{order_info}"
    )
    signature = hmac.new(VNPAY_HASH_SECRET.encode("utf-8"), hash_data.encode("utf-8"), hashlib.sha512).hexdigest()

    return {
        "vnp_RequestId": request_id,
        "vnp_Version": "2.1.0",
        "vnp_Command": "querydr",
        "vnp_TmnCode": VNPAY_TMN_CODE,
        "vnp_TxnRef": order["order_number"],
        "vnp_OrderInfo": order_info,
        "vnp_TransactionDate": txn_date,
        "vnp_CreateDate": create_date,
        "vnp_IpAddr": client_ip,
        "vnp_SecureHash": signature,
    }


def query_vnpay_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    """Gửi request tới API QueryDR của cổng VNPay."""
    try:
        import httpx
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(VNPAY_QUERYDR_URL, json=payload)
            if resp.status_code == 200:
                return resp.json()
            return {"vnp_ResponseCode": "99", "vnp_Message": f"HTTP Error {resp.status_code}"}
    except Exception as exc:
        logger.warning(f"Error querying VNPay QueryDR: {exc}")
        return {"vnp_ResponseCode": "99", "vnp_Message": str(exc)}


def run_reconciliation_batch(
    db: Session,
    lookback_minutes: int = 10,
    limit: int = 50,
    querydr_caller: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Quét và đối soát định kỳ các đơn hàng VNPay bị treo quá 10 phút."""
    caller = querydr_caller or query_vnpay_transaction
    cutoff = now() - timedelta(minutes=lookback_minutes)

    # Sử dụng FOR UPDATE SKIP LOCKED để ngăn worker chạy đè lên Webhook IPN đang xử lý cùng lúc
    stale_orders = db.execute(
        text("""
            SELECT id, order_number, total_vnd, status, payment_status, created_at, created_by, hold_expires_at, address_snapshot
            FROM orders
            WHERE payment_method = 'vnpay'
              AND status = 'pending_confirmation'
              AND payment_status = 'unpaid'
              AND created_at <= :cutoff
            ORDER BY created_at ASC
            LIMIT :limit
            FOR UPDATE SKIP LOCKED
        """),
        {"cutoff": cutoff, "limit": limit}
    ).mappings().all()

    processed_count = 0
    confirmed_count = 0
    skipped_count = 0

    for order in stale_orders:
        processed_count += 1
        addr = dict(order.get("address_snapshot") or {})
        attempts = addr.get("reconciliation_attempts", 0)

        # Cơ chế Exponential Backoff: Thử tối đa 3 chu kỳ rồi dừng
        if attempts >= 3:
            skipped_count += 1
            continue

        payload = build_querydr_payload(dict(order))
        result = caller(payload)

        # Cập nhật số lần đối soát
        addr["reconciliation_attempts"] = attempts + 1
        addr["last_reconciliation_at"] = str(now())

        # Nếu ngân hàng phản hồi đã thanh toán thành công
        if result.get("vnp_ResponseCode") == "00" and result.get("vnp_TransactionStatus") == "00":
            confirm_res = confirm_order(db, order["id"], actor_id=order["created_by"])
            if confirm_res == "confirmed":
                db.execute(
                    text("""UPDATE orders
                           SET payment_status = 'paid',
                               address_snapshot = CAST(:addr AS jsonb),
                               updated_at = now()
                           WHERE id = :id"""),
                    {"addr": json.dumps(addr), "id": order["id"]}
                )
                db.execute(
                    text("""INSERT INTO order_status_history(order_id, changed_by, from_status, to_status, note)
                           VALUES(:order_id, :actor_id, 'confirmed', 'confirmed', :note)"""),
                    {
                        "order_id": order["id"],
                        "actor_id": order["created_by"],
                        "note": "Reconciliation worker: Confirmed order via QueryDR",
                    }
                )
                db.commit()
                confirmed_count += 1
        else:
            db.execute(
                text("UPDATE orders SET address_snapshot = CAST(:addr AS jsonb), updated_at = now() WHERE id = :id"),
                {"addr": json.dumps(addr), "id": order["id"]}
            )
            db.commit()

    return {
        "scanned_orders": len(stale_orders),
        "processed_orders": processed_count,
        "confirmed_orders": confirmed_count,
        "skipped_orders": skipped_count,
    }


async def reconciliation_loop(interval_seconds: int = 300):
    """Tiến trình ngầm quét định kỳ (mặc định mỗi 5 phút = 300s)."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            db = SessionLocal()
            try:
                run_reconciliation_batch(db, lookback_minutes=10)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in reconciliation background loop: {e}")


def start_reconciliation_worker():
    """Khởi động worker quét đối soát chạy nền trong FastAPI."""
    global _reconciliation_task
    if _reconciliation_task is None or _reconciliation_task.done():
        try:
            loop = asyncio.get_running_loop()
            _reconciliation_task = loop.create_task(reconciliation_loop())
            logger.info("Reconciliation background worker started successfully.")
        except RuntimeError:
            pass


def stop_reconciliation_worker():
    """Dừng worker chạy nền khi tắt ứng dụng."""
    global _reconciliation_task
    if _reconciliation_task and not _reconciliation_task.done():
        _reconciliation_task.cancel()
        _reconciliation_task = None

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote_plus
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail
from app.schemas.sales.sales import CounterOrderCreate
from order_service import confirm_order, create_order

VIETQR_BANK_ID = os.getenv("VIETQR_BANK_ID", "970422")  # Mã BIN ngân hàng Quân Đội (MB Bank)
VIETQR_BANK_NAME = os.getenv("VIETQR_BANK_NAME", "MBBank")
VIETQR_ACCOUNT_NO = os.getenv("VIETQR_ACCOUNT_NO", "0912345678")
VIETQR_ACCOUNT_NAME = os.getenv("VIETQR_ACCOUNT_NAME", "CONG TY TNHH VIRTUFIT AI")
VIETQR_TEMPLATE = os.getenv("VIETQR_TEMPLATE", "compact2")


def crc16_ccitt(data: str) -> str:
    """Tính checksum CRC16-CCITT chuẩn EMVCo."""
    crc = 0xFFFF
    for byte in data.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def generate_emvco_qr(bank_bin: str, account_no: str, amount: int, memo: str) -> str:
    """Tạo chuỗi dữ liệu mã QR chuẩn quốc tế EMVCo / Napas 247."""
    guid_field = "0010A000000727"
    bank_field = f"00{len(bank_bin):02d}{bank_bin}"
    acc_field = f"01{len(account_no):02d}{account_no}"
    org_content = f"{bank_field}{acc_field}"
    org_field = f"01{len(org_content):02d}{org_content}"
    service_field = "0208QRIBFTTA"
    tag38_content = f"{guid_field}{org_field}{service_field}"
    tag38 = f"38{len(tag38_content):02d}{tag38_content}"

    tag53 = "5303704"
    amount_str = str(amount)
    tag54 = f"54{len(amount_str):02d}{amount_str}"
    tag58 = "5802VN"
    memo_field = f"08{len(memo):02d}{memo}"
    tag62 = f"62{len(memo_field):02d}{memo_field}"

    payload_before_crc = f"000201010212{tag38}{tag53}{tag54}{tag58}{tag62}6304"
    crc = crc16_ccitt(payload_before_crc)
    return f"{payload_before_crc}{crc}"


def create_counter_order(db: Session, staff_id: UUID, payload: CounterOrderCreate) -> dict[str, Any]:
    """Tạo đơn hàng tại quầy (bán hàng trực tiếp cho khách vãng lai hoặc thành viên)."""
    order_id = create_order(
        db,
        customer_id=payload.customer_id,
        actor_id=staff_id,
        order_type="counter",
        payment_method=payload.payment_method,
        lines=[i.model_dump() for i in payload.items],
        address_snapshot={"type": "in_store_counter", "note": payload.note or "Đơn bán hàng trực tiếp tại quầy"},
    )
    db.commit()

    order = db.execute(
        text("""SELECT id, order_number, order_type, status, payment_method, payment_status, total_vnd
               FROM orders WHERE id = :id"""),
        {"id": order_id}
    ).mappings().first()

    return dict(order)


def pay_order_cash(db: Session, order_id: UUID, staff_id: UUID, cash_received: int) -> dict[str, Any]:
    """Xử lý thanh toán tiền mặt tại quầy và hoàn tất đơn hàng."""
    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_status
               FROM orders WHERE id = :id FOR UPDATE"""),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    if order["status"] == "completed" or order["payment_status"] == "paid":
        fail(409, "ORDER_ALREADY_PAID", "Đơn hàng này đã được thanh toán hoàn tất.")

    if order["status"] != "pending_confirmation":
        fail(409, "ORDER_STATE_CONFLICT", f"Đơn hàng đang ở trạng thái '{order['status']}', không thể thanh toán.")

    if cash_received < order["total_vnd"]:
        fail(
            400,
            "INVALID_CASH_AMOUNT",
            f"Số tiền khách đưa ({cash_received:,} VND) không đủ để thanh toán tổng đơn ({order['total_vnd']:,} VND)."
        )

    cash_change = cash_received - order["total_vnd"]

    # Khấu trừ tồn kho qua confirm_order
    confirm_order(db, order["id"], actor_id=staff_id)

    # Chuyển trạng thái đơn sang completed và paid
    db.execute(
        text("""UPDATE orders
               SET status = 'completed',
                   payment_status = 'paid',
                   payment_method = 'cash',
                   updated_at = now()
               WHERE id = :id"""),
        {"id": order["id"]}
    )

    db.execute(
        text("""INSERT INTO order_status_history(order_id, changed_by, from_status, to_status, note)
               VALUES(:order_id, :staff_id, 'confirmed', 'completed', :note)"""),
        {
            "order_id": order["id"],
            "staff_id": staff_id,
            "note": f"Thanh toán tiền mặt tại quầy: Tiền nhận {cash_received:,} VND, Tiền thừa {cash_change:,} VND",
        }
    )
    db.commit()

    return {
        "order_id": order["id"],
        "order_number": order["order_number"],
        "total_vnd": order["total_vnd"],
        "cash_received": cash_received,
        "cash_change": cash_change,
        "status": "completed",
        "payment_status": "paid",
        "staff_id": staff_id,
        "message": f"Thanh toán tiền mặt thành công. Tiền thừa trả khách: {cash_change:,} VND.",
    }


def generate_vietqr_payload(db: Session, order_id: UUID) -> dict[str, Any]:
    """Sinh payload và link mã QR chuyển khoản VietQR Napas 247 tại quầy."""
    order = db.execute(
        text("SELECT id, order_number, total_vnd, status, payment_status FROM orders WHERE id = :id"),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    if order["status"] == "completed" or order["payment_status"] == "paid":
        fail(409, "ORDER_ALREADY_PAID", "Đơn hàng này đã được thanh toán hoàn tất.")

    if order["status"] != "pending_confirmation":
        fail(409, "ORDER_STATE_CONFLICT", f"Đơn hàng đang ở trạng thái '{order['status']}', không thể tạo mã chuyển khoản.")

    transfer_content = order["order_number"]
    qr_image_url = (
        f"https://img.vietqr.io/image/{VIETQR_BANK_ID}-{VIETQR_ACCOUNT_NO}-{VIETQR_TEMPLATE}.png"
        f"?amount={order['total_vnd']}&addInfo={transfer_content}&accountName={quote_plus(VIETQR_ACCOUNT_NAME)}"
    )

    emvco_payload = generate_emvco_qr(
        bank_bin=VIETQR_BANK_ID,
        account_no=VIETQR_ACCOUNT_NO,
        amount=order["total_vnd"],
        memo=transfer_content,
    )

    return {
        "order_id": order["id"],
        "order_number": order["order_number"],
        "bank_id": VIETQR_BANK_ID,
        "bank_name": VIETQR_BANK_NAME,
        "account_no": VIETQR_ACCOUNT_NO,
        "account_name": VIETQR_ACCOUNT_NAME,
        "amount_vnd": order["total_vnd"],
        "transfer_content": transfer_content,
        "qr_image_url": qr_image_url,
        "emvco_payload": emvco_payload,
    }


def confirm_bank_transfer(db: Session, order_id: UUID, staff_id: UUID) -> dict[str, Any]:
    """Nhân viên quầy xác nhận tiền đã vào tài khoản cửa hàng -> Hoàn tất đơn hàng."""
    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_status
               FROM orders WHERE id = :id FOR UPDATE"""),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    if order["status"] == "completed" or order["payment_status"] == "paid":
        fail(409, "ORDER_ALREADY_PAID", "Đơn hàng này đã được thanh toán hoàn tất.")

    if order["status"] != "pending_confirmation":
        fail(409, "ORDER_STATE_CONFLICT", f"Đơn hàng đang ở trạng thái '{order['status']}', không thể xác nhận chuyển khoản.")

    # Khấu trừ tồn kho qua confirm_order
    confirm_order(db, order["id"], actor_id=staff_id)

    db.execute(
        text("""UPDATE orders
               SET status = 'completed',
                   payment_status = 'paid',
                   payment_method = 'bank_transfer',
                   updated_at = now()
               WHERE id = :id"""),
        {"id": order["id"]}
    )

    db.execute(
        text("""INSERT INTO order_status_history(order_id, changed_by, from_status, to_status, note)
               VALUES(:order_id, :staff_id, 'confirmed', 'completed', :note)"""),
        {
            "order_id": order["id"],
            "staff_id": staff_id,
            "note": "Nhân viên xác nhận đã nhận đủ tiền chuyển khoản VietQR tại quầy",
        }
    )
    db.commit()

    return {
        "order_id": order["id"],
        "order_number": order["order_number"],
        "total_vnd": order["total_vnd"],
        "status": "completed",
        "payment_status": "paid",
        "payment_method": "bank_transfer",
        "staff_id": staff_id,
        "message": "Xác nhận chuyển khoản VietQR thành công. Đơn hàng đã hoàn tất.",
    }


from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail
from app.schemas.admin.orders import OrderRefundRequest
from shared_platform import now


def refund_and_restock_order(
    db: Session,
    order_id: UUID,
    admin_id: UUID,
    payload: OrderRefundRequest,
) -> dict[str, Any]:
    """Hoàn tiền đơn hàng đã thanh toán và tự động hoàn trả tồn kho sản phẩm."""
    order = db.execute(
        text("""SELECT id, order_number, total_vnd, status, payment_status, address_snapshot
               FROM orders WHERE id = :id FOR UPDATE"""),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    # Validate điều kiện hoàn tiền
    if order["payment_status"] == "refunded":
        fail(409, "ORDER_ALREADY_REFUNDED", "Đơn hàng này đã được hoàn tiền trước đó.")

    if order["payment_status"] != "paid":
        fail(
            400,
            "ORDER_NOT_PAID",
            f"Không thể hoàn tiền cho đơn hàng chưa thanh toán. Trạng thái thanh toán hiện tại: '{order['payment_status']}'."
        )

    # Tính toán số tiền hoàn
    refund_amount = payload.refund_amount if payload.refund_amount is not None else order["total_vnd"]
    if refund_amount > order["total_vnd"]:
        fail(
            400,
            "INVALID_REFUND_AMOUNT",
            f"Số tiền hoàn ({refund_amount:,} VND) không được vượt quá tổng giá trị đơn hàng ({order['total_vnd']:,} VND)."
        )

    # Restock Logic: Hoàn trả số lượng của từng món trong order_items về product_variants.stock_on_hand
    items = db.execute(
        text("""SELECT id, variant_id, quantity, product_name_snapshot
               FROM order_items WHERE order_id = :id"""),
        {"id": order_id}
    ).mappings().all()

    restocked_items = []
    for item in items:
        variant_id = item["variant_id"]
        quantity = item["quantity"]

        # Lấy tồn kho hiện tại với lock
        current_stock = db.execute(
            text("SELECT stock_on_hand FROM product_variants WHERE id = :v FOR UPDATE"),
            {"v": variant_id}
        ).scalar_one()

        new_stock = current_stock + quantity
        db.execute(
            text("UPDATE product_variants SET stock_on_hand = :s, updated_at = now() WHERE id = :v"),
            {"s": new_stock, "v": variant_id}
        )

        # Ghi nhật ký vào inventory_adjustments
        db.execute(
            text("""INSERT INTO inventory_adjustments(variant_id, changed_by, delta, quantity_before, quantity_after, reason)
                   VALUES(:v, :admin, :delta, :before, :after, :reason)"""),
            {
                "v": variant_id,
                "admin": admin_id,
                "delta": quantity,
                "before": current_stock,
                "after": new_stock,
                "reason": f"Order {order['order_number']} refunded & restocked by Admin",
            }
        )

        restocked_items.append({
            "variant_id": variant_id,
            "quantity_restocked": quantity,
            "stock_before": current_stock,
            "stock_after": new_stock,
        })

    # Cập nhật inventory_reservations nếu còn bản ghi chưa released
    db.execute(
        text("UPDATE inventory_reservations SET status = 'released', expires_at = NULL, updated_at = now() WHERE order_id = :id AND status != 'released'"),
        {"id": order_id}
    )

    # Cập nhật trạng thái đơn hàng
    refund_time = now()
    addr = dict(order.get("address_snapshot") or {})
    addr["refund_info"] = {
        "refund_amount": refund_amount,
        "refund_reason": payload.reason,
        "refunded_by": str(admin_id),
        "refunded_at": str(refund_time),
    }

    db.execute(
        text("""UPDATE orders
               SET status = 'cancelled',
                   payment_status = 'refunded',
                   cancelled_at = now(),
                   address_snapshot = CAST(:addr AS jsonb),
                   updated_at = now()
               WHERE id = :id"""),
        {"addr": json.dumps(addr), "id": order_id}
    )

    # Ghi log lịch sử đơn hàng
    db.execute(
        text("""INSERT INTO order_status_history(order_id, changed_by, from_status, to_status, note)
               VALUES(:id, :admin, :old_status, 'cancelled', :note)"""),
        {
            "id": order_id,
            "admin": admin_id,
            "old_status": order["status"],
            "note": f"Hoàn tiền {refund_amount:,} VND bởi Admin. Lý do: {payload.reason}",
        }
    )
    db.commit()

    return {
        "order_id": order["id"],
        "order_number": order["order_number"],
        "total_vnd": order["total_vnd"],
        "refund_amount": refund_amount,
        "status": "cancelled",
        "payment_status": "refunded",
        "refund_reason": payload.reason,
        "admin_id": admin_id,
        "refunded_at": refund_time,
        "restocked_items": restocked_items,
        "message": f"Hoàn tiền {refund_amount:,} VND và hoàn trả tồn kho thành công cho đơn hàng {order['order_number']}.",
    }


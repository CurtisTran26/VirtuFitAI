from __future__ import annotations

import json
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail
from app.schemas.warehouse.warehouse import WarehouseStatusUpdateRequest
from order_service import update_order_status
from shared_platform import now


def list_warehouse_orders(
    db: Session,
    status: str | None = None,
    order_type: str | None = None,
    date_filter: date | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    """Lấy danh sách đơn hàng cần xử lý đóng gói và giao nhận cho nhân viên kho."""
    conditions = []
    params: dict[str, Any] = {"limit": limit, "offset": (page - 1) * limit}

    if status:
        conditions.append("o.status = :status")
        params["status"] = status
    if order_type:
        conditions.append("o.order_type = :order_type")
        params["order_type"] = order_type
    if date_filter:
        conditions.append("DATE(o.created_at) = :date_filter")
        params["date_filter"] = date_filter

    where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    count_query = text(f"SELECT count(*) FROM orders o{where_clause}")
    total = db.execute(count_query, params).scalar_one()

    data_query = text(f"""
        SELECT o.id, o.order_number, o.order_type, o.status, o.payment_method, o.payment_status,
               o.total_vnd, o.address_snapshot, o.created_at, o.updated_at
        FROM orders o
        {where_clause}
        ORDER BY o.created_at ASC
        LIMIT :limit OFFSET :offset
    """)
    rows = db.execute(data_query, params).mappings().all()

    order_ids = [r["id"] for r in rows]
    items_by_order: dict[UUID, list[dict[str, Any]]] = {}
    if order_ids:
        items = db.execute(
            text("""SELECT id, order_id, product_id, variant_id, product_name_snapshot, sku_snapshot,
                           size_snapshot, color_snapshot, unit_price_vnd, quantity, line_total_vnd
                    FROM order_items WHERE order_id = ANY(:ids) ORDER BY created_at"""),
            {"ids": order_ids}
        ).mappings().all()
        for item in items:
            items_by_order.setdefault(item["order_id"], []).append(dict(item))

    items_result = []
    for r in rows:
        item_dict = dict(r)
        item_dict["items"] = items_by_order.get(r["id"], [])
        items_result.append(item_dict)

    return {
        "items": items_result,
        "total": total,
        "page": page,
        "limit": limit,
    }


def update_fulfillment_status(
    db: Session,
    order_id: UUID,
    staff_id: UUID,
    payload: WarehouseStatusUpdateRequest,
) -> dict[str, Any]:
    """Thực thi chuyển trạng thái Fulfillment nghiêm ngặt (confirmed -> processing -> ready_to_ship -> shipped -> completed)."""
    order = db.execute(
        text("SELECT id, order_number, status, address_snapshot FROM orders WHERE id = :id FOR UPDATE"),
        {"id": order_id}
    ).mappings().first()

    if not order:
        fail(404, "ORDER_NOT_FOUND", "Đơn hàng không tồn tại.")

    old_status = order["status"]
    next_status = payload.next_status

    # Validate bắt buộc khi chuyển sang shipped
    if next_status == "shipped":
        if not payload.carrier_name or not payload.carrier_name.strip():
            fail(422, "MISSING_CARRIER", "Đơn vị vận chuyển (carrier_name) là bắt buộc khi chuyển sang shipped.")
        if not payload.tracking_code or not payload.tracking_code.strip():
            fail(422, "MISSING_TRACKING_CODE", "Mã vận đơn (tracking_code) là bắt buộc khi chuyển sang shipped.")

    # Tạo ghi chú cho lịch sử chuyển trạng thái
    note_parts = []
    if payload.carrier_name and payload.tracking_code:
        note_parts.append(f"Vận chuyển: {payload.carrier_name} - Mã vận đơn: {payload.tracking_code}")
    if payload.note:
        note_parts.append(payload.note)
    status_note = " | ".join(note_parts) if note_parts else f"Chuyển trạng thái từ {old_status} sang {next_status}"

    # Gọi hàm state machine trong order_service.py (tự động kiểm tra nhảy cóc trạng thái)
    update_order_status(
        db,
        order_id=order_id,
        actor_id=staff_id,
        next_status=next_status,
        note=status_note,
    )

    # Nếu là shipped, cập nhật thông tin vận chuyển vào address_snapshot
    if next_status == "shipped":
        addr = dict(order.get("address_snapshot") or {})
        addr["carrier_name"] = payload.carrier_name
        addr["tracking_code"] = payload.tracking_code
        db.execute(
            text("UPDATE orders SET address_snapshot = CAST(:addr AS jsonb), updated_at = now() WHERE id = :id"),
            {"addr": json.dumps(addr), "id": order_id}
        )

    db.commit()

    updated_order = db.execute(
        text("SELECT order_number, updated_at FROM orders WHERE id = :id"),
        {"id": order_id}
    ).mappings().first()

    return {
        "order_id": order_id,
        "order_number": updated_order["order_number"],
        "from_status": old_status,
        "to_status": next_status,
        "carrier_name": payload.carrier_name,
        "tracking_code": payload.tracking_code,
        "changed_by": staff_id,
        "updated_at": updated_order["updated_at"],
        "message": f"Chuyển trạng thái đơn hàng sang '{next_status}' thành công.",
    }


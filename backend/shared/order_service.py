from __future__ import annotations

import json
import secrets
from datetime import timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import now


ONLINE_HOLD_MINUTES = 15
ORDER_STATUSES = (
    "pending_confirmation",
    "confirmed",
    "processing",
    "ready_to_ship",
    "shipped",
    "completed",
    "cancelled",
    "expired",
)


def _record_status(db: Session, order_id: UUID, actor_id: UUID | None, old: str | None, new: str, note: str = ""):
    db.execute(
        text("""INSERT INTO order_status_history(order_id,changed_by,from_status,to_status,note)
               VALUES(:order_id,:actor_id,:old,:new,:note)"""),
        {"order_id": order_id, "actor_id": actor_id, "old": old, "new": new, "note": note},
    )


def _release_active_reservations(db: Session, order_id: UUID):
    reservations = db.execute(
        text("SELECT id,variant_id,quantity FROM inventory_reservations WHERE order_id=:order_id AND status='active' ORDER BY variant_id FOR UPDATE"),
        {"order_id": order_id},
    ).mappings().all()
    for reservation in reservations:
        result = db.execute(
            text("UPDATE product_variants SET reserved_quantity=reserved_quantity-:quantity,updated_at=now() WHERE id=:variant_id AND reserved_quantity>=:quantity"),
            {"quantity": reservation["quantity"], "variant_id": reservation["variant_id"]},
        )
        if result.rowcount != 1:
            raise HTTPException(409, detail={"code": "RESERVATION_INCONSISTENT", "message": "Inventory reservation could not be released"})
        db.execute(text("UPDATE inventory_reservations SET status='released',updated_at=now() WHERE id=:id"), {"id": reservation["id"]})


def expire_stale_holds(db: Session, limit: int = 100) -> int:
    stale = db.execute(
        text("""SELECT id,order_number FROM orders
               WHERE status='pending_confirmation' AND hold_expires_at<=now()
               ORDER BY hold_expires_at LIMIT :limit FOR UPDATE SKIP LOCKED"""),
        {"limit": limit},
    ).mappings().all()
    for order in stale:
        _release_active_reservations(db, order["id"])
        db.execute(
            text("UPDATE orders SET status='expired',hold_expires_at=NULL,updated_at=now() WHERE id=:id"),
            {"id": order["id"]},
        )
        _record_status(db, order["id"], None, "pending_confirmation", "expired", "Inventory hold expired")
    return len(stale)


def _confirm_pending(db: Session, order: dict[str, Any], actor_id: UUID):
    reservations = db.execute(
        text("SELECT id,variant_id,quantity FROM inventory_reservations WHERE order_id=:id AND status='active' ORDER BY variant_id FOR UPDATE"),
        {"id": order["id"]},
    ).mappings().all()
    if not reservations:
        raise HTTPException(409, detail={"code": "RESERVATION_MISSING", "message": "Order has no active inventory reservation"})
    for reservation in reservations:
        result = db.execute(
            text("""UPDATE product_variants
                   SET stock_on_hand=stock_on_hand-:quantity,
                       reserved_quantity=reserved_quantity-:quantity,
                       updated_at=now()
                   WHERE id=:variant_id AND stock_on_hand>=:quantity AND reserved_quantity>=:quantity"""),
            {"quantity": reservation["quantity"], "variant_id": reservation["variant_id"]},
        )
        if result.rowcount != 1:
            raise HTTPException(409, detail={"code": "RESERVATION_INCONSISTENT", "message": "Reserved stock is no longer available"})
        before_after = db.execute(
            text("SELECT stock_on_hand FROM product_variants WHERE id=:id"), {"id": reservation["variant_id"]}
        ).scalar_one()
        db.execute(
            text("""INSERT INTO inventory_adjustments(variant_id,changed_by,delta,quantity_before,quantity_after,reason)
                   VALUES(:variant_id,:actor,:delta,:before,:after,:reason)"""),
            {
                "variant_id": reservation["variant_id"],
                "actor": actor_id,
                "delta": -reservation["quantity"],
                "before": before_after + reservation["quantity"],
                "after": before_after,
                "reason": f"Order {order['order_number']} confirmed",
            },
        )
        db.execute(text("UPDATE inventory_reservations SET status='consumed',expires_at=NULL,updated_at=now() WHERE id=:id"), {"id": reservation["id"]})
    db.execute(
        text("UPDATE orders SET status='confirmed',hold_expires_at=NULL,confirmed_at=now(),updated_at=now() WHERE id=:id"),
        {"id": order["id"]},
    )
    _record_status(db, order["id"], actor_id, "pending_confirmation", "confirmed", "Order confirmed; reserved stock deducted")


def create_order(
    db: Session,
    *,
    customer_id: UUID | None,
    actor_id: UUID,
    order_type: str,
    payment_method: str,
    lines: list[dict[str, Any]],
    address_snapshot: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
    confirm_immediately: bool = False,
) -> UUID:
    if not lines:
        raise HTTPException(422, detail={"code": "ORDER_ITEMS_REQUIRED", "message": "At least one order item is required"})
    if len({str(line["variant_id"]) for line in lines}) != len(lines):
        raise HTTPException(422, detail={"code": "DUPLICATE_VARIANT", "message": "Each variant may appear only once"})

    if idempotency_key:
        lock_key = f"{actor_id}:{idempotency_key}"
        db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"), {"key": lock_key})
        existing = db.execute(
            text("SELECT id FROM orders WHERE created_by=:actor AND idempotency_key=:key"),
            {"actor": actor_id, "key": idempotency_key},
        ).scalar_one_or_none()
        if existing:
            return existing

    selected = {}
    for line in sorted(lines, key=lambda item: str(item["variant_id"])):
        quantity = int(line["quantity"])
        if quantity < 1 or quantity > 100:
            raise HTTPException(422, detail={"code": "INVALID_QUANTITY", "message": "Quantity must be between 1 and 100"})
        row = db.execute(
            text("""SELECT v.id AS variant_id,v.product_id,v.sku AS variant_sku,v.size,v.color,
                          v.stock_on_hand,v.reserved_quantity,p.name AS product_name,p.price_vnd,p.is_active
                   FROM product_variants v JOIN products p ON p.id=v.product_id
                   WHERE v.id=:id FOR UPDATE OF v"""),
            {"id": line["variant_id"]},
        ).mappings().first()
        if not row or not row["is_active"]:
            raise HTTPException(404, detail={"code": "VARIANT_NOT_FOUND", "message": "Active product variant not found"})
        available = row["stock_on_hand"] - row["reserved_quantity"]
        if available < quantity:
            raise HTTPException(409, detail={"code": "OUT_OF_STOCK", "message": "Requested quantity exceeds available stock", "details": {"available": max(available, 0), "variant_id": str(line["variant_id"])}})
        selected[str(row["variant_id"])] = (row, quantity)

    subtotal = sum(row["price_vnd"] * quantity for row, quantity in selected.values())
    hold_expires = now() + timedelta(minutes=ONLINE_HOLD_MINUTES)
    order_number = f"VF-{now():%Y%m%d}-{secrets.token_hex(4).upper()}"
    inserted = db.execute(
        text("""INSERT INTO orders(order_number,customer_id,created_by,order_type,status,payment_method,
                                  address_snapshot,subtotal_vnd,discount_vnd,total_vnd,idempotency_key,hold_expires_at)
               VALUES(:number,:customer,:actor,:type,'pending_confirmation',:payment,CAST(:address AS jsonb),
                      :subtotal,0,:subtotal,:key,:expires)
               ON CONFLICT (created_by,idempotency_key) WHERE idempotency_key IS NOT NULL DO NOTHING
               RETURNING id"""),
        {
            "number": order_number,
            "customer": customer_id,
            "actor": actor_id,
            "type": order_type,
            "payment": payment_method,
            "address": json.dumps(address_snapshot or {}),
            "subtotal": subtotal,
            "key": idempotency_key,
            "expires": hold_expires,
        },
    ).scalar_one_or_none()
    if inserted is None:
        return db.execute(
            text("SELECT id FROM orders WHERE created_by=:actor AND idempotency_key=:key"),
            {"actor": actor_id, "key": idempotency_key},
        ).scalar_one()

    db.execute(
        text("INSERT INTO order_status_history(order_id,changed_by,to_status,note) VALUES(:id,:actor,'pending_confirmation','Order created and stock held')"),
        {"id": inserted, "actor": actor_id},
    )
    for row, quantity in selected.values():
        db.execute(
            text("""INSERT INTO order_items(order_id,product_id,variant_id,product_name_snapshot,sku_snapshot,
                                           size_snapshot,color_snapshot,unit_price_vnd,quantity,line_total_vnd)
                   VALUES(:order,:product,:variant,:name,:sku,:size,:color,:price,:quantity,:line_total)"""),
            {
                "order": inserted,
                "product": row["product_id"],
                "variant": row["variant_id"],
                "name": row["product_name"],
                "sku": row["variant_sku"],
                "size": row["size"],
                "color": row["color"],
                "price": row["price_vnd"],
                "quantity": quantity,
                "line_total": row["price_vnd"] * quantity,
            },
        )
        db.execute(text("UPDATE product_variants SET reserved_quantity=reserved_quantity+:q,updated_at=now() WHERE id=:id"), {"q": quantity, "id": row["variant_id"]})
        db.execute(
            text("INSERT INTO inventory_reservations(order_id,variant_id,quantity,status,expires_at) VALUES(:order,:variant,:q,'active',:expires)"),
            {"order": inserted, "variant": row["variant_id"], "q": quantity, "expires": hold_expires},
        )

    if confirm_immediately:
        order = db.execute(text("SELECT id,order_number,status FROM orders WHERE id=:id FOR UPDATE"), {"id": inserted}).mappings().one()
        _confirm_pending(db, order, actor_id)
    return inserted


def confirm_order(db: Session, order_id: UUID, actor_id: UUID) -> str:
    order = db.execute(text("SELECT id,order_number,status,hold_expires_at FROM orders WHERE id=:id FOR UPDATE"), {"id": order_id}).mappings().first()
    if not order:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    if order["status"] != "pending_confirmation":
        raise HTTPException(409, detail={"code": "ORDER_STATE_CONFLICT", "message": "Only pending orders can be confirmed"})
    if order["hold_expires_at"] is None or order["hold_expires_at"] <= now():
        _release_active_reservations(db, order_id)
        db.execute(text("UPDATE orders SET status='expired',hold_expires_at=NULL,updated_at=now() WHERE id=:id"), {"id": order_id})
        _record_status(db, order_id, None, "pending_confirmation", "expired", "Inventory hold expired before confirmation")
        return "expired"
    _confirm_pending(db, order, actor_id)
    return "confirmed"


def cancel_order(db: Session, order_id: UUID, actor_id: UUID, *, allow_confirmed: bool = False, note: str = "Cancelled") -> str:
    order = db.execute(text("SELECT id,order_number,status,customer_id FROM orders WHERE id=:id FOR UPDATE"), {"id": order_id}).mappings().first()
    if not order:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    allowed = {"pending_confirmation"}
    if allow_confirmed:
        allowed.add("confirmed")
    if order["status"] not in allowed:
        raise HTTPException(409, detail={"code": "ORDER_STATE_CONFLICT", "message": "Order can no longer be cancelled"})

    old_status = order["status"]
    reservations = db.execute(
        text("SELECT id,variant_id,quantity,status FROM inventory_reservations WHERE order_id=:id AND status IN ('active','consumed') ORDER BY variant_id FOR UPDATE"),
        {"id": order_id},
    ).mappings().all()
    for reservation in reservations:
        if reservation["status"] == "active":
            result = db.execute(
                text("UPDATE product_variants SET reserved_quantity=reserved_quantity-:q,updated_at=now() WHERE id=:id AND reserved_quantity>=:q"),
                {"q": reservation["quantity"], "id": reservation["variant_id"]},
            )
        else:
            current = db.execute(text("SELECT stock_on_hand FROM product_variants WHERE id=:id FOR UPDATE"), {"id": reservation["variant_id"]}).scalar_one()
            result = db.execute(
                text("UPDATE product_variants SET stock_on_hand=stock_on_hand+:q,updated_at=now() WHERE id=:id"),
                {"q": reservation["quantity"], "id": reservation["variant_id"]},
            )
            db.execute(
                text("""INSERT INTO inventory_adjustments(variant_id,changed_by,delta,quantity_before,quantity_after,reason)
                       VALUES(:variant,:actor,:delta,:before,:after,:reason)"""),
                {
                    "variant": reservation["variant_id"],
                    "actor": actor_id,
                    "delta": reservation["quantity"],
                    "before": current,
                    "after": current + reservation["quantity"],
                    "reason": f"Order {order['order_number']} cancelled; stock restored",
                },
            )
        if result.rowcount != 1:
            raise HTTPException(409, detail={"code": "RESERVATION_INCONSISTENT", "message": "Reserved stock could not be restored"})
        db.execute(text("UPDATE inventory_reservations SET status='released',expires_at=NULL,updated_at=now() WHERE id=:id"), {"id": reservation["id"]})

    db.execute(text("UPDATE orders SET status='cancelled',hold_expires_at=NULL,cancelled_at=now(),updated_at=now() WHERE id=:id"), {"id": order_id})
    _record_status(db, order_id, actor_id, old_status, "cancelled", note)
    return "cancelled"


def update_order_status(db: Session, order_id: UUID, actor_id: UUID, next_status: str, note: str = ""):
    allowed = {
        "confirmed": {"processing"},
        "processing": {"ready_to_ship"},
        "ready_to_ship": {"shipped"},
        "shipped": {"completed"},
    }
    order = db.execute(text("SELECT status FROM orders WHERE id=:id FOR UPDATE"), {"id": order_id}).mappings().first()
    if not order:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    old = order["status"]
    if next_status not in allowed.get(old, set()):
        raise HTTPException(409, detail={"code": "ORDER_STATE_CONFLICT", "message": f"Cannot move order from {old} to {next_status}"})
    db.execute(text("UPDATE orders SET status=:status,updated_at=now() WHERE id=:id"), {"status": next_status, "id": order_id})
    _record_status(db, order_id, actor_id, old, next_status, note)


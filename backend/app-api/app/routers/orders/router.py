from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from order_service import cancel_order, create_order, expire_stale_holds
from shared_platform import get_db, require_roles
from app.schemas.orders import OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


def order_detail(db: Session, order_id: UUID, customer_id: UUID | None = None):
    row = db.execute(
        text("""SELECT o.*,u.full_name AS customer_name,u.phone AS customer_phone
               FROM orders o LEFT JOIN users u ON u.id=o.customer_id
               WHERE o.id=:id AND (CAST(:customer AS uuid) IS NULL OR o.customer_id=:customer)"""),
        {"id": order_id, "customer": customer_id},
    ).mappings().first()
    if not row:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    items = db.execute(
        text("""SELECT id,product_id,variant_id,product_name_snapshot,sku_snapshot,size_snapshot,
                      color_snapshot,unit_price_vnd,quantity,line_total_vnd
               FROM order_items WHERE order_id=:id ORDER BY created_at"""),
        {"id": order_id},
    ).mappings().all()
    result = dict(row)
    result["items"] = [dict(item) for item in items]
    return result


@router.post("", status_code=201)
def place_order(
    body: OrderCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", min_length=1, max_length=128),
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    if expire_stale_holds(db):
        db.commit()
    order_id = create_order(
        db,
        customer_id=user["id"],
        actor_id=user["id"],
        order_type="online",
        payment_method=body.payment_method,
        lines=[item.model_dump() for item in body.items],
        address_snapshot=body.shipping_address.model_dump(exclude_none=True),
        idempotency_key=idempotency_key,
    )
    db.commit()
    return order_detail(db, order_id, user["id"])


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    if expire_stale_holds(db):
        db.commit()
    rows = db.execute(
        text("""SELECT id,order_number,status,payment_method,payment_status,total_vnd,created_at,updated_at
               FROM orders WHERE customer_id=:customer ORDER BY created_at DESC LIMIT :limit OFFSET :offset"""),
        {"customer": user["id"], "limit": limit, "offset": (page - 1) * limit},
    ).mappings().all()
    total = db.execute(text("SELECT count(*) FROM orders WHERE customer_id=:customer"), {"customer": user["id"]}).scalar_one()
    return {"items": [dict(row) for row in rows], "page": page, "limit": limit, "total": total}


@router.get("/{order_id}")
def get_order(order_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    return order_detail(db, order_id, user["id"])


@router.get("/{order_id}/history")
def order_history(order_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM orders WHERE id=:id AND customer_id=:customer"), {"id": order_id, "customer": user["id"]}).first():
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    rows = db.execute(
        text("SELECT from_status,to_status,note,created_at FROM order_status_history WHERE order_id=:id ORDER BY created_at"),
        {"id": order_id},
    ).mappings().all()
    return {"items": [dict(row) for row in rows]}


@router.post("/{order_id}/cancel", status_code=204)
def cancel_customer_order(order_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM orders WHERE id=:id AND customer_id=:customer"), {"id": order_id, "customer": user["id"]}).first():
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    cancel_order(db, order_id, user["id"], note="Cancelled by customer")
    db.commit()
    return Response(status_code=204)

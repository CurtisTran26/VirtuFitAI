from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from order_service import cancel_order, expire_stale_holds, update_order_status
from shared_platform import get_db, require_roles
from app.schemas.orders import OrderStatusUpdate

router = APIRouter()
OrderReaders = Depends(require_roles("admin", "sales_staff", "warehouse_staff"))
OrderManagers = Depends(require_roles("admin", "warehouse_staff"))
OrderCancellers = Depends(require_roles("admin", "sales_staff"))


def staff_order_detail(db: Session, order_id: UUID):
    row = db.execute(
        text("""SELECT o.*,u.full_name AS customer_name,u.phone AS customer_phone
               FROM orders o LEFT JOIN users u ON u.id=o.customer_id WHERE o.id=:id"""),
        {"id": order_id},
    ).mappings().first()
    if not row:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    items = db.execute(
        text("""SELECT id,product_id,variant_id,product_name_snapshot,sku_snapshot,size_snapshot,color_snapshot,
                      unit_price_vnd,quantity,line_total_vnd FROM order_items WHERE order_id=:id ORDER BY created_at"""),
        {"id": order_id},
    ).mappings().all()
    history = db.execute(
        text("SELECT from_status,to_status,note,changed_by,created_at FROM order_status_history WHERE order_id=:id ORDER BY created_at"),
        {"id": order_id},
    ).mappings().all()
    return {**dict(row), "items": [dict(item) for item in items], "status_history": [dict(item) for item in history]}


@router.get("/api/v1/orders")
def list_orders(
    status: str | None = None,
    order_type: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=OrderReaders,
    db: Session = Depends(get_db),
):
    if expire_stale_holds(db):
        db.commit()
    rows = db.execute(
        text("""SELECT o.id,o.order_number,o.customer_id,u.full_name AS customer_name,o.order_type,o.status,
                      o.payment_method,o.payment_status,o.total_vnd,o.created_at,o.updated_at
               FROM orders o LEFT JOIN users u ON u.id=o.customer_id
               WHERE (CAST(:status AS text) IS NULL OR o.status=:status)
                 AND (CAST(:type AS text) IS NULL OR o.order_type=:type)
               ORDER BY o.created_at DESC LIMIT :limit OFFSET :offset"""),
        {"status": status, "type": order_type, "limit": limit, "offset": (page - 1) * limit},
    ).mappings().all()
    total = db.execute(
        text("SELECT count(*) FROM orders WHERE (CAST(:status AS text) IS NULL OR status=:status) AND (CAST(:type AS text) IS NULL OR order_type=:type)"),
        {"status": status, "type": order_type},
    ).scalar_one()
    return {"items": [dict(row) for row in rows], "page": page, "limit": limit, "total": total}


@router.get("/api/v1/orders/{order_id}")
def get_order(order_id: UUID, user=OrderReaders, db: Session = Depends(get_db)):
    return staff_order_detail(db, order_id)


@router.patch("/api/v1/orders/{order_id}/status")
def set_order_status(order_id: UUID, body: OrderStatusUpdate, user=OrderManagers, db: Session = Depends(get_db)):
    update_order_status(db, order_id, user["id"], body.status, body.note)
    db.commit()
    return staff_order_detail(db, order_id)


@router.post("/api/v1/orders/{order_id}/cancel", status_code=204)
def cancel_staff_order(order_id: UUID, user=OrderCancellers, db: Session = Depends(get_db)):
    cancel_order(db, order_id, user["id"], allow_confirmed=True, note="Cancelled by staff")
    db.commit()
    return Response(status_code=204)

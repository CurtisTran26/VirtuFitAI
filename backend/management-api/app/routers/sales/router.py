from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from order_service import confirm_order, create_order, expire_stale_holds
from shared_platform import get_db, require_roles
from app.schemas.orders import CounterOrderCreate
from app.routers.orders.router import staff_order_detail

router = APIRouter(tags=["Sales"])
SalesRole = Depends(require_roles("admin", "sales_staff"))


@router.get("/api/v1/sales/lookup/products")
def lookup_products(q: str = Query(min_length=2, max_length=120), user=SalesRole, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""SELECT p.id AS product_id,p.name,p.sku AS product_sku,p.price_vnd,
                      v.id AS variant_id,v.sku AS variant_sku,v.size,v.color,v.stock_on_hand,
                      v.reserved_quantity,(v.stock_on_hand-v.reserved_quantity) AS available_quantity
               FROM products p JOIN product_variants v ON v.product_id=p.id
               WHERE p.is_active AND (p.name ILIKE :query OR p.sku ILIKE :query OR v.sku ILIKE :query)
               ORDER BY p.name,v.size,v.color LIMIT 50"""),
        {"query": f"%{q}%"},
    ).mappings().all()
    return {"items": [dict(row) for row in rows]}


@router.get("/api/v1/sales/lookup/customers")
def lookup_customers(phone: str = Query(min_length=4, max_length=20), user=SalesRole, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""SELECT u.id,u.phone,u.full_name FROM users u JOIN roles r ON r.id=u.role_id
               WHERE r.name='customer' AND u.is_active AND u.phone LIKE :prefix ORDER BY u.phone LIMIT 20"""),
        {"prefix": f"{phone}%"},
    ).mappings().all()
    return {"items": [dict(row) for row in rows]}


@router.get("/api/v1/sales/orders/by-number/{order_number}")
def lookup_order(order_number: str, user=SalesRole, db: Session = Depends(get_db)):
    order_id = db.execute(text("SELECT id FROM orders WHERE order_number=:number"), {"number": order_number}).scalar_one_or_none()
    if not order_id:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    return staff_order_detail(db, order_id)


@router.post("/api/v1/sales/orders/{order_id}/confirm")
def confirm_sales_order(order_id: UUID, user=SalesRole, db: Session = Depends(get_db)):
    result = confirm_order(db, order_id, user["id"])
    db.commit()
    if result == "expired":
        raise HTTPException(409, detail={"code": "ORDER_HOLD_EXPIRED", "message": "Inventory hold expired; the order cannot be confirmed"})
    return staff_order_detail(db, order_id)


@router.post("/api/v1/sales/counter-orders", status_code=201)
def create_counter_order(
    body: CounterOrderCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", min_length=1, max_length=128),
    user=SalesRole,
    db: Session = Depends(get_db),
):
    if body.customer_id and not db.execute(
        text("""SELECT 1 FROM users u JOIN roles r ON r.id=u.role_id
               WHERE u.id=:id AND u.is_active AND r.name='customer'"""),
        {"id": body.customer_id},
    ).first():
        raise HTTPException(404, detail={"code": "CUSTOMER_NOT_FOUND", "message": "Active customer account not found"})
    if expire_stale_holds(db):
        db.commit()
    order_id = create_order(
        db,
        customer_id=body.customer_id,
        actor_id=user["id"],
        order_type="counter",
        payment_method=body.payment_method,
        lines=[item.model_dump() for item in body.items],
        address_snapshot={},
        idempotency_key=idempotency_key,
        confirm_immediately=True,
    )
    db.commit()
    return staff_order_detail(db, order_id)

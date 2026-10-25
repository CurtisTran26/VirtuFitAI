from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.returns import ReturnCreate

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("", status_code=201)
def request_return(body: ReturnCreate, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    if len({item.order_item_id for item in body.items}) != len(body.items):
        raise HTTPException(422, detail={"code": "DUPLICATE_RETURN_ITEM", "message": "Each order item may appear only once"})
    order = db.execute(
        text("SELECT id,status FROM orders WHERE id=:id AND customer_id=:customer FOR UPDATE"),
        {"id": body.order_id, "customer": user["id"]},
    ).mappings().first()
    if not order:
        raise HTTPException(404, detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"})
    if order["status"] != "completed":
        raise HTTPException(409, detail={"code": "RETURN_NOT_ALLOWED", "message": "Items can be returned after order completion"})

    request_id = db.execute(
        text("INSERT INTO return_requests(order_id,customer_id,reason) VALUES(:order,:customer,:reason) RETURNING id"),
        {"order": body.order_id, "customer": user["id"], "reason": body.reason},
    ).scalar_one()
    for item in body.items:
        order_item = db.execute(
            text("SELECT id,quantity FROM order_items WHERE id=:id AND order_id=:order FOR UPDATE"),
            {"id": item.order_item_id, "order": body.order_id},
        ).mappings().first()
        if not order_item:
            raise HTTPException(404, detail={"code": "ORDER_ITEM_NOT_FOUND", "message": "Order item not found"})
        already_requested = db.execute(
            text("""SELECT COALESCE(sum(ri.quantity),0) FROM return_items ri
                   JOIN return_requests rr ON rr.id=ri.return_request_id
                   WHERE ri.order_item_id=:item AND rr.status<>'rejected'"""),
            {"item": item.order_item_id},
        ).scalar_one()
        if already_requested + item.quantity > order_item["quantity"]:
            raise HTTPException(409, detail={"code": "RETURN_QUANTITY_EXCEEDED", "message": "Return quantity exceeds the unreturned quantity"})
        db.execute(
            text("INSERT INTO return_items(return_request_id,order_item_id,quantity) VALUES(:request,:item,:quantity)"),
            {"request": request_id, "item": item.order_item_id, "quantity": item.quantity},
        )
    db.commit()
    return {"id": str(request_id), "order_id": str(body.order_id), "status": "requested"}


@router.get("")
def list_my_returns(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    rows = db.execute(
        text("""SELECT id,order_id,reason,status,inspection_note,created_at,updated_at
               FROM return_requests WHERE customer_id=:customer ORDER BY created_at DESC LIMIT :limit OFFSET :offset"""),
        {"customer": user["id"], "limit": limit, "offset": (page - 1) * limit},
    ).mappings().all()
    total = db.execute(text("SELECT count(*) FROM return_requests WHERE customer_id=:customer"), {"customer": user["id"]}).scalar_one()
    return {"items": [dict(row) for row in rows], "page": page, "limit": limit, "total": total}


@router.get("/{return_id}")
def get_my_return(return_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id,order_id,reason,status,inspection_note,inspected_at,created_at,updated_at FROM return_requests WHERE id=:id AND customer_id=:customer"),
        {"id": return_id, "customer": user["id"]},
    ).mappings().first()
    if not row:
        raise HTTPException(404, detail={"code": "RETURN_NOT_FOUND", "message": "Return request not found"})
    items = db.execute(
        text("""SELECT ri.id,ri.order_item_id,ri.quantity,ri.condition_note,ri.restock,oi.product_name_snapshot,
                      oi.sku_snapshot,oi.size_snapshot,oi.color_snapshot
               FROM return_items ri JOIN order_items oi ON oi.id=ri.order_item_id
               WHERE ri.return_request_id=:id"""),
        {"id": return_id},
    ).mappings().all()
    return {**dict(row), "items": [dict(item) for item in items]}

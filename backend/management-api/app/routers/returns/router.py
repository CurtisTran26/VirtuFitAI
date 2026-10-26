from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.returns import ReturnInspection

router = APIRouter(tags=["Returns"])
WarehouseRole = Depends(require_roles("admin", "warehouse_staff"))


def return_detail(db: Session, return_id: UUID):
    row = db.execute(
        text("""SELECT rr.*,o.order_number,u.full_name AS customer_name,u.phone AS customer_phone
               FROM return_requests rr JOIN orders o ON o.id=rr.order_id JOIN users u ON u.id=rr.customer_id
               WHERE rr.id=:id"""),
        {"id": return_id},
    ).mappings().first()
    if not row:
        raise HTTPException(404, detail={"code": "RETURN_NOT_FOUND", "message": "Return request not found"})
    items = db.execute(
        text("""SELECT ri.id,ri.order_item_id,ri.quantity,ri.condition_note,ri.restock,
                      oi.product_name_snapshot,oi.sku_snapshot,oi.size_snapshot,oi.color_snapshot
               FROM return_items ri JOIN order_items oi ON oi.id=ri.order_item_id WHERE ri.return_request_id=:id"""),
        {"id": return_id},
    ).mappings().all()
    return {**dict(row), "items": [dict(item) for item in items]}


@router.get("/api/v1/returns")
def list_returns(status: str | None = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), user=WarehouseRole, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""SELECT rr.id,rr.order_id,o.order_number,rr.customer_id,u.full_name AS customer_name,
                      rr.reason,rr.status,rr.created_at,
                      string_agg(DISTINCT oi.product_name_snapshot || ' (' || oi.color_snapshot || '/' || oi.size_snapshot || ')', ', ') AS product_summary,
                      bool_or(ri.restock) AS restocked
               FROM return_requests rr JOIN orders o ON o.id=rr.order_id JOIN users u ON u.id=rr.customer_id
               LEFT JOIN return_items ri ON ri.return_request_id=rr.id
               LEFT JOIN order_items oi ON oi.id=ri.order_item_id
               WHERE (CAST(:status AS text) IS NULL OR rr.status=:status)
               GROUP BY rr.id,o.order_number,u.full_name
               ORDER BY rr.created_at DESC LIMIT :limit OFFSET :offset"""),
        {"status": status, "limit": limit, "offset": (page - 1) * limit},
    ).mappings().all()
    total = db.execute(text("SELECT count(*) FROM return_requests WHERE (CAST(:status AS text) IS NULL OR status=:status)"), {"status": status}).scalar_one()
    return {"items": [dict(row) for row in rows], "page": page, "limit": limit, "total": total}


@router.get("/api/v1/returns/{return_id}")
def get_return(return_id: UUID, user=WarehouseRole, db: Session = Depends(get_db)):
    return return_detail(db, return_id)


@router.post("/api/v1/returns/{return_id}/inspect")
def inspect_return(return_id: UUID, body: ReturnInspection, user=WarehouseRole, db: Session = Depends(get_db)):
    request = db.execute(text("SELECT id,status FROM return_requests WHERE id=:id FOR UPDATE"), {"id": return_id}).mappings().first()
    if not request:
        raise HTTPException(404, detail={"code": "RETURN_NOT_FOUND", "message": "Return request not found"})
    if request["status"] != "requested":
        raise HTTPException(409, detail={"code": "RETURN_STATE_CONFLICT", "message": "Return request has already been inspected"})
    existing = db.execute(
        text("SELECT id,order_item_id,quantity FROM return_items WHERE return_request_id=:id FOR UPDATE"), {"id": return_id}
    ).mappings().all()
    submitted = {item.return_item_id: item for item in body.items}
    if len(submitted) != len(body.items) or {row["id"] for row in existing} != set(submitted):
        raise HTTPException(422, detail={"code": "RETURN_INSPECTION_ITEMS_MISMATCH", "message": "Inspection must include each returned item exactly once"})
    if body.outcome == "rejected" and any(item.restock for item in body.items):
        raise HTTPException(422, detail={"code": "INVALID_RESTOCK", "message": "Rejected items cannot be restocked"})

    for row in existing:
        inspection = submitted[row["id"]]
        order_item = db.execute(text("SELECT variant_id FROM order_items WHERE id=:id"), {"id": row["order_item_id"]}).mappings().one()
        if inspection.restock:
            if not order_item["variant_id"]:
                raise HTTPException(409, detail={"code": "VARIANT_UNAVAILABLE", "message": "The original variant no longer exists and cannot be restocked"})
            before = db.execute(text("SELECT stock_on_hand FROM product_variants WHERE id=:id FOR UPDATE"), {"id": order_item["variant_id"]}).scalar_one_or_none()
            if before is None:
                raise HTTPException(409, detail={"code": "VARIANT_UNAVAILABLE", "message": "The original variant no longer exists and cannot be restocked"})
            after = before + row["quantity"]
            db.execute(text("UPDATE product_variants SET stock_on_hand=:after,updated_at=now() WHERE id=:id"), {"after": after, "id": order_item["variant_id"]})
            db.execute(
                text("""INSERT INTO inventory_adjustments(variant_id,changed_by,delta,quantity_before,quantity_after,reason)
                       VALUES(:variant,:actor,:delta,:before,:after,:reason)"""),
                {"variant": order_item["variant_id"], "actor": user["id"], "delta": row["quantity"], "before": before, "after": after, "reason": f"Accepted return {return_id} restocked"},
            )
        db.execute(
            text("UPDATE return_items SET condition_note=:condition,restock=:restock WHERE id=:id"),
            {"condition": inspection.condition_note, "restock": inspection.restock, "id": row["id"]},
        )
    db.execute(
        text("UPDATE return_requests SET status=:status,inspected_by=:actor,inspection_note=:note,inspected_at=now(),updated_at=now() WHERE id=:id"),
        {"status": body.outcome, "actor": user["id"], "note": body.note, "id": return_id},
    )
    db.commit()
    return return_detail(db, return_id)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Inventory, InventoryAdjustment, Product
from app.schemas import InventoryAdjustmentOut, InventoryAdjustmentResult, InventoryOut
from app.security import require_roles

router = APIRouter(prefix="/api/inventory", tags=["Inventory and adjustments"])


class AdjustmentIn(BaseModel):
    product_id: int = Field(gt=0)
    size: str = Field(default="ONE_SIZE", max_length=30)
    delta: int = Field(ge=-2147483648, le=2147483647)
    reason: str = Field(min_length=1, max_length=255)


@router.get("", response_model=list[InventoryOut])
def get_inventory(product_id: int | None = None, db: Session = Depends(get_db), _=Depends(require_roles("staff", "inventory", "manager", "admin"))):
    query = db.query(Inventory)
    if product_id is not None:
        query = query.filter(Inventory.product_id == product_id)
    return query.all()


@router.post("/adjustments", response_model=InventoryAdjustmentResult, status_code=201)
def adjust_inventory(payload: AdjustmentIn, db: Session = Depends(get_db), actor=Depends(require_roles("inventory", "manager", "admin"))):
    if payload.delta == 0:
        raise HTTPException(422, "Adjustment delta must not be zero")
    if not db.get(Product, payload.product_id):
        raise HTTPException(404, "Product not found")

    # Insert the row if absent, then lock it before checking/updating quantity.
    # The unique key and ON CONFLICT serialize concurrent first adjustments.
    db.execute(
        insert(Inventory.__table__)
        .values(product_id=payload.product_id, size=payload.size, quantity=0)
        .on_conflict_do_nothing(index_elements=["product_id", "size"])
    )
    row = db.execute(
        select(Inventory)
        .where(Inventory.product_id == payload.product_id, Inventory.size == payload.size)
        .with_for_update()
    ).scalar_one()
    if row.quantity + payload.delta < 0:
        db.rollback()
        raise HTTPException(400, "Stock quantity cannot become negative")

    row.quantity += payload.delta
    event = InventoryAdjustment(product_id=payload.product_id, size=payload.size, delta=payload.delta, reason=payload.reason, actor_id=actor.id)
    db.add(event)
    db.commit()
    db.refresh(row)
    db.refresh(event)
    return {"inventory": row, "adjustment": event}


@router.get("/adjustments", response_model=list[InventoryAdjustmentOut])
def adjustment_history(product_id: int | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_roles("staff", "inventory", "manager", "admin"))):
    query = db.query(InventoryAdjustment).order_by(InventoryAdjustment.created_at.desc())
    if product_id is not None:
        query = query.filter(InventoryAdjustment.product_id == product_id)
    return query.offset(skip).limit(min(limit, 200)).all()

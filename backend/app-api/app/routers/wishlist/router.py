from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("")
def wishlist(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT p.id,p.name,p.price_vnd,p.image_url,w.created_at FROM wishlists w JOIN products p ON p.id=w.product_id WHERE w.user_id=:u ORDER BY w.created_at DESC LIMIT :l OFFSET :o"), {"u": user["id"], "l": limit, "o": (page - 1) * limit}).mappings().all()
    total = db.execute(text("SELECT count(*) FROM wishlists WHERE user_id=:u"), {"u": user["id"]}).scalar_one()
    return {"items": [dict(r) for r in rows], "page": page, "limit": limit, "total": total}


@router.put("/{product_id}", status_code=204)
def add_wishlist(product_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM products WHERE id=:p AND is_active"), {"p": product_id}).first():
        raise HTTPException(404, detail={"code": "PRODUCT_NOT_FOUND", "message": "Product not found"})
    db.execute(text("INSERT INTO wishlists(user_id,product_id) VALUES(:u,:p) ON CONFLICT DO NOTHING"), {"u": user["id"], "p": product_id})
    db.commit()


@router.delete("/{product_id}", status_code=204)
def remove_wishlist(product_id: UUID, user=Depends(require_roles("customer")), db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM wishlists WHERE user_id=:u AND product_id=:p"), {"u": user["id"], "p": product_id})
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, WishlistItem
from app.schemas import WishlistOut
from app.security import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["Wishlist"])


class WishlistIn(BaseModel):
    product_id: int


@router.get("", response_model=list[WishlistOut])
def list_wishlist(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WishlistItem).filter(WishlistItem.user_id == user.id).all()


@router.post("", response_model=WishlistOut, status_code=201)
def add_to_wishlist(payload: WishlistIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Product, payload.product_id):
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    item = db.query(WishlistItem).filter_by(user_id=user.id, product_id=payload.product_id).first()
    if item:
        return item
    item = WishlistItem(user_id=user.id, product_id=payload.product_id)
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        item = db.query(WishlistItem).filter_by(user_id=user.id, product_id=payload.product_id).first()
        if item is None:
            raise HTTPException(409, "Could not add product to wishlist") from exc
        return item
    db.refresh(item)
    return item


@router.delete("/{product_id}", status_code=204)
def remove_from_wishlist(product_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(WishlistItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not item:
        raise HTTPException(404, "Sản phẩm không có trong wishlist")
    db.delete(item)
    db.commit()
    return Response(status_code=204)

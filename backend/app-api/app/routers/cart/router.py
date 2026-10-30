from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from shared_platform import get_db, require_roles
from app.schemas.cart.cart import CartItemAdd, CartItemUpdate, CartResponse
from app.services.cart import (
    get_user_cart,
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_user_cart,
)

v1 = "/api/v1"
router = APIRouter(tags=["Cart"])


@router.get(f"{v1}/cart", response_model=CartResponse)
def get_cart(
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Lấy danh sách các sản phẩm trong giỏ hàng hiện tại."""
    return get_user_cart(db, user["id"])


@router.post(f"{v1}/cart/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    payload: CartItemAdd,
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Thêm một biến thể sản phẩm vào giỏ hàng (Upsert)."""
    return add_to_cart(db, user["id"], payload.variant_id, payload.quantity)


@router.patch(f"{v1}/cart/items/{{variant_id}}", response_model=CartResponse)
def update_item_quantity(
    variant_id: UUID,
    payload: CartItemUpdate,
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Cập nhật số lượng của một biến thể trong giỏ hàng."""
    return update_cart_item(db, user["id"], variant_id, payload.quantity)


@router.delete(f"{v1}/cart/items/{{variant_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    variant_id: UUID,
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Xóa một biến thể cụ thể khỏi giỏ hàng."""
    remove_cart_item(db, user["id"], variant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(f"{v1}/cart", status_code=status.HTTP_204_NO_CONTENT)
def delete_entire_cart(
    user=Depends(require_roles("customer")),
    db: Session = Depends(get_db),
):
    """Xóa sạch toàn bộ giỏ hàng của user."""
    clear_user_cart(db, user["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    variant_id: UUID
    quantity: int = Field(default=1, ge=1, le=100, description="Số lượng sản phẩm muốn thêm vào giỏ")


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=100, description="Số lượng mới cập nhật")


class CartItemResponse(BaseModel):
    id: UUID
    variant_id: UUID
    product_id: UUID
    product_name: str
    sku: str
    color: str
    size: str
    price_vnd: int
    quantity: int
    line_total_vnd: int
    image_url: str | None = None
    stock_available: int
    is_available: bool
    unavailable_reason: str | None = None


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_items: int
    total_unique_items: int
    subtotal_vnd: int


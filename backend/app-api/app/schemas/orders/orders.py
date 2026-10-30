from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderLineInput(BaseModel):
    variant_id: UUID
    quantity: int = Field(ge=1, le=100)


class ShippingAddress(BaseModel):
    name: str = Field(min_length=1, max_length=120, description="Họ tên người nhận")
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$", description="Số điện thoại nhận hàng")
    address: str = Field(min_length=5, max_length=500, description="Địa chỉ chi tiết (số nhà, đường...)")
    ward: str | None = Field(default=None, max_length=120, description="Phường/Xã")
    district: str | None = Field(default=None, max_length=120, description="Quận/Huyện")
    province: str | None = Field(default=None, max_length=120, description="Tỉnh/Thành phố")


class OrderCreate(BaseModel):
    items: list[OrderLineInput] = Field(min_length=1, max_length=50)
    payment_method: Literal["cod", "vnpay"]
    shipping_address: ShippingAddress


class CodCollectResponse(BaseModel):
    order_id: UUID
    order_number: str
    total_vnd: int
    payment_method: str
    payment_status: str
    status: str
    collector_id: UUID
    message: str

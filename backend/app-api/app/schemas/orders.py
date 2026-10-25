from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderLineInput(BaseModel):
    variant_id: UUID
    quantity: int = Field(ge=1, le=100)


class ShippingAddress(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    address: str = Field(min_length=5, max_length=500)
    ward: str | None = Field(default=None, max_length=120)
    district: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)


class OrderCreate(BaseModel):
    items: list[OrderLineInput] = Field(min_length=1, max_length=50)
    payment_method: Literal["cod", "vnpay"]
    shipping_address: ShippingAddress


from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderLineInput(BaseModel):
    variant_id: UUID
    quantity: int = Field(ge=1, le=100)


class CounterOrderCreate(BaseModel):
    customer_id: UUID | None = None
    items: list[OrderLineInput] = Field(min_length=1, max_length=50)
    payment_method: Literal["cash", "card", "bank_transfer"]


class OrderStatusUpdate(BaseModel):
    status: Literal["processing", "ready_to_ship", "shipped", "completed"]
    note: str = Field(default="", max_length=1000)



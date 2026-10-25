from uuid import UUID

from pydantic import BaseModel, Field


class ReturnLineInput(BaseModel):
    order_item_id: UUID
    quantity: int = Field(ge=1, le=100)


class ReturnCreate(BaseModel):
    order_id: UUID
    reason: str = Field(min_length=3, max_length=1000)
    items: list[ReturnLineInput] = Field(min_length=1, max_length=50)

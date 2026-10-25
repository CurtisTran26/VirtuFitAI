from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ReturnInspectionItem(BaseModel):
    return_item_id: UUID
    condition_note: str = Field(min_length=1, max_length=1000)
    restock: bool = False


class ReturnInspection(BaseModel):
    outcome: Literal["accepted", "rejected"]
    note: str = Field(default="", max_length=1000)
    items: list[ReturnInspectionItem] = Field(min_length=1, max_length=50)

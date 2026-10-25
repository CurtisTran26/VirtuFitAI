"""
Pydantic schemas cho Category (Danh mục).
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTreeNode(CategoryResponse):
    children: List["CategoryTreeNode"] = []

    model_config = ConfigDict(from_attributes=True)

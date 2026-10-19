from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

PhoneNumber = Annotated[str, StringConstraints(pattern=r"^\+?[0-9]{8,15}$")]


class UserCreate(BaseModel):
    phone: PhoneNumber
    full_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr | None = None


class UserOut(BaseModel):
    id: int
    phone: str
    full_name: str
    email: str | None
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    price: Decimal
    category_id: int | None
    model_config = ConfigDict(from_attributes=True)


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)


class SizeChartOut(BaseModel):
    id: int
    name: str
    measurements: Any
    model_config = ConfigDict(from_attributes=True)


class InventoryOut(BaseModel):
    id: int
    product_id: int
    size: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class InventoryAdjustmentOut(BaseModel):
    id: int
    product_id: int
    size: str
    delta: int
    reason: str
    actor_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InventoryAdjustmentResult(BaseModel):
    inventory: InventoryOut
    adjustment: InventoryAdjustmentOut


class WishlistOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    model_config = ConfigDict(from_attributes=True)


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    category_id: int | None = None


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class SizeChartIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    measurements: dict[str, object]

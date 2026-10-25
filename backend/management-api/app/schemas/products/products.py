from uuid import UUID

from pydantic import BaseModel, Field


class ProductIn(BaseModel):
    category_id: UUID
    name: str = Field(min_length=1, max_length=180)
    description: str = ""
    price_vnd: int = Field(ge=0)
    sku: str = Field(min_length=1, max_length=80)
    image_url: str | None = None
    is_active: bool = True


class SizeChartIn(BaseModel):
    category_id: UUID
    name: str = Field(min_length=1, max_length=120)
    measurements: list[dict]


class VariantIn(BaseModel):
    product_id: UUID
    size: str = Field(min_length=1, max_length=30)
    color: str = ""
    sku: str = Field(min_length=1, max_length=80)

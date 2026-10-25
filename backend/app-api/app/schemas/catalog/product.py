"""
Pydantic schemas cho Product, Image, Size và Filter parameters.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class StoreBriefResponse(BaseModel):
    store_id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductImageResponse(BaseModel):
    image_id: int
    image_url: str
    image_type: str
    is_primary: bool
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ProductSizeResponse(BaseModel):
    size_id: int
    size_label: str
    stock_quantity: int
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    length_cm: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListItemResponse(BaseModel):
    """Schema rút gọn hiển thị trên trang danh sách / tìm kiếm / lưới sản phẩm."""
    product_id: int
    name: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    color: Optional[str] = None
    is_active: bool
    view_count: int
    try_on_count: int
    created_at: datetime
    category_id: int
    category_name: Optional[str] = None
    primary_image_url: Optional[str] = None
    available_sizes: List[str] = []
    in_stock: bool = True

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(BaseModel):
    """Schema chi tiết đầy đủ khi người dùng xem trang sản phẩm (Product Detail Page)."""
    product_id: int
    store: StoreBriefResponse
    category_id: int
    category_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: Decimal
    discount_price: Optional[Decimal] = None
    color: Optional[str] = None
    is_active: bool
    view_count: int
    try_on_count: int
    created_at: datetime
    images: List[ProductImageResponse] = []
    sizes: List[ProductSizeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedProductResponse(BaseModel):
    """Schema phân trang chuẩn cho danh sách sản phẩm."""
    items: List[ProductListItemResponse]
    total: int = Field(..., description="Tổng số sản phẩm thỏa điều kiện lọc")
    page: int = Field(..., ge=1, description="Trang hiện tại")
    page_size: int = Field(..., ge=1, le=100, description="Số sản phẩm trên mỗi trang")
    total_pages: int = Field(..., description="Tổng số trang")

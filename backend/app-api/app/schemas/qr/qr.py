"""
Pydantic schemas cho chức năng QR code (Resolve, Scan & Generate).
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog.product import ProductImageResponse, ProductSizeResponse


class ProductQRCodeResponse(BaseModel):
    """Thông tin bản ghi mã QR đã lưu trong cơ sở dữ liệu."""
    qr_id: int
    product_id: int
    qr_data: str
    qr_image_url: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QRScanProductResponse(BaseModel):
    """
    Dữ liệu trả về khi người dùng quét mã QR tại cửa hàng.
    Bao gồm thông tin sản phẩm, bảng size, thông số đo ngực/eo/dài và liên kết phòng thử đồ AI.
    """
    product_id: int
    name: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    store_id: int
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    primary_image_url: Optional[str] = None
    images: List[ProductImageResponse] = []
    sizes: List[ProductSizeResponse] = []
    available_sizes: List[str] = []
    in_stock: bool = True
    
    # Thông tin chuyên biệt cho trải nghiệm O2O (Online-to-Offline) & AI Try-On
    try_on_ready: bool = Field(
        True,
        description="Đánh dấu sản phẩm đã sẵn sàng đưa vào phòng thử đồ ảo AI (đủ thông số đo may)"
    )
    deep_link: str = Field(
        ...,
        description="Deep link mở trực tiếp trong ứng dụng di động VirtuFit (VD: virtufit://product/1)"
    )
    web_url: str = Field(
        ...,
        description="URL web mở trên trình duyệt di động thông thường (VD: https://virtufit.vn/products/1)"
    )
    qr_data_scanned: str = Field(
        ...,
        description="Chuỗi mã QR gốc vừa quét"
    )

    model_config = ConfigDict(from_attributes=True)


class QRGenerateResponse(BaseModel):
    """Kết quả sinh mã QR cho sản phẩm."""
    product_id: int
    qr_data: str
    qr_image_url: str
    deep_link: str
    web_url: str
    message: str = "Sinh mã QR cho sản phẩm thành công."

"""
SQLAlchemy model cho ProductQRCode (mã QR sản phẩm).
QR sản phẩm khác QR chuyển khoản (theo README mục quy tắc nghiệp vụ).
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class ProductQRCode(Base):
    __tablename__ = "product_qr_codes"

    qr_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, unique=True)
    qr_image_url = Column(String(500), nullable=False)   # URL ảnh QR trên public bucket
    qr_data = Column(String(500), nullable=False)        # Nội dung encode trong QR (VD: virtufit://product/1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = relationship("Product")

    # Property alias for compatibility
    @property
    def qr_code_url(self) -> str:
        return self.qr_image_url

    @qr_code_url.setter
    def qr_code_url(self, value: str) -> None:
        self.qr_image_url = value

    def __repr__(self) -> str:
        return f"<ProductQRCode id={self.qr_id} product_id={self.product_id} data='{self.qr_data}'>"

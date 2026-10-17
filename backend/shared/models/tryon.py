"""
SQLAlchemy model cho TryOnJob (Tác vụ thử đồ AI).
Mỗi lần khách thử đồ tạo một job; kết quả ảnh lưu trên private bucket.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import TryOnJobStatus


class TryOnJob(Base):
    __tablename__ = "tryon_jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="SET NULL"), nullable=True)

    status = Column(
        SAEnum(TryOnJobStatus, name="tryon_job_status_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=TryOnJobStatus.PENDING, index=True
    )

    # Ảnh đầu vào và đầu ra (object_key trên MinIO private bucket)
    input_image_key = Column(String(500), nullable=False)      # Ảnh người dùng chụp/tải lên
    product_image_key = Column(String(500), nullable=True)     # Ảnh sản phẩm dùng thử
    result_image_key = Column(String(500), nullable=True)      # Ảnh kết quả AI
    ai_provider = Column(String(50), nullable=True)            # Tên model/API đã dùng
    error_message = Column(Text, nullable=True)                # Lý do nếu thất bại

    processing_time_ms = Column(Integer, nullable=True)        # Thời gian AI xử lý (ms)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tryon_jobs")
    product = relationship("Product")

    def __repr__(self) -> str:
        return f"<TryOnJob id={self.job_id} user={self.user_id} status={self.status}>"

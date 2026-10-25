"""
SQLAlchemy models cho DesignRequest, DesignConcept, DesignRevision.
Luồng: Customer gửi brief → AI tạo concept → Designer đánh giá → báo giá → Customer duyệt → đơn hàng.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import DesignRequestStatus


class DesignRequest(Base):
    """Yêu cầu thiết kế riêng từ Customer."""
    __tablename__ = "design_requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    request_code = Column(String(30), unique=True, nullable=False, index=True)  # DR-20261017-XXXX
    customer_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False)
    designer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    status = Column(
        SAEnum(DesignRequestStatus, name="design_request_status_enum", create_constraint=False, native_enum=False, length=30),
        nullable=False, default=DesignRequestStatus.SUBMITTED, index=True
    )

    # Brief từ khách hàng
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reference_images = Column(Text, nullable=True)  # JSON array of image URLs/object_keys
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    preferred_color = Column(String(100), nullable=True)
    preferred_size = Column(String(20), nullable=True)
    budget_min = Column(Numeric(15, 2), nullable=True)
    budget_max = Column(Numeric(15, 2), nullable=True)

    # Báo giá từ Designer
    quoted_price = Column(Numeric(15, 2), nullable=True)
    estimated_days = Column(Integer, nullable=True)
    designer_note = Column(Text, nullable=True)

    # Lý do từ chối
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    quoted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("User", back_populates="design_requests", foreign_keys=[customer_id])
    designer = relationship("User", foreign_keys=[designer_id])
    category = relationship("Category")
    concepts = relationship("DesignConcept", back_populates="request", cascade="all, delete-orphan")
    revisions = relationship("DesignRevision", back_populates="request", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DesignRequest id={self.request_id} code='{self.request_code}' status={self.status}>"


class DesignConcept(Base):
    """Concept do AI tạo ra từ brief của khách hàng."""
    __tablename__ = "design_concepts"

    concept_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("design_requests.request_id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)   # object_key trên MinIO (private bucket)
    prompt_used = Column(Text, nullable=True)          # Prompt gửi cho AI
    ai_provider = Column(String(50), nullable=True)    # Tên model/API đã dùng
    is_selected = Column(Integer, nullable=False, default=0)  # 0=chưa chọn, 1=được chọn
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    request = relationship("DesignRequest", back_populates="concepts")

    def __repr__(self) -> str:
        return f"<DesignConcept id={self.concept_id} request_id={self.request_id}>"


class DesignRevision(Base):
    """Bản chỉnh sửa / trao đổi giữa Designer và Customer."""
    __tablename__ = "design_revisions"

    revision_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("design_requests.request_id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    revision_number = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    request = relationship("DesignRequest", back_populates="revisions")
    author = relationship("User")

    def __repr__(self) -> str:
        return f"<DesignRevision id={self.revision_id} request_id={self.request_id} rev={self.revision_number}>"

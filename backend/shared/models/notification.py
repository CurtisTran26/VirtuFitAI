"""
SQLAlchemy model cho Notification (Thông báo).
Thông báo đưa người dùng về hồ sơ/đơn liên quan.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(
        SAEnum(NotificationType, name="notification_type_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=NotificationType.SYSTEM
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)

    # Deep link đến tài nguyên liên quan
    reference_type = Column(String(50), nullable=True)  # "order", "design_request", "tryon_job"
    reference_id = Column(Integer, nullable=True)        # ID của tài nguyên

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.notification_id} user={self.user_id} type={self.type}>"

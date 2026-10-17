"""
SQLAlchemy models cho ChatConversation và ChatMessage.
Trao đổi Customer–Sales/Designer qua hệ thống; phân biệt chatbot và nhân viên thật.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import ChatMessageType


class ChatConversation(Base):
    """Một cuộc hội thoại giữa Customer và nhân viên/chatbot."""
    __tablename__ = "chat_conversations"

    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    staff_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    # Liên kết đến đơn/yêu cầu nếu có
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="SET NULL"), nullable=True)
    design_request_id = Column(Integer, ForeignKey("design_requests.request_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    staff = relationship("User", foreign_keys=[staff_id])
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    def __repr__(self) -> str:
        return f"<ChatConversation id={self.conversation_id} customer={self.customer_id}>"


class ChatMessage(Base):
    """Một tin nhắn trong cuộc hội thoại."""
    __tablename__ = "chat_messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.conversation_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)  # Null = chatbot/system
    message_type = Column(
        SAEnum(ChatMessageType, name="chat_message_type_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=ChatMessageType.TEXT
    )
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")
    sender = relationship("User")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.message_id} conv={self.conversation_id} type={self.message_type}>"

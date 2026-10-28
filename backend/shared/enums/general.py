"""
Các enum tổng hợp dùng chung: giới tính, loại thông báo, loại tin nhắn chat.
"""
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class NotificationType(str, enum.Enum):
    """Phân loại thông báo để hiển thị icon/điều hướng phù hợp."""
    ORDER_UPDATE = "order_update"
    PAYMENT_UPDATE = "payment_update"
    DESIGN_UPDATE = "design_update"
    TRYON_RESULT = "tryon_result"
    CHAT_MESSAGE = "chat_message"
    PROMOTION = "promotion"
    SYSTEM = "system"


class ChatMessageType(str, enum.Enum):
    """Phân biệt tin nhắn chatbot và nhân viên thật."""
    TEXT = "text"
    IMAGE = "image"
    SYSTEM = "system"     # Tin hệ thống tự động
    CHATBOT = "chatbot"   # Chatbot AI trả lời

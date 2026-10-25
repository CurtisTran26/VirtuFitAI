"""
Enum definitions dùng chung toàn hệ thống VirtuFit AI.
Import tất cả enums từ đây để đảm bảo nhất quán giữa App API và Management API.
"""
from .roles import UserRole
from .order_status import OrderStatus, PaymentStatus, PaymentMethod, ShippingMethod
from .design_status import DesignRequestStatus
from .tryon_status import TryOnJobStatus
from .general import Gender, NotificationType, ChatMessageType

__all__ = [
    "UserRole",
    "OrderStatus", "PaymentStatus", "PaymentMethod", "ShippingMethod",
    "DesignRequestStatus",
    "TryOnJobStatus",
    "Gender", "NotificationType", "ChatMessageType",
]

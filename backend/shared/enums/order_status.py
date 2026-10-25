"""
Enum trạng thái đơn hàng, thanh toán, phương thức thanh toán và vận chuyển.
Theo đề xuất README mục 8 đã được nhóm duyệt.
"""
import enum


class OrderStatus(str, enum.Enum):
    """Trạng thái vòng đời đơn hàng."""
    PENDING = "pending"              # Vừa tạo, chờ xác nhận
    CONFIRMED = "confirmed"          # Đã xác nhận (đã thanh toán hoặc COD)
    PACKING = "packing"              # Warehouse đang đóng gói
    SHIPPED = "shipped"              # Đã giao cho đơn vị vận chuyển
    DELIVERED = "delivered"          # Giao hàng thành công
    CANCELLED = "cancelled"          # Đã hủy


class PaymentStatus(str, enum.Enum):
    """Trạng thái thanh toán — tách riêng khỏi trạng thái đơn."""
    UNPAID = "unpaid"                # Chưa thanh toán
    PENDING = "pending"              # Đang xử lý (chờ VNPay callback)
    PAID = "paid"                    # Đã thanh toán thành công
    FAILED = "failed"                # Thanh toán thất bại
    REFUNDED = "refunded"            # Đã hoàn tiền


class PaymentMethod(str, enum.Enum):
    """Phương thức thanh toán."""
    COD = "cod"                      # Thanh toán khi nhận hàng
    VNPAY = "vnpay"                  # Chuyển khoản qua VNPay
    CASH = "cash"                    # Tiền mặt (tại quầy)
    BANK_TRANSFER = "bank_transfer"  # Chuyển khoản QR tại quầy


class ShippingMethod(str, enum.Enum):
    """Phương thức giao hàng."""
    STANDARD = "standard"            # Giao hàng tiêu chuẩn
    EXPRESS = "express"              # Giao hàng nhanh
    IN_STORE = "in_store"            # Nhận tại cửa hàng

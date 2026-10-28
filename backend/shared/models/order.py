"""
SQLAlchemy models cho Order, OrderItem.
Đơn hàng thông thường (từ app) và đơn tại quầy (Sales Staff tạo).
Snapshot giá tại thời điểm đặt — không tin tổng tiền frontend gửi lên.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import OrderStatus, PaymentStatus, PaymentMethod, ShippingMethod


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String(30), unique=True, nullable=False, index=True)  # VF-20261017-XXXX
    customer_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True)  # Nullable cho đơn quầy khách vãng lai
    staff_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)  # Sales Staff tạo đơn quầy
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="RESTRICT"), nullable=True)

    # Trạng thái (tách riêng đơn vs thanh toán)
    status = Column(
        SAEnum(OrderStatus, name="order_status_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=OrderStatus.PENDING, index=True
    )
    payment_status = Column(
        SAEnum(PaymentStatus, name="payment_status_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=PaymentStatus.UNPAID
    )
    payment_method = Column(
        SAEnum(PaymentMethod, name="payment_method_enum", create_constraint=False, native_enum=False, length=20),
        nullable=True
    )
    shipping_method = Column(
        SAEnum(ShippingMethod, name="shipping_method_enum", create_constraint=False, native_enum=False, length=20),
        nullable=True, default=ShippingMethod.STANDARD
    )

    # Snapshot địa chỉ giao hàng (lưu tại thời điểm đặt, không tham chiếu bảng address)
    shipping_name = Column(String(200), nullable=True)
    shipping_phone = Column(String(20), nullable=True)
    shipping_address = Column(String(500), nullable=True)

    # Tài chính — backend tính, không tin client
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)          # Tổng tiền hàng
    shipping_fee = Column(Numeric(15, 2), nullable=False, default=0)      # Phí ship
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)   # Giảm giá / voucher
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)      # Tổng thanh toán

    # Đơn tại quầy
    is_counter_order = Column(Boolean, nullable=False, default=False)
    cash_received = Column(Numeric(15, 2), nullable=True)   # Tiền khách đưa (tiền mặt)
    cash_change = Column(Numeric(15, 2), nullable=True)     # Tiền thừa

    # Liên kết thiết kế riêng (nếu là đơn custom)
    design_request_id = Column(Integer, ForeignKey("design_requests.request_id", ondelete="SET NULL"), nullable=True)

    note = Column(Text, nullable=True)
    cancelled_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    staff = relationship("User", foreign_keys=[staff_id])
    store = relationship("Store")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment_transactions = relationship("PaymentTransaction", back_populates="order", cascade="all, delete-orphan")
    design_request = relationship("DesignRequest", foreign_keys=[design_request_id])

    def __repr__(self) -> str:
        return f"<Order id={self.order_id} code='{self.order_code}' status={self.status}>"


class OrderItem(Base):
    """Từng dòng sản phẩm trong đơn — snapshot giá tại thời điểm đặt."""
    __tablename__ = "order_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False)
    size_id = Column(Integer, ForeignKey("product_sizes.size_id", ondelete="RESTRICT"), nullable=True)

    # Snapshot tại thời điểm đặt hàng
    product_name = Column(String(255), nullable=False)
    size_label = Column(String(20), nullable=True)
    color = Column(String(50), nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)  # Giá gốc hoặc giá KM tại thời điểm đặt
    quantity = Column(Integer, nullable=False, default=1)
    line_total = Column(Numeric(15, 2), nullable=False)   # unit_price * quantity
    product_image_url = Column(String(500), nullable=True)  # Ảnh chính snapshot

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    size = relationship("ProductSize")

    def __repr__(self) -> str:
        return f"<OrderItem id={self.item_id} product='{self.product_name}' qty={self.quantity}>"

"""
SQLAlchemy model cho PaymentTransaction.
Ghi nhận từng giao dịch thanh toán (VNPay callback, tiền mặt, chuyển khoản).
Chống xử lý lặp bằng unique constraint trên transaction_ref.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import PaymentStatus, PaymentMethod


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    transaction_ref = Column(String(100), unique=True, nullable=True, index=True)  # Mã giao dịch VNPay/ngân hàng
    method = Column(
        SAEnum(PaymentMethod, name="txn_payment_method_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False
    )
    status = Column(
        SAEnum(PaymentStatus, name="txn_payment_status_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=PaymentStatus.PENDING
    )
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="VND")

    # Thông tin VNPay / ngân hàng
    gateway_response = Column(Text, nullable=True)     # JSON raw response từ VNPay
    bank_code = Column(String(20), nullable=True)
    card_type = Column(String(20), nullable=True)

    # Nhật ký nhân viên (đơn quầy)
    staff_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    staff_note = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payment_transactions")
    staff = relationship("User")

    def __repr__(self) -> str:
        return f"<PaymentTransaction id={self.transaction_id} ref='{self.transaction_ref}' status={self.status}>"

"""
SQLAlchemy model cho CartItem.
Giỏ hàng lưu DB, mỗi user_id + product_id + size_id là duy nhất.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    size_id = Column(Integer, ForeignKey("product_sizes.size_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "size_id", name="uq_cart_user_product_size"),
    )

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")
    size = relationship("ProductSize")

    def __repr__(self) -> str:
        return f"<CartItem id={self.cart_item_id} user={self.user_id} product={self.product_id} qty={self.quantity}>"

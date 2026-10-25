"""
SQLAlchemy model cho WishlistItem (Danh sách yêu thích).
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    wishlist_item_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )

    # Relationships
    user = relationship("User", back_populates="wishlists")
    product = relationship("Product")

    def __repr__(self) -> str:
        return f"<WishlistItem id={self.wishlist_item_id} user={self.user_id} product={self.product_id}>"

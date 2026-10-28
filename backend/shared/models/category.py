"""
SQLAlchemy model cho bảng categories (Danh mục sản phẩm đa cấp).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships: Self-referencing tree
    children = relationship("Category", backref="parent", remote_side=[category_id])
    products = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category id={self.category_id} name='{self.name}'>"

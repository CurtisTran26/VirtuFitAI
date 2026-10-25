"""
SQLAlchemy model cho bảng stores (Cửa hàng thời trang).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Store id={self.store_id} name='{self.name}'>"

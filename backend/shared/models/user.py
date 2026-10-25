"""
SQLAlchemy models cho User, UserAddress.
Bảng users lưu tất cả 5 vai trò: Customer tự đăng ký, nhân viên/Designer do Admin cấp.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base
from backend.shared.enums import UserRole, Gender


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable cho Google login
    full_name = Column(String(200), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    gender = Column(SAEnum(Gender, name="gender_enum", create_constraint=False, native_enum=False, length=10), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(
        SAEnum(UserRole, name="user_role_enum", create_constraint=False, native_enum=False, length=20),
        nullable=False, default=UserRole.CUSTOMER, index=True
    )
    google_id = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    height_cm = Column(Integer, nullable=True)  # Chiều cao (gợi ý size)
    weight_kg = Column(Integer, nullable=True)  # Cân nặng (gợi ý size)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    design_requests = relationship("DesignRequest", back_populates="customer", foreign_keys="DesignRequest.customer_id")
    tryon_jobs = relationship("TryOnJob", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.user_id} phone='{self.phone}' role={self.role}>"


class UserAddress(Base):
    """Địa chỉ giao hàng — nhập tại checkout, không quản lý sổ địa chỉ riêng (theo README)."""
    __tablename__ = "user_addresses"

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_name = Column(String(200), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    province = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    ward = Column(String(100), nullable=True)
    address_detail = Column(String(500), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="addresses")

    def __repr__(self) -> str:
        return f"<UserAddress id={self.address_id} user_id={self.user_id}>"

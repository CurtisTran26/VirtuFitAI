"""
SQLAlchemy models cho sản phẩm, hình ảnh và kích thước đo may.
Bao gồm: Product, ProductImage, ProductSize.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.shared.database.session import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    discount_price = Column(Numeric(12, 2), nullable=True)
    color = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    view_count = Column(Integer, nullable=False, default=0)
    try_on_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    store = relationship("Store", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan", order_by="ProductSize.size_id")

    def __repr__(self) -> str:
        return f"<Product id={self.product_id} name='{self.name}' price={self.price}>"


class ProductImage(Base):
    __tablename__ = "product_images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    image_type = Column(String(30), nullable=False, default="front") # front, back, detail, model
    is_primary = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    # Relationship
    product = relationship("Product", back_populates="images")

    def __repr__(self) -> str:
        return f"<ProductImage id={self.image_id} product_id={self.product_id} primary={self.is_primary}>"


class ProductSize(Base):
    __tablename__ = "product_sizes"

    size_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    size_label = Column(String(20), nullable=False) # S, M, L, XL, XXL
    stock_quantity = Column(Integer, nullable=False, default=0)
    chest_cm = Column(Numeric(5, 1), nullable=True) # Số đo vòng ngực áo
    waist_cm = Column(Numeric(5, 1), nullable=True) # Số đo vòng eo áo
    length_cm = Column(Numeric(5, 1), nullable=True) # Số đo chiều dài áo/quần

    # Relationship
    product = relationship("Product", back_populates="sizes")

    def __repr__(self) -> str:
        return f"<ProductSize id={self.size_id} size='{self.size_label}' stock={self.stock_quantity}>"

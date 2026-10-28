"""SQLAlchemy models package for VirtuFit AI.

Exports all ORM models for easy importing and Alembic metadata discovery.
"""
from .store import Store
from .category import Category
from .product import Product, ProductImage, ProductSize
from .user import User, UserAddress
from .order import Order, OrderItem
from .payment import PaymentTransaction
from .cart import CartItem
from .wishlist import WishlistItem
from .design import DesignRequest, DesignConcept, DesignRevision
from .tryon import TryOnJob
from .chat import ChatConversation, ChatMessage
from .notification import Notification
from .qr_code import ProductQRCode

__all__ = [
    # Catalog & Store
    "Store",
    "Category",
    "Product",
    "ProductImage",
    "ProductSize",
    # User & Auth
    "User",
    "UserAddress",
    # Order & Payment
    "Order",
    "OrderItem",
    "PaymentTransaction",
    # Cart & Wishlist
    "CartItem",
    "WishlistItem",
    # Custom Design
    "DesignRequest",
    "DesignConcept",
    "DesignRevision",
    # AI Try-on
    "TryOnJob",
    # Chat
    "ChatConversation",
    "ChatMessage",
    # Notification
    "Notification",
    # QR Code
    "ProductQRCode",
]

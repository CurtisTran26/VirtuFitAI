"""Initial database schema for VirtuFit AI

Revision ID: 20261017_0001
Revises: 
Create Date: 2026-10-17 19:00:00.000000

Covers all 20 tables:
1. stores
2. categories
3. products
4. product_images
5. product_sizes
6. users
7. user_addresses
8. orders
9. order_items
10. payment_transactions
11. cart_items
12. wishlist_items
13. design_requests
14. design_concepts
15. design_revisions
16. tryon_jobs
17. chat_conversations
18. chat_messages
19. notifications
20. product_qr_codes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20261017_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. stores
    op.create_table(
        "stores",
        sa.Column("store_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("store_id"),
    )

    # 2. categories
    op.create_table(
        "categories",
        sa.Column("category_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.category_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("category_id"),
        sa.UniqueConstraint("name"),
    )

    # 3. products
    op.create_table(
        "products",
        sa.Column("product_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("discount_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("try_on_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["category_id"], ["categories.category_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.store_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id"),
    )
    op.create_index(op.f("ix_products_created_at"), "products", ["created_at"], unique=False)
    op.create_index(op.f("ix_products_is_active"), "products", ["is_active"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)

    # 4. product_images
    op.create_table(
        "product_images",
        sa.Column("image_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("image_type", sa.String(length=30), nullable=False, server_default="front"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("image_id"),
    )

    # 5. product_sizes
    op.create_table(
        "product_sizes",
        sa.Column("size_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("size_label", sa.String(length=20), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chest_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("waist_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("length_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("size_id"),
    )

    # 6. users
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("gender", sa.String(length=10), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="customer"),
        sa.Column("google_id", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    # 7. user_addresses
    op.create_table(
        "user_addresses",
        sa.Column("address_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("receiver_name", sa.String(length=200), nullable=False),
        sa.Column("receiver_phone", sa.String(length=20), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("ward", sa.String(length=100), nullable=True),
        sa.Column("address_detail", sa.String(length=500), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("address_id"),
    )

    # 8. design_requests (needed before orders for FK reference)
    op.create_table(
        "design_requests",
        sa.Column("request_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_code", sa.String(length=30), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("designer_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="submitted"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reference_images", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("preferred_color", sa.String(length=100), nullable=True),
        sa.Column("preferred_size", sa.String(length=20), nullable=True),
        sa.Column("budget_min", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("budget_max", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("quoted_price", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("estimated_days", sa.Integer(), nullable=True),
        sa.Column("designer_note", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("quoted_at", sa.DateTime(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.category_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.user_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["designer_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("request_id"),
        sa.UniqueConstraint("request_code"),
    )
    op.create_index(op.f("ix_design_requests_created_at"), "design_requests", ["created_at"], unique=False)
    op.create_index(op.f("ix_design_requests_request_code"), "design_requests", ["request_code"], unique=True)
    op.create_index(op.f("ix_design_requests_status"), "design_requests", ["status"], unique=False)

    # 9. design_concepts
    op.create_table(
        "design_concepts",
        sa.Column("concept_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("prompt_used", sa.Text(), nullable=True),
        sa.Column("ai_provider", sa.String(length=50), nullable=True),
        sa.Column("is_selected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["request_id"], ["design_requests.request_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("concept_id"),
    )

    # 10. design_revisions
    op.create_table(
        "design_revisions",
        sa.Column("revision_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("revision_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["author_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["request_id"], ["design_requests.request_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("revision_id"),
    )

    # 11. orders
    op.create_table(
        "orders",
        sa.Column("order_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_code", sa.String(length=30), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("staff_id", sa.Integer(), nullable=True),
        sa.Column("store_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="unpaid"),
        sa.Column("payment_method", sa.String(length=20), nullable=True),
        sa.Column("shipping_method", sa.String(length=20), nullable=True, server_default="standard"),
        sa.Column("shipping_name", sa.String(length=200), nullable=True),
        sa.Column("shipping_phone", sa.String(length=20), nullable=True),
        sa.Column("shipping_address", sa.String(length=500), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0"),
        sa.Column("shipping_fee", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0"),
        sa.Column("is_counter_order", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("cash_received", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("cash_change", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("design_request_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("cancelled_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("shipped_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["users.user_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["design_request_id"], ["design_requests.request_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["staff_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.store_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("order_id"),
        sa.UniqueConstraint("order_code"),
    )
    op.create_index(op.f("ix_orders_created_at"), "orders", ["created_at"], unique=False)
    op.create_index(op.f("ix_orders_order_code"), "orders", ["order_code"], unique=True)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)

    # 12. order_items
    op.create_table(
        "order_items",
        sa.Column("item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("size_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("size_label", sa.String(length=20), nullable=True),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_total", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("product_image_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["size_id"], ["product_sizes.size_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("item_id"),
    )

    # 13. payment_transactions
    op.create_table(
        "payment_transactions",
        sa.Column("transaction_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("transaction_ref", sa.String(length=100), nullable=True),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("gateway_response", sa.Text(), nullable=True),
        sa.Column("bank_code", sa.String(length=20), nullable=True),
        sa.Column("card_type", sa.String(length=20), nullable=True),
        sa.Column("staff_id", sa.Integer(), nullable=True),
        sa.Column("staff_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["staff_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("transaction_id"),
        sa.UniqueConstraint("transaction_ref"),
    )
    op.create_index(op.f("ix_payment_transactions_transaction_ref"), "payment_transactions", ["transaction_ref"], unique=True)

    # 14. cart_items
    op.create_table(
        "cart_items",
        sa.Column("cart_item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("size_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["size_id"], ["product_sizes.size_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("cart_item_id"),
        sa.UniqueConstraint("user_id", "product_id", "size_id", name="uq_cart_user_product_size"),
    )
    op.create_index(op.f("ix_cart_items_user_id"), "cart_items", ["user_id"], unique=False)

    # 15. wishlist_items
    op.create_table(
        "wishlist_items",
        sa.Column("wishlist_item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("wishlist_item_id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
    op.create_index(op.f("ix_wishlist_items_user_id"), "wishlist_items", ["user_id"], unique=False)

    # 16. tryon_jobs
    op.create_table(
        "tryon_jobs",
        sa.Column("job_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("input_image_key", sa.String(length=500), nullable=False),
        sa.Column("product_image_key", sa.String(length=500), nullable=True),
        sa.Column("result_image_key", sa.String(length=500), nullable=True),
        sa.Column("ai_provider", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("job_id"),
    )
    op.create_index(op.f("ix_tryon_jobs_created_at"), "tryon_jobs", ["created_at"], unique=False)
    op.create_index(op.f("ix_tryon_jobs_status"), "tryon_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_tryon_jobs_user_id"), "tryon_jobs", ["user_id"], unique=False)

    # 17. chat_conversations
    op.create_table(
        "chat_conversations",
        sa.Column("conversation_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("design_request_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["customer_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["design_request_id"], ["design_requests.request_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["staff_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("conversation_id"),
    )
    op.create_index(op.f("ix_chat_conversations_customer_id"), "chat_conversations", ["customer_id"], unique=False)

    # 18. chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("message_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=True),
        sa.Column("message_type", sa.String(length=20), nullable=False, server_default="text"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.conversation_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(op.f("ix_chat_messages_conversation_id"), "chat_messages", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_created_at"), "chat_messages", ["created_at"], unique=False)

    # 19. notifications
    op.create_table(
        "notifications",
        sa.Column("notification_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False, server_default="system"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("notification_id"),
    )
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"], unique=False)
    op.create_index(op.f("ix_notifications_is_read"), "notifications", ["is_read"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    # 20. product_qr_codes
    op.create_table(
        "product_qr_codes",
        sa.Column("qr_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("qr_image_url", sa.String(length=500), nullable=False),
        sa.Column("qr_data", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("qr_id"),
        sa.UniqueConstraint("product_id"),
    )


def downgrade() -> None:
    # Drop tables in reverse topological order of dependencies
    op.drop_table("product_qr_codes")
    op.drop_table("notifications")
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
    op.drop_table("tryon_jobs")
    op.drop_table("wishlist_items")
    op.drop_table("cart_items")
    op.drop_table("payment_transactions")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("design_revisions")
    op.drop_table("design_concepts")
    op.drop_table("design_requests")
    op.drop_table("user_addresses")
    op.drop_table("users")
    op.drop_table("product_sizes")
    op.drop_table("product_images")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("stores")

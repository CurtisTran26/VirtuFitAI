from __future__ import annotations

from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.mobile_support import fail


def get_user_cart(db: Session, user_id: UUID) -> dict:
    """Lấy toàn bộ giỏ hàng của người dùng, kiểm tra tồn kho và tính toán giá thời gian thực."""
    rows = db.execute(
        text("""
            SELECT 
                c.id AS cart_item_id,
                c.variant_id,
                c.quantity,
                c.created_at,
                c.updated_at,
                v.product_id,
                v.sku,
                v.size,
                v.color,
                v.stock_on_hand,
                COALESCE(v.reserved_quantity, 0) AS reserved_quantity,
                p.name AS product_name,
                p.price_vnd,
                p.image_url,
                p.is_active AS product_is_active,
                cat.is_active AS category_is_active
            FROM cart_items c
            JOIN product_variants v ON v.id = c.variant_id
            JOIN products p ON p.id = v.product_id
            JOIN categories cat ON cat.id = p.category_id
            WHERE c.user_id = :user_id
            ORDER BY c.created_at ASC
        """),
        {"user_id": user_id}
    ).mappings().all()

    items = []
    total_items = 0
    subtotal_vnd = 0

    for r in rows:
        available_stock = r["stock_on_hand"] - r["reserved_quantity"]
        is_active = bool(r["product_is_active"] and r["category_is_active"])
        is_in_stock = available_stock >= r["quantity"]
        is_available = is_active and is_in_stock

        unavailable_reason = None
        if not is_active:
            unavailable_reason = "Sản phẩm đã ngừng kinh doanh."
        elif available_stock <= 0:
            unavailable_reason = "Sản phẩm đã hết hàng."
        elif not is_in_stock:
            unavailable_reason = f"Tồn kho khả dụng chỉ còn {max(available_stock, 0)} sản phẩm."

        line_total = r["price_vnd"] * r["quantity"]
        total_items += r["quantity"]
        if is_available:
            subtotal_vnd += line_total

        items.append({
            "id": r["cart_item_id"],
            "variant_id": r["variant_id"],
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "sku": r["sku"],
            "color": r["color"],
            "size": r["size"],
            "price_vnd": r["price_vnd"],
            "quantity": r["quantity"],
            "line_total_vnd": line_total,
            "image_url": r["image_url"],
            "stock_available": max(available_stock, 0),
            "is_available": is_available,
            "unavailable_reason": unavailable_reason
        })

    return {
        "items": items,
        "total_items": total_items,
        "total_unique_items": len(items),
        "subtotal_vnd": subtotal_vnd
    }


def add_to_cart(db: Session, user_id: UUID, variant_id: UUID, quantity: int = 1) -> dict:
    """Thêm một biến thể sản phẩm vào giỏ hàng. Nếu đã có thì cộng dồn số lượng (Upsert)."""
    if quantity < 1 or quantity > 100:
        fail(422, "INVALID_QUANTITY", "Số lượng sản phẩm phải từ 1 đến 100.")

    variant = db.execute(
        text("""
            SELECT 
                v.id AS variant_id,
                v.product_id,
                v.stock_on_hand,
                COALESCE(v.reserved_quantity, 0) AS reserved_quantity,
                p.name AS product_name,
                p.is_active AS product_is_active,
                c.is_active AS category_is_active
            FROM product_variants v
            JOIN products p ON p.id = v.product_id
            JOIN categories c ON c.id = p.category_id
            WHERE v.id = :variant_id
        """),
        {"variant_id": variant_id}
    ).mappings().first()

    if not variant:
        fail(404, "VARIANT_NOT_FOUND", "Biến thể sản phẩm không tồn tại.")

    if not variant["product_is_active"] or not variant["category_is_active"]:
        fail(400, "PRODUCT_INACTIVE", "Sản phẩm đã ngừng kinh doanh.")

    available_stock = variant["stock_on_hand"] - variant["reserved_quantity"]

    # Kiểm tra biến thể đã có trong giỏ chưa
    existing = db.execute(
        text("SELECT id, quantity FROM cart_items WHERE user_id = :user_id AND variant_id = :variant_id"),
        {"user_id": user_id, "variant_id": variant_id}
    ).mappings().first()

    target_quantity = (existing["quantity"] + quantity) if existing else quantity

    if target_quantity > 100:
        fail(422, "QUANTITY_EXCEEDED", "Tổng số lượng cho sản phẩm này trong giỏ không được vượt quá 100.")

    if target_quantity > available_stock:
        fail(409, "OUT_OF_STOCK", f"Số lượng yêu cầu ({target_quantity}) vượt quá tồn kho khả dụng ({max(available_stock, 0)}).")

    if existing:
        db.execute(
            text("UPDATE cart_items SET quantity = :quantity, updated_at = now() WHERE id = :id"),
            {"id": existing["id"], "quantity": target_quantity}
        )
    else:
        db.execute(
            text("INSERT INTO cart_items(user_id, variant_id, quantity) VALUES(:user_id, :variant_id, :quantity)"),
            {"user_id": user_id, "variant_id": variant_id, "quantity": target_quantity}
        )
    db.commit()
    return get_user_cart(db, user_id)


def update_cart_item(db: Session, user_id: UUID, item_id: UUID, quantity: int) -> dict:
    """Cập nhật số lượng của một biến thể trong giỏ hàng (hỗ trợ item_id hoặc variant_id)."""
    if quantity < 1 or quantity > 100:
        fail(422, "INVALID_QUANTITY", "Số lượng sản phẩm phải từ 1 đến 100.")

    item = db.execute(
        text("""
            SELECT 
                c.id AS cart_item_id,
                c.variant_id,
                c.quantity,
                v.stock_on_hand,
                COALESCE(v.reserved_quantity, 0) AS reserved_quantity,
                p.is_active AS product_is_active,
                cat.is_active AS category_is_active
            FROM cart_items c
            JOIN product_variants v ON v.id = c.variant_id
            JOIN products p ON p.id = v.product_id
            JOIN categories cat ON cat.id = p.category_id
            WHERE c.user_id = :user_id AND (c.id = :item_id OR c.variant_id = :item_id)
        """),
        {"user_id": user_id, "item_id": item_id}
    ).mappings().first()

    if not item:
        fail(404, "CART_ITEM_NOT_FOUND", "Mục giỏ hàng không tồn tại.")

    if not item["product_is_active"] or not item["category_is_active"]:
        fail(400, "PRODUCT_INACTIVE", "Sản phẩm đã ngừng kinh doanh.")

    available_stock = item["stock_on_hand"] - item["reserved_quantity"]
    if quantity > available_stock:
        fail(409, "OUT_OF_STOCK", f"Số lượng yêu cầu ({quantity}) vượt quá tồn kho khả dụng ({max(available_stock, 0)}).")

    db.execute(
        text("UPDATE cart_items SET quantity = :quantity, updated_at = now() WHERE id = :id"),
        {"id": item["cart_item_id"], "quantity": quantity}
    )
    db.commit()
    return get_user_cart(db, user_id)


def remove_cart_item(db: Session, user_id: UUID, item_id: UUID) -> None:
    """Xóa một mục khỏi giỏ hàng (hỗ trợ item_id hoặc variant_id)."""
    result = db.execute(
        text("DELETE FROM cart_items WHERE user_id = :user_id AND (id = :item_id OR variant_id = :item_id)"),
        {"user_id": user_id, "item_id": item_id}
    )
    db.commit()
    if result.rowcount == 0:
        fail(404, "CART_ITEM_NOT_FOUND", "Mục giỏ hàng không tồn tại.")


def clear_user_cart(db: Session, user_id: UUID) -> None:
    """Xóa toàn bộ giỏ hàng của người dùng."""
    db.execute(
        text("DELETE FROM cart_items WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    db.commit()


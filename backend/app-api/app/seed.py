"""Idempotently load starter catalog data and an optional bootstrap admin."""
from decimal import Decimal
import re

from app.database import SessionLocal
from app.models import Category, Inventory, InventoryAdjustment, Product, SizeChart, User
from app.security import hash_password
from app.settings import settings


def seed() -> None:
    with SessionLocal() as db:
        category = db.query(Category).filter_by(name="Áo thun").one_or_none()
        if category is None:
            category = Category(name="Áo thun", description="Áo thun cơ bản")
            db.add(category)
            db.flush()

        product = db.query(Product).filter_by(sku="TSHIRT-BASIC-001").one_or_none()
        if product is None:
            product = Product(
                name="Áo thun basic", sku="TSHIRT-BASIC-001",
                description="Sản phẩm mẫu để kiểm tra API catalog.",
                price=Decimal("199000.00"), category_id=category.id,
            )
            db.add(product)
            db.flush()

        if db.query(Inventory).filter_by(product_id=product.id, size="M").one_or_none() is None:
            db.add(Inventory(product_id=product.id, size="M", quantity=10))
            db.add(InventoryAdjustment(product_id=product.id, size="M", delta=10, reason="Initial seed stock", actor_id=None))

        if db.query(SizeChart).filter_by(name="Áo thun cơ bản").one_or_none() is None:
            measurements = {"unit": "cm", "sizes": {"S": {"chest": 48, "length": 66}, "M": {"chest": 52, "length": 70}, "L": {"chest": 56, "length": 74}}}
            db.add(SizeChart(name="Áo thun cơ bản", measurements=measurements))

        admin_phone = settings.seed_admin_phone
        admin_password = settings.seed_admin_password
        if admin_phone and admin_password:
            if not re.fullmatch(r"\+?[0-9]{8,15}", admin_phone):
                raise ValueError("SEED_ADMIN_PHONE must contain 8–15 digits with an optional leading +.")
            if len(admin_password) < 8:
                raise ValueError("SEED_ADMIN_PASSWORD must be at least 8 characters.")
            if db.query(User).filter_by(phone=admin_phone).one_or_none() is None:
                db.add(User(
                    phone=admin_phone,
                    full_name=settings.seed_admin_name,
                    password_hash=hash_password(admin_password),
                    role="admin",
                ))
        elif admin_phone or admin_password:
            raise ValueError("Set both SEED_ADMIN_PHONE and SEED_ADMIN_PASSWORD, or neither.")

        db.commit()
    print("Seed completed (safe to run again).")


if __name__ == "__main__":
    seed()

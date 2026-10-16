"""
Script nạp dữ liệu mẫu thực tế (Realistic & Idempotent Seed Data) cho VirtuFit AI.
Tính năng:
- Idempotent: Chạy nhiều lần mà không tạo bản ghi trùng lặp (duplicate).
- Thực tế: Dữ liệu thời trang Việt Nam (VNĐ, size form Việt, số đo ngực/eo/dài để AI try-on).
- Bao gồm cả Positive Cases (hàng bán chạy, giảm giá, đủ size) và Negative Cases (hết hàng, ẩn, size lẻ).
- Chạy bằng 1 lệnh: python -m backend.shared.database.seed
"""
import asyncio
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy import select

from backend.shared.database.session import AsyncSessionLocal, init_tables
from backend.shared.models import Store, Category, Product, ProductImage, ProductSize


async def run_seed() -> None:
    print("=" * 70)
    print("🌱 BẮT ĐẦU NẠP DỮ LIỆU MẪU (SEED DATA) CHO VIRTU FIT AI...")
    print("=" * 70)

    # 1. Đảm bảo bảng đã tồn tại
    print("[1/4] Kiểm tra và khởi tạo các bảng cơ sở dữ liệu...")
    await init_tables()

    async with AsyncSessionLocal() as session:
        # 2. Khởi tạo Cửa hàng mẫu (Store)
        print("[2/4] Kiểm tra & nạp Cửa hàng thời trang...")
        store_stmt = select(Store).where(Store.name == "VirtuFit Flagship Store - TP.HCM")
        store = (await session.execute(store_stmt)).scalars().first()
        if not store:
            store = Store(
                name="VirtuFit Flagship Store - TP.HCM",
                address="123 Đường Nguyễn Trãi, Phường Bến Thành, Quận 1, TP. Hồ Chí Minh",
                phone="0901234567",
                is_active=True
            )
            session.add(store)
            await session.flush()
            print(f"  + Đã tạo cửa hàng: {store.name}")
        else:
            print(f"  ~ Cửa hàng đã tồn tại (ID={store.store_id}), bỏ qua.")

        # 3. Khởi tạo Danh mục phân cấp (Categories)
        print("[3/4] Kiểm tra & nạp Cây danh mục thời trang...")
        categories_data = [
            {"name": "Áo Nam", "parent": None},
            {"name": "Áo Thun Nam", "parent": "Áo Nam"},
            {"name": "Áo Sơ Mi Nam", "parent": "Áo Nam"},
            {"name": "Áo Polo Nam", "parent": "Áo Nam"},
            {"name": "Áo Nữ", "parent": None},
            {"name": "Áo Kiểu Nữ", "parent": "Áo Nữ"},
            {"name": "Áo Croptop Nữ", "parent": "Áo Nữ"},
            {"name": "Quần", "parent": None},
            {"name": "Quần Jeans", "parent": "Quần"},
            {"name": "Quần Tây Âu", "parent": "Quần"},
            {"name": "Váy & Đầm", "parent": None},
            {"name": "Đầm Suông", "parent": "Váy & Đầm"},
            {"name": "Chân Váy Midi", "parent": "Váy & Đầm"},
        ]

        cat_map: Dict[str, Category] = {}
        for c in categories_data:
            c_name = c["name"]
            c_parent_name = c["parent"]
            parent_id = cat_map[c_parent_name].category_id if c_parent_name else None

            stmt = select(Category).where(Category.name == c_name)
            existing_cat = (await session.execute(stmt)).scalars().first()
            if not existing_cat:
                new_cat = Category(name=c_name, parent_id=parent_id)
                session.add(new_cat)
                await session.flush()
                cat_map[c_name] = new_cat
                print(f"  + Đã tạo danh mục: {c_name} (parent_id={parent_id})")
            else:
                cat_map[c_name] = existing_cat

        # 4. Khởi tạo Danh sách sản phẩm mẫu (Products with Sizes & Images)
        print("[4/4] Kiểm tra & nạp Sản phẩm, Kích thước đo may & Hình ảnh...")
        
        products_seed_data: List[Dict[str, Any]] = [
            # --- POSITIVE CASES: Hàng bán chạy, đủ size, có giảm giá ---
            {
                "name": "Áo Thun Cotton Oversize Form Rộng Basic",
                "category": "Áo Thun Nam",
                "description": "Chất liệu 100% Cotton 2 chiều định lượng 250gsm dày dặn, thoáng mát, thấm hút mồ hôi cực tốt. Phù hợp mặc đi chơi, dạo phố.",
                "price": Decimal("249000"),
                "discount_price": Decimal("189000"),
                "color": "Trắng",
                "is_active": True,
                "view_count": 520,
                "try_on_count": 135,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800", "type": "front", "primary": True},
                    {"url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800", "type": "back", "primary": False}
                ],
                "sizes": [
                    {"label": "S", "stock": 25, "chest": 92.0, "waist": 74.0, "length": 66.0},
                    {"label": "M", "stock": 40, "chest": 98.0, "waist": 78.0, "length": 68.0},
                    {"label": "L", "stock": 35, "chest": 104.0, "waist": 84.0, "length": 70.0},
                    {"label": "XL", "stock": 15, "chest": 110.0, "waist": 90.0, "length": 72.0}
                ]
            },
            {
                "name": "Áo Sơ Mi Nam Oxford Cổ Bẻ Dài Tay Slimfit",
                "category": "Áo Sơ Mi Nam",
                "description": "Vải Oxford cao cấp chống nhăn nhẹ, đường may tỉ mỉ, form chuẩn tôn dáng phái mạnh nơi công sở hoặc dự tiệc.",
                "price": Decimal("380000"),
                "discount_price": Decimal("340000"),
                "color": "Xanh nhạt",
                "is_active": True,
                "view_count": 410,
                "try_on_count": 92,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800", "type": "front", "primary": True},
                    {"url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800", "type": "detail", "primary": False}
                ],
                "sizes": [
                    {"label": "M", "stock": 20, "chest": 96.0, "waist": 80.0, "length": 70.0},
                    {"label": "L", "stock": 30, "chest": 102.0, "waist": 86.0, "length": 72.0},
                    {"label": "XL", "stock": 18, "chest": 108.0, "waist": 92.0, "length": 74.0}
                ]
            },
            {
                "name": "Áo Polo Nam Phối Cổ Dệt Thể Thao Pique",
                "category": "Áo Polo Nam",
                "description": "Chất cá sấu Pique co giãn 4 chiều, cổ áo dệt sọc thể thao trẻ trung, giữ form đứng đắn sau nhiều lần giặt.",
                "price": Decimal("320000"),
                "discount_price": None,
                "color": "Đen",
                "is_active": True,
                "view_count": 280,
                "try_on_count": 64,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1625910513413-7223b2072049?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "S", "stock": 12, "chest": 90.0, "waist": 76.0, "length": 67.0},
                    {"label": "M", "stock": 25, "chest": 96.0, "waist": 82.0, "length": 69.0},
                    {"label": "L", "stock": 22, "chest": 102.0, "waist": 88.0, "length": 71.0}
                ]
            },
            {
                "name": "Đầm Suông Linen Cổ V Nữ Tính Dáng Dài",
                "category": "Đầm Suông",
                "description": "Vải đũi linen tự nhiên mộc mạc, thiết kế cổ chữ V thanh thoát, eo thắt nhẹ nhàng giúp che khuyết điểm bụng.",
                "price": Decimal("480000"),
                "discount_price": Decimal("420000"),
                "color": "Be sữa",
                "is_active": True,
                "view_count": 630,
                "try_on_count": 180,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800", "type": "front", "primary": True},
                    {"url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800", "type": "model", "primary": False}
                ],
                "sizes": [
                    {"label": "S", "stock": 15, "chest": 86.0, "waist": 68.0, "length": 110.0},
                    {"label": "M", "stock": 28, "chest": 92.0, "waist": 74.0, "length": 112.0},
                    {"label": "L", "stock": 10, "chest": 98.0, "waist": 80.0, "length": 114.0}
                ]
            },
            {
                "name": "Áo Croptop Nữ Tay Ngắn Bo Eo Ôm Dáng",
                "category": "Áo Croptop Nữ",
                "description": "Áo croptop thun gân ôm sát cơ thể, tôn vòng eo thon gọn, phối cực đẹp cùng quần cạp cao hoặc chân váy.",
                "price": Decimal("160000"),
                "discount_price": Decimal("129000"),
                "color": "Hồng pastel",
                "is_active": True,
                "view_count": 340,
                "try_on_count": 88,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "S", "stock": 18, "chest": 82.0, "waist": 64.0, "length": 42.0},
                    {"label": "M", "stock": 22, "chest": 88.0, "waist": 70.0, "length": 44.0}
                ]
            },
            {
                "name": "Quần Jeans Nam Ống Suông Rộng Rách Gối Cá Tính",
                "category": "Quần Jeans",
                "description": "Chất denim 13oz bền chắc không xù, giặt công nghệ wash bụi bặm phong cách streetwear Hàn Quốc.",
                "price": Decimal("450000"),
                "discount_price": None,
                "color": "Xanh rêu",
                "is_active": True,
                "view_count": 390,
                "try_on_count": 75,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1542272604-780c96856592?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "M", "stock": 14, "chest": 0.0, "waist": 76.0, "length": 100.0},
                    {"label": "L", "stock": 20, "chest": 0.0, "waist": 82.0, "length": 102.0},
                    {"label": "XL", "stock": 16, "chest": 0.0, "waist": 88.0, "length": 104.0}
                ]
            },
            {
                "name": "Chân Váy Xếp Ly Midi Dáng Chữ A Thanh Lịch",
                "category": "Chân Váy Midi",
                "description": "Vải tuyết mưa xếp ly sắc sảo, cạp cao tôn dáng, có quần lót an toàn bên trong.",
                "price": Decimal("290000"),
                "discount_price": Decimal("245000"),
                "color": "Nâu cafe",
                "is_active": True,
                "view_count": 210,
                "try_on_count": 53,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "S", "stock": 15, "chest": 0.0, "waist": 66.0, "length": 75.0},
                    {"label": "M", "stock": 20, "chest": 0.0, "waist": 72.0, "length": 76.0}
                ]
            },

            # --- NEGATIVE CASE 1: SẢN PHẨM HẾT HÀNG (Out of Stock) ---
            # Dùng để kiểm thử bộ lọc `in_stock_only=true` (sản phẩm này sẽ biến mất khi bật filter)
            {
                "name": "Áo Khoác Bomber Da Lộn Phối Tay Limited Edition",
                "category": "Áo Nam",
                "description": "Phiên bản giới hạn mùa đông đã bán sạch toàn bộ kho hàng (Test Case: Hết Hàng).",
                "price": Decimal("750000"),
                "discount_price": None,
                "color": "Nâu da bò",
                "is_active": True,
                "view_count": 890,
                "try_on_count": 210,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "M", "stock": 0, "chest": 104.0, "waist": 90.0, "length": 68.0},
                    {"label": "L", "stock": 0, "chest": 110.0, "waist": 96.0, "length": 70.0}
                ]
            },

            # --- NEGATIVE CASE 2: SẢN PHẨM ẨN KHỎI HỆ THỐNG (Inactive) ---
            # Dùng để kiểm thử bảo mật: Sản phẩm này KHÔNG BAO GIỜ được xuất hiện trên catalog hay search
            {
                "name": "Áo Thun Cũ Mẫu Lỗi Năm Ngoái (Ngừng Kinh Doanh)",
                "category": "Áo Thun Nam",
                "description": "Sản phẩm bị vô hiệu hóa is_active=False (Test Case: Ẩn Sản Phẩm).",
                "price": Decimal("99000"),
                "discount_price": None,
                "color": "Xám chuột",
                "is_active": False,
                "view_count": 10,
                "try_on_count": 0,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "M", "stock": 10, "chest": 96.0, "waist": 80.0, "length": 68.0}
                ]
            },

            # --- NEGATIVE CASE 3: SẢN PHẨM LẺ SIZE (Chỉ còn đúng 1 size XL, các size khác hết) ---
            # Dùng để kiểm thử lọc theo `size=M` thì không ra, nhưng lọc `size=XL` thì ra
            {
                "name": "Quần Tây Âu Nam Cạp Cao Xếp Ly Form Rộng Classic",
                "category": "Quần Tây Âu",
                "description": "Mẫu quần âu xuất dư, hiện tại trong kho chỉ còn sót đúng 1 chiếc size XL.",
                "price": Decimal("390000"),
                "discount_price": Decimal("320000"),
                "color": "Xám than",
                "is_active": True,
                "view_count": 150,
                "try_on_count": 30,
                "images": [
                    {"url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800", "type": "front", "primary": True}
                ],
                "sizes": [
                    {"label": "S", "stock": 0, "chest": 0.0, "waist": 72.0, "length": 98.0},
                    {"label": "M", "stock": 0, "chest": 0.0, "waist": 78.0, "length": 100.0},
                    {"label": "XL", "stock": 1, "chest": 0.0, "waist": 90.0, "length": 104.0}
                ]
            }
        ]

        created_count = 0
        skipped_count = 0

        for p_data in products_seed_data:
            p_name = p_data["name"]
            p_cat_name = p_data["category"]
            cat_obj = cat_map.get(p_cat_name)

            if not cat_obj:
                print(f"  ! Không tìm thấy category '{p_cat_name}', bỏ qua sản phẩm: {p_name}")
                continue

            # Kiểm tra xem sản phẩm đã tồn tại hay chưa (Idempotent check)
            prod_stmt = select(Product).where(Product.name == p_name)
            existing_prod = (await session.execute(prod_stmt)).scalars().first()

            if existing_prod:
                skipped_count += 1
                continue

            # Tạo mới sản phẩm
            product = Product(
                store_id=store.store_id,
                category_id=cat_obj.category_id,
                name=p_name,
                description=p_data["description"],
                price=p_data["price"],
                discount_price=p_data["discount_price"],
                color=p_data["color"],
                is_active=p_data["is_active"],
                view_count=p_data["view_count"],
                try_on_count=p_data["try_on_count"]
            )
            session.add(product)
            await session.flush()

            # Thêm hình ảnh
            for idx, img in enumerate(p_data["images"]):
                p_img = ProductImage(
                    product_id=product.product_id,
                    image_url=img["url"],
                    image_type=img["type"],
                    is_primary=img["primary"],
                    sort_order=idx
                )
                session.add(p_img)

            # Thêm kích thước
            for s in p_data["sizes"]:
                p_size = ProductSize(
                    product_id=product.product_id,
                    size_label=s["label"],
                    stock_quantity=s["stock"],
                    chest_cm=Decimal(str(s["chest"])),
                    waist_cm=Decimal(str(s["waist"])),
                    length_cm=Decimal(str(s["length"]))
                )
                session.add(p_size)

            created_count += 1
            print(f"  + Đã tạo sản phẩm: {p_name} ({len(p_data['sizes'])} sizes, {len(p_data['images'])} images)")

        await session.commit()

        print("-" * 70)
        print(f"✅ HOÀN TẤT SEED DỮ LIỆU:")
        print(f"   - Tạo mới: {created_count} sản phẩm")
        print(f"   - Đã tồn tại từ trước (bỏ qua): {skipped_count} sản phẩm")
        print(f"   - Tổng số danh mục: {len(cat_map)} categories")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_seed())

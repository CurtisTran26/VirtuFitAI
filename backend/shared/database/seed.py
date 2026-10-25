"""
Script nạp dữ liệu mẫu thực tế (Realistic & Idempotent Seed Data) cho VirtuFit AI.
Tính năng:
- Idempotent: Chạy nhiều lần mà không tạo bản ghi trùng lặp (duplicate).
- Thực tế: Dữ liệu thời trang Việt Nam (VNĐ, size form Việt, số đo ngực/eo/dài để AI try-on).
- Bao gồm cả 5 vai trò (Admin, Sales Staff, Warehouse Staff, Designer, Customer).
- Bao gồm đơn hàng online, đơn tại quầy (counter order), giao dịch thanh toán (VNPay + tiền mặt).
- Bao gồm yêu cầu thiết kế riêng (Custom Design), tác vụ thử đồ AI (Try-on), mã QR, chat, thông báo.
- Chạy bằng 1 lệnh: python -m backend.shared.database.seed
"""
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy import select

from backend.shared.database.session import AsyncSessionLocal, init_tables
from backend.shared.enums import (
    UserRole, Gender, OrderStatus, PaymentStatus, PaymentMethod, ShippingMethod,
    DesignRequestStatus, TryOnJobStatus, NotificationType, ChatMessageType
)
from backend.shared.models import (
    Store, Category, Product, ProductImage, ProductSize,
    User, UserAddress, Order, OrderItem, PaymentTransaction,
    CartItem, WishlistItem, DesignRequest, DesignConcept, DesignRevision,
    TryOnJob, ChatConversation, ChatMessage, Notification, ProductQRCode
)


async def run_seed() -> None:
    print("=" * 70)
    print("🌱 BẮT ĐẦU NẠP DỮ LIỆU MẪU (SEED DATA) CHO VIRTU FIT AI...")
    print("=" * 70)

    # 1. Đảm bảo bảng đã tồn tại
    print("[1/9] Kiểm tra và khởi tạo các bảng cơ sở dữ liệu...")
    await init_tables()

    async with AsyncSessionLocal() as session:
        # 2. Khởi tạo Cửa hàng mẫu (Store)
        print("[2/9] Kiểm tra & nạp Cửa hàng thời trang...")
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
        print("[3/9] Kiểm tra & nạp Cây danh mục thời trang...")
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
        print("[4/9] Kiểm tra & nạp Sản phẩm, Kích thước đo may & Hình ảnh...")
        products_seed_data: List[Dict[str, Any]] = [
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

        saved_products: Dict[str, Product] = {}
        for p_data in products_seed_data:
            p_name = p_data["name"]
            cat_obj = cat_map.get(p_data["category"])
            if not cat_obj:
                continue

            prod_stmt = select(Product).where(Product.name == p_name)
            existing_prod = (await session.execute(prod_stmt)).scalars().first()
            if existing_prod:
                saved_products[p_name] = existing_prod
                continue

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
            saved_products[p_name] = product

            for idx, img in enumerate(p_data["images"]):
                session.add(ProductImage(
                    product_id=product.product_id,
                    image_url=img["url"],
                    image_type=img["type"],
                    is_primary=img["primary"],
                    sort_order=idx
                ))

            for s in p_data["sizes"]:
                session.add(ProductSize(
                    product_id=product.product_id,
                    size_label=s["label"],
                    stock_quantity=s["stock"],
                    chest_cm=Decimal(str(s["chest"])),
                    waist_cm=Decimal(str(s["waist"])),
                    length_cm=Decimal(str(s["length"]))
                ))
            print(f"  + Đã tạo sản phẩm: {p_name}")

        await session.flush()

        # 5. Khởi tạo 5 vai trò Người dùng (Users & Addresses)
        print("[5/9] Kiểm tra & nạp Người dùng cho cả 5 vai trò nghiệp vụ...")
        users_seed_data = [
            {
                "phone": "0909000001",
                "email": "admin@virtufit.ai",
                "full_name": "Quản Trị Viên Hệ Thống",
                "role": UserRole.ADMIN,
                "gender": Gender.MALE,
                "is_verified": True,
            },
            {
                "phone": "0909000002",
                "email": "sales@virtufit.ai",
                "full_name": "Nguyễn Văn Sales",
                "role": UserRole.SALES_STAFF,
                "gender": Gender.FEMALE,
                "is_verified": True,
            },
            {
                "phone": "0909000003",
                "email": "warehouse@virtufit.ai",
                "full_name": "Trần Văn Kho",
                "role": UserRole.WAREHOUSE_STAFF,
                "gender": Gender.MALE,
                "is_verified": True,
            },
            {
                "phone": "0909000004",
                "email": "designer@virtufit.ai",
                "full_name": "Lê Thị Designer",
                "role": UserRole.DESIGNER,
                "gender": Gender.FEMALE,
                "is_verified": True,
            },
            {
                "phone": "0909000005",
                "email": "customer@virtufit.ai",
                "full_name": "Hoàng Minh Khách",
                "role": UserRole.CUSTOMER,
                "gender": Gender.MALE,
                "height_cm": 174,
                "weight_kg": 67,
                "is_verified": True,
                "address": {
                    "receiver_name": "Hoàng Minh Khách",
                    "receiver_phone": "0909000005",
                    "province": "TP. Hồ Chí Minh",
                    "district": "Quận 1",
                    "ward": "Phường Bến Nghé",
                    "address_detail": "Tòa nhà Bitexco, 2 Hải Triều",
                    "is_default": True
                }
            },
            {
                "phone": "0909000006",
                "email": "customer2@virtufit.ai",
                "full_name": "Đặng Mai Vy",
                "role": UserRole.CUSTOMER,
                "gender": Gender.FEMALE,
                "height_cm": 162,
                "weight_kg": 48,
                "is_verified": True,
                "address": {
                    "receiver_name": "Đặng Mai Vy",
                    "receiver_phone": "0909000006",
                    "province": "TP. Hồ Chí Minh",
                    "district": "Quận 7",
                    "ward": "Phường Tân Phong",
                    "address_detail": "Chung cư Sunrise City, Nguyễn Hữu Thọ",
                    "is_default": True
                }
            }
        ]

        saved_users: Dict[str, User] = {}
        for u in users_seed_data:
            stmt = select(User).where(User.email == u["email"])
            existing_user = (await session.execute(stmt)).scalars().first()
            if not existing_user:
                # Password hash tượng trưng cho dev (plaintext password = 'password123')
                new_user = User(
                    phone=u["phone"],
                    email=u["email"],
                    password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQmG6W565v8v2fQ5a6n.e",
                    full_name=u["full_name"],
                    role=u["role"],
                    gender=u.get("gender"),
                    height_cm=u.get("height_cm"),
                    weight_kg=u.get("weight_kg"),
                    is_active=True,
                    is_verified=u["is_verified"]
                )
                session.add(new_user)
                await session.flush()
                saved_users[u["email"]] = new_user

                if "address" in u:
                    addr_data = u["address"]
                    session.add(UserAddress(
                        user_id=new_user.user_id,
                        receiver_name=addr_data["receiver_name"],
                        receiver_phone=addr_data["receiver_phone"],
                        province=addr_data["province"],
                        district=addr_data["district"],
                        ward=addr_data["ward"],
                        address_detail=addr_data["address_detail"],
                        is_default=addr_data["is_default"]
                    ))
                print(f"  + Đã tạo User: {u['full_name']} (Role={u['role'].value})")
            else:
                saved_users[u["email"]] = existing_user

        await session.flush()

        customer_user = saved_users.get("customer@virtufit.ai")
        sales_user = saved_users.get("sales@virtufit.ai")
        designer_user = saved_users.get("designer@virtufit.ai")

        # 6. Khởi tạo Giỏ hàng & Danh sách yêu thích mẫu
        print("[6/9] Kiểm tra & nạp Giỏ hàng & Wishlist...")
        tshirt_prod = saved_products.get("Áo Thun Cotton Oversize Form Rộng Basic")
        if customer_user and tshirt_prod:
            # Lấy size M của áo thun
            size_stmt = select(ProductSize).where(
                ProductSize.product_id == tshirt_prod.product_id,
                ProductSize.size_label == "M"
            )
            size_m = (await session.execute(size_stmt)).scalars().first()

            if size_m:
                cart_stmt = select(CartItem).where(
                    CartItem.user_id == customer_user.user_id,
                    CartItem.product_id == tshirt_prod.product_id
                )
                if not (await session.execute(cart_stmt)).scalars().first():
                    session.add(CartItem(
                        user_id=customer_user.user_id,
                        product_id=tshirt_prod.product_id,
                        size_id=size_m.size_id,
                        quantity=2
                    ))
                    print(f"  + Đã tạo Giỏ hàng mẫu cho {customer_user.full_name}")

            # Wishlist: Đầm Suông Linen
            dress_prod = saved_products.get("Đầm Suông Linen Cổ V Nữ Tính Dáng Dài")
            if dress_prod:
                wish_stmt = select(WishlistItem).where(
                    WishlistItem.user_id == customer_user.user_id,
                    WishlistItem.product_id == dress_prod.product_id
                )
                if not (await session.execute(wish_stmt)).scalars().first():
                    session.add(WishlistItem(
                        user_id=customer_user.user_id,
                        product_id=dress_prod.product_id
                    ))
                    print(f"  + Đã tạo Wishlist mẫu cho {customer_user.full_name}")

        await session.flush()

        # 7. Khởi tạo Đơn hàng mẫu (Online VNPay, Tại Quầy Tiền Mặt, Chờ Thanh Toán)
        print("[7/9] Kiểm tra & nạp Đơn hàng & Giao dịch thanh toán...")
        if customer_user and tshirt_prod:
            # Đơn 1: Đơn Online giao thành công, thanh toán VNPay
            order_stmt1 = select(Order).where(Order.order_code == "VF-20261017-0001")
            if not (await session.execute(order_stmt1)).scalars().first():
                order1 = Order(
                    order_code="VF-20261017-0001",
                    customer_id=customer_user.user_id,
                    store_id=store.store_id,
                    status=OrderStatus.DELIVERED,
                    payment_status=PaymentStatus.PAID,
                    payment_method=PaymentMethod.VNPAY,
                    shipping_method=ShippingMethod.EXPRESS,
                    shipping_name="Hoàng Minh Khách",
                    shipping_phone="0909000005",
                    shipping_address="Tòa nhà Bitexco, 2 Hải Triều, Q.1, TP.HCM",
                    subtotal=Decimal("378000"),
                    shipping_fee=Decimal("30000"),
                    discount_amount=Decimal("0"),
                    total_amount=Decimal("408000"),
                    is_counter_order=False,
                    delivered_at=datetime.utcnow()
                )
                session.add(order1)
                await session.flush()

                # Order item
                session.add(OrderItem(
                    order_id=order1.order_id,
                    product_id=tshirt_prod.product_id,
                    product_name=tshirt_prod.name,
                    size_label="M",
                    color="Trắng",
                    unit_price=Decimal("189000"),
                    quantity=2,
                    line_total=Decimal("378000"),
                    product_image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800"
                ))

                # Payment txn
                session.add(PaymentTransaction(
                    order_id=order1.order_id,
                    transaction_ref="VNP20261017123456",
                    method=PaymentMethod.VNPAY,
                    status=PaymentStatus.PAID,
                    amount=Decimal("408000"),
                    currency="VND",
                    bank_code="NCB",
                    card_type="ATM",
                    gateway_response='{"vnp_ResponseCode": "00", "vnp_TransactionStatus": "00"}',
                    completed_at=datetime.utcnow()
                ))
                print(f"  + Đã tạo đơn Online mẫu: {order1.order_code} (DELIVERED - PAID)")

            # Đơn 2: Đơn Tại Quầy do Sales Staff tạo, trả tiền mặt
            order_stmt2 = select(Order).where(Order.order_code == "VF-20261017-0002")
            if not (await session.execute(order_stmt2)).scalars().first():
                order2 = Order(
                    order_code="VF-20261017-0002",
                    customer_id=None,  # Khách vãng lai
                    staff_id=sales_user.user_id if sales_user else None,
                    store_id=store.store_id,
                    status=OrderStatus.DELIVERED,
                    payment_status=PaymentStatus.PAID,
                    payment_method=PaymentMethod.CASH,
                    subtotal=Decimal("380000"),
                    shipping_fee=Decimal("0"),
                    discount_amount=Decimal("0"),
                    total_amount=Decimal("380000"),
                    is_counter_order=True,
                    cash_received=Decimal("400000"),
                    cash_change=Decimal("20000"),
                    delivered_at=datetime.utcnow()
                )
                session.add(order2)
                await session.flush()

                somi_prod = saved_products.get("Áo Sơ Mi Nam Oxford Cổ Bẻ Dài Tay Slimfit")
                if somi_prod:
                    session.add(OrderItem(
                        order_id=order2.order_id,
                        product_id=somi_prod.product_id,
                        product_name=somi_prod.name,
                        size_label="L",
                        color="Xanh nhạt",
                        unit_price=Decimal("380000"),
                        quantity=1,
                        line_total=Decimal("380000")
                    ))

                session.add(PaymentTransaction(
                    order_id=order2.order_id,
                    transaction_ref="CASH-20261017-0002",
                    method=PaymentMethod.CASH,
                    status=PaymentStatus.PAID,
                    amount=Decimal("380000"),
                    currency="VND",
                    staff_id=sales_user.user_id if sales_user else None,
                    staff_note="Khách đưa 400.000đ, thối lại 20.000đ",
                    completed_at=datetime.utcnow()
                ))
                print(f"  + Đã tạo đơn tại quầy mẫu: {order2.order_code} (COUNTER - CASH)")

        await session.flush()

        # 8. Khởi tạo Yêu cầu Thiết kế Riêng (Custom Design Request) & Thử đồ AI (Try-on)
        print("[8/9] Kiểm tra & nạp Yêu cầu thiết kế riêng & AI Try-on...")
        if customer_user and designer_user:
            dr_stmt = select(DesignRequest).where(DesignRequest.request_code == "DR-20261017-0001")
            if not (await session.execute(dr_stmt)).scalars().first():
                dr = DesignRequest(
                    request_code="DR-20261017-0001",
                    customer_id=customer_user.user_id,
                    designer_id=designer_user.user_id,
                    status=DesignRequestStatus.QUOTED,
                    title="Thiết kế Áo Dài Cách Tân Nam Họa Tiết Hạc Trắng",
                    description="Em muốn đặt may áo dài cách tân màu xanh navy trầm, cổ tàu 3cm, thêu họa tiết chim hạc trắng trước ngực để mặc đám cưới.",
                    preferred_color="Xanh Navy",
                    preferred_size="L",
                    budget_min=Decimal("1500000"),
                    budget_max=Decimal("2500000"),
                    quoted_price=Decimal("2200000"),
                    estimated_days=7,
                    designer_note="Chất liệu vải lụa tơ tằm dệt cao cấp, thêu tay thủ công mũi đột sắc sảo.",
                    quoted_at=datetime.utcnow()
                )
                session.add(dr)
                await session.flush()

                # AI concept
                session.add(DesignConcept(
                    request_id=dr.request_id,
                    image_url="designs/concept_navy_crane_01.png",
                    prompt_used="Modern Vietnamese Ao Dai for men, navy blue silk, minimal white crane embroidery on chest, studio lighting",
                    ai_provider="Stable Diffusion XL",
                    is_selected=1
                ))

                # Revision message
                session.add(DesignRevision(
                    request_id=dr.request_id,
                    author_id=designer_user.user_id,
                    content="Chào anh Khách, em đã lên concept số 1 và báo giá 2.200.000đ hoàn thiện trong 7 ngày. Anh xem hình concept và xác nhận giúp em nhé!",
                    revision_number=1
                ))
                print(f"  + Đã tạo Design Request mẫu: {dr.request_code}")

            # AI Try-on Job
            tryon_stmt = select(TryOnJob).where(TryOnJob.user_id == customer_user.user_id)
            if not (await session.execute(tryon_stmt)).scalars().first() and tshirt_prod:
                session.add(TryOnJob(
                    user_id=customer_user.user_id,
                    product_id=tshirt_prod.product_id,
                    status=TryOnJobStatus.COMPLETED,
                    input_image_key="users/tryon/user_avatar_pose.jpg",
                    product_image_key="products/tshirt_front.jpg",
                    result_image_key="users/tryon/result_tshirt_fit.jpg",
                    ai_provider="IDM-VTON",
                    processing_time_ms=4200,
                    completed_at=datetime.utcnow()
                ))
                print(f"  + Đã tạo AI Try-On Job mẫu cho {customer_user.full_name}")

        await session.flush()

        # 9. Khởi tạo QR Code Sản Phẩm, Chat & Thông Báo mẫu
        print("[9/9] Kiểm tra & nạp QR Code Sản phẩm, Chat & Thông báo...")
        if tshirt_prod:
            qr_stmt = select(ProductQRCode).where(ProductQRCode.product_id == tshirt_prod.product_id)
            if not (await session.execute(qr_stmt)).scalars().first():
                session.add(ProductQRCode(
                    product_id=tshirt_prod.product_id,
                    qr_image_url="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=virtufit://product/1",
                    qr_data="virtufit://product/1",
                    is_active=True
                ))
                print(f"  + Đã tạo QR Code cho sản phẩm: {tshirt_prod.name}")

        if customer_user and sales_user:
            # Chat conversation
            chat_stmt = select(ChatConversation).where(ChatConversation.customer_id == customer_user.user_id)
            if not (await session.execute(chat_stmt)).scalars().first():
                conv = ChatConversation(
                    customer_id=customer_user.user_id,
                    staff_id=sales_user.user_id,
                    subject="Tư vấn chọn size áo thun",
                    is_active=True
                )
                session.add(conv)
                await session.flush()

                session.add(ChatMessage(
                    conversation_id=conv.conversation_id,
                    sender_id=customer_user.user_id,
                    message_type=ChatMessageType.TEXT,
                    content="Chào shop, mình cao 1m74 nặng 67kg thì mặc size nào vừa vặn ạ?"
                ))
                session.add(ChatMessage(
                    conversation_id=conv.conversation_id,
                    sender_id=sales_user.user_id,
                    message_type=ChatMessageType.TEXT,
                    content="Dạ chào anh Khách! Với số đo 1m74 - 67kg, anh mặc size L sẽ rất thoải mái theo form oversize ạ. Hoặc size M nếu anh thích mặc vừa người."
                ))
                print(f"  + Đã tạo Chat Conversation mẫu")

            # Notifications
            notif_stmt = select(Notification).where(Notification.user_id == customer_user.user_id)
            if not (await session.execute(notif_stmt)).scalars().first():
                session.add(Notification(
                    user_id=customer_user.user_id,
                    type=NotificationType.ORDER_UPDATE,
                    title="Đơn hàng VF-20261017-0001 đã giao thành công",
                    content="Kiện hàng của quý khách đã được giao tận tay. Cảm ơn bạn đã lựa chọn VirtuFit AI!",
                    reference_type="order",
                    reference_id=1,
                    is_read=True
                ))
                session.add(Notification(
                    user_id=customer_user.user_id,
                    type=NotificationType.DESIGN_UPDATE,
                    title="Designer đã gửi báo giá cho yêu cầu DR-20261017-0001",
                    content="Nhà thiết kế Lê Thị Designer đã hoàn thành concept và gửi báo giá 2.200.000đ. Vui lòng kiểm tra và phản hồi.",
                    reference_type="design_request",
                    reference_id=1,
                    is_read=False
                ))
                print(f"  + Đã tạo Thông báo mẫu cho {customer_user.full_name}")

        await session.commit()

        print("-" * 70)
        print("✅ HOÀN TẤT TOÀN BỘ NẠP SEED DATA:")
        print("   ✓ Cửa hàng (Store) & 13 Danh mục (Categories)")
        print(f"   ✓ {len(saved_products)} Sản phẩm kèm ảnh và kích thước đo may")
        print("   ✓ 6 Tài khoản người dùng phủ đủ 5 vai trò (Admin, Sales, Warehouse, Designer, Customer)")
        print("   ✓ Giỏ hàng & Danh sách yêu thích mẫu")
        print("   ✓ 2 Đơn hàng (Online VNPay & Tại quầy tiền mặt)")
        print("   ✓ 1 Yêu cầu thiết kế riêng (Custom Design) kèm Concept AI")
        print("   ✓ 1 Tác vụ thử đồ AI (AI Try-on Job)")
        print("   ✓ QR Code sản phẩm, Hội thoại Chat tư vấn, 2 Thông báo hệ thống")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_seed())

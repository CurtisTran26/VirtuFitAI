"""
Dịch vụ xử lý nghiệp vụ Catalog, Tìm kiếm, Lọc và Chi tiết sản phẩm.
Thiết kế theo chuẩn Repository/Service Layer (truy vấn trực tiếp DB, dễ dàng bọc Redis Caching về sau).
"""
import math
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.shared.models import Category, Product, ProductImage, ProductSize, Store
from app.schemas.catalog import (
    CategoryTreeNode,
    ProductListItemResponse,
    ProductDetailResponse,
    PaginatedProductResponse,
    StoreBriefResponse,
    ProductImageResponse,
    ProductSizeResponse
)


class CatalogService:
    async def get_categories_tree(self, db: AsyncSession) -> List[CategoryTreeNode]:
        """Lấy toàn bộ danh mục và xây dựng thành cây phân cấp (Category Tree)."""
        stmt = select(Category).order_by(Category.name.asc())
        result = await db.execute(stmt)
        categories = result.scalars().all()

        # Tạo map id -> node
        nodes: Dict[int, CategoryTreeNode] = {}
        for cat in categories:
            nodes[cat.category_id] = CategoryTreeNode(
                category_id=cat.category_id,
                name=cat.name,
                parent_id=cat.parent_id,
                created_at=cat.created_at,
                children=[]
            )

        # Xây dựng quan hệ cha - con
        tree: List[CategoryTreeNode] = []
        for cat in categories:
            node = nodes[cat.category_id]
            if cat.parent_id and cat.parent_id in nodes:
                nodes[cat.parent_id].children.append(node)
            else:
                tree.append(node)

        return tree

    async def get_products_list(
        self,
        db: AsyncSession,
        q: Optional[str] = None,
        category_id: Optional[int] = None,
        store_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        in_stock_only: bool = False,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedProductResponse:
        """
        Tìm kiếm và lọc sản phẩm linh hoạt:
        - q: Tìm kiếm từ khóa theo tên hoặc mô tả
        - category_id: Lọc theo danh mục
        - min_price, max_price: Lọc theo khoảng giá
        - color: Lọc theo màu sắc
        - size: Lọc theo size còn hàng (S, M, L, XL)
        - in_stock_only: Chỉ hiển thị sản phẩm còn tồn kho > 0
        - sort_by: 'newest', 'price_asc', 'price_desc', 'popular', 'try_on'
        """
        # Điều kiện lọc cơ bản
        filters = [Product.is_active.is_(True)]

        if q:
            keyword = f"%{q.strip()}%"
            filters.append(
                or_(
                    Product.name.ilike(keyword),
                    Product.description.ilike(keyword)
                )
            )

        if category_id is not None:
            # Lấy cả danh mục con nếu có
            sub_cat_stmt = select(Category.category_id).where(
                or_(Category.category_id == category_id, Category.parent_id == category_id)
            )
            sub_cats = (await db.execute(sub_cat_stmt)).scalars().all()
            filters.append(Product.category_id.in_(sub_cats))

        if store_id is not None:
            filters.append(Product.store_id == store_id)

        if min_price is not None:
            filters.append(Product.price >= min_price)

        if max_price is not None:
            filters.append(Product.price <= max_price)

        if color:
            filters.append(Product.color.ilike(f"%{color.strip()}%"))

        # Query cơ sở
        base_query = select(Product).where(and_(*filters))

        # Join bảng ProductSize nếu lọc theo size hoặc in_stock_only
        if size or in_stock_only:
            base_query = base_query.join(Product.sizes)
            if size:
                base_query = base_query.where(
                    and_(
                        ProductSize.size_label.ilike(size.strip()),
                        ProductSize.stock_quantity > 0
                    )
                )
            if in_stock_only:
                base_query = base_query.where(ProductSize.stock_quantity > 0)
            base_query = base_query.distinct()

        # 1. Tính tổng số lượng bản ghi thỏa mãn điều kiện lọc
        count_stmt = select(func.count(distinct(Product.product_id))).select_from(base_query.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # 2. Xử lý sắp xếp (Sorting)
        if sort_by == "price_asc":
            order_clause = Product.price.asc()
        elif sort_by == "price_desc":
            order_clause = Product.price.desc()
        elif sort_by == "popular":
            order_clause = Product.view_count.desc()
        elif sort_by == "try_on":
            order_clause = Product.try_on_count.desc()
        else: # "newest"
            order_clause = Product.created_at.desc()

        # 3. Phân trang và tải kèm quan hệ (Eager loading để tránh lỗi N+1)
        offset = (page - 1) * page_size
        query = (
            base_query
            .options(
                selectinload(Product.images),
                selectinload(Product.sizes),
                selectinload(Product.category)
            )
            .order_by(order_clause)
            .offset(offset)
            .limit(page_size)
        )

        result = await db.execute(query)
        products = result.scalars().unique().all()

        # Chuyển đổi sang schema response
        items: List[ProductListItemResponse] = []
        for p in products:
            # Tìm ảnh chính (primary image) hoặc ảnh đầu tiên
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url

            # Danh sách size còn hàng
            available_sizes = [s.size_label for s in p.sizes if s.stock_quantity > 0]
            in_stock = len(available_sizes) > 0

            items.append(
                ProductListItemResponse(
                    product_id=p.product_id,
                    name=p.name,
                    price=p.price,
                    discount_price=p.discount_price,
                    color=p.color,
                    is_active=p.is_active,
                    view_count=p.view_count,
                    try_on_count=p.try_on_count,
                    created_at=p.created_at,
                    category_id=p.category_id,
                    category_name=p.category.name if p.category else None,
                    primary_image_url=primary_img,
                    available_sizes=available_sizes,
                    in_stock=in_stock
                )
            )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return PaginatedProductResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def get_product_detail(self, db: AsyncSession, product_id: int) -> ProductDetailResponse:
        """
        Lấy chi tiết một sản phẩm:
        - Tự động tăng lượt xem (view_count)
        - Trả về danh sách ảnh, thông số đo ngực/eo/dài của từng size, và thông tin cửa hàng.
        """
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.sizes),
                selectinload(Product.category),
                selectinload(Product.store)
            )
            .where(
                and_(
                    Product.product_id == product_id,
                    Product.is_active.is_(True)
                )
            )
        )
        result = await db.execute(stmt)
        product = result.scalars().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sản phẩm với ID {product_id} không tồn tại hoặc đã ngừng kinh doanh."
            )

        # Tăng view_count
        product.view_count += 1
        await db.commit()

        # Chuẩn bị dữ liệu response
        images_resp = [
            ProductImageResponse(
                image_id=img.image_id,
                image_url=img.image_url,
                image_type=img.image_type,
                is_primary=img.is_primary,
                sort_order=img.sort_order
            )
            for img in sorted(product.images, key=lambda x: x.sort_order)
        ]

        sizes_resp = [
            ProductSizeResponse(
                size_id=s.size_id,
                size_label=s.size_label,
                stock_quantity=s.stock_quantity,
                chest_cm=float(s.chest_cm) if s.chest_cm is not None else None,
                waist_cm=float(s.waist_cm) if s.waist_cm is not None else None,
                length_cm=float(s.length_cm) if s.length_cm is not None else None
            )
            for s in product.sizes
        ]

        store_resp = StoreBriefResponse(
            store_id=product.store.store_id,
            name=product.store.name,
            address=product.store.address,
            phone=product.store.phone
        )

        return ProductDetailResponse(
            product_id=product.product_id,
            store=store_resp,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            name=product.name,
            description=product.description,
            price=product.price,
            discount_price=product.discount_price,
            color=product.color,
            is_active=product.is_active,
            view_count=product.view_count,
            try_on_count=product.try_on_count,
            created_at=product.created_at,
            images=images_resp,
            sizes=sizes_resp
        )


catalog_service = CatalogService()

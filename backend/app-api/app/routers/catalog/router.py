"""
Router phục vụ API Catalog, Chi tiết sản phẩm, Tìm kiếm và Bộ lọc.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.session import get_db
from app.services.catalog import catalog_service
from app.schemas.catalog import (
    CategoryTreeNode,
    PaginatedProductResponse,
    ProductDetailResponse
)

router = APIRouter(prefix="/catalog", tags=["Catalog & Products"])


@router.get(
    "/categories",
    response_model=List[CategoryTreeNode],
    status_code=status.HTTP_200_OK,
    summary="Get category tree",
    description="Lấy danh sách danh mục sản phẩm theo cấu trúc cây (Parent - Children)."
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await catalog_service.get_categories_tree(db=db)


@router.get(
    "/products",
    response_model=PaginatedProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Search & Filter products",
    description=(
        "Lấy danh sách sản phẩm hỗ trợ tìm kiếm theo từ khóa (tên, mô tả) "
        "và lọc nâng cao theo danh mục, khoảng giá, màu sắc, size, tình trạng tồn kho."
    )
)
async def search_and_filter_products(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (tên hoặc mô tả sản phẩm)"),
    category_id: Optional[int] = Query(None, description="Lọc theo ID danh mục (bao gồm cả danh mục con)"),
    store_id: Optional[int] = Query(None, description="Lọc theo ID cửa hàng"),
    min_price: Optional[float] = Query(None, ge=0, description="Giá tối thiểu (VNĐ)"),
    max_price: Optional[float] = Query(None, ge=0, description="Giá tối đa (VNĐ)"),
    color: Optional[str] = Query(None, description="Lọc theo màu sắc (ví dụ: 'Trắng', 'Đen', 'Be')"),
    size: Optional[str] = Query(None, description="Lọc theo size còn hàng (ví dụ: 'S', 'M', 'L', 'XL')"),
    in_stock_only: bool = Query(False, description="True: Chỉ hiển thị sản phẩm còn hàng trong kho"),
    sort_by: str = Query(
        "newest",
        regex="^(newest|price_asc|price_desc|popular|try_on)$",
        description="Tiêu chí sắp xếp: 'newest' (mới nhất), 'price_asc' (giá tăng dần), 'price_desc' (giá giảm dần), 'popular' (xem nhiều), 'try_on' (thử đồ nhiều)"
    ),
    page: int = Query(1, ge=1, description="Số trang hiện tại (bắt đầu từ 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng sản phẩm trên mỗi trang"),
    db: AsyncSession = Depends(get_db)
):
    return await catalog_service.get_products_list(
        db=db,
        q=q,
        category_id=category_id,
        store_id=store_id,
        min_price=min_price,
        max_price=max_price,
        color=color,
        size=size,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product detail",
    description="Lấy thông tin chi tiết của một sản phẩm (kèm bộ ảnh, bảng size, số đo áo may và thông tin cửa hàng)."
)
async def get_product_detail(
    product_id: int = Path(..., ge=1, description="ID của sản phẩm"),
    db: AsyncSession = Depends(get_db)
):
    return await catalog_service.get_product_detail(db=db, product_id=product_id)

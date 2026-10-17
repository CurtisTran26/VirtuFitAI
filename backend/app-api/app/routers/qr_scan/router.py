"""
Router phục vụ API quét và giải mã mã QR sản phẩm tại cửa hàng (QR Code Scan & Resolve).
Tuân thủ đặc tả OpenAPI: GET /api/v1/qr/scan
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.session import get_db
from app.services.qr_scan import qr_service
from app.schemas.qr.qr import QRScanProductResponse

router = APIRouter(prefix="/api/v1/qr", tags=["QR Code"])


@router.get(
    "/scan",
    response_model=QRScanProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Quét mã QR tại cửa hàng để mở ngay thông tin sản phẩm và phòng thử đồ",
    description=(
        "Giải mã nội dung chuỗi QR quét được tại quầy/cửa hàng. "
        "Hỗ trợ linh hoạt: Deep Link (virtufit://product/1), Web URL (https://virtufit.vn/products/1), "
        "Mã định danh (VF-PROD-0001) hoặc ID sản phẩm. "
        "Trả về đầy đủ thông tin sản phẩm, bảng size, thông số đo ngực/eo/dài để lập tức mở phòng thử đồ AI."
    )
)
async def scan_qr_code(
    code: str = Query(
        ...,
        example="virtufit://product/1",
        description="Nội dung mã QR quét được từ camera hoặc thiết bị quét tại cửa hàng"
    ),
    db: AsyncSession = Depends(get_db)
):
    return await qr_service.resolve_qr_code(db=db, code=code)

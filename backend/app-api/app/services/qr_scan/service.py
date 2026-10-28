"""
Dịch vụ xử lý mã QR sản phẩm (QR Code Service).
Chức năng:
- Bóc tách và Resolve mã sản phẩm từ chuỗi QR quét được (hỗ trợ Deep Link, Web URL, Code prefix, plain ID).
- Trả về thông tin sản phẩm và phòng thử đồ ảo AI.
- Sinh ảnh mã QR chuẩn chất lượng cao và lưu vào Object Storage (MinIO).
"""
import io
import re
from typing import Optional, Tuple
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import qrcode

from backend.shared.models import Product, ProductQRCode, ProductImage, ProductSize
from app.integrations.object_storage import storage_service
from app.schemas.catalog.product import ProductImageResponse, ProductSizeResponse
from app.schemas.qr.qr import QRScanProductResponse, QRGenerateResponse


class QRService:
    # Các mẫu regex nhận diện mã sản phẩm từ QR
    DEEP_LINK_PATTERN = re.compile(r"^virtufit://products?/(\d+)/?", re.IGNORECASE)
    WEB_URL_PATTERN = re.compile(r"https?://[^/]+/products?/(\d+)/?", re.IGNORECASE)
    CODE_PREFIX_PATTERN = re.compile(r"^(?:VF[-_]?PROD[-_]?|PROD[-_]?)(\d+)$", re.IGNORECASE)

    @classmethod
    def parse_product_id_from_code(cls, code: str) -> Optional[int]:
        """
        Bóc tách ID sản phẩm từ các định dạng QR được hỗ trợ:
        - Deep Link: 'virtufit://product/1' hoặc 'virtufit://products/1'
        - Web URL: 'https://virtufit.vn/products/1'
        - Prefix: 'VF-PROD-0001', 'PROD-1'
        - Plain ID: '1'
        """
        if not code:
            return None

        clean_code = code.strip()

        # 1. Kiểm tra Deep Link
        match = cls.DEEP_LINK_PATTERN.match(clean_code)
        if match:
            return int(match.group(1))

        # 2. Kiểm tra Web URL
        match = cls.WEB_URL_PATTERN.match(clean_code)
        if match:
            return int(match.group(1))

        # 3. Kiểm tra mã định danh có tiền tố (VF-PROD-1)
        match = cls.CODE_PREFIX_PATTERN.match(clean_code)
        if match:
            return int(match.group(1))

        # 4. Kiểm tra chuỗi số nguyên thuần túy
        if clean_code.isdigit():
            return int(clean_code)

        return None

    async def resolve_qr_code(self, db: AsyncSession, code: str) -> QRScanProductResponse:
        """
        Quét/Resolve mã QR tại cửa hàng:
        - Giải mã nội dung chuỗi QR để tìm product_id.
        - Truy vấn chi tiết sản phẩm, bảng kích thước và số đo may mặc cho phòng thử đồ.
        - Tăng lượt xem (view_count) sản phẩm khi được quét tại quầy.
        """
        product_id = self.parse_product_id_from_code(code)

        # Nếu không bóc tách được bằng regex, tra cứu trong bảng product_qr_codes
        if not product_id:
            qr_stmt = select(ProductQRCode.product_id).where(
                and_(
                    ProductQRCode.qr_data == code.strip(),
                    ProductQRCode.is_active.is_(True)
                )
            )
            product_id = (await db.execute(qr_stmt)).scalar_one_or_none()

        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã QR không đúng định dạng VirtuFit AI hoặc không thể giải mã: '{code}'"
            )

        # Truy vấn thông tin sản phẩm
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
                detail=f"Không tìm thấy sản phẩm (ID={product_id}) hoặc sản phẩm đã ngừng kinh doanh."
            )

        # Tăng view_count khi quét mã tại cửa hàng
        product.view_count += 1
        await db.commit()

        # Chuẩn bị dữ liệu hình ảnh
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
        primary_img = next((img.image_url for img in product.images if img.is_primary), None)
        if not primary_img and product.images:
            primary_img = product.images[0].image_url

        # Chuẩn bị dữ liệu bảng size & số đo
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
        available_sizes = [s.size_label for s in product.sizes if s.stock_quantity > 0]
        in_stock = len(available_sizes) > 0

        # Kiểm tra tính sẵn sàng cho phòng thử đồ ảo (AI Try-On Ready)
        has_measurements = any(s.chest_cm or s.waist_cm for s in product.sizes)
        try_on_ready = bool(product.images and has_measurements)

        deep_link = f"virtufit://product/{product.product_id}"
        web_url = f"https://virtufit.vn/products/{product.product_id}"

        return QRScanProductResponse(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            discount_price=product.discount_price,
            color=product.color,
            description=product.description,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            store_id=product.store_id,
            store_name=product.store.name if product.store else None,
            store_address=product.store.address if product.store else None,
            primary_image_url=primary_img,
            images=images_resp,
            sizes=sizes_resp,
            available_sizes=available_sizes,
            in_stock=in_stock,
            try_on_ready=try_on_ready,
            deep_link=deep_link,
            web_url=web_url,
            qr_data_scanned=code
        )

    def generate_qr_image_bytes(self, payload: str) -> bytes:
        """Sinh ảnh PNG mã QR chất lượng cao từ chuỗi payload."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    async def generate_and_save_product_qr(
        self,
        db: AsyncSession,
        product_id: int
    ) -> ProductQRCode:
        """
        Sinh mã QR cho sản phẩm, upload lên MinIO public bucket và lưu vào database.
        Hỗ trợ tái sử dụng cho script seed hoặc khi mở rộng cho Management API sau này.
        """
        # Kiểm tra sản phẩm có tồn tại không
        prod_stmt = select(Product).where(Product.product_id == product_id)
        product = (await db.execute(prod_stmt)).scalars().first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sản phẩm ID {product_id} không tồn tại."
            )

        # Định dạng payload chuẩn (Deep Link để mobile app mở ngay phòng thử đồ)
        qr_data = f"virtufit://product/{product_id}"

        # Sinh ảnh QR PNG
        image_bytes = self.generate_qr_image_bytes(qr_data)

        # Upload lên MinIO Storage (Public Bucket)
        upload_result = storage_service.upload_file(
            content=image_bytes,
            original_filename=f"qr_product_{product_id}.png",
            is_public=True,
            folder="qr-codes",
            content_type="image/png"
        )
        qr_image_url = upload_result["url"]

        # Lưu hoặc cập nhật vào bảng product_qr_codes
        qr_stmt = select(ProductQRCode).where(ProductQRCode.product_id == product_id)
        qr_record = (await db.execute(qr_stmt)).scalars().first()

        if qr_record:
            qr_record.qr_image_url = qr_image_url
            qr_record.qr_data = qr_data
            qr_record.is_active = True
        else:
            qr_record = ProductQRCode(
                product_id=product_id,
                qr_image_url=qr_image_url,
                qr_data=qr_data,
                is_active=True
            )
            session.add(qr_record) if 'session' in locals() else db.add(qr_record)

        await db.commit()
        await db.refresh(qr_record)
        return qr_record


qr_service = QRService()

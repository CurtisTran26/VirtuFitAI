"""
Router quản lý tải lên hình ảnh và sinh URL phân quyền (Public/Private Presigned URL).
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Query, status

from app.integrations.object_storage import storage_service, validate_image_upload

router = APIRouter(prefix="/media", tags=["Media & Cloud Storage"])


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload image",
    description="Tải ảnh lên Cloud Storage (MinIO/S3). Hỗ trợ phân quyền Public (ảnh sản phẩm) hoặc Private (ảnh thử đồ cá nhân)."
)
async def upload_image(
    file: UploadFile = File(..., description="File ảnh (JPG, PNG, WEBP; tối đa 5MB)"),
    is_public: bool = Form(
        False,
        description="True: Lưu vào bucket công khai (truy cập vĩnh viễn không cần auth). False: Lưu vào bucket riêng tư (bảo mật, sinh Presigned URL)."
    ),
    folder: str = Form(
        "general",
        description="Thư mục phân nhóm (ví dụ: 'products', 'try-on', 'designs', 'avatars')"
    )
):
    # 1. Xác thực tính hợp lệ và bảo mật của file ảnh
    content, content_type = await validate_image_upload(file)

    # 2. Upload lên Cloud Storage theo đúng phân quyền
    result = storage_service.upload_file(
        content=content,
        original_filename=file.filename or "image.jpg",
        is_public=is_public,
        folder=folder,
        content_type=content_type
    )

    return {
        "success": True,
        "message": "Tải ảnh lên Cloud Storage thành công.",
        "data": result
    }


@router.get(
    "/presigned-url",
    status_code=status.HTTP_200_OK,
    summary="Get Presigned URL for private image",
    description="Sinh URL tạm thời để xem hoặc tải ảnh riêng tư (ảnh người dùng, ảnh thử đồ AI). URL sẽ tự hết hạn."
)
async def get_presigned_url(
    object_key: str = Query(..., description="Mã định danh file (ví dụ: 'try-on/abc1234.jpg')"),
    expires_in: Optional[int] = Query(
        None,
        ge=60,
        le=86400,
        description="Thời gian hiệu lực tính bằng giây (tối thiểu 60s, tối đa 86400s / 24 giờ; mặc định 1800s / 30 phút)"
    )
):
    url = storage_service.generate_presigned_download_url(
        object_key=object_key,
        expiration_seconds=expires_in
    )

    return {
        "success": True,
        "object_key": object_key,
        "presigned_url": url,
        "expires_in_seconds": expires_in or 1800
    }

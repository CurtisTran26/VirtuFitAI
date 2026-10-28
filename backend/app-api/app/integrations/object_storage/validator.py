"""
Module kiểm tra tính hợp lệ và bảo mật của file ảnh tải lên.
"""
from typing import Tuple
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}

# Magic bytes (file signature) của các định dạng ảnh phổ biến
MAGIC_SIGNATURES = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": b"RIFF"  # Byte 8-12 là WEBP
}


def _verify_magic_bytes(header: bytes) -> bool:
    """Kiểm tra byte đầu của file để chống giả mạo định dạng."""
    if header.startswith(MAGIC_SIGNATURES["jpeg"]):
        return True
    if header.startswith(MAGIC_SIGNATURES["png"]):
        return True
    if header.startswith(MAGIC_SIGNATURES["webp"]) and b"WEBP" in header[:16]:
        return True
    return False


async def validate_image_upload(file: UploadFile) -> Tuple[bytes, str]:
    """
    Xác thực toàn diện file ảnh tải lên:
    1. Kiểm tra đuôi file (extension)
    2. Kiểm tra MIME type
    3. Kiểm tra dung lượng file (<= 5MB)
    4. Kiểm tra magic bytes thực tế để ngăn chặn mã độc cải trang thành ảnh.

    Trả về:
        Tuple[bytes, str]: (nội dung file dạng bytes, MIME type chuẩn)
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên file không hợp lệ hoặc bị trống."
        )

    # 1. Kiểm tra phần mở rộng file
    filename_lower = file.filename.lower()
    has_valid_ext = any(filename_lower.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)
    if not has_valid_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # 2. Kiểm tra Content-Type header
    content_type = file.content_type.lower() if file.content_type else ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type '{content_type}' không hợp lệ. Chỉ chấp nhận các loại ảnh hợp lệ."
        )

    # 3. Đọc dữ liệu và kiểm tra kích thước
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File rỗng (dung lượng 0 bytes)."
        )

    if file_size > settings.STORAGE_MAX_FILE_SIZE_BYTES:
        max_mb = settings.STORAGE_MAX_FILE_SIZE_BYTES / (1024 * 1024)
        current_mb = round(file_size / (1024 * 1024), 2)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Dung lượng file ({current_mb}MB) vượt quá giới hạn cho phép ({max_mb}MB)."
        )

    # 4. Kiểm tra magic bytes
    if not _verify_magic_bytes(content[:16]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung file không phải là định dạng hình ảnh hợp lệ (Phát hiện giả mạo phần mở rộng)."
        )

    return content, content_type

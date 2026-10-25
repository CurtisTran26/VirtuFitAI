"""
Dịch vụ tương tác với Cloud Object Storage (MinIO / AWS S3).
Hỗ trợ upload ảnh, phân quyền Public/Private, và sinh Presigned URL an toàn.
"""
import io
import os
import uuid
import re
from typing import Dict, Any, Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.core.config import settings


class S3StorageService:
    def __init__(self):
        # Khởi tạo S3 Client với cấu hình signature v4 chuẩn AWS/MinIO
        self._s3_client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            config=Config(signature_version="s3v4")
        )
        self.public_bucket = settings.STORAGE_PUBLIC_BUCKET
        self.private_bucket = settings.STORAGE_PRIVATE_BUCKET

    def _sanitize_folder(self, folder: str) -> str:
        """Chuẩn hóa đường dẫn thư mục lưu trữ, tránh Path Traversal."""
        clean = re.sub(r"[^a-zA-Z0-9_\-/]", "", folder).strip("/")
        return clean if clean else "general"

    def upload_file(
        self,
        content: bytes,
        original_filename: str,
        is_public: bool = False,
        folder: str = "general",
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Tải file lên Object Storage:
        - Nếu is_public=True: Lưu vào public bucket, trả về URL cố định truy cập trực tiếp.
        - Nếu is_public=False: Lưu vào private bucket, sinh Presigned URL có thời hạn.
        """
        bucket = self.public_bucket if is_public else self.private_bucket
        safe_folder = self._sanitize_folder(folder)

        # Trích xuất phần mở rộng của file
        _, ext = os.path.splitext(original_filename.lower())
        if not ext:
            ext = ".jpg"

        # Sinh định danh duy nhất (UUID) để tránh trùng tên hoặc đè file
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        object_key = f"{safe_folder}/{unique_filename}"

        try:
            self._s3_client.put_object(
                Bucket=bucket,
                Key=object_key,
                Body=content,
                ContentType=content_type
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi lưu trữ file lên Cloud Storage: {str(e)}"
            )

        # Xác định URL trả về cho client
        if is_public:
            file_url = f"{settings.STORAGE_PUBLIC_ENDPOINT}/{bucket}/{object_key}"
        else:
            file_url = self.generate_presigned_download_url(
                object_key=object_key,
                expiration_seconds=settings.STORAGE_PRESIGNED_EXPIRATION_SECONDS
            )

        return {
            "object_key": object_key,
            "bucket": bucket,
            "is_public": is_public,
            "file_size": len(content),
            "content_type": content_type,
            "url": file_url,
            "expires_in_seconds": None if is_public else settings.STORAGE_PRESIGNED_EXPIRATION_SECONDS
        }

    def generate_presigned_download_url(
        self,
        object_key: str,
        expiration_seconds: Optional[int] = None
    ) -> str:
        """
        Sinh Presigned URL cho phép client tải/xem ảnh riêng tư tạm thời.
        Hết thời gian hiệu lực, URL sẽ tự động vô hiệu hóa.
        """
        exp = expiration_seconds or settings.STORAGE_PRESIGNED_EXPIRATION_SECONDS
        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.private_bucket,
                    "Key": object_key
                },
                ExpiresIn=exp
            )
            # Trong môi trường Dev Docker, thay thế endpoint nội bộ bằng endpoint máy host
            if "minio:9000" in url:
                url = url.replace("http://minio:9000", settings.STORAGE_PUBLIC_ENDPOINT)
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể sinh Presigned URL: {str(e)}"
            )

    def delete_file(self, object_key: str, is_public: bool = False) -> bool:
        """Xóa file khỏi bucket."""
        bucket = self.public_bucket if is_public else self.private_bucket
        try:
            self._s3_client.delete_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể xóa file: {str(e)}"
            )

    def check_connection(self) -> bool:
        """Kiểm tra kết nối tới Storage phục vụ Readiness Probe."""
        try:
            self._s3_client.list_buckets()
            return True
        except Exception:
            return False


storage_service = S3StorageService()

"""
Pydantic schemas cho luồng đăng nhập nhanh bằng Google OAuth2.
"""
from pydantic import BaseModel, Field


class GoogleLoginRequest(BaseModel):
    """Yêu cầu xác thực tài khoản qua Google OAuth2 ID Token."""
    id_token: str = Field(
        ...,
        example="mock-google-token",
        description="ID Token (dạng chuỗi JWT) nhận được từ Google Sign-in SDK phía client"
    )

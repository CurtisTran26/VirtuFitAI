"""
Module xác minh Google OAuth2 ID Token ở Backend (Google Token Verifier).
Cơ chế kép:
1. Xác minh thật trực tiếp với Google OAuth2 API (tokeninfo endpoint).
2. Hỗ trợ Mock Token tiện lợi khi dev để kiểm thử không cần Google Cloud Console credentials.
"""
import logging
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("google_auth")

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleTokenVerifier:
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Xác minh tính hợp lệ của Google ID Token và trích xuất thông tin người dùng:
        - sub: Google User ID duy nhất
        - email: Địa chỉ email của tài khoản Google
        - name: Họ và tên
        - picture: Ảnh đại diện Google
        """
        if not id_token or not id_token.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google ID Token không được để trống."
            )

        token_str = id_token.strip()

        # ----------------------------------------------------------------------
        # 1. Hỗ trợ Mock/Dev Token khi đang phát triển hoặc chưa có Google Client ID
        # ----------------------------------------------------------------------
        if token_str.startswith(("mock-google", "dev-google", "test-google")):
            if settings.APP_DEBUG or settings.APP_ENV == "development" or not settings.GOOGLE_CLIENT_ID:
                # Cú pháp mở rộng: mock-google:email@gmail.com:Họ Tên
                parts = token_str.split(":")
                email = parts[1] if len(parts) > 1 else "tester.google@virtufit.ai"
                name = parts[2] if len(parts) > 2 else "Nguyễn Văn Google"
                mock_sub = f"mock_google_{abs(hash(email)) % 10000000000000000}"

                logger.info(f"Đang sử dụng Mock Google Token cho email: {email}")
                return {
                    "google_id": mock_sub,
                    "email": email.lower(),
                    "full_name": name,
                    "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200",
                    "email_verified": True
                }

        # ----------------------------------------------------------------------
        # 2. Xác minh thật với Google OAuth2 API
        # ----------------------------------------------------------------------
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    GOOGLE_TOKENINFO_URL,
                    params={"id_token": token_str},
                    timeout=10.0
                )
            except Exception as net_err:
                logger.error(f"Lỗi kết nối tới máy chủ Google OAuth: {str(net_err)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Không thể kết nối tới máy chủ xác thực của Google. Vui lòng thử lại sau."
                )

        if response.status_code != 200:
            logger.warning(f"Google TokenInfo từ chối token: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google ID Token không hợp lệ hoặc đã hết hạn."
            )

        payload = response.json()

        # 3. Kiểm tra Audience (aud) nếu đã cấu hình GOOGLE_CLIENT_ID
        if settings.GOOGLE_CLIENT_ID:
            token_aud = payload.get("aud")
            if token_aud != settings.GOOGLE_CLIENT_ID:
                logger.warning(f"Token aud ({token_aud}) không khớp GOOGLE_CLIENT_ID cấu hình ({settings.GOOGLE_CLIENT_ID})")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google ID Token không được cấp phát cho ứng dụng này (Client ID mismatch)."
                )

        # 4. Kiểm tra trạng thái xác minh email của tài khoản Google
        email_verified = payload.get("email_verified")
        if email_verified not in (True, "true", "True", 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản Google này chưa được xác minh địa chỉ email."
            )

        google_id = payload.get("sub")
        email = payload.get("email")
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token không chứa định danh người dùng Google hoặc email hợp lệ."
            )

        return {
            "google_id": str(google_id),
            "email": email.strip().lower(),
            "full_name": payload.get("name") or f"User {email.split('@')[0]}",
            "avatar_url": payload.get("picture"),
            "email_verified": True
        }


google_verifier = GoogleTokenVerifier()

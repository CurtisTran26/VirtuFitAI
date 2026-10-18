"""
Dịch vụ xử lý đăng nhập, xác thực và đổi mật khẩu qua Phone OTP (Auth Service).
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.shared.models import User
from backend.shared.enums import UserRole
from backend.shared.authentication import create_access_token, get_password_hash
from app.integrations.phone_otp import phone_otp_service
from app.integrations.google_login import google_verifier
from app.schemas.auth.otp import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    OTPLoginRequest,
    AuthTokenResponse,
    ResetPasswordWithOTPRequest
)
from app.schemas.auth.google import GoogleLoginRequest



class AuthOTPService:
    async def send_otp(self, payload: SendOTPRequest) -> SendOTPResponse:
        """Gửi mã OTP đến số điện thoại người dùng."""
        result = await phone_otp_service.send_otp(
            phone=payload.phone,
            purpose=payload.purpose
        )
        return SendOTPResponse(**result)

    async def verify_otp(self, payload: VerifyOTPRequest) -> VerifyOTPResponse:
        """Kiểm tra mã OTP và trả về Verification Token."""
        token = await phone_otp_service.verify_otp(
            phone=payload.phone,
            otp=payload.otp,
            purpose=payload.purpose,
            clear_on_success=True
        )
        normalized_phone = phone_otp_service.normalize_phone(payload.phone)
        return VerifyOTPResponse(
            success=True,
            message="Xác thực mã OTP thành công.",
            phone=normalized_phone,
            verification_token=token
        )

    async def login_with_otp(
        self,
        db: AsyncSession,
        payload: OTPLoginRequest
    ) -> AuthTokenResponse:
        """
        Đăng nhập nhanh bằng OTP (Passwordless Login):
        1. Xác thực mã OTP với Redis.
        2. Nếu số điện thoại đã tồn tại -> Đăng nhập và cập nhật trạng thái verified.
        3. Nếu số điện thoại chưa tồn tại -> Tự động đăng ký tài khoản Customer mới.
        4. Tạo JWT Access Token & Refresh Token trả về cho Client.
        """
        normalized_phone = phone_otp_service.normalize_phone(payload.phone)

        # 1. Xác thực mã OTP (cho phép mục đích 'login' hoặc 'auth')
        try:
            await phone_otp_service.verify_otp(
                phone=normalized_phone,
                otp=payload.otp,
                purpose="login",
                clear_on_success=True
            )
        except HTTPException:
            # Cho phép fallback sang purpose 'auth' nếu client gửi chung
            await phone_otp_service.verify_otp(
                phone=normalized_phone,
                otp=payload.otp,
                purpose="auth",
                clear_on_success=True
            )

        # 2. Tìm kiếm tài khoản trong cơ sở dữ liệu
        stmt = select(User).where(User.phone == normalized_phone)
        user = (await db.execute(stmt)).scalars().first()

        is_new_user = False
        now = datetime.now(timezone.utc)

        if user:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ hỗ trợ."
                )
            user.is_verified = True
            user.last_login_at = now
        else:
            # 3. Tự động tạo tài khoản Customer mới cho khách hàng
            is_new_user = True
            user = User(
                phone=normalized_phone,
                full_name=f"Khách hàng {normalized_phone[-4:]}",
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=True,
                last_login_at=now
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        # 4. Sinh JWT Token
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        token_payload = {
            "sub": str(user.user_id),
            "user_id": user.user_id,
            "role": role_str,
            "phone": user.phone
        }
        access_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(days=7) # 7 ngày cho app di động
        )
        refresh_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(days=30)
        )

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=7 * 24 * 3600,
            role=role_str,
            user_id=user.user_id,
            full_name=user.full_name,
            phone=user.phone,
            is_new_user=is_new_user
        )

    async def reset_password_with_otp(
        self,
        db: AsyncSession,
        payload: ResetPasswordWithOTPRequest
    ) -> Dict[str, Any]:
        """Đặt lại mật khẩu mới cho tài khoản bằng cách xác thực mã OTP."""
        normalized_phone = phone_otp_service.normalize_phone(payload.phone)

        # 1. Xác thực mã OTP mục đích 'reset_password' hoặc 'auth'
        try:
            await phone_otp_service.verify_otp(
                phone=normalized_phone,
                otp=payload.otp,
                purpose="reset_password",
                clear_on_success=True
            )
        except HTTPException:
            await phone_otp_service.verify_otp(
                phone=normalized_phone,
                otp=payload.otp,
                purpose="auth",
                clear_on_success=True
            )

        # 2. Tìm tài khoản
        stmt = select(User).where(User.phone == normalized_phone)
        user = (await db.execute(stmt)).scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy tài khoản liên kết với số điện thoại {normalized_phone}."
            )

        # 3. Mã hóa và cập nhật mật khẩu mới
        user.password_hash = get_password_hash(payload.new_password)
        await db.commit()

        return {
            "success": True,
            "message": "Đặt lại mật khẩu thành công. Quý khách có thể đăng nhập bằng mật khẩu mới."
        }

    async def login_with_google(
        self,
        db: AsyncSession,
        payload: GoogleLoginRequest
    ) -> AuthTokenResponse:
        """
        Đăng nhập hoặc đăng ký nhanh qua Google OAuth2 ID Token:
        1. Xác minh tính hợp lệ của token trực tiếp với Google API (hoặc Mock Token khi dev).
        2. Nếu google_id đã liên kết -> Đăng nhập ngay.
        3. Nếu email đã được đăng ký bằng phương thức mật khẩu truyền thống -> Báo lỗi 409 Conflict (Chính sách Tách biệt).
        4. Nếu là người dùng hoàn toàn mới -> Tự động đăng ký tài khoản Customer và trả về JWT Token.
        """
        # 1. Xác minh Google ID Token
        google_info = await google_verifier.verify_id_token(payload.id_token)
        google_id = google_info["google_id"]
        email = google_info["email"]
        full_name = google_info["full_name"]
        avatar_url = google_info.get("avatar_url")

        now = datetime.now(timezone.utc)
        is_new_user = False

        # 2. Tìm kiếm user theo google_id
        stmt = select(User).where(User.google_id == google_id)
        user = (await db.execute(stmt)).scalars().first()

        if user:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tài khoản của bạn đã bị khóa hoặc ngừng hoạt động."
                )
            user.last_login_at = now
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
        else:
            # 3. Kiểm tra xem email này đã tồn tại trong hệ thống chưa (Chính sách Tách biệt)
            email_stmt = select(User).where(User.email == email)
            existing_email_user = (await db.execute(email_stmt)).scalars().first()

            if existing_email_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{email}' đã được đăng ký bằng phương thức mật khẩu. Vui lòng đăng nhập bằng mật khẩu để bảo vệ an toàn tài khoản."
                )

            # 4. Tạo tài khoản khách hàng mới qua Google
            is_new_user = True
            user = User(
                google_id=google_id,
                email=email,
                phone=None,
                full_name=full_name,
                avatar_url=avatar_url,
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=True, # Email Google đã được Google xác thực
                password_hash=None, # Không dùng mật khẩu
                last_login_at=now
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        # 5. Sinh JWT Access Token & Refresh Token
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        token_payload = {
            "sub": str(user.user_id),
            "user_id": user.user_id,
            "role": role_str,
            "email": user.email,
            "google_id": user.google_id
        }
        access_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(days=7)
        )
        refresh_token = create_access_token(
            data=token_payload,
            expires_delta=timedelta(days=30)
        )

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=7 * 24 * 3600,
            role=role_str,
            user_id=user.user_id,
            full_name=user.full_name,
            phone=user.phone or "",
            is_new_user=is_new_user
        )


auth_otp_service = AuthOTPService()


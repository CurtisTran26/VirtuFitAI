"""
Router xử lý xác thực tài khoản qua số điện thoại và mã OTP (Phone OTP Authentication).
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.session import get_db
from app.services.auth import auth_otp_service
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


router = APIRouter(prefix="/api/v1/auth", tags=["Auth & Phone OTP"])


@router.post(
    "/otp/send",
    response_model=SendOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Gửi mã xác thực OTP qua số điện thoại",
    description=(
        "Sinh mã OTP ngẫu nhiên 6 chữ số và gửi qua tin nhắn SMS (mặc định xuất mã ra Terminal console khi dev). "
        "Mã có hiệu lực trong 5 phút. Cooldown 60 giây giữa 2 lần gửi để chống spam."
    )
)
async def send_phone_otp(payload: SendOTPRequest):
    return await auth_otp_service.send_otp(payload=payload)


@router.post(
    "/otp/verify",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Xác thực mã OTP",
    description=(
        "Kiểm tra mã OTP người dùng nhập vào. "
        "Hỗ trợ cơ chế chống brute-force (nhập sai quá 3 lần mã sẽ bị hủy). "
        "Trả về Verification Token có hạn 10 phút để thực hiện đăng ký hoặc đổi mật khẩu."
    )
)
async def verify_phone_otp(payload: VerifyOTPRequest):
    return await auth_otp_service.verify_otp(payload=payload)


@router.post(
    "/otp/login",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập nhanh bằng OTP (Passwordless Login)",
    description=(
        "Khách hàng đăng nhập nhanh không cần mật khẩu chỉ với Số điện thoại và mã OTP. "
        "Nếu số điện thoại chưa từng đăng ký, hệ thống tự động tạo tài khoản Customer mới. "
        "Trả về JWT Access Token & Refresh Token."
    )
)
async def login_with_phone_otp(
    payload: OTPLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_otp_service.login_with_otp(db=db, payload=payload)


@router.post(
    "/password/reset-with-otp",
    status_code=status.HTTP_200_OK,
    summary="Đặt lại mật khẩu tài khoản bằng mã OTP",
    description=(
        "Người dùng quên mật khẩu có thể xác thực số điện thoại qua OTP để tạo mật khẩu mới an toàn."
    )
)
async def reset_password_with_otp(
    payload: ResetPasswordWithOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_otp_service.reset_password_with_otp(db=db, payload=payload)


@router.post(
    "/google",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập / Đăng ký nhanh qua Google OAuth2",
    description=(
        "Xác minh Google ID Token trực tiếp từ máy chủ Google OAuth2 (hỗ trợ Mock Token khi dev). "
        "Nếu là khách hàng mới, hệ thống tự động tạo tài khoản Customer và cấp JWT Token. "
        "Chính sách bảo mật tách biệt: Báo lỗi 409 Conflict nếu email đã đăng ký bằng mật khẩu."
    )
)
async def login_with_google(
    payload: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_otp_service.login_with_google(db=db, payload=payload)


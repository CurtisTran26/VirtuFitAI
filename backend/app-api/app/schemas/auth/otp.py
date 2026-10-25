"""
Pydantic schemas cho luồng xác thực qua số điện thoại và mã OTP (Phone OTP Schemas).
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SendOTPRequest(BaseModel):
    """Yêu cầu gửi mã OTP tới số điện thoại."""
    phone: str = Field(
        ...,
        example="0901234567",
        description="Số điện thoại di động Việt Nam (10 chữ số)"
    )
    purpose: str = Field(
        "auth",
        example="login",
        description="Mục đích gửi OTP: 'login', 'register', 'reset_password', hoặc 'auth'"
    )


class SendOTPResponse(BaseModel):
    """Kết quả gửi mã OTP."""
    success: bool = True
    message: str
    phone: str
    cooldown_seconds: int = 60
    expires_in_seconds: int = 300
    debug_otp: Optional[str] = Field(
        None,
        description="Mã OTP hiển thị khi bật chế độ Debug/Dev để kiểm thử thuận tiện"
    )


class VerifyOTPRequest(BaseModel):
    """Yêu cầu kiểm tra mã OTP."""
    phone: str = Field(..., example="0901234567", description="Số điện thoại nhận mã")
    otp: str = Field(..., min_length=6, max_length=6, example="123456", description="Mã OTP 6 chữ số")
    purpose: str = Field("auth", description="Mục đích xác thực khớp với lúc gửi")


class VerifyOTPResponse(BaseModel):
    """Kết quả xác thực mã OTP."""
    success: bool = True
    message: str = "Xác thực mã OTP thành công."
    phone: str
    verification_token: str = Field(
        ...,
        description="Token tạm thời có thời hạn 10 phút để thực hiện bước tiếp theo"
    )


class OTPLoginRequest(BaseModel):
    """Đăng nhập nhanh bằng số điện thoại và mã OTP (Passwordless Login)."""
    phone: str = Field(..., example="0901234567", description="Số điện thoại đăng nhập")
    otp: str = Field(..., min_length=6, max_length=6, example="123456", description="Mã OTP nhận được")


class AuthTokenResponse(BaseModel):
    """Kết quả đăng nhập thành công trả về JWT Token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    role: str
    user_id: int
    full_name: str
    phone: str
    is_new_user: bool = Field(
        False,
        description="True nếu tài khoản vừa được tự động khởi tạo khi đăng nhập lần đầu"
    )

    model_config = ConfigDict(from_attributes=True)


class ResetPasswordWithOTPRequest(BaseModel):
    """Đặt lại mật khẩu mới bằng xác thực số điện thoại và mã OTP."""
    phone: str = Field(..., example="0901234567", description="Số điện thoại tài khoản")
    otp: str = Field(..., min_length=6, max_length=6, example="123456", description="Mã OTP nhận được")
    new_password: str = Field(..., min_length=6, example="NewPass@123", description="Mật khẩu mới (tối thiểu 6 ký tự)")

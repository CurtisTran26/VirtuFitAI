"""Authentication schemas used by app API routes."""
from .auth import ChangePassword, Login, OtpPassword, OtpRequest, Register
from .google import GoogleLoginRequest
from .otp import (
    AuthTokenResponse,
    OTPLoginRequest,
    ResetPasswordWithOTPRequest,
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)

__all__ = [
    "AuthTokenResponse",
    "ChangePassword",
    "GoogleLoginRequest",
    "Login",
    "OTPLoginRequest",
    "OtpPassword",
    "OtpRequest",
    "Register",
    "ResetPasswordWithOTPRequest",
    "SendOTPRequest",
    "SendOTPResponse",
    "VerifyOTPRequest",
    "VerifyOTPResponse",
]

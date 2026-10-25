"""Auth schemas package."""
from .otp import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    OTPLoginRequest,
    AuthTokenResponse,
    ResetPasswordWithOTPRequest
)
from .google import GoogleLoginRequest

__all__ = [
    "SendOTPRequest",
    "SendOTPResponse",
    "VerifyOTPRequest",
    "VerifyOTPResponse",
    "OTPLoginRequest",
    "AuthTokenResponse",
    "ResetPasswordWithOTPRequest",
    "GoogleLoginRequest"
]

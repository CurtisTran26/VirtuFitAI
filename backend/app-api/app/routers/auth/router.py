"""Phone OTP and Google authentication routes for the app API."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth.google import GoogleLoginRequest
from app.schemas.auth.otp import (
    AuthTokenResponse,
    OTPLoginRequest,
    ResetPasswordWithOTPRequest,
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.services.auth import auth_otp_service
from backend.shared.database.session import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth & Phone OTP"])


@router.post("/otp/send", response_model=SendOTPResponse, status_code=status.HTTP_200_OK)
async def send_phone_otp(payload: SendOTPRequest):
    return await auth_otp_service.send_otp(payload=payload)


@router.post("/otp/verify", response_model=VerifyOTPResponse, status_code=status.HTTP_200_OK)
async def verify_phone_otp(payload: VerifyOTPRequest):
    return await auth_otp_service.verify_otp(payload=payload)


@router.post("/otp/login", response_model=AuthTokenResponse, status_code=status.HTTP_200_OK)
async def login_with_phone_otp(payload: OTPLoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_otp_service.login_with_otp(db=db, payload=payload)


@router.post("/password/reset-with-otp", status_code=status.HTTP_200_OK)
async def reset_password_with_otp(payload: ResetPasswordWithOTPRequest, db: AsyncSession = Depends(get_db)):
    return await auth_otp_service.reset_password_with_otp(db=db, payload=payload)


@router.post("/google", response_model=AuthTokenResponse, status_code=status.HTTP_200_OK)
async def login_with_google(payload: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_otp_service.login_with_google(db=db, payload=payload)

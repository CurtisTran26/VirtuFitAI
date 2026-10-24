from __future__ import annotations
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class OtpRequest(BaseModel):
    phone: str = Field(max_length=24)
    purpose: Literal['register','reset_password','change_password']


class Register(BaseModel):
    phone: str = Field(max_length=24)
    full_name: str = Field(min_length=1,max_length=120)
    password: str = Field(min_length=8,max_length=72)
    otp_code: str = Field(pattern=r'^\d{6}$')


class Login(BaseModel):
    phone: str = Field(max_length=24)
    password: str = Field(max_length=72)


class VerifyOtp(BaseModel):
    phone: str = Field(max_length=24)
    otp_code: str = Field(pattern=r'^\d{6}$')


class ResetPassword(BaseModel):
    reset_token: str | None = Field(default=None,max_length=200)
    phone: str | None = Field(default=None,max_length=24)
    otp_code: str | None = Field(default=None,pattern=r'^\d{6}$')
    new_password: str = Field(min_length=8,max_length=72)


class ChangePassword(BaseModel):
    current_password: str | None = Field(default=None,max_length=72)
    otp_code: str | None = Field(default=None,pattern=r'^\d{6}$')
    new_password: str = Field(min_length=8,max_length=72)


class GoogleLogin(BaseModel):
    id_token: str = Field(min_length=1,max_length=10000)



from pydantic import BaseModel, Field


class Login(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    password: str = Field(min_length=1, max_length=72)


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)


class PasswordResetOtp(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")


class PasswordReset(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    otp_code: str = Field(pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=8, max_length=72)

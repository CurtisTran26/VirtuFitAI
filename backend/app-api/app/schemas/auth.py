from pydantic import BaseModel, Field


class OtpRequest(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    purpose: str = Field(pattern="^(register|reset_password)$")


class Register(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    otp_code: str = Field(pattern=r"^[0-9]{6}$")


class Login(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    password: str = Field(min_length=1, max_length=72)


class OtpPassword(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    otp_code: str = Field(pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=8, max_length=72)


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

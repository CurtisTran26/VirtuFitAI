from pydantic import BaseModel, Field
from uuid import UUID


class Login(BaseModel):
    phone: str
    password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class PasswordResetOtp(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")


class PasswordReset(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    otp_code: str = Field(pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=8, max_length=72)


class UserCreate(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=72)
    role: str = Field(pattern="^(sales_staff|warehouse_staff|designer|admin)$")


class RoleUpdate(BaseModel):
    role: str = Field(pattern="^(sales_staff|warehouse_staff|designer|admin)$")


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    is_active: bool = True


class ProductIn(BaseModel):
    category_id: UUID
    name: str = Field(min_length=1, max_length=180)
    description: str = ""
    price_vnd: int = Field(ge=0)
    sku: str = Field(min_length=1, max_length=80)
    image_url: str | None = None
    is_active: bool = True


class SizeChartIn(BaseModel):
    category_id: UUID
    name: str = Field(min_length=1, max_length=120)
    measurements: list[dict]


class VariantIn(BaseModel):
    product_id: UUID
    size: str = Field(min_length=1, max_length=30)
    color: str = ""
    sku: str = Field(min_length=1, max_length=80)


class AdjustIn(BaseModel):
    delta: int = Field(ne=0)
    reason: str = Field(min_length=3, max_length=500)

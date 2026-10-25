from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=72)
    role: str = Field(pattern="^(sales_staff|warehouse_staff|designer|admin)$")


class RoleUpdate(BaseModel):
    role: str = Field(pattern="^(sales_staff|warehouse_staff|designer|admin)$")

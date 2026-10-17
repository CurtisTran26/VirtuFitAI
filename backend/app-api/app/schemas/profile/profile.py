"""
Pydantic schemas cho API Hồ sơ cá nhân (Profile) và số đo người dùng.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserProfileResponse(BaseModel):
    """Schema thông tin hồ sơ người dùng đầy đủ."""
    user_id: int
    phone: Optional[str] = None
    email: Optional[str] = None
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    height_cm: Optional[int] = Field(None, description="Chiều cao (cm)")
    weight_kg: Optional[int] = Field(None, description="Cân nặng (kg)")
    gender: Optional[str] = None
    is_verified: bool
    created_at: datetime

    # Tính toán mở rộng hỗ trợ phòng thử đồ AI và đề xuất kích cỡ
    bmi: Optional[float] = Field(None, description="Chỉ số khối cơ thể BMI tính tự động từ chiều cao & cân nặng")
    recommended_size: Optional[str] = Field(None, description="Gợi ý size quần áo sơ bộ (S, M, L, XL)")

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateRequest(BaseModel):
    """Schema cập nhật thông tin cá nhân và số đo cơ thể."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Họ và tên đầy đủ")
    height_cm: Optional[int] = Field(None, ge=100, le=250, description="Chiều cao cơ thể (cm, từ 100 đến 250)")
    weight_kg: Optional[int] = Field(None, ge=30, le=200, description="Cân nặng cơ thể (kg, từ 30 đến 200)")
    gender: Optional[str] = Field(None, description="Giới tính: 'male', 'female', hoặc 'other'")
    avatar_url: Optional[str] = Field(None, description="URL ảnh đại diện")


class ChangePasswordRequest(BaseModel):
    """Schema đổi mật khẩu tài khoản."""
    current_password: str = Field(..., min_length=6, description="Mật khẩu hiện tại")
    new_password: str = Field(..., min_length=6, description="Mật khẩu mới (tối thiểu 6 ký tự)")


class AvatarUploadResponse(BaseModel):
    """Schema phản hồi khi upload ảnh đại diện thành công."""
    success: bool = True
    avatar_url: str
    message: str = "Tải lên ảnh đại diện thành công."

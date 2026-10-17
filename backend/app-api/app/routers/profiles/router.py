"""
Router quản lý thông tin hồ sơ và số đo cơ thể người dùng (Profile API).
Tuân thủ đặc tả OpenAPI:
- GET /api/v1/users/me: Xem thông tin cá nhân và số đo gợi ý size
- PUT /api/v1/users/me: Cập nhật thông tin & số đo chiều cao/cân nặng
- PUT /api/v1/users/me/password: Đổi mật khẩu
- POST /api/v1/users/me/avatar: Tải lên và cập nhật ảnh đại diện trực tiếp
"""
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.session import get_db
from backend.shared.models import User
from app.core.security import get_current_user
from app.services.profile import profile_service
from app.schemas.profile.profile import (
    UserProfileResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest,
    AvatarUploadResponse
)

router = APIRouter(prefix="/api/v1/users", tags=["Profile"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân và số đo của khách hàng hiện tại",
    description=(
        "Trả về đầy đủ thông tin tài khoản, vai trò, số đo chiều cao (cm), cân nặng (kg), "
        "kèm chỉ số khối cơ thể (BMI) và kích cỡ quần áo gợi ý tự động (S, M, L, XL, XXL) "
        "dành cho phòng thử đồ ảo AI."
    )
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return profile_service.get_profile(user=current_user)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật hồ sơ, số đo chiều cao, cân nặng để AI gợi ý size",
    description="Cập nhật họ tên, giới tính, chiều cao (cm), cân nặng (kg) và URL ảnh đại diện."
)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await profile_service.update_profile(
        db=db,
        user=current_user,
        payload=payload
    )


@router.put(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Đổi mật khẩu tài khoản",
    description="Xác thực mật khẩu hiện tại và cập nhật mật khẩu mới (mã hóa bcrypt an toàn)."
)
async def change_my_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await profile_service.change_password(
        db=db,
        user=current_user,
        payload=payload
    )


@router.post(
    "/me/avatar",
    response_model=AvatarUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Tải lên và cập nhật ảnh đại diện trực tiếp",
    description="Tải file ảnh đại diện (JPG, PNG, WEBP; <=5MB) lên MinIO Storage và tự động lưu URL vào hồ sơ người dùng."
)
async def upload_my_avatar(
    file: UploadFile = File(..., description="File ảnh đại diện hợp lệ (JPG, PNG, WEBP; tối đa 5MB)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    avatar_url = await profile_service.upload_avatar(
        db=db,
        user=current_user,
        file=file
    )
    return AvatarUploadResponse(
        success=True,
        avatar_url=avatar_url,
        message="Tải lên ảnh đại diện thành công."
    )

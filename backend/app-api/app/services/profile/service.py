"""
Dịch vụ xử lý hồ sơ người dùng (Profile Service).
Hỗ trợ:
- Xem và tính toán BMI, gợi ý size may mặc sơ bộ từ số đo.
- Cập nhật thông tin cá nhân và số đo chiều cao, cân nặng.
- Đổi mật khẩu tài khoản an toàn với bcrypt.
- Tải ảnh đại diện trực tiếp lên Cloud Storage (MinIO).
"""
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile, status

from backend.shared.models import User
from backend.shared.enums import Gender
from backend.shared.authentication import verify_password, get_password_hash
from app.integrations.object_storage import storage_service, validate_image_upload
from app.schemas.profile.profile import (
    UserProfileResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest
)


class ProfileService:
    @staticmethod
    def calculate_bmi_and_size(
        height_cm: Optional[int],
        weight_kg: Optional[int],
        gender: Optional[str] = None
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Tính toán chỉ số BMI và đề xuất size quần áo chuẩn theo form Việt Nam:
        - Dưới 53kg hoặc < 1m62: Size S
        - 54kg - 64kg và 1m62 - 1m70: Size M
        - 65kg - 74kg và 1m68 - 1m76: Size L
        - 75kg - 84kg và 1m74 - 1m82: Size XL
        - Trên 85kg: Size XXL
        """
        if not height_cm or not weight_kg or height_cm <= 0 or weight_kg <= 0:
            return None, None

        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m ** 2), 1)

        # Ước lượng size dựa trên ma trận chiều cao / cân nặng form Việt Nam
        if weight_kg < 54 or height_cm < 162:
            recommended_size = "S"
        elif weight_kg <= 64:
            recommended_size = "M"
        elif weight_kg <= 74:
            recommended_size = "L"
        elif weight_kg <= 84:
            recommended_size = "XL"
        else:
            recommended_size = "XXL"

        return bmi, recommended_size

    def get_profile(self, user: User) -> UserProfileResponse:
        """Định dạng dữ liệu hồ sơ kèm chỉ số BMI và size gợi ý."""
        gender_val = user.gender.value if hasattr(user.gender, "value") else user.gender
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)

        bmi, size = self.calculate_bmi_and_size(
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            gender=gender_val
        )

        return UserProfileResponse(
            user_id=user.user_id,
            phone=user.phone,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            role=role_val,
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            gender=gender_val,
            is_verified=user.is_verified,
            created_at=user.created_at,
            bmi=bmi,
            recommended_size=size
        )

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        payload: ProfileUpdateRequest
    ) -> UserProfileResponse:
        """Cập nhật thông tin cá nhân và số đo chiều cao, cân nặng."""
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()

        if payload.height_cm is not None:
            user.height_cm = payload.height_cm

        if payload.weight_kg is not None:
            user.weight_kg = payload.weight_kg

        if payload.gender is not None:
            try:
                user.gender = Gender(payload.gender.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Giới tính không hợp lệ: '{payload.gender}'. Chỉ chấp nhận: male, female, other."
                )

        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url.strip()

        await db.commit()
        await db.refresh(user)

        return self.get_profile(user)

    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        payload: ChangePasswordRequest
    ) -> Dict[str, Any]:
        """Đổi mật khẩu người dùng."""
        # Nếu người dùng có mật khẩu cũ thì phải đối chiếu chính xác
        if user.password_hash:
            if not verify_password(payload.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mật khẩu hiện tại không chính xác."
                )

        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới không được trùng với mật khẩu cũ."
            )

        # Băm mật khẩu mới và lưu vào cơ sở dữ liệu
        user.password_hash = get_password_hash(payload.new_password)
        await db.commit()

        return {
            "success": True,
            "message": "Đổi mật khẩu tài khoản thành công."
        }

    async def upload_avatar(
        self,
        db: AsyncSession,
        user: User,
        file: UploadFile
    ) -> str:
        """Tải ảnh đại diện lên MinIO Public Bucket và tự động cập nhật avatar_url."""
        # 1. Xác thực file ảnh (định dạng, kích thước, magic bytes)
        content, content_type = await validate_image_upload(file)

        # 2. Upload lên MinIO Storage trong thư mục 'avatars'
        upload_result = storage_service.upload_file(
            content=content,
            original_filename=file.filename or "avatar.jpg",
            is_public=True,
            folder="avatars",
            content_type=content_type
        )
        avatar_url = upload_result["url"]

        # 3. Cập nhật vào thông tin người dùng
        user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)

        return avatar_url


profile_service = ProfileService()

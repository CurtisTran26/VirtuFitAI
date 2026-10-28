"""
Dịch vụ quản lý mã xác thực OTP điện thoại (Phone OTP Service).
Tích hợp:
- Lưu trữ và tự động hết hạn với Redis (TTL 5 phút).
- Cơ chế Cooldown chống spam SMS (60 giây).
- Cơ chế chống tấn công Brute-force (tối đa 3 lần nhập sai).
- Sinh mã xác nhận tạm thời (verification_token) cho các bước tiếp theo.
"""
import json
import re
import secrets
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from backend.shared.database.redis import get_redis
from app.integrations.phone_otp.provider import get_sms_provider, BaseSMSProvider

# Regex kiểm tra số điện thoại di động hợp lệ tại Việt Nam (10 chữ số, bắt đầu bằng 03, 05, 07, 08, 09)
VN_PHONE_REGEX = re.compile(r"^0(3[2-9]|5[2689]|7[06-9]|8[1-9]|9[0-9])[0-9]{7}$")


class PhoneOTPService:
    def __init__(self, sms_provider: Optional[BaseSMSProvider] = None):
        self.sms_provider = sms_provider or get_sms_provider()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Chuẩn hóa và kiểm tra số điện thoại Việt Nam:
        - Xóa khoảng trắng, dấu gạch nối, dấu chấm.
        - Chuyển đầu số '+84' hoặc '84' về '0'.
        - Kiểm tra tính hợp lệ của đầu số di động Việt Nam.
        """
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số điện thoại không được để trống."
            )

        clean_phone = re.sub(r"[\s\-\.\(\)]", "", phone.strip())

        if clean_phone.startswith("+84"):
            clean_phone = "0" + clean_phone[3:]
        elif clean_phone.startswith("84") and len(clean_phone) == 11:
            clean_phone = "0" + clean_phone[2:]

        if not VN_PHONE_REGEX.match(clean_phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số điện thoại '{phone}' không hợp lệ tại Việt Nam. Vui lòng nhập đúng 10 chữ số (VD: 0901234567)."
            )

        return clean_phone

    async def send_otp(self, phone: str, purpose: str = "auth") -> Dict[str, Any]:
        """
        Tạo và gửi mã OTP 6 số ngẫu nhiên:
        - Kiểm tra Cooldown 60s (chống spam liên tục).
        - Lưu mã vào Redis với TTL 300s (5 phút).
        - Gửi tin nhắn qua SMS Gateway.
        """
        normalized_phone = self.normalize_phone(phone)
        redis_client = get_redis()

        cooldown_key = f"otp:cooldown:{normalized_phone}"
        code_key = f"otp:code:{normalized_phone}"

        # 1. Kiểm tra Cooldown
        ttl_remaining = await redis_client.ttl(cooldown_key)
        if ttl_remaining > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Thao tác quá nhanh. Vui lòng chờ {ttl_remaining} giây trước khi yêu cầu mã OTP mới."
            )

        # 2. Sinh mã OTP ngẫu nhiên 6 chữ số bảo mật bằng module secrets
        otp_code = f"{secrets.SystemRandom().randint(100000, 999999)}"

        # 3. Lưu vào Redis kèm số lần thử (attempts) và mục đích (purpose)
        otp_data = {
            "otp": otp_code,
            "attempts": 0,
            "purpose": purpose
        }
        await redis_client.set(
            code_key,
            json.dumps(otp_data),
            ex=settings.OTP_TTL_SECONDS
        )

        # 4. Đặt thời gian cooldown chống spam
        await redis_client.set(
            cooldown_key,
            "1",
            ex=settings.OTP_COOLDOWN_SECONDS
        )

        # 5. Gửi tin nhắn qua SMS Provider
        sms_content = f"Ma xac thuc VirtuFit AI cua ban la: {otp_code}. Hieu luc trong {settings.OTP_TTL_SECONDS // 60} phut. Tuyet doi khong chia se ma nay cho bat ky ai."
        await self.sms_provider.send_sms(normalized_phone, sms_content)

        return {
            "success": True,
            "message": f"Mã xác thực OTP đã được gửi đến số điện thoại {normalized_phone}.",
            "phone": normalized_phone,
            "cooldown_seconds": settings.OTP_COOLDOWN_SECONDS,
            "expires_in_seconds": settings.OTP_TTL_SECONDS,
            # Trả về mã trong response khi đang dev để lập trình viên và kiểm thử test thuận tiện
            "debug_otp": otp_code if (settings.APP_DEBUG or settings.APP_ENV == "development") else None
        }

    async def verify_otp(
        self,
        phone: str,
        otp: str,
        purpose: str = "auth",
        clear_on_success: bool = True
    ) -> str:
        """
        Xác thực mã OTP do người dùng nhập:
        - Kiểm tra tồn tại trong Redis.
        - Đếm số lần nhập sai (tối đa 3 lần).
        - Nếu hợp lệ: sinh verification_token có thời hạn 10 phút để thực hiện bước tiếp theo.
        """
        normalized_phone = self.normalize_phone(phone)
        redis_client = get_redis()
        code_key = f"otp:code:{normalized_phone}"

        # 1. Lấy dữ liệu OTP từ Redis
        raw_data = await redis_client.get(code_key)
        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã OTP đã hết hạn hoặc chưa từng được gửi. Vui lòng yêu cầu mã mới."
            )

        otp_info = json.loads(raw_data)

        # 2. Kiểm tra mục đích xác thực
        if otp_info.get("purpose") != purpose:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mục đích xác thực mã OTP không chính xác."
            )

        # 3. Đối chiếu mã OTP
        if otp_info.get("otp") != otp.strip():
            attempts = otp_info.get("attempts", 0) + 1
            if attempts >= settings.OTP_MAX_ATTEMPTS:
                # Nhập sai quá số lần quy định -> Hủy mã ngay lập tức
                await redis_client.delete(code_key)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bạn đã nhập sai mã OTP quá {settings.OTP_MAX_ATTEMPTS} lần. Mã đã bị hủy để bảo đảm an toàn. Vui lòng gửi lại mã mới."
                )
            
            # Cập nhật số lần thử còn lại vào Redis
            otp_info["attempts"] = attempts
            ttl = await redis_client.ttl(code_key)
            if ttl > 0:
                await redis_client.set(code_key, json.dumps(otp_info), ex=ttl)

            remaining = settings.OTP_MAX_ATTEMPTS - attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã OTP không chính xác. Bạn còn {remaining} lần thử."
            )

        # 4. Xác thực thành công -> Xóa mã OTP nếu cần
        if clear_on_success:
            await redis_client.delete(code_key)

        # 5. Sinh Verification Token dùng cho các bước tiếp theo (đăng ký, đổi mật khẩu)
        verification_token = secrets.token_hex(24)
        verified_key = f"otp:verified:{verification_token}"
        verified_data = {
            "phone": normalized_phone,
            "purpose": purpose
        }
        # Token này có hiệu lực trong 10 phút (600 giây)
        await redis_client.set(verified_key, json.dumps(verified_data), ex=600)

        return verification_token

    async def consume_verification_token(
        self,
        token: str,
        expected_phone: str,
        purpose: str = "auth"
    ) -> bool:
        """
        Xác nhận và tiêu thụ Verification Token (dùng một lần):
        Đảm bảo số điện thoại đã được xác thực mã OTP hợp lệ trước đó.
        """
        if not token:
            return False

        normalized_phone = self.normalize_phone(expected_phone)
        redis_client = get_redis()
        verified_key = f"otp:verified:{token}"

        raw_data = await redis_client.get(verified_key)
        if not raw_data:
            return False

        data = json.loads(raw_data)
        if data.get("phone") != normalized_phone or data.get("purpose") != purpose:
            return False

        # Tiêu thụ token (xóa để chỉ dùng được 1 lần duy nhất)
        await redis_client.delete(verified_key)
        return True


phone_otp_service = PhoneOTPService()

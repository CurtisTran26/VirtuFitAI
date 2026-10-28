"""
Hệ thống cung cấp dịch vụ gửi tin nhắn SMS (SMS Provider Strategy Pattern).
Hỗ trợ:
- MockSMSProvider: Mặc định cho phát triển & đồ án (in mã ra Terminal rõ ràng, không tốn chi phí).
- TwilioSMSProvider: Tích hợp cổng quốc tế Twilio qua REST API.
- SpeedSMSProvider: Tích hợp cổng SMS Brandname Việt Nam.
"""
import abc
import logging
from typing import Optional
import httpx

from app.core.config import settings

logger = logging.getLogger("phone_otp")


class BaseSMSProvider(abc.ABC):
    @abc.abstractmethod
    async def send_sms(self, phone: str, message: str) -> bool:
        """Gửi tin nhắn SMS đến số điện thoại chỉ định."""
        pass


class MockSMSProvider(BaseSMSProvider):
    """
    Provider giả lập cho môi trường Development & Kiểm thử đồ án:
    In mã OTP nổi bật ra Terminal console để người chấm và lập trình viên dễ dàng lấy mã.
    """
    async def send_sms(self, phone: str, message: str) -> bool:
        print("\n" + "=" * 65)
        print("📱 [VIRTU FIT AI - SMS GATEWAY SIMULATOR]")
        print(f"📞 Số điện thoại nhận: {phone}")
        print(f"💬 Nội dung tin nhắn:  {message}")
        print("=" * 65 + "\n")
        return True


class TwilioSMSProvider(BaseSMSProvider):
    """Gửi SMS qua cổng Twilio API."""
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_PHONE_NUMBER
        self.url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

    async def send_sms(self, phone: str, message: str) -> bool:
        if not self.account_sid or not self.auth_token or not self.from_phone:
            logger.warning("Twilio chưa được cấu hình đầy đủ credentials, chuyển hướng sang Mock Provider.")
            return await MockSMSProvider().send_sms(phone, message)

        # Chuyển đầu số 090... sang chuẩn quốc tế +8490... cho Twilio
        to_phone = phone
        if to_phone.startswith("0"):
            to_phone = "+84" + to_phone[1:]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.url,
                    data={
                        "From": self.from_phone,
                        "To": to_phone,
                        "Body": message
                    },
                    auth=(self.account_sid, self.auth_token),
                    timeout=10.0
                )
                return response.status_code in (200, 201)
            except Exception as e:
                logger.error(f"Lỗi gửi SMS qua Twilio: {str(e)}")
                return False


def get_sms_provider() -> BaseSMSProvider:
    """Factory trả về SMS Provider tương ứng theo biến môi trường SMS_PROVIDER."""
    provider_name = (settings.SMS_PROVIDER or "mock").lower()
    if provider_name == "twilio":
        return TwilioSMSProvider()
    return MockSMSProvider()

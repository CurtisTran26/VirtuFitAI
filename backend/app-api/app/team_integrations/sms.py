"""Adapted from An 8079668: integrations/phone_otp/provider.py.
Sync provider for sync FastAPI endpoints; never silently fall back to mock.
"""
import os
import re
import httpx
from fastapi import HTTPException


def error(code, message):
    raise HTTPException(503, detail={'code': code, 'message': message})


class MockSMSProvider:
    def send_sms(self, phone, message):
        # The OTP API explicitly returns debug_code in development only.
        return True


class TwilioSMSProvider:
    def send_sms(self, phone, message):
        sid = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
        secret = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
        sender = os.getenv('TWILIO_FROM_NUMBER', '').strip()
        alias = os.getenv('TWILIO_PHONE_NUMBER', '').strip()
        if sender and alias and sender != alias:
            error('SMS_CONFIG_CONFLICT', 'Hai biến số gửi Twilio không trùng nhau.')
        sender = sender or alias
        if not re.fullmatch(r'AC[a-fA-F0-9]{32}', sid) or not secret or not sender:
            error('SMS_NOT_CONFIGURED', 'Chưa cấu hình đầy đủ dịch vụ SMS Twilio.')
        recipient = '+84' + phone[1:] if phone.startswith('0') else phone
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json',
                    data={'From': sender, 'To': recipient, 'Body': message}, auth=(sid, secret))
        except httpx.HTTPError:
            error('SMS_SEND_FAILED', 'Không kết nối được dịch vụ SMS.')
        if response.status_code not in (200, 201):
            error('SMS_SEND_FAILED', 'Dịch vụ SMS từ chối gửi mã. Kiểm tra tài khoản dịch vụ.')
        return True


def get_sms_provider(debug):
    name = os.getenv('SMS_PROVIDER', '').strip().lower() or ('mock' if debug else 'twilio')
    if name == 'mock' and debug:
        return MockSMSProvider()
    if name == 'twilio' and not debug:
        return TwilioSMSProvider()
    if name == 'twilio_verify' and not debug:
        return TwilioVerifyProvider()
    if name not in ('mock', 'twilio', 'twilio_verify'):
        error('SMS_PROVIDER_UNSUPPORTED', 'Dịch vụ OTP chưa được cấu hình hợp lệ.')
    error('SMS_CONFIG_CONFLICT', 'Mock cần OTP_DEBUG=true ở development; Twilio cần OTP_DEBUG=false.')


class TwilioVerifyProvider:
    """Twilio owns the code. Store only its Verification SID, never a local OTP."""
    def __init__(self):
        sid = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
        token = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
        service = os.getenv('TWILIO_VERIFY_SERVICE_SID', '').strip()
        if not re.fullmatch(r'AC[0-9a-fA-F]{32}', sid) or not token or not re.fullmatch(r'VA[0-9a-fA-F]{32}', service):
            error('SMS_NOT_CONFIGURED', 'Dịch vụ gửi mã chưa được cấu hình đầy đủ.')
        self.auth = (sid, token)
        self.base = f'https://verify.twilio.com/v2/Services/{service}'

    def _post(self, path, data, missing_ok=False):
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.base + path, data=data, auth=self.auth)
        except httpx.HTTPError:
            error('SMS_UNAVAILABLE', 'Không kết nối được dịch vụ OTP. Vui lòng thử lại sau.')
        if missing_ok and response.status_code == 404:
            return {}
        if response.status_code == 429:
            raise HTTPException(429, detail={'code': 'OTP_RATE_LIMIT', 'message': 'Đã thử quá nhiều lần. Vui lòng đợi rồi thử lại.'})
        if response.status_code not in (200, 201):
            # Do not reflect provider payloads, credentials or recipient details.
            error('SMS_PROVIDER_REJECTED', 'Dịch vụ OTP chưa xử lý được yêu cầu. Vui lòng thử lại sau hoặc liên hệ hỗ trợ.')
        try:
            result = response.json()
            if not isinstance(result, dict): raise ValueError()
            return result
        except ValueError:
            error('SMS_UNAVAILABLE', 'Dịch vụ OTP trả về kết quả không hợp lệ.')

    def start(self, phone):
        recipient = '+84' + phone[1:] if phone.startswith('0') else phone
        result = self._post('/Verifications', {'To': recipient, 'Channel': 'sms'})
        sid = result.get('sid', '')
        if result.get('status') != 'pending' or not isinstance(sid, str) or not re.fullmatch(r'VE[0-9a-fA-F]{32}', sid):
            error('SMS_SEND_FAILED', 'Chưa thể gửi mã xác minh. Vui lòng thử lại sau.')
        return sid

    def check(self, sid, code, phone):
        if not re.fullmatch(r'VE[0-9a-fA-F]{32}', sid): return False
        result = self._post('/VerificationCheck', {'To': '+84' + phone[1:] if phone.startswith('0') else phone, 'VerificationSid': sid, 'Code': code}, missing_ok=True)
        return result.get('status') == 'approved' and result.get('sid') == sid

    def cancel(self, sid):
        if not re.fullmatch(r'VE[0-9a-fA-F]{32}', sid):
            error('SMS_UNAVAILABLE', 'Phiên OTP không hợp lệ. Vui lòng liên hệ hỗ trợ.')
        result = self._post('/Verifications/' + sid, {'Status': 'canceled'}, missing_ok=True)
        if result and result.get('status') != 'canceled':
            error('SMS_UNAVAILABLE', 'Chưa thể chuyển phiên OTP. Vui lòng thử lại sau.')

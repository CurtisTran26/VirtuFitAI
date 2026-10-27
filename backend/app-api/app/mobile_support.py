"""Integration helpers; retain Giap's shared sessions and UUID database."""
import base64
import hashlib
import io
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from datetime import date
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token


def fail(status, code, message):
    raise HTTPException(status, detail={"code": code, "message": message})


def phone_key(value):
    value = value.strip().replace(' ', '').replace('-', '')
    if value.startswith('+84'): value = '0' + value[3:]
    if not re.fullmatch(r'0[35789][0-9]{8}', value):
        fail(422, 'PHONE_INVALID', 'Nhập số điện thoại Việt Nam hợp lệ.')
    return value


def password_ok(value):
    if not 8 <= len(value.encode('utf-8')) <= 72 or not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
        fail(422, 'PASSWORD_INVALID', 'Mật khẩu cần 8–72 byte, có chữ và số.')
    return value


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def otp_debug():
    return os.getenv('OTP_DEBUG', 'false').lower() == 'true' and os.getenv('APP_ENV', 'development').strip().lower() in ('development', 'test', 'testing')


def deliver_sms(phone, code):
    from app.team_integrations.sms import get_sms_provider
    return get_sms_provider(otp_debug()).send_sms(phone, f'VirtuFitAI: ma xac nhan {code}. Het han sau 5 phut.')


def verify_google(value):
    audience = os.getenv('GOOGLE_WEB_CLIENT_ID', '').strip()
    alias = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    if audience and alias and audience != alias:
        fail(503, 'GOOGLE_CONFIG_CONFLICT', 'Hai biến Google Client ID không trùng nhau.')
    audience = audience or alias
    if value.startswith(('mock-google', 'dev-google', 'test-google')):
        fail(401, 'GOOGLE_INVALID', 'Không chấp nhận token Google giả lập.')
    if not audience.endswith('.apps.googleusercontent.com'):
        fail(503, 'GOOGLE_NOT_CONFIGURED', 'Backend chưa cấu hình Google Web Client ID.')
    try:
        info = id_token.verify_oauth2_token(value, GoogleRequest(), audience)
    except ValueError:
        fail(401, 'GOOGLE_INVALID', 'Google ID token không hợp lệ hoặc hết hạn.')
    except Exception:
        fail(503, 'GOOGLE_UNAVAILABLE', 'Chưa kết nối được dịch vụ xác minh Google.')
    if not info.get('sub') or info.get('email_verified') is not True or not info.get('email'):
        fail(401, 'GOOGLE_INVALID', 'Google chưa xác minh email của tài khoản.')
    return info


def validate_avatar(value):
    if not value: return None
    if not value.startswith('data:image/') or ',' not in value:
        fail(422, 'AVATAR_INVALID', 'Ảnh phải là dữ liệu JPEG hoặc PNG được tải lên từ app.')
    try:
        raw = base64.b64decode(value.split(',',1)[1], validate=True)
        if len(raw) > 2 * 1024 * 1024: raise ValueError()
        with Image.open(io.BytesIO(raw)) as img:
            if img.format not in ('JPEG','PNG') or img.width*img.height > 16000000: raise ValueError()
            img.verify()
        with Image.open(io.BytesIO(raw)) as img:
            img = img.convert('RGB'); img.thumbnail((512,512))
            output=io.BytesIO(); img.save(output,format='JPEG',quality=85)
        return 'data:image/jpeg;base64,'+base64.b64encode(output.getvalue()).decode()
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError):
        fail(422, 'AVATAR_INVALID', 'Ảnh JPEG/PNG tối đa 2 MB và 16 megapixel.')

import os
from pathlib import Path
from dotenv import dotenv_values
for _key, _value in dotenv_values(Path(__file__).resolve().parents[1] / '.env.integration', encoding='utf-8-sig').items():
    if _key in {'GOOGLE_WEB_CLIENT_ID','TWILIO_ACCOUNT_SID','TWILIO_AUTH_TOKEN','TWILIO_FROM_NUMBER','TWILIO_VERIFY_SERVICE_SID','OTP_DEBUG','APP_ENV','SMS_PROVIDER','TWILIO_PHONE_NUMBER','GOOGLE_CLIENT_ID','AVATAR_STORAGE','STORAGE_ENDPOINT','STORAGE_PUBLIC_ENDPOINT','STORAGE_ACCESS_KEY','STORAGE_SECRET_KEY','STORAGE_REGION','STORAGE_PRIVATE_BUCKET'} and _value is not None:
        os.environ[_key] = _value

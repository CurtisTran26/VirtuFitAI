"""
Cấu hình tập trung ứng dụng sử dụng Pydantic Settings.
Tự động nạp biến môi trường từ hệ thống hoặc file .env.
"""
from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App General
    APP_ENV: str = "development"
    APP_NAME: str = "VirtuFit AI Backend"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"

    # Database
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "virtufit_db"
    DB_USER: str = "virtufit_user"
    DB_PASSWORD: str = "virtufit_secure_password_dev"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DATABASE_URL: str = "postgresql+asyncpg://virtufit_user:virtufit_secure_password_dev@postgres:5432/virtufit_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_DEFAULT_TTL_SECONDS: int = 3600

    # JWT Authentication
    JWT_SECRET_KEY: str = "default_insecure_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True

    # Cloud Object Storage (MinIO / S3)
    STORAGE_ENDPOINT: str = "http://minio:9000"
    STORAGE_PUBLIC_ENDPOINT: str = "http://localhost:9000"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_PUBLIC_BUCKET: str = "virtufit-public"
    STORAGE_PRIVATE_BUCKET: str = "virtufit-private"
    STORAGE_PRESIGNED_EXPIRATION_SECONDS: int = 1800
    STORAGE_MAX_FILE_SIZE_BYTES: int = 5242880 # 5MB

    # Phone OTP & SMS Gateway
    SMS_PROVIDER: str = "mock" # mock | twilio | speedsms
    OTP_TTL_SECONDS: int = 300 # 5 phút
    OTP_COOLDOWN_SECONDS: int = 60 # 60 giây chờ gửi lại
    OTP_MAX_ATTEMPTS: int = 3 # Tối đa 3 lần nhập sai
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    SPEEDSMS_ACCESS_TOKEN: str = ""

    # Google OAuth2 Authentication
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""




    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

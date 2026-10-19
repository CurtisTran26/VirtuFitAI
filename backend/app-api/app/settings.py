from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/capstone"
    jwt_secret: str = "change-this-secret-before-deploying"
    jwt_expire_minutes: int = Field(default=60, gt=0)
    seed_admin_phone: str | None = None
    seed_admin_password: str | None = None
    seed_admin_name: str = "Bootstrap Admin"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

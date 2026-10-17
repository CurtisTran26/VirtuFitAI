"""
Cấu hình kết nối cơ sở dữ liệu PostgreSQL bất đồng bộ (Async SQLAlchemy + asyncpg).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

import os

try:
    from app.core.config import settings
    DB_URL = settings.DATABASE_URL
    DB_POOL = settings.DB_POOL_SIZE
    DB_OVERFLOW = settings.DB_MAX_OVERFLOW
except Exception:
    DB_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://virtufit_user:virtufit_secure_password_dev@localhost:5432/virtufit_db"
    )
    DB_POOL = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# Khởi tạo Async Engine cho PostgreSQL
engine = create_async_engine(
    DB_URL,
    pool_size=DB_POOL,
    max_overflow=DB_OVERFLOW,
    pool_pre_ping=True,
    echo=False
)

# Session factory cho các transaction bất đồng bộ
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Declarative Base cho toàn bộ models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency cung cấp database session cho từng request và tự động đóng sau khi xong."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_tables() -> None:
    """Tự động tạo tất cả các bảng nếu chưa tồn tại (Dùng cho môi trường Dev)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

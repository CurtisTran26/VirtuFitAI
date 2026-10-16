"""
Cấu hình kết nối cơ sở dữ liệu PostgreSQL bất đồng bộ (Async SQLAlchemy + asyncpg).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Khởi tạo Async Engine cho PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
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

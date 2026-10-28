"""
Quản lý kết nối Redis tập trung bất đồng bộ (Async Redis Connection Pool).
Phục vụ lưu trữ OTP, Session, Cache và Rate Limiting.
"""
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

# Global async Redis pool
_redis_pool: Optional[aioredis.ConnectionPool] = None


def get_redis_pool() -> aioredis.ConnectionPool:
    """Khởi tạo hoặc tái sử dụng Connection Pool tới Redis."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=True
        )
    return _redis_pool


def get_redis() -> aioredis.Redis:
    """Trả về client Redis bất đồng bộ sử dụng connection pool."""
    pool = get_redis_pool()
    return aioredis.Redis(connection_pool=pool)


async def close_redis() -> None:
    """Đóng toàn bộ connection pool khi ứng dụng tắt."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.disconnect()
        _redis_pool = None

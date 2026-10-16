"""
Router kiểm tra trạng thái sức khỏe của hệ thống (Health Check endpoints).
Tuân thủ tiêu chuẩn Cloud-Native (Liveness & Readiness Probes).
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as aioredis

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health Checks"])

START_TIME = time.time()


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Kiểm tra ứng dụng có đang sống hay bị deadlock/treo tiến trình."
)
async def liveness_probe() -> Dict[str, Any]:
    """
    Liveness Probe: Chỉ kiểm tra nội tại tiến trình FastAPI.
    Nếu trả về HTTP 200, container được coi là đang hoạt động.
    """
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "status": "alive",
        "service": settings.APP_NAME,
        "uptime_seconds": uptime_seconds
    }


@router.get(
    "/ready",
    summary="Readiness Probe",
    description="Kiểm tra ứng dụng đã sẵn sàng tiếp nhận request (kiểm tra PostgreSQL & Redis)."
)
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """
    Readiness Probe: Kiểm tra tất cả các dependencies bên ngoài (PostgreSQL, Redis).
    Nếu 1 trong các dịch vụ ngắt kết nối, trả về HTTP 503 Service Unavailable.
    """
    checks: Dict[str, Any] = {
        "database": False,
        "redis": False,
        "storage": False
    }

    # 1. Kiểm tra kết nối PostgreSQL
    try:
        engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        checks["database"] = True
    except Exception as db_err:
        checks["database"] = False
        checks["database_error"] = str(db_err)

    # 2. Kiểm tra kết nối Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pong = await r.ping()
        await r.aclose()
        checks["redis"] = bool(pong)
    except Exception as redis_err:
        checks["redis"] = False
        checks["redis_error"] = str(redis_err)

    # 3. Kiểm tra kết nối MinIO / S3 Storage
    try:
        from app.integrations.object_storage import storage_service
        checks["storage"] = storage_service.check_connection()
    except Exception as storage_err:
        checks["storage"] = False
        checks["storage_error"] = str(storage_err)

    # Đánh giá trạng thái tổng thể
    is_healthy = checks["database"] and checks["redis"] and checks["storage"]
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "checks": checks
        }


    return {
        "status": "ready",
        "checks": checks
    }


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="General System Info",
    description="Endpoint thông tin tổng hợp cho Dashboard và Developer."
)
async def general_health() -> Dict[str, Any]:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "operational",
        "timestamp": time.time()
    }

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.orm import Session

from order_service import expire_stale_holds
from shared_platform import SessionLocal

logger = logging.getLogger(__name__)

_expiration_task: asyncio.Task | None = None


def run_expiration_batch(db: Session, limit: int = 100) -> dict[str, int]:
    """Quét và hủy các đơn hàng quá hạn 15 phút giữ chỗ tạm thời (pending_confirmation)."""
    expired_count = expire_stale_holds(db, limit=limit)
    if expired_count > 0:
        db.commit()
        logger.info(f"Expiration worker: Auto-cancelled {expired_count} expired order(s) and released reservations.")
    return {"expired_count": expired_count}


async def expiration_loop(interval_seconds: int = 300):
    """Tiến trình chạy nền định kỳ mỗi 5 phút (300s)."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            db = SessionLocal()
            try:
                run_expiration_batch(db)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in order expiration background loop: {e}")


def start_expiration_worker():
    """Khởi động worker hủy đơn quá hạn trong FastAPI."""
    global _expiration_task
    if _expiration_task is None or _expiration_task.done():
        try:
            loop = asyncio.get_running_loop()
            _expiration_task = loop.create_task(expiration_loop())
            logger.info("Order expiration background worker started successfully.")
        except RuntimeError:
            pass


def stop_expiration_worker():
    """Dừng worker khi tắt ứng dụng."""
    global _expiration_task
    if _expiration_task and not _expiration_task.done():
        _expiration_task.cancel()
        _expiration_task = None


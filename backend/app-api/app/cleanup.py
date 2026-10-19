"""Remove expired session and consumed reset-token records."""
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import ConsumedPasswordResetToken, UserSession


def cleanup_expired_records() -> int:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        sessions_deleted = db.query(UserSession).filter(UserSession.expires_at < now).delete(synchronize_session=False)
        reset_tokens_deleted = db.query(ConsumedPasswordResetToken).filter(ConsumedPasswordResetToken.expires_at < now).delete(synchronize_session=False)
        db.commit()
    return sessions_deleted + reset_tokens_deleted


if __name__ == "__main__":
    print(f"Removed {cleanup_expired_records()} expired session/token records.")

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConsumedPasswordResetToken, User, UserSession
from app.schemas import PhoneNumber
from app.security import get_current_user, hash_password, verify_password
from app.settings import settings

router = APIRouter(prefix="/api/auth", tags=["Password management"])


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordReset(BaseModel):
    phone: PhoneNumber
    new_password: str = Field(min_length=8, max_length=128)
    reset_token: str = Field(description="Short-lived token issued after SMS OTP verification")


@router.post("/change-password")
def change_password(payload: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.now(timezone.utc)})
    db.commit()
    return {"message": "Password changed. Sign in again."}


@router.post("/reset-password")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    try:
        claims = jwt.decode(payload.reset_token, settings.jwt_secret, algorithms=["HS256"])
        if "exp" not in claims or not claims.get("jti") or claims.get("purpose") != "password_reset" or claims.get("phone") != payload.phone:
            raise jwt.InvalidTokenError("invalid reset token claims")
        reset_jti = str(UUID(claims["jti"]))
    except jwt.PyJWTError:
        raise HTTPException(400, "Reset token is invalid or expired")
    except (TypeError, ValueError, OverflowError):
        raise HTTPException(400, "Reset token is invalid or expired")
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        raise HTTPException(404, "Account not found")
    if db.get(ConsumedPasswordResetToken, reset_jti):
        raise HTTPException(400, "Reset token has already been used")
    user.password_hash = hash_password(payload.new_password)
    try:
        expires_at = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        raise HTTPException(400, "Reset token is invalid or expired")
    if expires_at > datetime.now(timezone.utc) + timedelta(minutes=15):
        raise HTTPException(400, "Reset token lifetime must not exceed 15 minutes")
    db.add(ConsumedPasswordResetToken(jti=reset_jti, expires_at=expires_at))
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.now(timezone.utc)})
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(400, "Reset token has already been used") from exc
    return {"message": "Password reset. Sign in again."}

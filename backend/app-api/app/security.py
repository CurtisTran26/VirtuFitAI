from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession
from app.settings import settings

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
ROLES = ("customer", "staff", "inventory", "manager", "admin")


def hash_password(value: str) -> str:
    return password_hash.hash(value)


def verify_password(value: str, hashed: str) -> bool:
    return password_hash.verify(value, hashed)


def create_session(user: User, db: Session) -> tuple[str, datetime]:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    jti = str(uuid4())
    token = jwt.encode({"sub": str(user.id), "jti": jti, "exp": expires}, settings.jwt_secret, algorithm="HS256")
    db.add(UserSession(jti=jti, user_id=user.id, expires_at=expires))
    db.commit()
    return token, expires


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id, jti = int(claims["sub"]), claims["jti"]
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized

    session = db.get(UserSession, jti)
    user = db.get(User, user_id)
    expires_at = session.expires_at if session else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if not session or session.user_id != user_id or session.revoked_at or expires_at <= now or not user or not user.is_active:
        raise unauthorized
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency

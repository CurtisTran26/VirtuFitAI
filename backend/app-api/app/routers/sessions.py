from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession
from app.security import bearer, get_current_user
from app.settings import settings

router = APIRouter(prefix="/api/auth", tags=["Sessions"])


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    session = db.get(UserSession, claims["jti"])
    if session and session.user_id == user.id:
        session.revoked_at = session.revoked_at or datetime.now(timezone.utc)
        db.commit()
    return {"message": "Logged out"}

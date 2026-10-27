from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/virtufit")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)
ROLES = ("customer", "sales_staff", "warehouse_staff", "designer", "admin")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def now(): return datetime.now(timezone.utc)
def hash_password(value: str) -> str: return passwords.hash(value)
def verify_password(value: str, hashed: str) -> bool: return passwords.verify(value, hashed)
def token_digest(token: str) -> str: return hashlib.sha256(token.encode()).hexdigest()

def issue_session(db: Session, user_id: UUID):
    token = secrets.token_urlsafe(40)
    expires = now() + timedelta(hours=int(os.getenv("SESSION_TTL_HOURS", "24")))
    db.execute(text("INSERT INTO user_sessions(id,user_id,token_hash,expires_at) VALUES(gen_random_uuid(),:uid,:hash,:exp)"), {"uid":user_id,"hash":token_digest(token),"exp":expires})
    return {"access_token":token,"token_type":"bearer","expires_at":expires}

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(401, detail={"code":"UNAUTHENTICATED","message":"Authentication required"})
    row=db.execute(text("SELECT u.id,u.phone,u.full_name,u.is_active,r.name AS role FROM user_sessions s JOIN users u ON u.id=s.user_id JOIN roles r ON r.id=u.role_id WHERE s.token_hash=:hash AND s.revoked_at IS NULL AND s.expires_at>now() AND u.is_active"), {"hash":token_digest(credentials.credentials)}).mappings().first()
    if row is None: raise HTTPException(401, detail={"code":"SESSION_EXPIRED","message":"Session is invalid or expired"})
    return dict(row)

def require_roles(*allowed: str):
    def check(user=Depends(current_user)):
        if user["role"] not in allowed: raise HTTPException(403,detail={"code":"FORBIDDEN","message":"Insufficient role"})
        return user
    return check

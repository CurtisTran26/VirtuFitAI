from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserSession
from app.schemas import PhoneNumber, UserOut
from app.security import ROLES, hash_password, require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin accounts and roles"])
STAFF_ROLES = tuple(role for role in ROLES if role != "customer")


class StaffCreate(BaseModel):
    phone: PhoneNumber
    full_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    role: str


class RoleUpdate(BaseModel):
    role: str


@router.get("/roles")
def list_roles(_=Depends(require_roles("admin"))):
    return [{"name": role} for role in ROLES]


@router.get("/accounts", response_model=list[UserOut])
def list_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return db.query(User).offset(max(skip, 0)).limit(min(max(limit, 1), 200)).all()


@router.post("/accounts", response_model=UserOut, status_code=201)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    if payload.role not in STAFF_ROLES:
        raise HTTPException(422, "A staff role is required")
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(409, "Phone number is already registered")
    user = User(phone=payload.phone, full_name=payload.full_name, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Phone number is already registered") from exc
    db.refresh(user)
    return user


@router.patch("/accounts/{user_id}/role", response_model=UserOut)
def update_role(user_id: int, payload: RoleUpdate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    if payload.role not in ROLES:
        raise HTTPException(422, "Unknown role")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Account not found")
    active_admin_rows = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).order_by(User.id).with_for_update().all()
    if user.role == "admin" and user.is_active and payload.role != "admin" and len(active_admin_rows) <= 1:
        raise HTTPException(409, "Cannot remove the last active administrator")
    user.role = payload.role
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.now(timezone.utc)})
    db.commit()
    db.refresh(user)
    return user


@router.patch("/accounts/{user_id}/active")
def set_account_active(user_id: int, active: bool, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Account not found")
    active_admin_rows = db.query(User).filter(User.role == "admin", User.is_active.is_(True)).order_by(User.id).with_for_update().all()
    if user.role == "admin" and user.is_active and not active and len(active_admin_rows) <= 1:
        raise HTTPException(409, "Cannot deactivate the last active administrator")
    user.is_active = active
    if not active:
        db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.now(timezone.utc)})
    db.commit()
    return {"id": user.id, "is_active": user.is_active}

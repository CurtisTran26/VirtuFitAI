from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import PhoneNumber
from app.security import create_session, verify_password

router = APIRouter(prefix="/api/auth", tags=["RBAC and staff login"])
STAFF_ROLES = ("staff", "inventory", "manager", "admin")


class StaffLoginIn(BaseModel):
    phone: PhoneNumber
    password: str = Field(min_length=1)


@router.post("/staff-login")
def staff_login(payload: StaffLoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or user.role not in STAFF_ROLES or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Staff credentials are incorrect")
    token, expires = create_session(user, db)
    return {"access_token": token, "token_type": "bearer", "expires_at": expires, "role": user.role}

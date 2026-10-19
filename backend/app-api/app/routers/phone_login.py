from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import PhoneNumber
from app.security import create_session, verify_password

router = APIRouter(prefix="/api/auth", tags=["Phone login"])


class LoginIn(BaseModel):
    phone: PhoneNumber
    password: str = Field(min_length=1)


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Phone number or password is incorrect")
    token, expires = create_session(user, db)
    return {"access_token": token, "token_type": "bearer", "expires_at": expires, "role": user.role}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/api/accounts", tags=["Customer accounts"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_customer(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(409, "Phone number is already registered")
    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(409, "Email is already registered")
    user = User(
        phone=payload.phone,
        full_name=payload.full_name,
        email=str(payload.email) if payload.email else None,
        password_hash=hash_password(payload.password),
        role="customer",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Phone number or email is already registered") from exc
    db.refresh(user)
    return user

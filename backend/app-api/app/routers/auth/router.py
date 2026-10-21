from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import current_user, get_db, hash_password, issue_session, require_roles, verify_password
from app.schemas.auth import ChangePassword, Login, OtpPassword, OtpRequest, Register
from app.services.auth import consume_otp, create_otp

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/otp", status_code=202)
def request_otp(body: OtpRequest, db: Session = Depends(get_db)):
    account = db.execute(text("SELECT r.name AS role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:p"), {"p": body.phone}).mappings().first()
    exists = account is not None
    if (body.purpose == "register" and exists) or (body.purpose == "reset_password" and not exists):
        raise HTTPException(400, detail={"code": "OTP_UNAVAILABLE", "message": "OTP cannot be issued for this account"})
    if body.purpose == "reset_password" and account["role"] != "customer":
        raise HTTPException(400, detail={"code": "OTP_UNAVAILABLE", "message": "OTP cannot be issued for this account"})
    return create_otp(db, body.phone, body.purpose)


@router.post("/register", status_code=201)
def register(body: Register, db: Session = Depends(get_db)):
    if db.execute(text("SELECT 1 FROM users WHERE phone=:p"), {"p": body.phone}).first():
        raise HTTPException(409, detail={"code": "PHONE_EXISTS", "message": "Phone is already registered"})
    consume_otp(db, body.phone, "register", body.otp_code)
    row = db.execute(text("""INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at)
        SELECT :phone,:name,:password,r.id,now() FROM roles r WHERE r.name='customer'
        RETURNING id,phone,full_name"""), {"phone": body.phone, "name": body.full_name, "password": hash_password(body.password)}).mappings().one()
    session = issue_session(db, row["id"])
    db.commit()
    return {"user": {**dict(row), "role": "customer"}, **session}


@router.post("/login")
def login(body: Login, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT u.id,u.phone,u.full_name,u.password_hash,u.is_active,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:p"), {"p": body.phone}).mappings().first()
    if not row or not row["is_active"] or row["role"] != "customer" or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS", "message": "Phone or password is incorrect"})
    session = issue_session(db, row["id"])
    db.commit()
    return {"user": {"id": str(row["id"]), "phone": row["phone"], "full_name": row["full_name"], "role": row["role"]}, **session}


@router.post("/logout", status_code=204)
def logout(request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:hash AND revoked_at IS NULL"), {"hash": hashlib.sha256(token.encode()).hexdigest()})
    db.commit()
    return Response(status_code=204)


@router.post("/change-password", status_code=204)
def change_password(body: ChangePassword, user=Depends(current_user), db: Session = Depends(get_db)):
    row = db.execute(text("SELECT password_hash FROM users WHERE id=:id"), {"id": user["id"]}).mappings().one()
    if not verify_password(body.current_password, row["password_hash"]):
        raise HTTPException(400, detail={"code": "PASSWORD_INVALID", "message": "Current password is incorrect"})
    db.execute(text("UPDATE users SET password_hash=:h,updated_at=now() WHERE id=:id"), {"h": hash_password(body.new_password), "id": user["id"]})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"), {"id": user["id"]})
    db.commit()
    return Response(status_code=204)


@router.post("/reset-password", status_code=204)
def reset_password(body: OtpPassword, db: Session = Depends(get_db)):
    consume_otp(db, body.phone, "reset_password", body.otp_code)
    db.execute(text("UPDATE users SET password_hash=:h,updated_at=now() WHERE phone=:p AND role_id=(SELECT id FROM roles WHERE name='customer')"), {"h": hash_password(body.new_password), "p": body.phone})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=(SELECT id FROM users WHERE phone=:p)"), {"p": body.phone})
    db.commit()
    return Response(status_code=204)

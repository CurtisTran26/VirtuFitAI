from __future__ import annotations

import hashlib
import os
import secrets
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import get_db, current_user, require_roles, issue_session, hash_password, verify_password, now

app = FastAPI(title="VirtuFit App API", version="1.0.0", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
origins = [v.strip() for v in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if v.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
v1 = "/api/v1"

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    from fastapi.responses import JSONResponse
    detail=exc.detail if isinstance(exc.detail,dict) else {"code":"HTTP_ERROR","message":str(exc.detail)}
    if "code" not in detail: detail={"code":"HTTP_ERROR","message":str(detail)}
    return JSONResponse(status_code=exc.status_code,content={"error":detail},headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder
    return JSONResponse(status_code=422,content={"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":jsonable_encoder(exc.errors())}})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An internal error occurred","details":{}}})


class OtpRequest(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    purpose: str = Field(pattern="^(register|reset_password)$")

class Register(BaseModel):
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    otp_code: str = Field(pattern=r"^[0-9]{6}$")

class Login(BaseModel):
    phone: str
    password: str

class OtpPassword(BaseModel):
    phone: str
    otp_code: str = Field(pattern=r"^[0-9]{6}$")
    new_password: str = Field(min_length=8, max_length=72)

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


def create_otp(db: Session, phone: str, purpose: str):
    recent = db.execute(text("SELECT count(*) FROM otp_challenges WHERE phone=:p AND created_at > now()-interval '1 hour'"), {"p": phone}).scalar_one()
    if recent >= 5:
        raise HTTPException(429, detail={"code":"OTP_RATE_LIMIT","message":"Too many codes requested"})
    code = f"{secrets.randbelow(1_000_000):06d}"
    db.execute(text("INSERT INTO otp_challenges(phone,purpose,code_hash,expires_at) VALUES(:p,:purpose,:hash,:exp)"),
               {"p": phone, "purpose": purpose, "hash": hashlib.sha256(code.encode()).hexdigest(), "exp": now()+timedelta(minutes=5)})
    db.commit()
    result = {"message": "OTP request accepted"}
    if os.getenv("OTP_DEBUG", "false").lower() == "true":
        result["debug_code"] = code
    return result


def consume_otp(db: Session, phone: str, purpose: str, code: str):
    row = db.execute(text("SELECT id,code_hash,attempts FROM otp_challenges WHERE phone=:p AND purpose=:purpose AND consumed_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1 FOR UPDATE"),
                     {"p": phone, "purpose": purpose}).mappings().first()
    if not row or row["attempts"] >= 5 or row["code_hash"] != hashlib.sha256(code.encode()).hexdigest():
        if row:
            db.execute(text("UPDATE otp_challenges SET attempts=attempts+1 WHERE id=:id"), {"id": row["id"]})
        db.commit()
        raise HTTPException(400, detail={"code":"OTP_INVALID","message":"OTP is invalid or expired"})
    db.execute(text("UPDATE otp_challenges SET consumed_at=now() WHERE id=:id"), {"id": row["id"]})


@app.get(f"{v1}/health")
def health():
    return {"status":"ok"}

@app.post(f"{v1}/auth/otp", status_code=202)
def request_otp(body: OtpRequest, db: Session = Depends(get_db)):
    exists = db.execute(text("SELECT 1 FROM users WHERE phone=:p"), {"p": body.phone}).first()
    if (body.purpose == "register" and exists) or (body.purpose == "reset_password" and not exists):
        raise HTTPException(400, detail={"code":"OTP_UNAVAILABLE","message":"OTP cannot be issued for this account"})
    return create_otp(db, body.phone, body.purpose)

@app.post(f"{v1}/auth/register", status_code=201)
def register(body: Register, db: Session = Depends(get_db)):
    if db.execute(text("SELECT 1 FROM users WHERE phone=:p"), {"p": body.phone}).first():
        raise HTTPException(409, detail={"code":"PHONE_EXISTS","message":"Phone is already registered"})
    consume_otp(db, body.phone, "register", body.otp_code)
    row = db.execute(text("""INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at)
        SELECT :phone,:name,:password,r.id,now() FROM roles r WHERE r.name='customer'
        RETURNING id,phone,full_name"""), {"phone":body.phone,"name":body.full_name,"password":hash_password(body.password)}).mappings().one()
    session = issue_session(db, row["id"])
    db.commit()
    return {"user": {**dict(row), "role":"customer"}, **session}

@app.post(f"{v1}/auth/login")
def login(body: Login, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT u.id,u.phone,u.full_name,u.password_hash,u.is_active,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:p"), {"p":body.phone}).mappings().first()
    if not row or not row["is_active"] or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, detail={"code":"INVALID_CREDENTIALS","message":"Phone or password is incorrect"})
    session = issue_session(db, row["id"])
    db.commit()
    return {"user":{"id":str(row["id"]),"phone":row["phone"],"full_name":row["full_name"],"role":row["role"]}, **session}

@app.post(f"{v1}/auth/logout", status_code=204)
def logout(request: Request, user=Depends(current_user), db: Session=Depends(get_db)):
    token=request.headers.get("authorization", "").removeprefix("Bearer ")
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:hash AND revoked_at IS NULL"), {"hash":hashlib.sha256(token.encode()).hexdigest()})
    db.commit()
    return Response(status_code=204)

@app.post(f"{v1}/auth/change-password", status_code=204)
def change_password(body: ChangePassword, user=Depends(current_user), db: Session=Depends(get_db)):
    row = db.execute(text("SELECT password_hash FROM users WHERE id=:id"), {"id":user["id"]}).mappings().one()
    if not verify_password(body.current_password, row["password_hash"]):
        raise HTTPException(400, detail={"code":"PASSWORD_INVALID","message":"Current password is incorrect"})
    db.execute(text("UPDATE users SET password_hash=:h,updated_at=now() WHERE id=:id"), {"h":hash_password(body.new_password),"id":user["id"]})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"), {"id":user["id"]})
    db.commit()
    return Response(status_code=204)

@app.post(f"{v1}/auth/reset-password", status_code=204)
def reset_password(body: OtpPassword, db: Session=Depends(get_db)):
    consume_otp(db, body.phone, "reset_password", body.otp_code)
    db.execute(text("UPDATE users SET password_hash=:h,updated_at=now() WHERE phone=:p"), {"h":hash_password(body.new_password),"p":body.phone})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=(SELECT id FROM users WHERE phone=:p)"), {"p":body.phone})
    db.commit()

@app.get(f"{v1}/wishlist")
def wishlist(page:int=Query(1,ge=1), limit:int=Query(20,ge=1,le=100), user=Depends(require_roles("customer")), db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT p.id,p.name,p.price_vnd,p.image_url,w.created_at FROM wishlists w JOIN products p ON p.id=w.product_id WHERE w.user_id=:u ORDER BY w.created_at DESC LIMIT :l OFFSET :o"), {"u":user["id"],"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM wishlists WHERE user_id=:u"), {"u":user["id"]}).scalar_one()
    return {"items":[dict(r) for r in rows],"page":page,"limit":limit,"total":total}

@app.put(f"{v1}/wishlist/{{product_id}}", status_code=204)
def add_wishlist(product_id:UUID,user=Depends(require_roles("customer")),db:Session=Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM products WHERE id=:p AND is_active"), {"p":product_id}).first():
        raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    db.execute(text("INSERT INTO wishlists(user_id,product_id) VALUES(:u,:p) ON CONFLICT DO NOTHING"), {"u":user["id"],"p":product_id}); db.commit()

@app.delete(f"{v1}/wishlist/{{product_id}}", status_code=204)
def remove_wishlist(product_id:UUID,user=Depends(require_roles("customer")),db:Session=Depends(get_db)):
    db.execute(text("DELETE FROM wishlists WHERE user_id=:u AND product_id=:p"), {"u":user["id"],"p":product_id}); db.commit()

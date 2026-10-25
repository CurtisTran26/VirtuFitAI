from app.routers.common import *
from app.schemas.auth import ChangePassword, Login, PasswordReset, PasswordResetOtp

router = APIRouter()

@router.post(f"{v1}/auth/staff-login")
def staff_login(body:Login,db:Session=Depends(get_db)):
    row=db.execute(text("SELECT u.id,u.phone,u.full_name,u.password_hash,u.is_active,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:p"),{"p":body.phone}).mappings().first()
    if not row or not row["is_active"] or row["role"]=="customer" or not verify_password(body.password,row["password_hash"]):
        raise HTTPException(401,detail={"code":"INVALID_CREDENTIALS","message":"Staff credentials are incorrect"})
    result=issue_session(db,row["id"]); db.commit()
    return {"user":{"id":str(row["id"]),"phone":row["phone"],"full_name":row["full_name"],"role":row["role"]},**result}

@router.post(f"{v1}/auth/logout",status_code=204)
def logout(request:Request,user=Depends(current_user),db:Session=Depends(get_db)):
    token=request.headers.get("authorization", "").removeprefix("Bearer ")
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:hash AND revoked_at IS NULL"),{"hash":hashlib.sha256(token.encode()).hexdigest()}); db.commit()
    return Response(status_code=204)

@router.post(f"{v1}/auth/change-password",status_code=204)
def change_password(body:ChangePassword,user=Depends(current_user),db:Session=Depends(get_db)):
    row=db.execute(text("SELECT password_hash FROM users WHERE id=:id"),{"id":user["id"]}).mappings().one()
    if not verify_password(body.current_password,row["password_hash"]): raise HTTPException(400,detail={"code":"PASSWORD_INVALID","message":"Current password is incorrect"})
    db.execute(text("UPDATE users SET password_hash=:hash,updated_at=now() WHERE id=:id"),{"hash":hash_password(body.new_password),"id":user["id"]})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user["id"]}); db.commit()
    return Response(status_code=204)

@router.post(f"{v1}/auth/password-reset-otp",status_code=202)
def request_password_reset(body:PasswordResetOtp,db:Session=Depends(get_db)):
    row=db.execute(text("SELECT u.id FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:phone AND r.name<>'customer' AND u.is_active"),{"phone":body.phone}).first()
    if not row: raise HTTPException(400,detail={"code":"OTP_UNAVAILABLE","message":"OTP cannot be issued for this account"})
    recent=db.execute(text("SELECT count(*) FROM otp_challenges WHERE phone=:phone AND created_at>now()-interval '1 hour'"),{"phone":body.phone}).scalar_one()
    if recent>=5: raise HTTPException(429,detail={"code":"OTP_RATE_LIMIT","message":"Too many codes requested"})
    code=f"{secrets.randbelow(1_000_000):06d}"
    db.execute(text("INSERT INTO otp_challenges(phone,purpose,code_hash,expires_at) VALUES(:phone,'reset_password',:hash,:expires)"),{"phone":body.phone,"hash":hashlib.sha256(code.encode()).hexdigest(),"expires":now()+timedelta(minutes=5)}); db.commit()
    result={"message":"OTP request accepted"}
    if os.getenv("OTP_DEBUG","false").lower()=="true": result["debug_code"]=code
    return result

@router.post(f"{v1}/auth/reset-password",status_code=204)
def reset_password(body:PasswordReset,db:Session=Depends(get_db)):
    otp=db.execute(text("SELECT id,code_hash,attempts FROM otp_challenges WHERE phone=:phone AND purpose='reset_password' AND consumed_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1 FOR UPDATE"),{"phone":body.phone}).mappings().first()
    if not otp or otp["attempts"]>=5 or otp["code_hash"]!=hashlib.sha256(body.otp_code.encode()).hexdigest():
        if otp: db.execute(text("UPDATE otp_challenges SET attempts=attempts+1 WHERE id=:id"),{"id":otp["id"]})
        db.commit(); raise HTTPException(400,detail={"code":"OTP_INVALID","message":"OTP is invalid or expired"})
    db.execute(text("UPDATE otp_challenges SET consumed_at=now() WHERE id=:id"),{"id":otp["id"]})
    db.execute(text("UPDATE users SET password_hash=:hash,updated_at=now() WHERE phone=:phone AND role_id<>(SELECT id FROM roles WHERE name='customer')"),{"hash":hash_password(body.new_password),"phone":body.phone})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=(SELECT id FROM users WHERE phone=:phone)"),{"phone":body.phone}); db.commit()
    return Response(status_code=204)

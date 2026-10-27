from __future__ import annotations
from datetime import date
from typing import Literal
from uuid import UUID
import secrets
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from shared_platform import get_db, current_user, require_roles, issue_session, hash_password, verify_password
from app.mobile_support import fail, phone_key, password_ok, digest, otp_debug, deliver_sms, verify_google, validate_avatar

v1 = "/api/v1"
from app.schemas.auth import OtpRequest, Register, Login, VerifyOtp, ResetPassword, ChangePassword, GoogleLogin
from app.services.auth import session_response, lock_phone, consume_otp, update_password
from app.services.otp_delivery import start_challenge
router = APIRouter(tags=["Authentication"])


@router.post(f'{v1}/auth/otp',status_code=202)
def request_otp(body:OtpRequest,request:Request,db:Session=Depends(get_db)):
    phone=phone_key(body.phone); lock_phone(db,phone)
    row=db.execute(text('SELECT id,password_hash,is_active FROM users WHERE phone=:p'),{'p':phone}).mappings().first()
    if body.purpose=='register' and row:
        fail(409,'PHONE_EXISTS','Số điện thoại đã có tài khoản.')
    if body.purpose!='register' and (not row or not row['is_active'] or not row['password_hash']):
        fail(400,'OTP_UNAVAILABLE','Không thể cấp OTP cho tài khoản này.')
    if body.purpose=='change_password':
        from fastapi.security import HTTPAuthorizationCredentials
        raw=request.headers.get('authorization','')
        if not raw.startswith('Bearer '): fail(401,'UNAUTHENTICATED','Vui lòng đăng nhập.')
        user=current_user(HTTPAuthorizationCredentials(scheme='Bearer',credentials=raw[7:]),db)
        if user['id']!=row['id']: fail(403,'FORBIDDEN','Không thể đổi mật khẩu tài khoản khác.')
    count=db.execute(text("SELECT count(*) FROM otp_challenges WHERE phone=:p AND created_at>now()-interval '1 hour'"),{'p':phone}).scalar_one()
    cooldown=db.execute(text("SELECT 1 FROM otp_challenges WHERE phone=:p AND created_at>now()-interval '60 seconds' LIMIT 1"),{'p':phone}).first()
    if count>=5 or cooldown: fail(429,'OTP_RATE_LIMIT','Chờ 60 giây giữa các lần gửi; tối đa 5 mã mỗi giờ.')
    code=f'{secrets.randbelow(1000000):06d}'
    stored_code=start_challenge(db,phone,body.purpose,code)
    db.execute(text('UPDATE otp_challenges SET consumed_at=now() WHERE phone=:p AND consumed_at IS NULL'),{'p':phone})
    db.execute(text("INSERT INTO otp_challenges(phone,purpose,code_hash,expires_at) VALUES(:p,:s,:h,now()+interval '5 minutes')"),{'p':phone,'s':body.purpose,'h':stored_code})
    db.commit()
    result={'message':'OTP request accepted','expires_in':300,'resend_after':60}
    if otp_debug(): result['debug_code']=code
    return result


@router.post(f'{v1}/auth/register',status_code=201)
def register(body:Register,db:Session=Depends(get_db)):
    phone=phone_key(body.phone); password_ok(body.password)
    if not body.full_name.strip(): fail(422,'NAME_INVALID','Họ tên không được để trống.')
    lock_phone(db,phone)
    if db.execute(text('SELECT 1 FROM users WHERE phone=:p'),{'p':phone}).first(): fail(409,'PHONE_EXISTS','Số điện thoại đã đăng ký.')
    consume_otp(db,phone,'register',body.otp_code)
    uid=db.execute(text('''INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at)
      SELECT :p,:n,:h,id,now() FROM roles WHERE name='customer' RETURNING id'''),{'p':phone,'n':body.full_name.strip(),'h':hash_password(body.password)}).scalar_one()
    return session_response(db,uid)


@router.post(f'{v1}/auth/login')
def login(body:Login,db:Session=Depends(get_db)):
    phone=phone_key(body.phone); lock_phone(db,phone)
    attempts=db.execute(text("SELECT count(*) FROM auth_login_attempts WHERE phone=:p AND created_at>now()-interval '15 minutes'"),{'p':phone}).scalar_one()
    if attempts>=10: fail(429,'LOGIN_RATE_LIMIT','Đã thử quá nhiều lần. Vui lòng đợi 15 phút.')
    row=db.execute(text('SELECT id,password_hash,is_active FROM users WHERE phone=:p FOR UPDATE'),{'p':phone}).mappings().first()
    if not row or not row['is_active'] or not row['password_hash'] or len(body.password.encode())>72 or not verify_password(body.password,row['password_hash']):
        db.execute(text('INSERT INTO auth_login_attempts(phone) VALUES(:p)'),{'p':phone});db.commit()
        fail(401,'INVALID_CREDENTIALS','Số điện thoại hoặc mật khẩu không đúng.')
    db.execute(text('DELETE FROM auth_login_attempts WHERE phone=:p'),{'p':phone})
    return session_response(db,row['id'])


@router.post(f'{v1}/auth/google')
def google_login(body:GoogleLogin,db:Session=Depends(get_db)):
    info=verify_google(body.id_token)
    lock_phone(db,'google:'+info['sub'])
    row=db.execute(text('SELECT id,is_active FROM users WHERE google_sub=:s FOR UPDATE'),{'s':info['sub']}).mappings().first()
    if row:
        if not row['is_active']: fail(403,'ACCOUNT_DISABLED','Tài khoản đã bị khóa.')
        return session_response(db,row['id'])
    email=info['email'].lower()
    if db.execute(text('SELECT 1 FROM users WHERE lower(email)=:e'),{'e':email}).first():
        fail(409,'ACCOUNT_LINK_REQUIRED','Email đã có tài khoản. Cần xác minh để liên kết, không tự động gộp.')
    try:
        uid=db.execute(text('''INSERT INTO users(full_name,email,google_sub,role_id)
          SELECT :n,:e,:s,id FROM roles WHERE name='customer' RETURNING id'''),{'n':str(info.get('name') or email)[:120],'e':email,'s':info['sub']}).scalar_one()
        return session_response(db,uid)
    except IntegrityError:
        db.rollback();fail(409,'ACCOUNT_EXISTS','Tài khoản vừa được tạo. Vui lòng đăng nhập lại.')


@router.post(f'{v1}/auth/logout',status_code=204)
def logout(request:Request,user=Depends(current_user),db:Session=Depends(get_db)):
    token=request.headers.get('authorization','').split(' ',1)[-1]
    db.execute(text('UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:h'),{'h':digest(token)});db.commit()
    return Response(status_code=204)


@router.post(f'{v1}/auth/verify-reset-otp')
def verify_reset(body:VerifyOtp,db:Session=Depends(get_db)):
    phone=phone_key(body.phone);lock_phone(db,phone)
    row=db.execute(text('SELECT id FROM users WHERE phone=:p AND is_active AND password_hash IS NOT NULL'),{'p':phone}).first()
    if not row: fail(400,'OTP_INVALID','Mã OTP không hợp lệ.')
    consume_otp(db,phone,'reset_password',body.otp_code)
    token=secrets.token_urlsafe(40)
    db.execute(text('UPDATE password_reset_tickets SET used_at=now() WHERE user_id=:u AND used_at IS NULL'),{'u':row.id})
    db.execute(text("INSERT INTO password_reset_tickets(token_hash,user_id,expires_at) VALUES(:h,:u,now()+interval '5 minutes')"),{'h':digest(token),'u':row.id})
    db.commit();return {'reset_token':token,'phone':phone,'expires_in':300}


@router.post(f'{v1}/auth/reset-password',status_code=204)
def reset_password(body:ResetPassword,db:Session=Depends(get_db)):
    password_ok(body.new_password)
    if body.reset_token:
        ticket=db.execute(text('''SELECT t.user_id FROM password_reset_tickets t JOIN users u ON u.id=t.user_id
          WHERE t.token_hash=:h AND t.used_at IS NULL AND t.expires_at>now() AND u.is_active FOR UPDATE OF t'''),{'h':digest(body.reset_token)}).first()
        if not ticket: fail(400,'RESET_EXPIRED','Phiên đặt lại mật khẩu đã hết hạn hoặc được sử dụng.')
        uid=ticket.user_id
    elif body.phone and body.otp_code:
        phone=phone_key(body.phone);lock_phone(db,phone)
        row=db.execute(text('SELECT id FROM users WHERE phone=:p AND is_active AND password_hash IS NOT NULL FOR UPDATE'),{'p':phone}).first()
        if not row: fail(400,'OTP_INVALID','Không thể đặt lại mật khẩu.')
        consume_otp(db,phone,'reset_password',body.otp_code);uid=row.id
    else: fail(422,'RESET_REQUIRED','Cần phiên xác minh OTP để đặt lại mật khẩu.')
    update_password(db,uid,body.new_password)
    return Response(status_code=204)


@router.post(f'{v1}/auth/change-password',status_code=204)
def change_password(body:ChangePassword,user=Depends(current_user),db:Session=Depends(get_db)):
    password_ok(body.new_password)
    row=db.execute(text('SELECT phone,password_hash FROM users WHERE id=:u FOR UPDATE'),{'u':user['id']}).mappings().one()
    if not row['password_hash'] or not row['phone']: fail(400,'GOOGLE_ACCOUNT','Tài khoản Google không có mật khẩu điện thoại.')
    if body.otp_code: consume_otp(db,row['phone'],'change_password',body.otp_code)
    elif body.current_password and len(body.current_password.encode())<=72 and verify_password(body.current_password,row['password_hash']): pass
    else: fail(400,'PASSWORD_INVALID','Cần OTP hợp lệ hoặc mật khẩu hiện tại.')
    update_password(db,user['id'],body.new_password)
    return Response(status_code=204)



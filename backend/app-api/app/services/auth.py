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

from app.services.profiles import account
from app.services.otp_delivery import check_challenge

def session_response(db, uid):
    result={'user':account(db,uid),**issue_session(db,uid)}
    db.commit(); return result


def lock_phone(db, phone):
    db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:p,0))'),{'p':phone})


def consume_otp(db, phone, purpose, code):
    row=db.execute(text('''SELECT id,code_hash,attempts FROM otp_challenges WHERE phone=:p AND purpose=:s
        AND consumed_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1 FOR UPDATE'''),{'p':phone,'s':purpose}).mappings().first()
    attempts = row['attempts'] if row else 0
    if row and row['code_hash'].strip().startswith('verify:'):
        attempts = db.execute(text('SELECT COALESCE(sum(attempts),0) FROM otp_challenges WHERE phone=:p AND code_hash=:h'), {'p':phone,'h':row['code_hash']}).scalar_one()
    if not row or attempts>=5 or not check_challenge(row['code_hash'],code,phone):
        if row: db.execute(text('UPDATE otp_challenges SET attempts=LEAST(attempts+1,5) WHERE id=:id'),{'id':row['id']})
        db.commit(); fail(400,'OTP_INVALID','Mã OTP sai, hết hạn hoặc đã được sử dụng.')
    db.execute(text('UPDATE otp_challenges SET consumed_at=now() WHERE id=:id'),{'id':row['id']})


def update_password(db,uid,password):
    db.execute(text('UPDATE users SET password_hash=:h,updated_at=now() WHERE id=:u'),{'h':hash_password(password),'u':uid})
    db.execute(text('UPDATE user_sessions SET revoked_at=now() WHERE user_id=:u AND revoked_at IS NULL'),{'u':uid})
    db.execute(text('UPDATE password_reset_tickets SET used_at=now() WHERE user_id=:u AND used_at IS NULL'),{'u':uid})
    db.execute(text('UPDATE otp_challenges SET consumed_at=now() WHERE phone=(SELECT phone FROM users WHERE id=:u) AND consumed_at IS NULL'),{'u':uid})
    db.commit()



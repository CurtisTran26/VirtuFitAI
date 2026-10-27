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
from app.schemas.profile import ProfileUpdate
from app.services.profiles import account
router = APIRouter(tags=["Profile"])


@router.get(f'{v1}/users/me')
def get_profile(user=Depends(current_user),db:Session=Depends(get_db)):
    return account(db,user['id'])


@router.put(f'{v1}/users/me')
def put_profile(body:ProfileUpdate,user=Depends(require_roles('customer')),db:Session=Depends(get_db)):
    if not body.full_name.strip(): fail(422,'NAME_INVALID','Họ tên không được trống.')
    if body.date_of_birth and body.date_of_birth>date.today(): fail(422,'BIRTHDAY_INVALID','Ngày sinh không được ở tương lai.')
    values={'n':body.full_name.strip(),'b':body.date_of_birth,'h':body.height_cm,'w':body.weight_kg,'u':user['id']}
    extra=''
    if 'avatar_data' in body.model_fields_set:
        values['a']=validate_avatar(body.avatar_data)
        from app.team_integrations.storage import enabled, storage_service
        if values['a'] and enabled():
            values['a']=storage_service.upload_avatar(values['a'],user['id'])
        extra=',avatar_url=:a'
    db.execute(text('UPDATE users SET full_name=:n,date_of_birth=:b,height_cm=:h,weight_kg=:w,updated_at=now()'+extra+' WHERE id=:u'),values)
    db.commit();return account(db,user['id'])



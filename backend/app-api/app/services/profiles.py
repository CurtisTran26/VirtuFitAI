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


def account(db, uid):
    row=db.execute(text('''SELECT u.id,u.phone,u.full_name,u.email,u.google_sub,u.avatar_url,
        u.date_of_birth,u.height_cm,u.weight_kg,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.id=:id'''),{'id':uid}).mappings().one()
    result=dict(row); result['name']=row['full_name']; result['auth_method']='google' if row['google_sub'] else 'phone'
    result.pop('google_sub')
    from app.team_integrations.storage import storage_service
    result['avatar_url']=storage_service.avatar_url(result['avatar_url'])
    return result



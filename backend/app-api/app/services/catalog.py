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


def product_detail(db, pid):
    row=db.execute(text('''SELECT p.*,c.name category FROM products p JOIN categories c ON c.id=p.category_id
      WHERE p.id=:p AND p.is_active AND c.is_active'''),{'p':pid}).mappings().first()
    if not row: fail(404,'PRODUCT_NOT_FOUND','Không tìm thấy sản phẩm đang bán.')
    result=dict(row)
    result['variants']=[dict(v) for v in db.execute(text('SELECT id,size,color,sku,stock_on_hand FROM product_variants WHERE product_id=:p ORDER BY color,size'),{'p':pid}).mappings()]
    return result



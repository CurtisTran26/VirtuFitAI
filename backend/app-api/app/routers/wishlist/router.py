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
from app.services.catalog import product_detail
router = APIRouter(tags=["Wishlist"])


@router.get(f'{v1}/wishlist')
def wishlist(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Depends(require_roles('customer')),db:Session=Depends(get_db)):
    where='w.user_id=:u AND p.is_active AND c.is_active'
    args={'u':user['id'],'l':limit,'o':(page-1)*limit}
    joins=' FROM wishlists w JOIN products p ON p.id=w.product_id JOIN categories c ON c.id=p.category_id WHERE '+where
    total=db.execute(text('SELECT count(*)'+joins),args).scalar_one()
    ids=db.execute(text('SELECT p.id'+joins+' ORDER BY w.created_at DESC,p.id LIMIT :l OFFSET :o'),args).scalars().all()
    return {'items':[product_detail(db,p) for p in ids],'page':page,'limit':limit,'total':total}


@router.put(f'{v1}/wishlist/{{product_id}}',status_code=204)
def add_wishlist(product_id:UUID,user=Depends(require_roles('customer')),db:Session=Depends(get_db)):
    product_detail(db,product_id)
    db.execute(text('INSERT INTO wishlists(user_id,product_id) VALUES(:u,:p) ON CONFLICT DO NOTHING'),{'u':user['id'],'p':product_id});db.commit()
    return Response(status_code=204)


@router.delete(f'{v1}/wishlist/{{product_id}}',status_code=204)
def remove_wishlist(product_id:UUID,user=Depends(require_roles('customer')),db:Session=Depends(get_db)):
    db.execute(text('DELETE FROM wishlists WHERE user_id=:u AND product_id=:p'),{'u':user['id'],'p':product_id});db.commit()
    return Response(status_code=204)



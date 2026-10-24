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
router = APIRouter(tags=["Catalog"])


@router.get(f'{v1}/catalog/categories')
def categories(db:Session=Depends(get_db)):
    return [dict(r) for r in db.execute(text('SELECT id,name FROM categories WHERE is_active ORDER BY name')).mappings()]


@router.get(f'{v1}/catalog/products')
def products(q:str=Query('',max_length=100),category_id:UUID|None=None,
             page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),page_size:int|None=Query(None,ge=1,le=100),
             min_price:int|None=Query(None,ge=0),max_price:int|None=Query(None,ge=0),
             color:str|None=Query(None,max_length=50),size:str|None=Query(None,max_length=30),
             in_stock_only:bool=False,sort_by:Literal['newest','price_asc','price_desc']='newest',db:Session=Depends(get_db)):
    from app.team_integrations.catalog import list_products
    return list_products(db,product_detail,q=q,category_id=category_id,page=page,limit=page_size or limit,
        min_price=min_price,max_price=max_price,color=color,size=size,in_stock_only=in_stock_only,sort_by=sort_by)


@router.get(f'{v1}/catalog/filter-options')
def filter_options(category_id:UUID|None=None,db:Session=Depends(get_db)):
    where='p.is_active AND c.is_active'
    args={}
    if category_id: where+=' AND p.category_id=:cat'; args['cat']=category_id
    rows=db.execute(text('SELECT DISTINCT v.color,v.size FROM product_variants v JOIN products p ON p.id=v.product_id JOIN categories c ON c.id=p.category_id WHERE '+where),args).mappings().all()
    return {'colors':sorted({r['color'] for r in rows if r['color']}),'sizes':sorted({r['size'] for r in rows if r['size']})}


@router.get(f'{v1}/catalog/products/{{product_id}}')
def product(product_id:UUID,db:Session=Depends(get_db)):
    return product_detail(db,product_id)



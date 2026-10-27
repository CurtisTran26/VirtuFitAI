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
from app.schemas.qr import QrScan
from app.services.catalog import product_detail
router = APIRouter(tags=["QR"])


@router.post(f'{v1}/qr/scan')
def scan(body:QrScan,db:Session=Depends(get_db)):
    from app.team_integrations.qr import qr_service
    return {'product':product_detail(db,qr_service.resolve_id(db,body.content))}


@router.get(f'{v1}/qr/scan')
def scan_get(code:str=Query(...,min_length=1,max_length=1000),db:Session=Depends(get_db)):
    return scan(QrScan(content=code),db)


@router.get(f'{v1}/qr/products/{{product_id}}/image')
def qr_image(product_id:UUID,user=Depends(require_roles('admin','warehouse_staff','sales_staff')),db:Session=Depends(get_db)):
    from app.team_integrations.qr import qr_service
    product_detail(db,product_id)
    return Response(qr_service.generate_qr_image_bytes(f'virtufit://products/{product_id}'),media_type='image/png',
        headers={'Content-Disposition':f'attachment; filename="qr-{product_id}.png"'})



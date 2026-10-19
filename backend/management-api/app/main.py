from __future__ import annotations

import os
import secrets
import hashlib
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Response, Request
from fastapi.exceptions import RequestValidationError
import hashlib
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import get_db, current_user, require_roles, verify_password, hash_password, issue_session, now

app=FastAPI(title="VirtuFit Management API",version="1.0.0",openapi_url="/api/v1/openapi.json",docs_url="/api/v1/docs")
origins=[v.strip() for v in os.getenv("CORS_ORIGINS","http://localhost:5173").split(",") if v.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
v1="/api/v1"
Admin=Depends(require_roles("admin"))
CatalogEditor=Depends(require_roles("admin","warehouse_staff"))
Warehouse=Depends(require_roles("admin","warehouse_staff"))

@app.exception_handler(HTTPException)
async def http_error(request,exc):
    from fastapi.responses import JSONResponse
    detail=exc.detail if isinstance(exc.detail,dict) else {"code":"HTTP_ERROR","message":str(exc.detail)}
    if "code" not in detail: detail={"code":"HTTP_ERROR","message":str(detail)}
    return JSONResponse(status_code=exc.status_code,content={"error":detail},headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder
    return JSONResponse(status_code=422,content={"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":jsonable_encoder(exc.errors())}})

@app.exception_handler(Exception)
async def unexpected_error(request,exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An internal error occurred","details":{}}})

class Login(BaseModel): phone:str; password:str
class ChangePassword(BaseModel): current_password:str; new_password:str=Field(min_length=8,max_length=72)
class PasswordResetOtp(BaseModel): phone:str=Field(pattern=r"^\+?[0-9]{9,15}$")
class PasswordReset(BaseModel): phone:str=Field(pattern=r"^\+?[0-9]{9,15}$"); otp_code:str=Field(pattern=r"^[0-9]{6}$"); new_password:str=Field(min_length=8,max_length=72)
class UserCreate(BaseModel): phone:str=Field(pattern=r"^\+?[0-9]{9,15}$"); full_name:str=Field(min_length=1,max_length=120); password:str=Field(min_length=12,max_length=72); role:str=Field(pattern="^(sales_staff|warehouse_staff|designer|admin)$")
class RoleUpdate(BaseModel): role:str=Field(pattern="^(customer|sales_staff|warehouse_staff|designer|admin)$")
class CategoryIn(BaseModel): name:str=Field(min_length=1,max_length=120); description:str=""; is_active:bool=True
class ProductIn(BaseModel): category_id:UUID; name:str=Field(min_length=1,max_length=180); description:str=""; price_vnd:int=Field(ge=0); sku:str=Field(min_length=1,max_length=80); image_url:str|None=None; is_active:bool=True
class SizeChartIn(BaseModel): category_id:UUID; name:str=Field(min_length=1,max_length=120); measurements:list[dict]
class VariantIn(BaseModel): product_id:UUID; size:str=Field(min_length=1,max_length=30); color:str=""; sku:str=Field(min_length=1,max_length=80)
class AdjustIn(BaseModel): delta:int=Field(ne=0); reason:str=Field(min_length=3,max_length=500)

@app.get(f"{v1}/health")
def health(): return {"status":"ok"}

@app.post(f"{v1}/auth/staff-login")
def staff_login(body:Login,db:Session=Depends(get_db)):
    row=db.execute(text("SELECT u.id,u.phone,u.full_name,u.password_hash,u.is_active,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:p"),{"p":body.phone}).mappings().first()
    if not row or not row["is_active"] or row["role"]=="customer" or not verify_password(body.password,row["password_hash"]):
        raise HTTPException(401,detail={"code":"INVALID_CREDENTIALS","message":"Staff credentials are incorrect"})
    result=issue_session(db,row["id"]); db.commit()
    return {"user":{"id":str(row["id"]),"phone":row["phone"],"full_name":row["full_name"],"role":row["role"]},**result}

@app.post(f"{v1}/auth/logout",status_code=204)
def logout(request:Request,user=Depends(current_user),db:Session=Depends(get_db)):
    token=request.headers.get("authorization", "").removeprefix("Bearer ")
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:hash AND revoked_at IS NULL"),{"hash":hashlib.sha256(token.encode()).hexdigest()}); db.commit()
    return Response(status_code=204)

@app.post(f"{v1}/auth/change-password",status_code=204)
def change_password(body:ChangePassword,user=Depends(current_user),db:Session=Depends(get_db)):
    row=db.execute(text("SELECT password_hash FROM users WHERE id=:id"),{"id":user["id"]}).mappings().one()
    if not verify_password(body.current_password,row["password_hash"]): raise HTTPException(400,detail={"code":"PASSWORD_INVALID","message":"Current password is incorrect"})
    db.execute(text("UPDATE users SET password_hash=:hash,updated_at=now() WHERE id=:id"),{"hash":hash_password(body.new_password),"id":user["id"]})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user["id"]}); db.commit()
    return Response(status_code=204)

@app.post(f"{v1}/auth/password-reset-otp",status_code=202)
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

@app.post(f"{v1}/auth/reset-password",status_code=204)
def reset_password(body:PasswordReset,db:Session=Depends(get_db)):
    otp=db.execute(text("SELECT id,code_hash,attempts FROM otp_challenges WHERE phone=:phone AND purpose='reset_password' AND consumed_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1 FOR UPDATE"),{"phone":body.phone}).mappings().first()
    if not otp or otp["attempts"]>=5 or otp["code_hash"]!=hashlib.sha256(body.otp_code.encode()).hexdigest():
        if otp: db.execute(text("UPDATE otp_challenges SET attempts=attempts+1 WHERE id=:id"),{"id":otp["id"]})
        db.commit(); raise HTTPException(400,detail={"code":"OTP_INVALID","message":"OTP is invalid or expired"})
    db.execute(text("UPDATE otp_challenges SET consumed_at=now() WHERE id=:id"),{"id":otp["id"]})
    db.execute(text("UPDATE users SET password_hash=:hash,updated_at=now() WHERE phone=:phone AND role_id<>(SELECT id FROM roles WHERE name='customer')"),{"hash":hash_password(body.new_password),"phone":body.phone})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=(SELECT id FROM users WHERE phone=:phone)"),{"phone":body.phone}); db.commit()
    return Response(status_code=204)

@app.get(f"{v1}/admin/roles")
def roles(user=Admin,db:Session=Depends(get_db)):
    return {"items":[dict(x) for x in db.execute(text("SELECT name,description FROM roles ORDER BY name")).mappings().all()]}

@app.get(f"{v1}/admin/users")
def users(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),role:str|None=None,user=Admin,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT u.id,u.phone,u.full_name,u.is_active,r.name role,u.created_at FROM users u JOIN roles r ON r.id=u.role_id WHERE (CAST(:role AS text) IS NULL OR r.name=:role) ORDER BY u.created_at DESC LIMIT :lim OFFSET :off"),{"role":role,"lim":limit,"off":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM users u JOIN roles r ON r.id=u.role_id WHERE (CAST(:role AS text) IS NULL OR r.name=:role)"),{"role":role}).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@app.post(f"{v1}/admin/users",status_code=201)
def create_user(body:UserCreate,user=Admin,db:Session=Depends(get_db)):
    if db.execute(text("SELECT 1 FROM users WHERE phone=:p"),{"p":body.phone}).first(): raise HTTPException(409,detail={"code":"PHONE_EXISTS","message":"Phone already exists"})
    row=db.execute(text("INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at) SELECT :p,:n,:h,id,now() FROM roles WHERE name=:role RETURNING id,phone,full_name"),{"p":body.phone,"n":body.full_name,"h":hash_password(body.password),"role":body.role}).mappings().one()
    db.commit(); return {**dict(row),"role":body.role,"is_active":True}

@app.patch(f"{v1}/admin/users/{{user_id}}/role")
def change_role(user_id:UUID,body:RoleUpdate,user=Admin,db:Session=Depends(get_db)):
    if str(user_id)==str(user["id"]): raise HTTPException(409,detail={"code":"SELF_ROLE_CHANGE","message":"Administrators cannot change their own role"})
    result=db.execute(text("UPDATE users SET role_id=(SELECT id FROM roles WHERE name=:role),updated_at=now() WHERE id=:id RETURNING id"),{"role":body.role,"id":user_id})
    if not result.first(): raise HTTPException(404,detail={"code":"USER_NOT_FOUND","message":"User not found"})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user_id}); db.commit()
    return {"id":str(user_id),"role":body.role}

@app.patch(f"{v1}/admin/users/{{user_id}}/status")
def set_user_status(user_id:UUID,is_active:bool,user=Admin,db:Session=Depends(get_db)):
    if str(user_id)==str(user["id"]) and not is_active: raise HTTPException(409,detail={"code":"SELF_DEACTIVATION","message":"Administrators cannot deactivate their own account"})
    row=db.execute(text("UPDATE users SET is_active=:active,updated_at=now() WHERE id=:id RETURNING id,is_active"),{"active":is_active,"id":user_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"USER_NOT_FOUND","message":"User not found"})
    if not is_active: db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user_id})
    db.commit(); return {"id":str(row["id"]),"is_active":row["is_active"]}

@app.get(f"{v1}/categories")
def list_categories(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,name,description,is_active,created_at FROM categories ORDER BY name LIMIT :l OFFSET :o"),{"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM categories")).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@app.post(f"{v1}/categories",status_code=201)
def create_category(body:CategoryIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO categories(name,description,is_active) VALUES(:n,:d,:a) RETURNING id,name,description,is_active,created_at"),{"n":body.name,"d":body.description,"a":body.is_active}).mappings().one(); db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"CATEGORY_CONFLICT","message":"Category name already exists"}) from exc

@app.patch(f"{v1}/categories/{{category_id}}")
def update_category(category_id:UUID,body:CategoryIn,user=CatalogEditor,db:Session=Depends(get_db)):
    row=db.execute(text("UPDATE categories SET name=:n,description=:d,is_active=:a WHERE id=:id RETURNING id,name,description,is_active,created_at"),{"n":body.name,"d":body.description,"a":body.is_active,"id":category_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    db.commit(); return dict(row)

@app.delete(f"{v1}/categories/{{category_id}}",status_code=204)
def archive_category(category_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("UPDATE categories SET is_active=false WHERE id=:id"),{"id":category_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    db.commit(); return Response(status_code=204)

@app.get(f"{v1}/products")
def list_products(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),category_id:UUID|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at FROM products p JOIN categories c ON c.id=p.category_id WHERE (CAST(:c AS uuid) IS NULL OR p.category_id=:c) ORDER BY p.created_at DESC LIMIT :l OFFSET :o"),{"c":category_id,"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM products WHERE (CAST(:c AS uuid) IS NULL OR category_id=:c)"),{"c":category_id}).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@app.get(f"{v1}/products/{{product_id}}")
def get_product(product_id:UUID,user=Depends(current_user),db:Session=Depends(get_db)):
    row=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at FROM products p JOIN categories c ON c.id=p.category_id WHERE p.id=:id"),{"id":product_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    return dict(row)

@app.post(f"{v1}/products",status_code=201)
def create_product(body:ProductIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO products(category_id,name,description,price_vnd,sku,image_url,is_active) VALUES(:c,:n,:d,:price,:sku,:img,:active) RETURNING id,category_id,name,description,price_vnd,sku,image_url,is_active,created_at"),{"c":body.category_id,"n":body.name,"d":body.description,"price":body.price_vnd,"sku":body.sku,"img":body.image_url,"active":body.is_active}).mappings().one(); db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"PRODUCT_CONFLICT","message":"Invalid category or duplicate SKU"}) from exc

@app.patch(f"{v1}/products/{{product_id}}")
def update_product(product_id:UUID,body:ProductIn,user=CatalogEditor,db:Session=Depends(get_db)):
    row=db.execute(text("UPDATE products SET category_id=:c,name=:n,description=:d,price_vnd=:price,sku=:sku,image_url=:img,is_active=:active,updated_at=now() WHERE id=:id RETURNING id,category_id,name,description,price_vnd,sku,image_url,is_active,created_at"),{"c":body.category_id,"n":body.name,"d":body.description,"price":body.price_vnd,"sku":body.sku,"img":body.image_url,"active":body.is_active,"id":product_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    db.commit(); return dict(row)

@app.delete(f"{v1}/products/{{product_id}}",status_code=204)
def archive_product(product_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("UPDATE products SET is_active=false,updated_at=now() WHERE id=:id"),{"id":product_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    db.commit(); return Response(status_code=204)

@app.get(f"{v1}/size-charts")
def list_size_charts(category_id:UUID|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,category_id,name,measurements,created_at FROM size_charts WHERE (CAST(:c AS uuid) IS NULL OR category_id=:c) ORDER BY name"),{"c":category_id}).mappings().all()
    return {"items":[dict(x) for x in rows]}

@app.post(f"{v1}/size-charts",status_code=201)
def create_size_chart(body:SizeChartIn,user=CatalogEditor,db:Session=Depends(get_db)):
    row=db.execute(text("INSERT INTO size_charts(category_id,name,measurements) VALUES(:c,:n,CAST(:m AS jsonb)) RETURNING id,category_id,name,measurements,created_at"),{"c":body.category_id,"n":body.name,"m":__import__('json').dumps(body.measurements)}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    db.commit(); return dict(row)

@app.put(f"{v1}/size-charts/{{chart_id}}")
def update_size_chart(chart_id:UUID,body:SizeChartIn,user=CatalogEditor,db:Session=Depends(get_db)):
    row=db.execute(text("UPDATE size_charts SET category_id=:c,name=:n,measurements=CAST(:m AS jsonb) WHERE id=:id RETURNING id,category_id,name,measurements,created_at"),{"c":body.category_id,"n":body.name,"m":__import__('json').dumps(body.measurements),"id":chart_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"SIZE_CHART_NOT_FOUND","message":"Size chart not found"})
    db.commit(); return dict(row)

@app.delete(f"{v1}/size-charts/{{chart_id}}",status_code=204)
def delete_size_chart(chart_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("DELETE FROM size_charts WHERE id=:id"),{"id":chart_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"SIZE_CHART_NOT_FOUND","message":"Size chart not found"})
    db.commit(); return Response(status_code=204)

@app.post(f"{v1}/products/{{product_id}}/variants",status_code=201)
def create_variant(product_id:UUID,body:VariantIn,user=CatalogEditor,db:Session=Depends(get_db)):
    if product_id!=body.product_id: raise HTTPException(400,detail={"code":"PRODUCT_MISMATCH","message":"Path and body product IDs differ"})
    try:
        row=db.execute(text("INSERT INTO product_variants(product_id,size,color,sku) VALUES(:p,:s,:c,:sku) RETURNING id,product_id,size,color,sku,stock_on_hand"),{"p":product_id,"s":body.size,"c":body.color,"sku":body.sku}).mappings().one(); db.commit(); return dict(row)
    except Exception as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"VARIANT_CONFLICT","message":"Invalid product or duplicate variant/SKU"}) from exc

@app.post(f"{v1}/inventory/variants/{{variant_id}}/adjustments",status_code=201)
def adjust_stock(variant_id:UUID,body:AdjustIn,user=Warehouse,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("SELECT stock_on_hand FROM product_variants WHERE id=:id FOR UPDATE"),{"id":variant_id}).mappings().first()
        if not row: raise HTTPException(404,detail={"code":"VARIANT_NOT_FOUND","message":"Variant not found"})
        before=row["stock_on_hand"]; after=before+body.delta
        if after<0: raise HTTPException(409,detail={"code":"OUT_OF_STOCK","message":"Adjustment would make stock negative"})
        db.execute(text("UPDATE product_variants SET stock_on_hand=:q,updated_at=now() WHERE id=:id"),{"q":after,"id":variant_id})
        record=db.execute(text("INSERT INTO inventory_adjustments(variant_id,changed_by,delta,quantity_before,quantity_after,reason) VALUES(:v,:u,:d,:b,:a,:r) RETURNING id,variant_id,changed_by,delta,quantity_before,quantity_after,reason,created_at"),{"v":variant_id,"u":user["id"],"d":body.delta,"b":before,"a":after,"r":body.reason}).mappings().one()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(record)

@app.get(f"{v1}/inventory/variants/{{variant_id}}/adjustments")
def inventory_history(variant_id:UUID,page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Warehouse,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,variant_id,changed_by,delta,quantity_before,quantity_after,reason,created_at FROM inventory_adjustments WHERE variant_id=:v ORDER BY created_at DESC LIMIT :l OFFSET :o"),{"v":variant_id,"l":limit,"o":(page-1)*limit}).mappings().all()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit}

@app.get(f"{v1}/inventory/variants")
def list_inventory(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Warehouse,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT v.id variant_id,v.product_id,p.name product_name,v.sku,v.size,v.color,v.stock_on_hand,v.updated_at FROM product_variants v JOIN products p ON p.id=v.product_id ORDER BY p.name,v.size,v.color LIMIT :l OFFSET :o"),{"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM product_variants")).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

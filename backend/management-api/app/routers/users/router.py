from app.routers.common import *
from app.schemas.users import RoleUpdate, UserCreate

router = APIRouter()

@router.get(f"{v1}/admin/users")
def users(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),role:str|None=None,user=Admin,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT u.id,u.phone,u.phone AS account,u.full_name,u.is_active,r.name role,u.created_at,COALESCE((SELECT count(*) FROM orders o WHERE o.customer_id=u.id),0) AS order_count FROM users u JOIN roles r ON r.id=u.role_id WHERE (CAST(:role AS text) IS NULL OR r.name=:role) ORDER BY u.created_at DESC LIMIT :lim OFFSET :off"),{"role":role,"lim":limit,"off":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM users u JOIN roles r ON r.id=u.role_id WHERE (CAST(:role AS text) IS NULL OR r.name=:role)"),{"role":role}).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@router.post(f"{v1}/admin/users",status_code=201)
def create_user(body:UserCreate,user=Admin,db:Session=Depends(get_db)):
    if body.role=="admin": raise HTTPException(409,detail={"code":"ADMIN_ROLE_RESERVED","message":"The initial administrator account is managed separately"})
    if db.execute(text("SELECT 1 FROM users WHERE phone=:account"),{"account":body.account}).first(): raise HTTPException(409,detail={"code":"ACCOUNT_EXISTS","message":"Account already exists"})
    row=db.execute(text("INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at) SELECT :account,:n,:h,id,now() FROM roles WHERE name=:role RETURNING id,phone,phone AS account,full_name"),{"account":body.account,"n":body.full_name,"h":hash_password(body.password),"role":body.role}).mappings().one()
    db.commit(); return {**dict(row),"role":body.role,"is_active":True}

@router.patch(f"{v1}/admin/users/{{user_id}}/role")
def change_role(user_id:UUID,body:RoleUpdate,user=Admin,db:Session=Depends(get_db)):
    if body.role=="admin": raise HTTPException(409,detail={"code":"ADMIN_ROLE_RESERVED","message":"The administrator role cannot be assigned to another account"})
    if str(user_id)==str(user["id"]): raise HTTPException(409,detail={"code":"SELF_ROLE_CHANGE","message":"Administrators cannot change their own role"})
    result=db.execute(text("UPDATE users SET role_id=(SELECT id FROM roles WHERE name=:role),updated_at=now() WHERE id=:id RETURNING id"),{"role":body.role,"id":user_id})
    if not result.first(): raise HTTPException(404,detail={"code":"USER_NOT_FOUND","message":"User not found"})
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user_id}); db.commit()
    return {"id":str(user_id),"role":body.role}

@router.patch(f"{v1}/admin/users/{{user_id}}/status")
def set_user_status(user_id:UUID,is_active:bool,user=Admin,db:Session=Depends(get_db)):
    if str(user_id)==str(user["id"]) and not is_active: raise HTTPException(409,detail={"code":"SELF_DEACTIVATION","message":"Administrators cannot deactivate their own account"})
    row=db.execute(text("UPDATE users SET is_active=:active,updated_at=now() WHERE id=:id RETURNING id,is_active"),{"active":is_active,"id":user_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"USER_NOT_FOUND","message":"User not found"})
    if not is_active: db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE user_id=:id"),{"id":user_id})
    db.commit(); return {"id":str(row["id"]),"is_active":row["is_active"]}

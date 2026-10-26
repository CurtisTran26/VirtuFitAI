from app.routers.common import *
from app.schemas.auth import Login

router = APIRouter()

@router.post(f"{v1}/auth/staff-login")
def staff_login(body:Login,db:Session=Depends(get_db)):
    row=db.execute(text("SELECT u.id,u.phone,u.full_name,u.password_hash,u.is_active,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.phone=:account"),{"account":body.account}).mappings().first()
    if not row or not row["is_active"] or row["role"]=="customer" or not verify_password(body.password,row["password_hash"]):
        raise HTTPException(401,detail={"code":"INVALID_CREDENTIALS","message":"Staff credentials are incorrect"})
    result=issue_session(db,row["id"]); db.commit()
    return {"user":{"id":str(row["id"]),"phone":row["phone"],"full_name":row["full_name"],"role":row["role"]},**result}

@router.post(f"{v1}/auth/logout",status_code=204)
def logout(request:Request,user=Depends(current_user),db:Session=Depends(get_db)):
    token=request.headers.get("authorization", "").removeprefix("Bearer ")
    db.execute(text("UPDATE user_sessions SET revoked_at=now() WHERE token_hash=:hash AND revoked_at IS NULL"),{"hash":hashlib.sha256(token.encode()).hexdigest()}); db.commit()
    return Response(status_code=204)


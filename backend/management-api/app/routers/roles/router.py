from app.routers.common import *

router = APIRouter()

@router.get(f"{v1}/admin/roles")
def roles(user=Admin,db:Session=Depends(get_db)):
    return {"items":[dict(x) for x in db.execute(text("SELECT name,description FROM roles ORDER BY name")).mappings().all()]}

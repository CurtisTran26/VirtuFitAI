from app.routers.common import *

router = APIRouter()

@router.get(f"{v1}/categories")
def list_categories(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,name,description,is_active,created_at FROM categories ORDER BY name LIMIT :l OFFSET :o"),{"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM categories")).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@router.post(f"{v1}/categories",status_code=201)
def create_category(body:CategoryIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO categories(name,description,is_active) VALUES(:n,:d,:a) RETURNING id,name,description,is_active,created_at"),{"n":body.name,"d":body.description,"a":body.is_active}).mappings().one(); db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"CATEGORY_CONFLICT","message":"Category name already exists"}) from exc

@router.patch(f"{v1}/categories/{{category_id}}")
def update_category(category_id:UUID,body:CategoryIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("UPDATE categories SET name=:n,description=:d,is_active=:a WHERE id=:id RETURNING id,name,description,is_active,created_at"),{"n":body.name,"d":body.description,"a":body.is_active,"id":category_id}).mappings().first()
        if not row: raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
        db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"CATEGORY_CONFLICT","message":"Category name already exists"}) from exc

@router.delete(f"{v1}/categories/{{category_id}}",status_code=204)
def archive_category(category_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("UPDATE categories SET is_active=false WHERE id=:id"),{"id":category_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    db.commit(); return Response(status_code=204)

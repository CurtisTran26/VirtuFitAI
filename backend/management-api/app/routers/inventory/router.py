from app.routers.common import *
from app.schemas.inventory import AdjustIn

router = APIRouter()

@router.post(f"{v1}/inventory/variants/{{variant_id}}/adjustments",status_code=201)
def adjust_stock(variant_id:UUID,body:AdjustIn,user=Warehouse,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("SELECT stock_on_hand,reserved_quantity FROM product_variants WHERE id=:id FOR UPDATE"),{"id":variant_id}).mappings().first()
        if not row: raise HTTPException(404,detail={"code":"VARIANT_NOT_FOUND","message":"Variant not found"})
        before=row["stock_on_hand"]; after=before+body.delta
        if after<0: raise HTTPException(409,detail={"code":"OUT_OF_STOCK","message":"Adjustment would make stock negative"})
        if after<row["reserved_quantity"]: raise HTTPException(409,detail={"code":"STOCK_RESERVED","message":"Adjustment would reduce on-hand stock below active reservations"})
        db.execute(text("UPDATE product_variants SET stock_on_hand=:q,updated_at=now() WHERE id=:id"),{"q":after,"id":variant_id})
        record=db.execute(text("INSERT INTO inventory_adjustments(variant_id,changed_by,delta,quantity_before,quantity_after,reason) VALUES(:v,:u,:d,:b,:a,:r) RETURNING id,variant_id,changed_by,delta,quantity_before,quantity_after,reason,created_at"),{"v":variant_id,"u":user["id"],"d":body.delta,"b":before,"a":after,"r":body.reason}).mappings().one()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(record)

@router.get(f"{v1}/inventory/variants/{{variant_id}}/adjustments")
def inventory_history(variant_id:UUID,page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Warehouse,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,variant_id,changed_by,delta,quantity_before,quantity_after,reason,created_at FROM inventory_adjustments WHERE variant_id=:v ORDER BY created_at DESC LIMIT :l OFFSET :o"),{"v":variant_id,"l":limit,"o":(page-1)*limit}).mappings().all()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit}

@router.get(f"{v1}/inventory/variants")
def list_inventory(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),user=Warehouse,db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT v.id variant_id,v.product_id,p.name product_name,v.sku,v.size,v.color,v.stock_on_hand,v.updated_at FROM product_variants v JOIN products p ON p.id=v.product_id ORDER BY p.name,v.size,v.color LIMIT :l OFFSET :o"),{"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM product_variants")).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

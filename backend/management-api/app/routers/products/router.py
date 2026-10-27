from app.routers.common import *

router = APIRouter()

@router.get(f"{v1}/products")
def list_products(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),category_id:UUID|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at FROM products p JOIN categories c ON c.id=p.category_id WHERE (CAST(:c AS uuid) IS NULL OR p.category_id=:c) ORDER BY p.created_at DESC LIMIT :l OFFSET :o"),{"c":category_id,"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM products WHERE (CAST(:c AS uuid) IS NULL OR category_id=:c)"),{"c":category_id}).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}

@router.get(f"{v1}/products/{{product_id}}")
def get_product(product_id:UUID,user=Depends(current_user),db:Session=Depends(get_db)):
    row=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at FROM products p JOIN categories c ON c.id=p.category_id WHERE p.id=:id"),{"id":product_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    return dict(row)

@router.post(f"{v1}/products",status_code=201)
def create_product(body:ProductIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO products(category_id,name,description,price_vnd,sku,image_url,is_active) VALUES(:c,:n,:d,:price,:sku,:img,:active) RETURNING id,category_id,name,description,price_vnd,sku,image_url,is_active,created_at"),{"c":body.category_id,"n":body.name,"d":body.description,"price":body.price_vnd,"sku":body.sku,"img":body.image_url,"active":body.is_active}).mappings().one(); db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"PRODUCT_CONFLICT","message":"Invalid category or duplicate SKU"}) from exc

@router.patch(f"{v1}/products/{{product_id}}")
def update_product(product_id:UUID,body:ProductIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("UPDATE products SET category_id=:c,name=:n,description=:d,price_vnd=:price,sku=:sku,image_url=:img,is_active=:active,updated_at=now() WHERE id=:id RETURNING id,category_id,name,description,price_vnd,sku,image_url,is_active,created_at"),{"c":body.category_id,"n":body.name,"d":body.description,"price":body.price_vnd,"sku":body.sku,"img":body.image_url,"active":body.is_active,"id":product_id}).mappings().first()
        if not row: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
        db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"PRODUCT_CONFLICT","message":"Invalid category or duplicate SKU"}) from exc

@router.delete(f"{v1}/products/{{product_id}}",status_code=204)
def archive_product(product_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("UPDATE products SET is_active=false,updated_at=now() WHERE id=:id"),{"id":product_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    db.commit(); return Response(status_code=204)

@router.get(f"{v1}/size-charts")
def list_size_charts(category_id:UUID|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,category_id,name,measurements,created_at FROM size_charts WHERE (CAST(:c AS uuid) IS NULL OR category_id=:c) ORDER BY name"),{"c":category_id}).mappings().all()
    return {"items":[dict(x) for x in rows]}

@router.post(f"{v1}/size-charts",status_code=201)
def create_size_chart(body:SizeChartIn,user=CatalogEditor,db:Session=Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM categories WHERE id=:id"),{"id":body.category_id}).first():
        raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    row=db.execute(text("INSERT INTO size_charts(category_id,name,measurements) VALUES(:c,:n,CAST(:m AS jsonb)) RETURNING id,category_id,name,measurements,created_at"),{"c":body.category_id,"n":body.name,"m":__import__('json').dumps(body.measurements)}).mappings().first()
    db.commit(); return dict(row)

@router.put(f"{v1}/size-charts/{{chart_id}}")
def update_size_chart(chart_id:UUID,body:SizeChartIn,user=CatalogEditor,db:Session=Depends(get_db)):
    if not db.execute(text("SELECT 1 FROM categories WHERE id=:id"),{"id":body.category_id}).first():
        raise HTTPException(404,detail={"code":"CATEGORY_NOT_FOUND","message":"Category not found"})
    row=db.execute(text("UPDATE size_charts SET category_id=:c,name=:n,measurements=CAST(:m AS jsonb) WHERE id=:id RETURNING id,category_id,name,measurements,created_at"),{"c":body.category_id,"n":body.name,"m":__import__('json').dumps(body.measurements),"id":chart_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"SIZE_CHART_NOT_FOUND","message":"Size chart not found"})
    db.commit(); return dict(row)

@router.delete(f"{v1}/size-charts/{{chart_id}}",status_code=204)
def delete_size_chart(chart_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("DELETE FROM size_charts WHERE id=:id"),{"id":chart_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"SIZE_CHART_NOT_FOUND","message":"Size chart not found"})
    db.commit(); return Response(status_code=204)

@router.post(f"{v1}/products/{{product_id}}/variants",status_code=201)
def create_variant(product_id:UUID,body:VariantIn,user=CatalogEditor,db:Session=Depends(get_db)):
    if product_id!=body.product_id: raise HTTPException(400,detail={"code":"PRODUCT_MISMATCH","message":"Path and body product IDs differ"})
    try:
        row=db.execute(text("INSERT INTO product_variants(product_id,size,color,sku) VALUES(:p,:s,:c,:sku) RETURNING id,product_id,size,color,sku,stock_on_hand"),{"p":product_id,"s":body.size,"c":body.color,"sku":body.sku}).mappings().one(); db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"VARIANT_CONFLICT","message":"Invalid product or duplicate variant/SKU"}) from exc

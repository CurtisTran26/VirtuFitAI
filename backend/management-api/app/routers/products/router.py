import io
import os
from uuid import UUID

import boto3
import qrcode
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.routers.common import *
from app.schemas.products import ColorOptionIn, ProductIn, SizeChartIn, SizeOptionIn, VariantIn

router = APIRouter()


@router.get(f"{v1}/catalog-options")
def list_catalog_options(user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT id,option_type,name,hex_color,created_at FROM catalog_options ORDER BY option_type,name")).mappings().all()
    options={"colors":[],"sizes":[]}
    for row in rows:
        item={"id":row["id"],"name":row["name"]}
        if row["option_type"]=="color":
            item["hex_color"]=row["hex_color"]
            options["colors"].append(item)
        else:
            options["sizes"].append(item)
    return options


@router.post(f"{v1}/catalog-options/colors",status_code=201)
def create_color_option(body:ColorOptionIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO catalog_options(option_type,name,hex_color) VALUES('color',:name,:hex) RETURNING id,name,hex_color"),{"name":body.name.strip(),"hex":body.hex_color}).mappings().one()
        db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"COLOR_EXISTS","message":"Color already exists"}) from exc


@router.delete(f"{v1}/catalog-options/colors/{{option_id}}",status_code=204)
def delete_color_option(option_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("DELETE FROM catalog_options WHERE id=:id AND option_type='color'"),{"id":option_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"COLOR_NOT_FOUND","message":"Color not found"})
    db.commit(); return Response(status_code=204)


@router.post(f"{v1}/catalog-options/sizes",status_code=201)
def create_size_option(body:SizeOptionIn,user=CatalogEditor,db:Session=Depends(get_db)):
    try:
        row=db.execute(text("INSERT INTO catalog_options(option_type,name) VALUES('size',:name) RETURNING id,name"),{"name":body.name.strip()}).mappings().one()
        db.commit(); return dict(row)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,detail={"code":"SIZE_EXISTS","message":"Size already exists"}) from exc


@router.delete(f"{v1}/catalog-options/sizes/{{option_id}}",status_code=204)
def delete_size_option(option_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    result=db.execute(text("DELETE FROM catalog_options WHERE id=:id AND option_type='size'"),{"id":option_id})
    if not result.rowcount: raise HTTPException(404,detail={"code":"SIZE_NOT_FOUND","message":"Size not found"})
    db.commit(); return Response(status_code=204)

@router.get(f"{v1}/products")
def list_products(page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),category_id:UUID|None=None,user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at,q.qr_data,q.qr_image_url FROM products p JOIN categories c ON c.id=p.category_id LEFT JOIN product_qr_codes q ON q.product_id=p.id AND q.is_active=true WHERE (CAST(:c AS uuid) IS NULL OR p.category_id=:c) ORDER BY p.created_at DESC LIMIT :l OFFSET :o"),{"c":category_id,"l":limit,"o":(page-1)*limit}).mappings().all()
    total=db.execute(text("SELECT count(*) FROM products WHERE (CAST(:c AS uuid) IS NULL OR category_id=:c)"),{"c":category_id}).scalar_one()
    return {"items":[dict(x) for x in rows],"page":page,"limit":limit,"total":total}


@router.post(f"{v1}/admin/products/{{product_id}}/qr")
def create_product_qr(product_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    product=db.execute(text("SELECT id FROM products WHERE id=:id AND is_active=true"),{"id":product_id}).mappings().first()
    if not product:
        raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found or archived"})

    # Keep An's product deep-link format while using the UUID from the current catalog.
    qr_data=f"virtufit://product/{product_id}"
    qr=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=10,border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    image=qr.make_image(fill_color="black",back_color="white")
    buffer=io.BytesIO()
    image.save(buffer,format="PNG")

    endpoint=os.getenv("STORAGE_ENDPOINT","http://minio:9000")
    public_endpoint=os.getenv("STORAGE_PUBLIC_ENDPOINT","http://localhost:9000").rstrip("/")
    bucket=os.getenv("STORAGE_PUBLIC_BUCKET","virtufit-public")
    object_key=f"qr-codes/{product_id}.png"
    storage=boto3.client("s3",endpoint_url=endpoint,aws_access_key_id=os.getenv("STORAGE_ACCESS_KEY","minioadmin"),aws_secret_access_key=os.getenv("STORAGE_SECRET_KEY","minioadmin"),region_name=os.getenv("STORAGE_REGION","us-east-1"),config=Config(signature_version="s3v4"))
    try:
        storage.put_object(Bucket=bucket,Key=object_key,Body=buffer.getvalue(),ContentType="image/png")
    except (BotoCoreError,ClientError) as exc:
        raise HTTPException(502,detail={"code":"QR_STORAGE_FAILED","message":"Không thể lưu ảnh QR lên Cloud Storage"}) from exc

    image_url=f"{public_endpoint}/{bucket}/{object_key}"
    row=db.execute(text("""INSERT INTO product_qr_codes(product_id,qr_data,qr_image_url,is_active)
        VALUES(:product,:data,:url,true)
        ON CONFLICT(product_id) DO UPDATE SET qr_data=EXCLUDED.qr_data,qr_image_url=EXCLUDED.qr_image_url,is_active=true,created_at=now()
        RETURNING id,product_id,qr_data,qr_image_url,is_active,created_at"""),{"product":product_id,"data":qr_data,"url":image_url}).mappings().one()
    db.commit()
    return dict(row)

@router.get(f"{v1}/products/{{product_id}}")
def get_product(product_id:UUID,user=Depends(current_user),db:Session=Depends(get_db)):
    row=db.execute(text("SELECT p.id,p.category_id,c.name category_name,p.name,p.description,p.price_vnd,p.sku,p.image_url,p.is_active,p.created_at FROM products p JOIN categories c ON c.id=p.category_id WHERE p.id=:id"),{"id":product_id}).mappings().first()
    if not row: raise HTTPException(404,detail={"code":"PRODUCT_NOT_FOUND","message":"Product not found"})
    variants=db.execute(text("SELECT id,size,color,sku,stock_on_hand FROM product_variants WHERE product_id=:id ORDER BY size,color"),{"id":product_id}).mappings().all()
    return {**dict(row),"variants":[dict(variant) for variant in variants]}

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


@router.delete(f"{v1}/products/{{product_id}}/variants/{{variant_id}}",status_code=204)
def delete_variant(product_id:UUID,variant_id:UUID,user=CatalogEditor,db:Session=Depends(get_db)):
    variant=db.execute(text("SELECT id,stock_on_hand FROM product_variants WHERE id=:variant AND product_id=:product FOR UPDATE"),{"variant":variant_id,"product":product_id}).mappings().first()
    if not variant:
        raise HTTPException(404,detail={"code":"VARIANT_NOT_FOUND","message":"Variant not found"})
    if variant["stock_on_hand"] != 0:
        raise HTTPException(409,detail={"code":"VARIANT_HAS_STOCK","message":"Cannot remove a variant with stock"})
    references=db.execute(text("""SELECT
        EXISTS(SELECT 1 FROM inventory_adjustments WHERE variant_id=:id)
        OR EXISTS(SELECT 1 FROM inventory_reservations WHERE variant_id=:id)
        OR EXISTS(SELECT 1 FROM order_items WHERE variant_id=:id) AS in_use"""),{"id":variant_id}).scalar_one()
    if references:
        raise HTTPException(409,detail={"code":"VARIANT_IN_USE","message":"Variant has inventory history or order references"})
    db.execute(text("DELETE FROM product_variants WHERE id=:id"),{"id":variant_id})
    db.commit()

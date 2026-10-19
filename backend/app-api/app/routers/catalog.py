from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product, SizeChart
from app.schemas import CategoryIn, CategoryOut, ProductIn, ProductOut, SizeChartIn, SizeChartOut
from app.security import require_roles

router = APIRouter(prefix="/api", tags=["Catalog"])
EDITORS = ("staff", "manager", "admin")


def commit_or_conflict(db: Session, detail: str = "A unique value already exists") -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, detail) from exc


@router.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return db.query(Product).offset(max(skip, 0)).limit(min(max(limit, 1), 200)).all()


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(409, "SKU already exists")
    if payload.category_id is not None and not db.get(Category, payload.category_id):
        raise HTTPException(404, "Category not found")
    product = Product(**payload.model_dump())
    db.add(product)
    commit_or_conflict(db, "SKU already exists")
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if payload.category_id is not None and not db.get(Category, payload.category_id):
        raise HTTPException(404, "Category not found")
    if db.query(Product).filter(Product.sku == payload.sku, Product.id != product_id).first():
        raise HTTPException(409, "SKU already exists")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    commit_or_conflict(db, "SKU already exists")
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_roles("manager", "admin"))):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Product has inventory adjustment history and cannot be deleted") from exc
    return Response(status_code=204)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    row = Category(**payload.model_dump())
    db.add(row)
    commit_or_conflict(db, "Category name already exists")
    db.refresh(row)
    return row


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    row = db.get(Category, category_id)
    if not row:
        raise HTTPException(404, "Category not found")
    row.name, row.description = payload.name, payload.description
    commit_or_conflict(db, "Category name already exists")
    db.refresh(row)
    return row


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), _=Depends(require_roles("manager", "admin"))):
    row = db.get(Category, category_id)
    if not row:
        raise HTTPException(404, "Category not found")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/size-charts", response_model=list[SizeChartOut])
def list_size_charts(db: Session = Depends(get_db)):
    return db.query(SizeChart).all()


@router.post("/size-charts", response_model=SizeChartOut, status_code=201)
def create_size_chart(payload: SizeChartIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    row = SizeChart(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/size-charts/{chart_id}", response_model=SizeChartOut)
def update_size_chart(chart_id: int, payload: SizeChartIn, db: Session = Depends(get_db), _=Depends(require_roles(*EDITORS))):
    row = db.get(SizeChart, chart_id)
    if not row:
        raise HTTPException(404, "Size chart not found")
    row.name, row.measurements = payload.name, payload.measurements
    db.commit()
    db.refresh(row)
    return row


@router.delete("/size-charts/{chart_id}", status_code=204)
def delete_size_chart(chart_id: int, db: Session = Depends(get_db), _=Depends(require_roles("manager", "admin"))):
    row = db.get(SizeChart, chart_id)
    if not row:
        raise HTTPException(404, "Size chart not found")
    db.delete(row)
    db.commit()
    return Response(status_code=204)

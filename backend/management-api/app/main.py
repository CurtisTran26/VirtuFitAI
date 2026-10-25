from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.routers.auth.router import router as auth_router
from app.routers.roles.router import router as roles_router
from app.routers.users.router import router as users_router
from app.routers.categories.router import router as categories_router
from app.routers.products.router import router as products_router
from app.routers.inventory.router import router as inventory_router
from app.routers.orders.router import router as orders_router
from app.routers.sales.router import router as sales_router
from app.routers.returns.router import router as returns_router

app = FastAPI(title="VirtuFit Management API", version="1.0.0", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
origins = [v.strip() for v in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if v.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    detail = exc.detail if isinstance(exc.detail, dict) else {"code": "HTTP_ERROR", "message": str(exc.detail)}
    if "code" not in detail: detail = {"code": "HTTP_ERROR", "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": detail}, headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": jsonable_encoder(exc.errors())}})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred", "details": {}}})

@app.get("/api/v1/health")
def health(): return {"status": "ok"}

for route_group in (auth_router, roles_router, users_router, categories_router, products_router, inventory_router, orders_router, sales_router, returns_router):
    app.include_router(route_group)

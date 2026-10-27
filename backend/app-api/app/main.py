from __future__ import annotations
# Load integration settings before importing API modules.
from app import config
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from shared_platform import get_db
from app.routers.auth.router import router as auth_router
from app.routers.wishlist.router import router as wishlist_router
from app.routers.profiles.router import router as profiles_router
from app.routers.catalog.router import router as catalog_router
from app.routers.qr.router import router as qr_router

app = FastAPI(title="VirtuFit App API", version="1.0.0", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
origins = [v.strip() for v in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if v.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
v1 = "/api/v1"

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    from fastapi.responses import JSONResponse
    detail=exc.detail if isinstance(exc.detail,dict) else {"code":"HTTP_ERROR","message":str(exc.detail)}
    if "code" not in detail: detail={"code":"HTTP_ERROR","message":str(detail)}
    return JSONResponse(status_code=exc.status_code,content={"error":detail},headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder
    return JSONResponse(status_code=422,content={"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":[{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}})


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An internal error occurred","details":{}}})


@app.get(f'{v1}/health')
def health(db:Session=Depends(get_db)):
    db.execute(text('SELECT 1')); return {'status':'ok','integration_version':'twilio-verify-20261023'}


for route_group in (auth_router, wishlist_router, profiles_router, catalog_router, qr_router):
    app.include_router(route_group)

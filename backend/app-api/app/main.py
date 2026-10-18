"""
Entrypoint chính cho FastAPI App API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.media import router as media_router
from app.routers.catalog import router as catalog_router
from app.routers.qr_scan import router as qr_router
from app.routers.profiles import router as profile_router
from app.routers.auth import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API phục vụ cho Mobile Customer & Sales Staff (VirtuFit AI).",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# Cấu hình CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Routers
app.include_router(health_router)
app.include_router(media_router)
app.include_router(catalog_router)
app.include_router(qr_router)
app.include_router(profile_router)
app.include_router(auth_router)







@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health"
    }

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.settings import settings

from app.routers import accounts, admin, catalog, inventory, password, phone_login, sessions, staff_login, wishlist

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if len(settings.jwt_secret) < 32 or settings.jwt_secret in {
        "change-this-secret-before-deploying",
        "replace-with-a-long-random-secret",
    }:
        raise RuntimeError("Set JWT_SECRET to a unique random value of at least 32 characters before starting the API.")
    yield


app = FastAPI(title="Capstone Store API", version="1.0.0", lifespan=lifespan)
for module in (accounts, phone_login, staff_login, password, sessions, catalog, admin, inventory, wishlist):
    app.include_router(module.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
def readiness(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready", "database": "ok"}

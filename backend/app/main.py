"""
Google Maps İşletme Keşif Platformu - Backend
FastAPI tabanlı REST API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import search, businesses, exports
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü yönetimi"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="İşletme Keşif Platformu",
    description="Google Maps üzerinden işletme verilerini toplayan ve yöneten platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(search.router, prefix="/api/search", tags=["Arama"])
app.include_router(businesses.router, prefix="/api/businesses", tags=["İşletmeler"])
app.include_router(exports.router, prefix="/api/exports", tags=["Dışa Aktarım"])


@app.get("/")
async def root():
    return {
        "message": "İşletme Keşif Platformu API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

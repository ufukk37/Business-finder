"""
Uygulama Konfigürasyonu
Ortam değişkenlerinden ayarları yükler
"""

from typing import List
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Settings:
    """Uygulama ayarları"""
    
    # Uygulama
    APP_NAME: str = "İşletme Keşif Platformu"
    DEBUG: bool = True
    
    # Veritabanı - SQLite (Docker gerektirmez)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./business_finder.db")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Arama Ayarları
    DEFAULT_SEARCH_RADIUS: int = int(os.getenv("DEFAULT_SEARCH_RADIUS", "5000"))
    MAX_SEARCH_RADIUS: int = int(os.getenv("MAX_SEARCH_RADIUS", "50000"))
    MAX_RESULTS_PER_SEARCH: int = int(os.getenv("MAX_RESULTS_PER_SEARCH", "100"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    
    # Önbellek
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))


settings = Settings()

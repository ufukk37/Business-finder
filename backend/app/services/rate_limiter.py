"""
Rate Limiter Servisi
API isteklerini sınırlandırır
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket algoritması ile rate limiting
    """
    
    def __init__(
        self,
        max_requests: int = None,
        window_seconds: int = None
    ):
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str = "global") -> bool:
        """
        İsteğin izin verilip verilmediğini kontrol et
        """
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Eski istekleri temizle
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            # Limit kontrolü
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Yeni isteği kaydet
            self.requests[key].append(now)
            return True
    
    async def wait_if_needed(self, key: str = "global") -> float:
        """
        Gerekirse bekle ve bekleme süresini döndür
        """
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Eski istekleri temizle
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
            
            if len(self.requests[key]) >= self.max_requests:
                # En eski isteğin süresinin dolmasını bekle
                oldest = min(self.requests[key])
                wait_time = (oldest + timedelta(seconds=self.window_seconds) - now).total_seconds()
                
                if wait_time > 0:
                    logger.info(f"Rate limit: {wait_time:.2f} saniye bekleniyor")
                    await asyncio.sleep(wait_time)
                    return wait_time
            
            # İsteği kaydet
            self.requests[key].append(now)
            return 0
    
    def get_remaining(self, key: str = "global") -> int:
        """
        Kalan istek sayısını döndür
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        current_requests = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(current_requests))
    
    def get_reset_time(self, key: str = "global") -> Optional[datetime]:
        """
        Rate limit reset zamanını döndür
        """
        if not self.requests[key]:
            return None
        
        oldest = min(self.requests[key])
        return oldest + timedelta(seconds=self.window_seconds)


class GooglePlacesRateLimiter(RateLimiter):
    """
    Google Places API için özelleştirilmiş rate limiter
    
    Google Places API limitleri:
    - Nearby Search: 1000 istek/gün (ücretsiz)
    - Place Details: 1000 istek/gün (ücretsiz)
    """
    
    def __init__(self):
        # Dakikada 10 istek (güvenli limit)
        super().__init__(max_requests=10, window_seconds=60)
        
        # Günlük limit takibi
        self.daily_counts: Dict[str, int] = defaultdict(int)
        self.daily_reset: Optional[datetime] = None
        self._daily_lock = asyncio.Lock()
    
    async def track_daily(self, api_type: str = "search") -> bool:
        """
        Günlük kullanımı takip et
        """
        async with self._daily_lock:
            now = datetime.utcnow()
            
            # Gün değişimi kontrolü
            if self.daily_reset is None or now.date() > self.daily_reset.date():
                self.daily_counts.clear()
                self.daily_reset = now
            
            # Günlük limit (güvenli marj ile)
            daily_limit = 900  # 1000'in altında tutuyoruz
            
            if self.daily_counts[api_type] >= daily_limit:
                logger.warning(f"Günlük {api_type} limiti aşıldı")
                return False
            
            self.daily_counts[api_type] += 1
            return True
    
    def get_daily_usage(self) -> Dict[str, int]:
        """
        Günlük kullanım istatistiklerini döndür
        """
        return dict(self.daily_counts)


# Singleton instances
rate_limiter = RateLimiter()
google_rate_limiter = GooglePlacesRateLimiter()

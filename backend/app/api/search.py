"""
Arama API Endpoint'leri
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import math

from app.core.database import get_db
from app.schemas.business import (
    SearchRequest, SearchResponse, SearchStatus, BusinessSummary, CategoryResponse
)
from app.services.google_places import google_places_service
from app.services.business_service import BusinessService, SearchService
from app.services.rate_limiter import google_rate_limiter
from app.models.business import Category

logger = logging.getLogger(__name__)
router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    İki koordinat arası mesafeyi hesapla (Haversine formülü)
    Sonuç metre cinsinden
    """
    R = 6371000  # Dünya yarıçapı (metre)
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


@router.post("/", response_model=SearchResponse)
async def search_businesses(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletme araması başlat
    
    - **location**: Şehir, ilçe veya adres (ör: "Kadıköy, İstanbul")
    - **business_type**: İşletme türü (ör: "restoran", "kafe", "oto servis")
    - **radius**: Arama yarıçapı metre cinsinden (100-50000)
    - **keyword**: Ek anahtar kelime (opsiyonel)
    """
    
    # Rate limit kontrolü
    if not await google_rate_limiter.is_allowed("search"):
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek. Lütfen biraz bekleyin."
        )
    
    # Günlük limit kontrolü
    if not await google_rate_limiter.track_daily("search"):
        raise HTTPException(
            status_code=429,
            detail="Günlük arama limiti doldu. Yarın tekrar deneyin."
        )
    
    # Koordinatları al veya geocode yap
    latitude = request.latitude
    longitude = request.longitude
    
    if latitude is None or longitude is None:
        coords = await google_places_service.geocode_location(request.location)
        if coords is None:
            raise HTTPException(
                status_code=400,
                detail=f"'{request.location}' konumu bulunamadı. Lütfen geçerli bir adres girin."
            )
        latitude, longitude = coords
    
    # Arama sorgusunu kaydet
    search_service = SearchService(db)
    search_query = await search_service.create_search_query(request, latitude, longitude)
    
    try:
        # Google Places'tan sonuçları al
        places = await google_places_service.search_all_pages(
            latitude=latitude,
            longitude=longitude,
            radius=request.radius,
            business_type=request.business_type,
            keyword=request.keyword
        )
        
        if not places:
            await search_service.update_search_results(
                search_query, 0, 0, "completed"
            )
            return SearchResponse(
                search_id=search_query.id,
                status=SearchStatus.COMPLETED,
                message="Arama tamamlandı, sonuç bulunamadı.",
                results_count=0,
                new_count=0,
                businesses=[]
            )
        
        # İşletmeleri veritabanına kaydet
        business_service = BusinessService(db)
        businesses_data = []
        
        for place in places:
            # OSM verisi zaten tam, detay çağrısı gerek yok
            business_data = google_places_service.parse_place_to_business(place)
            businesses_data.append(business_data)
        
        # Toplu upsert
        total_count, new_count = await business_service.bulk_upsert(businesses_data)
        
        # Sonuçları arama ile ilişkilendir
        for bdata in businesses_data:
            existing = await business_service.get_by_place_id(bdata["place_id"])
            if existing:
                distance = calculate_distance(
                    latitude, longitude,
                    existing.latitude, existing.longitude
                )
                await search_service.link_business_to_search(
                    search_query.id, existing.id, distance
                )
        
        # Arama sonucunu güncelle
        await search_service.update_search_results(
            search_query, total_count, new_count, "completed"
        )
        
        # Sonuç listesi oluştur
        result_businesses = []
        for bdata in businesses_data[:20]:  # İlk 20 sonuç
            existing = await business_service.get_by_place_id(bdata["place_id"])
            if existing:
                result_businesses.append(BusinessSummary(
                    id=existing.id,
                    place_id=existing.place_id,
                    name=existing.name,
                    category=existing.category,
                    address=existing.address,
                    city=existing.city,
                    phone=existing.phone,
                    website=existing.website,
                    rating=existing.rating,
                    rating_count=existing.rating_count or 0,
                    latitude=existing.latitude,
                    longitude=existing.longitude,
                    google_maps_url=existing.google_maps_url
                ))
        
        return SearchResponse(
            search_id=search_query.id,
            status=SearchStatus.COMPLETED,
            message=f"Arama tamamlandı. {total_count} işletme bulundu, {new_count} yeni eklendi.",
            results_count=total_count,
            new_count=new_count,
            businesses=result_businesses
        )
        
    except Exception as e:
        logger.error(f"Arama hatası: {e}")
        await search_service.update_search_results(
            search_query, 0, 0, "failed", str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Arama sırasında hata oluştu: {str(e)}"
        )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Mevcut kategorileri listele
    """
    # Varsayılan kategoriler
    default_categories = [
        {"name": "restaurant", "name_tr": "Restoran", "icon": "🍽️", "google_type": "restaurant"},
        {"name": "cafe", "name_tr": "Kafe", "icon": "☕", "google_type": "cafe"},
        {"name": "hotel", "name_tr": "Otel", "icon": "🏨", "google_type": "lodging"},
        {"name": "hospital", "name_tr": "Hastane", "icon": "🏥", "google_type": "hospital"},
        {"name": "pharmacy", "name_tr": "Eczane", "icon": "💊", "google_type": "pharmacy"},
        {"name": "bank", "name_tr": "Banka", "icon": "🏦", "google_type": "bank"},
        {"name": "supermarket", "name_tr": "Market", "icon": "🛒", "google_type": "supermarket"},
        {"name": "gym", "name_tr": "Spor Salonu", "icon": "💪", "google_type": "gym"},
        {"name": "dentist", "name_tr": "Diş Kliniği", "icon": "🦷", "google_type": "dentist"},
        {"name": "car_repair", "name_tr": "Oto Servis", "icon": "🔧", "google_type": "car_repair"},
        {"name": "beauty_salon", "name_tr": "Güzellik Salonu", "icon": "💅", "google_type": "beauty_salon"},
        {"name": "hair_care", "name_tr": "Kuaför", "icon": "💇", "google_type": "hair_care"},
        {"name": "lawyer", "name_tr": "Avukat", "icon": "⚖️", "google_type": "lawyer"},
        {"name": "real_estate", "name_tr": "Emlak", "icon": "🏠", "google_type": "real_estate_agency"},
        {"name": "veterinary", "name_tr": "Veteriner", "icon": "🐾", "google_type": "veterinary_care"},
    ]
    
    return [
        CategoryResponse(
            id=cat["name"],
            name=cat["name"],
            name_tr=cat["name_tr"],
            google_type=cat["google_type"],
            icon=cat["icon"]
        )
        for cat in default_categories
    ]


@router.get("/history")
async def get_search_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Arama geçmişini getir
    """
    search_service = SearchService(db)
    history = await search_service.get_search_history(limit)
    
    return [
        {
            "id": h.id,
            "location": h.location_query,
            "business_type": h.business_type,
            "radius": h.radius,
            "results_count": h.results_count,
            "new_count": h.new_businesses_count,
            "status": h.status,
            "created_at": h.created_at.isoformat() if h.created_at else None,
            "completed_at": h.completed_at.isoformat() if h.completed_at else None
        }
        for h in history
    ]


@router.get("/rate-limit-status")
async def get_rate_limit_status():
    """
    Rate limit durumunu göster
    """
    return {
        "remaining_requests": google_rate_limiter.get_remaining("search"),
        "daily_usage": google_rate_limiter.get_daily_usage(),
        "reset_time": google_rate_limiter.get_reset_time("search")
    }

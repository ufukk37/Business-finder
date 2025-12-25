"""
Pydantic Şemaları
API request/response modelleri
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============ Enum'lar ============

class SearchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============ Arama Şemaları ============

class SearchRequest(BaseModel):
    """Arama isteği"""
    location: str = Field(..., min_length=2, max_length=500, description="Şehir, ilçe veya adres")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    business_type: str = Field(..., min_length=2, max_length=100, description="İşletme türü")
    radius: int = Field(5000, ge=100, le=50000, description="Arama yarıçapı (metre)")
    keyword: Optional[str] = Field(None, max_length=100, description="Ek anahtar kelime")
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Kadıköy, İstanbul",
                "business_type": "restoran",
                "radius": 3000,
                "keyword": "deniz ürünleri"
            }
        }


class SearchResponse(BaseModel):
    """Arama yanıtı"""
    search_id: str
    status: SearchStatus
    message: str
    results_count: int = 0
    new_count: int = 0
    businesses: List["BusinessSummary"] = []


# ============ İşletme Şemaları ============

class BusinessBase(BaseModel):
    """İşletme temel bilgileri"""
    name: str
    category: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None


class BusinessSummary(BaseModel):
    """İşletme özet bilgisi (liste görünümü)"""
    id: str
    place_id: str
    name: str
    category: Optional[str]
    address: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    rating_count: int = 0
    latitude: float
    longitude: float
    google_maps_url: Optional[str]
    
    class Config:
        from_attributes = True


class BusinessDetail(BusinessSummary):
    """İşletme detaylı bilgisi"""
    formatted_phone: Optional[str]
    district: Optional[str]
    postal_code: Optional[str]
    types: Optional[List[str]] = []
    is_open_now: Optional[bool]
    opening_hours: Optional[List[str]] = []
    photos: Optional[List[str]] = []
    tags: List[str] = []
    notes: List["NoteResponse"] = []
    created_at: datetime
    updated_at: Optional[datetime]
    last_fetched_at: datetime
    
    class Config:
        from_attributes = True


class BusinessUpdate(BaseModel):
    """İşletme güncelleme"""
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


# ============ Filtre Şemaları ============

class BusinessFilter(BaseModel):
    """İşletme filtreleme"""
    city: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_rating: Optional[float] = Field(None, ge=0, le=5)
    min_reviews: Optional[int] = Field(None, ge=0)
    has_phone: Optional[bool] = None
    has_website: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=100, description="İsim araması")
    tags: Optional[List[str]] = None
    
    # Sayfalama
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=10000)
    
    # Sıralama
    sort_by: str = Field("rating", pattern="^(name|rating|rating_count|created_at)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class BusinessListResponse(BaseModel):
    """İşletme listesi yanıtı"""
    businesses: List[BusinessSummary]
    total: int
    page: int
    per_page: int
    total_pages: int


# ============ Etiket ve Not Şemaları ============

class TagCreate(BaseModel):
    """Etiket oluşturma"""
    tag: str = Field(..., min_length=1, max_length=100)


class NoteCreate(BaseModel):
    """Not oluşturma"""
    note: str = Field(..., min_length=1, max_length=2000)


class NoteResponse(BaseModel):
    """Not yanıtı"""
    id: str
    note: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ Dışa Aktarım Şemaları ============

class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"


class ExportRequest(BaseModel):
    """Dışa aktarım isteği"""
    format: ExportFormat = ExportFormat.EXCEL
    filters: Optional[BusinessFilter] = None
    include_fields: Optional[List[str]] = None


class ExportResponse(BaseModel):
    """Dışa aktarım yanıtı"""
    filename: str
    download_url: str
    record_count: int


# ============ Kategori Şemaları ============

class CategoryResponse(BaseModel):
    """Kategori yanıtı"""
    id: str
    name: str
    name_tr: Optional[str]
    google_type: Optional[str]
    icon: Optional[str]
    
    class Config:
        from_attributes = True


# ============ İstatistik Şemaları ============

class DashboardStats(BaseModel):
    """Dashboard istatistikleri"""
    total_businesses: int
    total_searches: int
    businesses_with_phone: int
    businesses_with_website: int
    average_rating: float
    top_cities: List[dict]
    top_categories: List[dict]
    recent_searches: List[dict]


# Circular import çözümü
BusinessDetail.model_rebuild()
SearchResponse.model_rebuild()

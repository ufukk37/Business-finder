"""
İşletme API Endpoint'leri
CRUD işlemleri ve filtreleme
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import json
import math

from app.core.database import get_db
from app.schemas.business import (
    BusinessSummary, BusinessDetail, BusinessUpdate, BusinessFilter,
    BusinessListResponse, TagCreate, NoteCreate, NoteResponse, DashboardStats
)
from app.services.business_service import BusinessService

router = APIRouter()


@router.get("/", response_model=BusinessListResponse)
async def list_businesses(
    city: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_rating: Optional[float] = Query(None, ge=0, le=5),
    min_reviews: Optional[int] = Query(None, ge=0),
    has_phone: Optional[bool] = None,
    has_website: Optional[bool] = None,
    search: Optional[str] = Query(None, max_length=100),
    tags: Optional[str] = None,  # Virgülle ayrılmış
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("rating", pattern="^(name|rating|rating_count|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    İşletmeleri listele ve filtrele
    
    Filtreleme seçenekleri:
    - **city**: Şehir adı
    - **district**: İlçe adı
    - **category**: Kategori
    - **min_rating** / **max_rating**: Puan aralığı
    - **min_reviews**: Minimum yorum sayısı
    - **has_phone**: Telefon numarası olan/olmayan
    - **has_website**: Web sitesi olan/olmayan
    - **search**: İsim/adres araması
    - **tags**: Etiketler (virgülle ayrılmış)
    """
    
    # Tags'i listeye çevir
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    filters = BusinessFilter(
        city=city,
        district=district,
        category=category,
        min_rating=min_rating,
        max_rating=max_rating,
        min_reviews=min_reviews,
        has_phone=has_phone,
        has_website=has_website,
        search=search,
        tags=tag_list,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    service = BusinessService(db)
    businesses, total = await service.list_businesses(filters)
    
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    
    return BusinessListResponse(
        businesses=[
            BusinessSummary(
                id=b.id,
                place_id=b.place_id,
                name=b.name,
                category=b.category,
                address=b.address,
                city=b.city,
                phone=b.phone,
                website=b.website,
                rating=b.rating,
                rating_count=b.rating_count or 0,
                latitude=b.latitude,
                longitude=b.longitude,
                google_maps_url=b.google_maps_url
            )
            for b in businesses
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Dashboard istatistiklerini getir
    """
    service = BusinessService(db)
    return await service.get_stats()


@router.get("/{business_id}", response_model=BusinessDetail)
async def get_business(
    business_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletme detaylarını getir
    """
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    
    # JSON alanlarını parse et
    types = []
    if business.types:
        try:
            types = json.loads(business.types)
        except:
            pass
    
    opening_hours = []
    if business.opening_hours:
        try:
            opening_hours = json.loads(business.opening_hours)
        except:
            pass
    
    photos = []
    if business.photos:
        try:
            photos = json.loads(business.photos)
        except:
            pass
    
    tags = [t.tag for t in business.tags]
    notes = [
        NoteResponse(
            id=n.id,
            note=n.note,
            created_at=n.created_at,
            updated_at=n.updated_at
        )
        for n in business.notes
    ]
    
    return BusinessDetail(
        id=business.id,
        place_id=business.place_id,
        name=business.name,
        category=business.category,
        address=business.address,
        city=business.city,
        district=business.district,
        postal_code=business.postal_code,
        phone=business.phone,
        formatted_phone=business.formatted_phone,
        website=business.website,
        rating=business.rating,
        rating_count=business.rating_count or 0,
        latitude=business.latitude,
        longitude=business.longitude,
        google_maps_url=business.google_maps_url,
        types=types,
        is_open_now=business.is_open_now,
        opening_hours=opening_hours,
        photos=photos,
        tags=tags,
        notes=notes,
        created_at=business.created_at,
        updated_at=business.updated_at,
        last_fetched_at=business.last_fetched_at
    )


@router.patch("/{business_id}", response_model=BusinessSummary)
async def update_business(
    business_id: str,
    update_data: BusinessUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletme bilgilerini güncelle
    """
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    
    updated = await service.update(business, update_data.model_dump(exclude_unset=True))
    
    return BusinessSummary(
        id=updated.id,
        place_id=updated.place_id,
        name=updated.name,
        category=updated.category,
        address=updated.address,
        city=updated.city,
        phone=updated.phone,
        website=updated.website,
        rating=updated.rating,
        rating_count=updated.rating_count or 0,
        latitude=updated.latitude,
        longitude=updated.longitude,
        google_maps_url=updated.google_maps_url
    )


@router.delete("/{business_id}")
async def delete_business(
    business_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletmeyi pasif yap (soft delete)
    """
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    
    await service.update(business, {"is_active": False})
    
    return {"message": "İşletme silindi", "id": business_id}


# ============ Etiketler ============

@router.post("/{business_id}/tags")
async def add_tag(
    business_id: str,
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletmeye etiket ekle
    """
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    
    tag = await service.add_tag(business_id, tag_data.tag)
    
    return {"message": "Etiket eklendi", "tag": tag.tag}


@router.delete("/{business_id}/tags/{tag}")
async def remove_tag(
    business_id: str,
    tag: str,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletmeden etiket kaldır
    """
    service = BusinessService(db)
    removed = await service.remove_tag(business_id, tag)
    
    if not removed:
        raise HTTPException(status_code=404, detail="Etiket bulunamadı")
    
    return {"message": "Etiket kaldırıldı", "tag": tag}


# ============ Notlar ============

@router.post("/{business_id}/notes", response_model=NoteResponse)
async def add_note(
    business_id: str,
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    İşletmeye not ekle
    """
    service = BusinessService(db)
    business = await service.get_by_id(business_id)
    
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")
    
    note = await service.add_note(business_id, note_data.note)
    
    return NoteResponse(
        id=note.id,
        note=note.note,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.delete("/{business_id}/notes/{note_id}")
async def delete_note(
    business_id: str,
    note_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Notu sil
    """
    service = BusinessService(db)
    deleted = await service.delete_note(note_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Not bulunamadı")
    
    return {"message": "Not silindi", "id": note_id}


# ============ Toplu İşlemler ============

@router.post("/bulk/tags")
async def bulk_add_tags(
    business_ids: List[str],
    tag: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Birden fazla işletmeye etiket ekle
    """
    service = BusinessService(db)
    added = 0
    
    for bid in business_ids:
        try:
            await service.add_tag(bid, tag)
            added += 1
        except:
            pass
    
    return {"message": f"{added} işletmeye etiket eklendi", "tag": tag}

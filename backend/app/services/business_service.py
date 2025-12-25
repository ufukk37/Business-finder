"""
İşletme Servisi
Veritabanı CRUD işlemleri ve iş mantığı
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import logging

from app.models.business import Business, SearchQuery, SearchResult, BusinessTag, BusinessNote
from app.schemas.business import BusinessFilter, SearchRequest

logger = logging.getLogger(__name__)


class BusinessService:
    """İşletme veritabanı işlemleri"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, business_id: str) -> Optional[Business]:
        """ID ile işletme getir"""
        result = await self.db.execute(
            select(Business)
            .options(
                selectinload(Business.tags),
                selectinload(Business.notes)
            )
            .where(Business.id == business_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_place_id(self, place_id: str) -> Optional[Business]:
        """Google Place ID ile işletme getir"""
        result = await self.db.execute(
            select(Business).where(Business.place_id == place_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: Dict[str, Any]) -> Business:
        """Yeni işletme oluştur"""
        business = Business(**data)
        self.db.add(business)
        await self.db.flush()
        await self.db.refresh(business)
        return business
    
    async def update(self, business: Business, data: Dict[str, Any]) -> Business:
        """İşletme güncelle"""
        for key, value in data.items():
            if hasattr(business, key) and value is not None:
                setattr(business, key, value)
        
        business.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(business)
        return business
    
    async def upsert(self, data: Dict[str, Any]) -> Tuple[Business, bool]:
        """
        İşletme ekle veya güncelle (tekilleştirme)
        
        Returns:
            (business, is_new) tuple
        """
        place_id = data.get("place_id")
        if not place_id:
            raise ValueError("place_id zorunludur")
        
        existing = await self.get_by_place_id(place_id)
        
        if existing:
            # Mevcut kaydı güncelle
            updated = await self.update(existing, data)
            return (updated, False)
        else:
            # Yeni kayıt oluştur
            new_business = await self.create(data)
            return (new_business, True)
    
    async def bulk_upsert(self, items: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Toplu upsert işlemi
        
        Returns:
            (total_count, new_count)
        """
        new_count = 0
        
        for item in items:
            try:
                _, is_new = await self.upsert(item)
                if is_new:
                    new_count += 1
            except Exception as e:
                logger.error(f"Upsert hatası: {e} - {item.get('name', 'Unknown')}")
        
        return (len(items), new_count)
    
    async def list_businesses(
        self,
        filters: BusinessFilter
    ) -> Tuple[List[Business], int]:
        """
        Filtrelenmiş işletme listesi
        
        Returns:
            (businesses, total_count)
        """
        # Base query
        query = select(Business).where(Business.is_active == True)
        count_query = select(func.count(Business.id)).where(Business.is_active == True)
        
        # Filtreler
        conditions = []
        
        if filters.city:
            conditions.append(Business.city.ilike(f"%{filters.city}%"))
        
        if filters.district:
            conditions.append(Business.district.ilike(f"%{filters.district}%"))
        
        if filters.category:
            conditions.append(Business.category.ilike(f"%{filters.category}%"))
        
        if filters.min_rating is not None:
            conditions.append(Business.rating >= filters.min_rating)
        
        if filters.max_rating is not None:
            conditions.append(Business.rating <= filters.max_rating)
        
        if filters.min_reviews is not None:
            conditions.append(Business.rating_count >= filters.min_reviews)
        
        if filters.has_phone is not None:
            if filters.has_phone:
                conditions.append(Business.phone.isnot(None))
                conditions.append(Business.phone != "")
            else:
                conditions.append(or_(Business.phone.is_(None), Business.phone == ""))
        
        if filters.has_website is not None:
            if filters.has_website:
                conditions.append(Business.website.isnot(None))
                conditions.append(Business.website != "")
            else:
                conditions.append(or_(Business.website.is_(None), Business.website == ""))
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Business.name.ilike(search_term),
                    Business.address.ilike(search_term),
                    Business.category.ilike(search_term)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Etiket filtresi
        if filters.tags:
            query = query.join(Business.tags).where(BusinessTag.tag.in_(filters.tags))
            count_query = count_query.join(Business.tags).where(BusinessTag.tag.in_(filters.tags))
        
        # Sıralama
        sort_column = getattr(Business, filters.sort_by, Business.rating)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column).nulls_last())
        else:
            query = query.order_by(asc(sort_column).nulls_last())
        
        # Toplam sayı
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Sayfalama
        offset = (filters.page - 1) * filters.per_page
        query = query.offset(offset).limit(filters.per_page)
        
        # Sonuçlar
        result = await self.db.execute(query)
        businesses = result.scalars().all()
        
        return (list(businesses), total)
    
    async def add_tag(self, business_id: str, tag: str) -> BusinessTag:
        """İşletmeye etiket ekle"""
        # Mevcut etiket kontrolü
        result = await self.db.execute(
            select(BusinessTag).where(
                and_(
                    BusinessTag.business_id == business_id,
                    BusinessTag.tag == tag
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        new_tag = BusinessTag(business_id=business_id, tag=tag)
        self.db.add(new_tag)
        await self.db.flush()
        return new_tag
    
    async def remove_tag(self, business_id: str, tag: str) -> bool:
        """İşletmeden etiket kaldır"""
        result = await self.db.execute(
            select(BusinessTag).where(
                and_(
                    BusinessTag.business_id == business_id,
                    BusinessTag.tag == tag
                )
            )
        )
        tag_obj = result.scalar_one_or_none()
        
        if tag_obj:
            await self.db.delete(tag_obj)
            return True
        return False
    
    async def add_note(self, business_id: str, note_text: str) -> BusinessNote:
        """İşletmeye not ekle"""
        note = BusinessNote(business_id=business_id, note=note_text)
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note
    
    async def delete_note(self, note_id: str) -> bool:
        """Notu sil"""
        result = await self.db.execute(
            select(BusinessNote).where(BusinessNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        
        if note:
            await self.db.delete(note)
            return True
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Dashboard istatistikleri"""
        # Toplam işletme
        total_result = await self.db.execute(
            select(func.count(Business.id)).where(Business.is_active == True)
        )
        total_businesses = total_result.scalar()
        
        # Telefonu olan
        phone_result = await self.db.execute(
            select(func.count(Business.id)).where(
                and_(
                    Business.is_active == True,
                    Business.phone.isnot(None),
                    Business.phone != ""
                )
            )
        )
        with_phone = phone_result.scalar()
        
        # Web sitesi olan
        website_result = await self.db.execute(
            select(func.count(Business.id)).where(
                and_(
                    Business.is_active == True,
                    Business.website.isnot(None),
                    Business.website != ""
                )
            )
        )
        with_website = website_result.scalar()
        
        # Ortalama puan
        avg_result = await self.db.execute(
            select(func.avg(Business.rating)).where(
                and_(
                    Business.is_active == True,
                    Business.rating.isnot(None)
                )
            )
        )
        avg_rating = avg_result.scalar() or 0
        
        # Toplam arama
        search_result = await self.db.execute(
            select(func.count(SearchQuery.id))
        )
        total_searches = search_result.scalar()
        
        # En çok işletme olan şehirler
        city_result = await self.db.execute(
            select(Business.city, func.count(Business.id).label("count"))
            .where(and_(Business.is_active == True, Business.city.isnot(None)))
            .group_by(Business.city)
            .order_by(desc("count"))
            .limit(5)
        )
        top_cities = [{"city": row[0], "count": row[1]} for row in city_result.all()]
        
        # En çok işletme olan kategoriler
        category_result = await self.db.execute(
            select(Business.category, func.count(Business.id).label("count"))
            .where(and_(Business.is_active == True, Business.category.isnot(None)))
            .group_by(Business.category)
            .order_by(desc("count"))
            .limit(5)
        )
        top_categories = [{"category": row[0], "count": row[1]} for row in category_result.all()]
        
        # Son aramalar
        recent_result = await self.db.execute(
            select(SearchQuery)
            .order_by(desc(SearchQuery.created_at))
            .limit(5)
        )
        recent_searches = [
            {
                "id": s.id,
                "location": s.location_query,
                "type": s.business_type,
                "results": s.results_count,
                "date": s.created_at.isoformat() if s.created_at else None
            }
            for s in recent_result.scalars().all()
        ]
        
        return {
            "total_businesses": total_businesses,
            "total_searches": total_searches,
            "businesses_with_phone": with_phone,
            "businesses_with_website": with_website,
            "average_rating": round(float(avg_rating), 2),
            "top_cities": top_cities,
            "top_categories": top_categories,
            "recent_searches": recent_searches
        }


class SearchService:
    """Arama işlemleri servisi"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_search_query(self, request: SearchRequest, lat: float, lng: float) -> SearchQuery:
        """Arama sorgusu oluştur"""
        search_query = SearchQuery(
            location_query=request.location,
            latitude=lat,
            longitude=lng,
            radius=request.radius,
            business_type=request.business_type,
            keyword=request.keyword,
            status="processing"
        )
        self.db.add(search_query)
        await self.db.flush()
        await self.db.refresh(search_query)
        return search_query
    
    async def update_search_results(
        self,
        search_query: SearchQuery,
        total_count: int,
        new_count: int,
        status: str = "completed",
        error: Optional[str] = None
    ):
        """Arama sonuçlarını güncelle"""
        search_query.results_count = total_count
        search_query.new_businesses_count = new_count
        search_query.status = status
        search_query.error_message = error
        search_query.completed_at = datetime.utcnow()
        await self.db.flush()
    
    async def link_business_to_search(
        self,
        search_query_id: str,
        business_id: str,
        distance: Optional[float] = None
    ):
        """İşletmeyi arama sonucuna bağla"""
        search_result = SearchResult(
            search_query_id=search_query_id,
            business_id=business_id,
            distance=distance
        )
        self.db.add(search_result)
    
    async def get_search_history(self, limit: int = 20) -> List[SearchQuery]:
        """Arama geçmişini getir"""
        result = await self.db.execute(
            select(SearchQuery)
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

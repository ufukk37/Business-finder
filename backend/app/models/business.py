"""
Veritabanı Modelleri
SQLAlchemy ORM modelleri
"""

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, 
    Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base


class Business(Base):
    """İşletme modeli"""
    __tablename__ = "businesses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Google Places bilgileri
    place_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Temel bilgiler
    name = Column(String(500), nullable=False, index=True)
    category = Column(String(255), index=True)
    types = Column(Text)  # JSON array olarak saklanacak
    
    # İletişim bilgileri
    phone = Column(String(50))
    formatted_phone = Column(String(50))
    website = Column(String(1000))
    
    # Adres bilgileri
    address = Column(String(1000))
    city = Column(String(100), index=True)
    district = Column(String(100), index=True)
    country = Column(String(100), default="Türkiye")
    postal_code = Column(String(20))
    
    # Konum
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Google puanlama
    rating = Column(Float, index=True)
    rating_count = Column(Integer, default=0)
    
    # İşletme durumu
    is_open_now = Column(Boolean)
    opening_hours = Column(Text)  # JSON
    
    # Meta bilgiler
    google_maps_url = Column(String(1000))
    photos = Column(Text)  # JSON array
    
    # Sistem alanları
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # İlişkiler
    search_results = relationship("SearchResult", back_populates="business")
    tags = relationship("BusinessTag", back_populates="business", cascade="all, delete-orphan")
    notes = relationship("BusinessNote", back_populates="business", cascade="all, delete-orphan")
    
    # İndeksler
    __table_args__ = (
        Index('idx_business_location', 'latitude', 'longitude'),
        Index('idx_business_city_category', 'city', 'category'),
        Index('idx_business_rating', 'rating', 'rating_count'),
    )
    
    def __repr__(self):
        return f"<Business {self.name} ({self.place_id})>"


class SearchQuery(Base):
    """Arama sorgusu geçmişi"""
    __tablename__ = "search_queries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Arama parametreleri
    location_query = Column(String(500))  # Kullanıcının girdiği lokasyon
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Integer)
    business_type = Column(String(255))
    keyword = Column(String(255))
    
    # Sonuç bilgileri
    results_count = Column(Integer, default=0)
    new_businesses_count = Column(Integer, default=0)
    
    # Durum
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Zamanlar
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # İlişkiler
    results = relationship("SearchResult", back_populates="search_query")
    
    def __repr__(self):
        return f"<SearchQuery {self.location_query} - {self.business_type}>"


class SearchResult(Base):
    """Arama sonucu - işletme ilişkisi"""
    __tablename__ = "search_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    search_query_id = Column(String(36), ForeignKey("search_queries.id"), nullable=False)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    
    # Arama bağlamında bilgiler
    distance = Column(Float)  # Metre cinsinden
    relevance_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # İlişkiler
    search_query = relationship("SearchQuery", back_populates="results")
    business = relationship("Business", back_populates="search_results")
    
    __table_args__ = (
        UniqueConstraint('search_query_id', 'business_id', name='unique_search_business'),
    )


class BusinessTag(Base):
    """İşletme etiketleri (kullanıcı tanımlı)"""
    __tablename__ = "business_tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    tag = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    business = relationship("Business", back_populates="tags")
    
    __table_args__ = (
        UniqueConstraint('business_id', 'tag', name='unique_business_tag'),
    )


class BusinessNote(Base):
    """İşletme notları"""
    __tablename__ = "business_notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    business = relationship("Business", back_populates="notes")


class Category(Base):
    """İşletme kategorileri"""
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    name_tr = Column(String(100))  # Türkçe karşılık
    google_type = Column(String(100))  # Google Places type
    icon = Column(String(50))
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Category {self.name}>"

"""
OpenStreetMap Servisi (Ücretsiz)
İşletme verilerini OpenStreetMap'ten çeker
"""

import httpx
import asyncio
import json
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OpenStreetMapService:
    """OpenStreetMap API ile etkileşim servisi - Tamamen Ücretsiz"""
    
    # Türkçe kategori -> OSM tag eşleştirmeleri
    CATEGORY_MAPPING = {
        "restoran": {"amenity": "restaurant"},
        "kafe": {"amenity": "cafe"},
        "kahve": {"amenity": "cafe"},
        "otel": {"tourism": "hotel"},
        "hastane": {"amenity": "hospital"},
        "eczane": {"amenity": "pharmacy"},
        "banka": {"amenity": "bank"},
        "market": {"shop": "supermarket"},
        "süpermarket": {"shop": "supermarket"},
        "bakkal": {"shop": "convenience"},
        "okul": {"amenity": "school"},
        "üniversite": {"amenity": "university"},
        "benzinlik": {"amenity": "fuel"},
        "oto servis": {"shop": "car_repair"},
        "araba servisi": {"shop": "car_repair"},
        "kuaför": {"shop": "hairdresser"},
        "berber": {"shop": "hairdresser"},
        "güzellik salonu": {"shop": "beauty"},
        "spor salonu": {"leisure": "fitness_centre"},
        "fitness": {"leisure": "fitness_centre"},
        "diş kliniği": {"amenity": "dentist"},
        "dişçi": {"amenity": "dentist"},
        "veteriner": {"amenity": "veterinary"},
        "avukat": {"office": "lawyer"},
        "muhasebeci": {"office": "accountant"},
        "sigorta": {"office": "insurance"},
        "emlak": {"office": "estate_agent"},
        "mağaza": {"shop": "yes"},
        "alışveriş": {"shop": "mall"},
        "sinema": {"amenity": "cinema"},
        "tiyatro": {"amenity": "theatre"},
        "müze": {"tourism": "museum"},
        "park": {"leisure": "park"},
        "cami": {"amenity": "place_of_worship", "religion": "muslim"},
        "kilise": {"amenity": "place_of_worship", "religion": "christian"},
        "atm": {"amenity": "atm"},
        "postane": {"amenity": "post_office"},
        "kütüphane": {"amenity": "library"},
        "bar": {"amenity": "bar"},
        "pastane": {"shop": "bakery"},
        "fırın": {"shop": "bakery"},
        "kasap": {"shop": "butcher"},
        "manav": {"shop": "greengrocer"},
    }
    
    # Türkçe kategori isimleri
    CATEGORY_NAMES = {
        "restaurant": "Restoran",
        "cafe": "Kafe",
        "hotel": "Otel",
        "hospital": "Hastane",
        "pharmacy": "Eczane",
        "bank": "Banka",
        "supermarket": "Market",
        "convenience": "Bakkal",
        "school": "Okul",
        "university": "Üniversite",
        "fuel": "Benzinlik",
        "car_repair": "Oto Servis",
        "hairdresser": "Kuaför",
        "beauty": "Güzellik Salonu",
        "fitness_centre": "Spor Salonu",
        "dentist": "Diş Kliniği",
        "veterinary": "Veteriner",
        "lawyer": "Avukat",
        "accountant": "Muhasebeci",
        "insurance": "Sigorta",
        "estate_agent": "Emlak",
        "mall": "AVM",
        "cinema": "Sinema",
        "theatre": "Tiyatro",
        "museum": "Müze",
        "park": "Park",
        "place_of_worship": "İbadet Yeri",
        "atm": "ATM",
        "post_office": "Postane",
        "library": "Kütüphane",
        "bar": "Bar",
        "bakery": "Fırın/Pastane",
        "butcher": "Kasap",
        "greengrocer": "Manav",
    }
    
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={"User-Agent": "BusinessFinder/1.0"}
        )
    
    async def close(self):
        """HTTP client'ı kapat"""
        await self.client.aclose()
    
    def _get_osm_tags(self, business_type: str) -> Dict[str, str]:
        """Türkçe kategoriyi OSM tag'lerine çevir"""
        business_type_lower = business_type.lower().strip()
        return self.CATEGORY_MAPPING.get(business_type_lower, {"amenity": business_type_lower})
    
    async def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Lokasyonu koordinatlara çevir (Nominatim - Ücretsiz)
        
        Returns:
            (latitude, longitude) tuple veya None
        """
        try:
            url = f"{self.nominatim_url}/search"
            params = {
                "q": location,
                "format": "json",
                "limit": 1,
                "countrycodes": "tr",
                "accept-language": "tr"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                logger.info(f"Geocoding başarılı: {location} -> {lat}, {lon}")
                return (lat, lon)
            
            logger.warning(f"Geocoding başarısız: {location} - Sonuç bulunamadı")
            return None
            
        except Exception as e:
            logger.error(f"Geocoding hatası: {e}")
            return None
    
    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        business_type: str,
        keyword: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Yakındaki işletmeleri ara (Overpass API - Ücretsiz)
        """
        try:
            osm_tags = self._get_osm_tags(business_type)
            
            # Overpass QL sorgusu oluştur
            tag_filters = "".join([f'["{k}"="{v}"]' for k, v in osm_tags.items()])
            
            # Eğer sadece bir ana tag varsa, daha geniş arama yap
            if len(osm_tags) == 1:
                key, value = list(osm_tags.items())[0]
                if value == "yes":
                    tag_filters = f'["{key}"]'
            
            query = f"""
            [out:json][timeout:30];
            (
              node{tag_filters}(around:{radius},{latitude},{longitude});
              way{tag_filters}(around:{radius},{latitude},{longitude});
              relation{tag_filters}(around:{radius},{latitude},{longitude});
            );
            out center meta;
            """
            
            response = await self.client.post(
                self.overpass_url,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
            
            elements = data.get("elements", [])
            logger.info(f"Overpass search: {len(elements)} sonuç bulundu")
            
            # Keyword filtresi uygula
            if keyword and elements:
                keyword_lower = keyword.lower()
                elements = [
                    e for e in elements 
                    if keyword_lower in e.get("tags", {}).get("name", "").lower()
                ]
            
            return {"results": elements, "status": "OK"}
            
        except Exception as e:
            logger.error(f"Overpass search hatası: {e}")
            return {"results": [], "status": "ERROR", "error": str(e)}
    
    async def search_all_pages(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        business_type: str,
        keyword: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Tüm sonuçları getir
        """
        data = await self.search_nearby(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            business_type=business_type,
            keyword=keyword
        )
        
        results = data.get("results", [])
        return results[:max_results]
    
    def parse_place_to_business(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """
        OSM element'ini veritabanı formatına çevir
        """
        tags = element.get("tags", {})
        
        # Koordinatları al
        if element.get("type") == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            # Way veya relation için center kullan
            center = element.get("center", {})
            lat = center.get("lat") or element.get("lat")
            lon = center.get("lon") or element.get("lon")
        
        # Kategori belirle
        category = self._determine_category(tags)
        
        # Adres oluştur
        address_parts = []
        if tags.get("addr:street"):
            if tags.get("addr:housenumber"):
                address_parts.append(f"{tags['addr:street']} No:{tags['addr:housenumber']}")
            else:
                address_parts.append(tags["addr:street"])
        if tags.get("addr:district"):
            address_parts.append(tags["addr:district"])
        if tags.get("addr:city"):
            address_parts.append(tags["addr:city"])
        
        address = ", ".join(address_parts) if address_parts else tags.get("addr:full", "")
        
        # Unique place_id oluştur
        place_id = f"osm_{element.get('type', 'node')}_{element.get('id', uuid.uuid4().hex)}"
        
        return {
            "place_id": place_id,
            "name": tags.get("name", tags.get("brand", "İsimsiz İşletme")),
            "category": category,
            "types": json.dumps(list(tags.keys())),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "formatted_phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "address": address,
            "city": tags.get("addr:city"),
            "district": tags.get("addr:district") or tags.get("addr:suburb"),
            "postal_code": tags.get("addr:postcode"),
            "latitude": lat,
            "longitude": lon,
            "rating": None,  # OSM'de rating yok
            "rating_count": 0,
            "is_open_now": None,
            "opening_hours": json.dumps(self._parse_opening_hours(tags.get("opening_hours", ""))),
            "google_maps_url": f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id', '')}",
            "photos": json.dumps([]),
            "last_fetched_at": datetime.utcnow()
        }
    
    def _determine_category(self, tags: Dict[str, str]) -> str:
        """OSM tags'ten kategori belirle"""
        # Önce amenity kontrol et
        if "amenity" in tags:
            amenity = tags["amenity"]
            return self.CATEGORY_NAMES.get(amenity, amenity.replace("_", " ").title())
        
        # Sonra shop kontrol et
        if "shop" in tags:
            shop = tags["shop"]
            return self.CATEGORY_NAMES.get(shop, shop.replace("_", " ").title())
        
        # Tourism
        if "tourism" in tags:
            tourism = tags["tourism"]
            return self.CATEGORY_NAMES.get(tourism, tourism.replace("_", " ").title())
        
        # Leisure
        if "leisure" in tags:
            leisure = tags["leisure"]
            return self.CATEGORY_NAMES.get(leisure, leisure.replace("_", " ").title())
        
        # Office
        if "office" in tags:
            office = tags["office"]
            return self.CATEGORY_NAMES.get(office, office.replace("_", " ").title())
        
        return "Diğer"
    
    def _parse_opening_hours(self, hours_str: str) -> List[str]:
        """Çalışma saatlerini parse et"""
        if not hours_str:
            return []
        
        # Basit parse - OSM formatı karmaşık olabilir
        try:
            return [hours_str]
        except:
            return []


# Singleton instance
google_places_service = OpenStreetMapService()

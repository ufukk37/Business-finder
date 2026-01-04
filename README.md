# BizFinder - İşletme Keşif Platformu

B2B satış destek aracı - Potansiyel müşterileri otomatik keşfedin.

## 🚀 Özellikler

- ✅ **Kullanıcı Sistemi**: Kayıt/Giriş, JWT authentication
- ✅ **Modern Dashboard**: İstatistikler ve hızlı erişim
- ✅ **Harita Tabanlı Arama**: Leaflet harita, yarıçap seçimi
- ✅ **Polygon Çizimi**: Harita üzerinden alan seçimi
- ✅ **Ön Tanımlı Lokasyonlar**: Türkiye şehirleri ve ilçeleri
- ✅ **Kategori Bazlı Arama**: 20+ işletme kategorisi
- ✅ **Mükerrer Kayıt Engelleme**: Aynı işletme tekrar eklenmez
- ✅ **Filtrelenmiş Excel İndirme**: Sadece seçili veriler
- ✅ **Dinamik Arama Limiti**: 100 - 5000 arası
- ✅ **Ücretsiz API**: OpenStreetMap/Nominatim (Google gerektirmez)

## 📋 Gereksinimler

- Python 3.10+ (3.13 dahil)
- Node.js 18+
- npm veya yarn

## 🛠️ Kurulum

### 1. Backend Kurulumu

```cmd
cd business-finder\backend

# Virtual environment oluştur
python -m venv venv

# Aktive et (Windows)
venv\Scripts\activate

# Paketleri yükle
pip install -r requirements.txt
```

### 2. Frontend Kurulumu

```cmd
cd business-finder\frontend

# Paketleri yükle
npm install
```

## ▶️ Çalıştırma

### Terminal 1 - Backend

```cmd
cd business-finder\backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

Backend: http://localhost:8000

### Terminal 2 - Frontend

```cmd
cd business-finder\frontend
npm run dev
```

Frontend: http://localhost:5173

## 📖 Kullanım

1. http://localhost:5173 adresini aç
2. **Kayıt Ol** ile yeni hesap oluştur
3. Dashboard'dan **Arama** sayfasına git
4. Şehir ve kategori seç
5. Haritadan konum veya alan belirle
6. **Ara** butonuna tıkla
7. **İşletmeler** sayfasından filtrele ve Excel'e aktar

## 🔧 API Endpoints

| Endpoint | Açıklama |
|----------|----------|
| POST /api/auth/register | Kayıt ol |
| POST /api/auth/login | Giriş yap |
| GET /api/auth/me | Kullanıcı bilgisi |
| POST /api/search/ | İşletme ara |
| GET /api/businesses/ | İşletme listesi |
| GET /api/businesses/stats | İstatistikler |
| GET /api/exports/download/{format} | Dışa aktar |

## 📁 Proje Yapısı

```
business-finder/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoint'leri
│   │   ├── core/          # Database, config, security
│   │   ├── models/        # SQLAlchemy modelleri
│   │   ├── schemas/       # Pydantic şemaları
│   │   ├── services/      # İş mantığı
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React bileşenleri
│   │   ├── contexts/      # Auth context
│   │   ├── pages/         # Sayfa bileşenleri
│   │   └── utils/         # Yardımcı fonksiyonlar
│   └── package.json
└── README.md
```

## 🐛 Sorun Giderme

### "Module not found" hatası
```cmd
pip install -r requirements.txt --break-system-packages
```

### Port kullanımda hatası
```cmd
# Backend için farklı port
python -m uvicorn app.main:app --reload --port 8001

# Frontend için farklı port
npm run dev -- --port 5174
```

### CORS hatası
Backend ve frontend'in aynı anda çalıştığından emin ol.



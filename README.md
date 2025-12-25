# 🏢 İşletme Keşif Platformu (Business Finder)

Google Maps üzerinden işletmeleri otomatik olarak keşfeden, veritabanına kaydeden ve yönetmenizi sağlayan modern bir web uygulaması.

![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-React-blue)
![Database](https://img.shields.io/badge/Database-SQLite-blue)

## 🎯 Özellikler

### Arama & Keşif
- 📍 Lokasyon bazlı işletme arama (şehir, ilçe veya koordinat)
- 🏪 Kategori bazlı filtreleme (restoran, kafe, oto servis, vb.)
- 📏 Özelleştirilebilir arama yarıçapı (100m - 50km)
- 🔍 Anahtar kelime ile detaylı arama

### Veri Toplama
- 📞 İşletme adı, telefon, website
- 📍 Tam adres ve koordinatlar
- ⭐ Google puanı ve yorum sayısı
- 🕐 Çalışma saatleri
- 📷 Fotoğraflar

### Yönetim & Organizasyon
- 🏷️ Özel etiketleme sistemi
- 📝 Not ekleme özelliği
- 🔄 Tekilleştirme (aynı işletme tekrar eklenmez)
- 📊 Dashboard istatistikleri

### Dışa Aktarım
- 📑 Excel (.xlsx)
- 📄 CSV
- 📋 JSON

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy |
| **Frontend** | React 18, Vite, TailwindCSS |
| **Veritabanı** | SQLite (kurulum gerektirmez) |

## 🚀 Hızlı Başlangıç (Windows)

### Gereksinimler

1. **Python 3.10+** - [İndir](https://www.python.org/downloads/)
   - Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretle!
   
2. **Node.js 18+** - [İndir](https://nodejs.org/)

3. **Google Places API Key** - [Buradan al](https://console.cloud.google.com/apis/library/places-backend.googleapis.com)

### Kurulum (3 Adım)

#### 1. Projeyi İndir ve Aç
```
Zip dosyasını indir ve bir klasöre çıkar
```

#### 2. API Key'i Ayarla
`backend\.env` dosyasını aç ve API key'ini gir:
```
GOOGLE_PLACES_API_KEY=AIzaSyXXXXXXXXXXXXXXXXX
```

#### 3. Başlat
`start-windows.bat` dosyasına çift tıkla!

Otomatik olarak:
- ✅ Python bağımlılıkları kurulur
- ✅ Node.js bağımlılıkları kurulur  
- ✅ Backend başlar (http://localhost:8000)
- ✅ Frontend başlar (http://localhost:5173)
- ✅ Tarayıcı açılır

### Manuel Başlatma (Alternatif)

İki ayrı CMD penceresi aç:

**Pencere 1 - Backend:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Pencere 2 - Frontend:**
```cmd
cd frontend
npm install
npm run dev
```

## 📁 Proje Yapısı

```
business-finder/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoint'leri
│   │   ├── core/           # Konfigürasyon, veritabanı
│   │   ├── models/         # SQLAlchemy modelleri
│   │   ├── schemas/        # Pydantic şemaları
│   │   └── services/       # İş mantığı servisleri
│   ├── requirements.txt
│   └── .env                # API Key buraya
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React bileşenleri
│   │   ├── pages/          # Sayfa bileşenleri
│   │   └── services/       # API servisleri
│   └── package.json
├── start-windows.bat       # Tek tıkla başlat
├── start-backend.bat       # Sadece backend
└── start-frontend.bat      # Sadece frontend
```

## 🔌 API Kullanımı

### İşletme Arama
```bash
curl -X POST "http://localhost:8000/api/search/" ^
  -H "Content-Type: application/json" ^
  -d "{\"location\": \"Kadıköy, İstanbul\", \"business_type\": \"restoran\", \"radius\": 3000}"
```

### İşletmeleri Listele
```
GET http://localhost:8000/api/businesses/?city=İstanbul&min_rating=4
```

### API Dokümantasyonu
Tarayıcıda aç: http://localhost:8000/docs

## 🔐 Google Places API Key Alma

1. [Google Cloud Console](https://console.cloud.google.com/) aç
2. Yeni proje oluştur
3. "APIs & Services" > "Enable APIs"
4. **"Places API"** ve **"Geocoding API"** etkinleştir
5. "Credentials" > "Create Credentials" > "API Key"
6. Key'i kopyala ve `backend\.env` dosyasına yapıştır

### API Limitleri
- **Ücretsiz**: Aylık $200 kredi (yaklaşık 5000 arama)
- Detaylı fiyatlandırma: [Google Maps Pricing](https://developers.google.com/maps/billing-and-pricing/pricing)

## 🔮 Gelecek Özellikler

- [ ] WhatsApp mesaj gönderimi
- [ ] E-posta kampanyaları
- [ ] Harita görünümü
- [ ] CRM entegrasyonu

## 📞 Sorun Giderme

### "Python bulunamadı" hatası
- Python'u yeniden kur ve **"Add Python to PATH"** seçeneğini işaretle
- Bilgisayarı yeniden başlat

### "npm bulunamadı" hatası
- Node.js'i yeniden kur
- Bilgisayarı yeniden başlat

### API Key hatası
- `backend\.env` dosyasındaki key'i kontrol et
- Google Cloud Console'da API'lerin aktif olduğundan emin ol

---

⭐ Dijital Gen için geliştirildi - Genvizit müşteri adaylarını bul!

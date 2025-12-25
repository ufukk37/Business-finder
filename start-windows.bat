@echo off
chcp 65001 > nul
title İşletme Keşif Platformu

echo ========================================
echo    İşletme Keşif Platformu Başlatıcı
echo ========================================
echo.

:: Python kontrolü
python --version > nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo Python'u https://www.python.org/downloads/ adresinden indirin.
    echo Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin.
    pause
    exit /b 1
)

:: Node.js kontrolü
node --version > nul 2>&1
if errorlevel 1 (
    echo [HATA] Node.js bulunamadı!
    echo Node.js'i https://nodejs.org/ adresinden indirin.
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo [OK] Node.js bulundu
echo.

:: Backend kurulumu
echo [1/4] Backend bağımlılıkları kuruluyor...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
cd ..

:: Frontend kurulumu
echo [2/4] Frontend bağımlılıkları kuruluyor...
cd frontend
call npm install --silent
cd ..

echo.
echo [3/4] Servisler başlatılıyor...
echo.

:: Backend'i arka planda başlat
echo Backend başlatılıyor (http://localhost:8000)...
cd backend
start "Backend API" cmd /c "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

:: 3 saniye bekle
timeout /t 3 /nobreak > nul

:: Frontend'i arka planda başlat
echo Frontend başlatılıyor (http://localhost:5173)...
cd frontend
start "Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ========================================
echo    Uygulama başarıyla başlatıldı!
echo ========================================
echo.
echo  Frontend:  http://localhost:5173
echo  API Docs:  http://localhost:8000/docs
echo.
echo  Kapatmak için açılan CMD pencerelerini kapatın.
echo ========================================

:: 3 saniye bekle ve tarayıcıyı aç
timeout /t 3 /nobreak > nul
start http://localhost:5173

pause

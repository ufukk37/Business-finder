@echo off
chcp 65001 > nul
title Backend API

cd backend

if not exist "venv" (
    echo Virtual environment oluşturuluyor...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Bağımlılıklar yükleniyor...
pip install -r requirements.txt -q

echo.
echo ========================================
echo   Backend API başlatılıyor...
echo   http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

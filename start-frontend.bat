@echo off
chcp 65001 > nul
title Frontend

cd frontend

echo Bağımlılıklar kontrol ediliyor...
if not exist "node_modules" (
    echo node_modules bulunamadı, npm install çalıştırılıyor...
    call npm install
)

echo.
echo ========================================
echo   Frontend başlatılıyor...
echo   http://localhost:5173
echo ========================================
echo.

call npm run dev

@echo off
title Menjalankan MotoRent - Website Rental Motor Django
echo ====================================================
echo      MEMULAI SERVER LOKAL WEBSITE RENTAL MOTOR      
echo ====================================================
echo.
echo [1/2] Membuka browser default ke http://127.0.0.1:8000/ ...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000/
echo.
echo [2/2] Menjalankan server Django (Tekan CTRL+C untuk menghentikan)...
echo.
python manage.py runserver
pause

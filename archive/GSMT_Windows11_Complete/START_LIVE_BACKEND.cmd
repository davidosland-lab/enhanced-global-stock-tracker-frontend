@echo off
cls
color 0A
title GSMT - Live Market Data Server (NO DEMO DATA)

echo ============================================
echo  GSMT - LIVE Market Data Server
echo  Yahoo Finance Real Data ONLY
echo  NO DEMO/SYNTHETIC DATA
echo ============================================
echo.

REM Kill any existing Python servers on port 8000
echo Stopping any existing servers on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo Starting LIVE Market Data Server...
echo.
echo Server Configuration:
echo - Port: 8000
echo - Data Source: Yahoo Finance API
echo - No demo data fallback
echo - Real-time updates only
echo.

cd backend
python live_market_server.py

pause
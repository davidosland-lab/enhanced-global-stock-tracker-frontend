@echo off
cls
color 0A
title GSMT - Live Market Data Server (SIMPLE - NO DEMO DATA)

echo ============================================
echo  GSMT - LIVE Market Data Server (SIMPLE)
echo  Yahoo Finance Real Data ONLY
echo  NO DEMO/SYNTHETIC DATA
echo ============================================
echo.

REM Check if dependencies are installed
python -c "import yfinance, fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    echo.
    call INSTALL_DEPENDENCIES.cmd
    echo.
)

REM Kill any existing Python servers on port 8000
echo Stopping any existing servers on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo Starting LIVE Market Data Server (Simple Version)...
echo.
echo Server Configuration:
echo - Port: 8000
echo - Data Source: Yahoo Finance API
echo - No demo data fallback
echo - Real-time updates only
echo - Simple version (no cachetools required)
echo.

cd backend
python live_market_server_simple.py

echo.
echo Server stopped.
pause
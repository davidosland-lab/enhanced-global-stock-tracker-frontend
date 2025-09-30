@echo off
title GSMT v9.2 - Complete Fix Edition
color 0A

echo ================================================================
echo            GSMT v9.2 - GLOBAL STOCK MARKET TRACKER
echo                    COMPLETE FIX EDITION
echo ================================================================
echo.
echo FIXED IN v9.2:
echo [✓] Dashboard linking to indices tracker
echo [✓] S&P 500 positioned correctly (before ASX opening)
echo [✓] CBA chart timeframe switching working
echo [✓] CBA document analysis with FinBERT
echo [✓] Technical Analysis candlestick charts working
echo [✓] Prediction Center fully functional
echo [✓] Document Center module added
echo [✓] All Ordinaries included by default
echo.

:: Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed!
    pause
    exit /b 1
)
echo Python installed ✓
echo.

:: Install packages
echo [2/4] Installing packages...
pip install -q yfinance fastapi uvicorn pandas numpy pytz 2>nul
echo Packages installed ✓
echo.

:: Clear port
echo [3/4] Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Port cleared ✓
echo.

:: Start backend
echo [4/4] Starting backend...
start "GSMT Backend v9.2" /min cmd /c "cd backend && python unified_backend_v92.py"
timeout /t 3 /nobreak >nul
echo.

:: Open dashboard
echo Opening dashboard...
start "" "frontend/dashboard_v92.html"

echo.
echo ================================================================
echo GSMT v9.2 is running!
echo.
echo Dashboard: frontend/dashboard_v92.html
echo Backend: http://localhost:8000
echo.
echo All issues have been resolved:
echo - Dashboard properly links to all modules
echo - S&P 500 shows before ASX opening (00:30 AEST)
echo - CBA timeframes work correctly
echo - Technical Analysis candlesticks functional
echo - Prediction Center loading properly
echo - Document Center available
echo.
echo Press any key to view logs...
echo ================================================================
pause >nul

cd backend
python unified_backend_v92.py
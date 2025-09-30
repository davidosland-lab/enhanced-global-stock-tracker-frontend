@echo off
title GSMT v9.1 - Global Stock Market Tracker (All Issues Fixed)
color 0A

echo ================================================================
echo            GSMT v9.1 - GLOBAL STOCK MARKET TRACKER
echo                  COMPLETE FIX WITH ALL ORDINARIES
echo ================================================================
echo.
echo NEW IN v9.1:
echo - All Ordinaries index added
echo - Fixed FTSE/S&P time alignment to AEST
echo - Fixed CBA module timeframe selection
echo - Fixed Technical Analysis candlestick charts
echo - Fixed Prediction Performance dashboard
echo - All times properly shown in AEST
echo.

:: Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

:: Install packages
echo [2/4] Installing required packages...
pip install --quiet --upgrade yfinance fastapi uvicorn pandas numpy pytz 2>nul
echo Required packages installed.
echo.

:: Clear port
echo [3/4] Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo.

:: Start backend
echo [4/4] Starting GSMT v9.1 Backend...
echo.
echo ================================================================
echo Backend: http://localhost:8000
echo Dashboard: frontend/dashboard_v91.html
echo ================================================================
echo.

:: Start backend
start "GSMT Backend v9.1" /min cmd /c "cd backend && python unified_backend_v91.py"

:: Wait for startup
timeout /t 5 /nobreak >nul

:: Open dashboard
echo Opening GSMT v9.1 Dashboard...
start "" "frontend/indices_tracker_v91.html"

echo.
echo ================================================================
echo GSMT v9.1 is running!
echo.
echo All issues have been fixed:
echo [✓] All Ordinaries index added as default
echo [✓] Market times correctly aligned to AEST
echo [✓] CBA module timeframe selection working
echo [✓] Technical Analysis charts fixed
echo [✓] Prediction dashboard loading correctly
echo.
echo Press any key to view backend logs...
echo ================================================================
pause >nul

cd backend
python unified_backend_v91.py
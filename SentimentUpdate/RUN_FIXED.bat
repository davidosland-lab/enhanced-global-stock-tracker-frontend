@echo off
title Stock Analysis - Fixed Charts
echo ============================================================
echo    STOCK ANALYSIS - FIXED CHART.JS DATE ADAPTER
echo ============================================================
echo.
echo This version fixes the Chart.js date adapter error
echo.
echo Features:
echo - Proper Chart.js date adapter included
echo - Yahoo Finance with 3-second delays (avoids 429 error)
echo - Alpha Vantage as automatic fallback
echo - Australian stocks supported (CBA, BHP, etc.)
echo.

REM Stop existing services
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

echo Starting fixed version...
python app_fixed_charts.py

if errorlevel 1 (
    echo.
    echo Error starting application.
    echo Make sure Python and required packages are installed:
    echo   pip install flask flask-cors yfinance pandas numpy requests
)

pause
@echo off
title Stock Analysis - Robust Version
echo ============================================================
echo    STOCK ANALYSIS WITH SENTIMENT - ROBUST VERSION
echo ============================================================
echo.
echo This version handles network issues gracefully:
echo - Retries failed API calls
echo - Uses fallback data sources
echo - Generates demo data if APIs are down
echo - Never crashes due to missing data
echo.

REM Set encoding
chcp 65001 >nul 2>&1

REM Kill any existing processes on port 5000
echo [*] Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

REM Start the robust version
echo [*] Starting robust server...
echo.
echo ============================================================
echo    Server running at http://localhost:5000
echo    Press Ctrl+C to stop
echo ============================================================
echo.

python app_enhanced_sentiment_robust.py

if errorlevel 1 (
    echo.
    echo [!] Error starting application
    echo.
    echo Try running: python app_enhanced_sentiment_robust.py
    echo.
)

pause
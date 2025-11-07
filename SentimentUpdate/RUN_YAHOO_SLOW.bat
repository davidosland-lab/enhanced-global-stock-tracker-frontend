@echo off
title Stock Analysis - Yahoo Finance with Delays
echo ============================================================
echo    YAHOO FINANCE WITH RATE LIMIT PROTECTION
echo ============================================================
echo.
echo This version adds 3-second delays between requests
echo to avoid the 429 rate limit error.
echo.
echo It will be SLOWER but should work!
echo.
echo Australian stocks supported: CBA, BHP, CSL, etc.
echo (Automatically adds .AX suffix)
echo.

REM Stop existing services
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

echo Starting Yahoo Finance with delays...
python app_yfinance_slow.py

pause
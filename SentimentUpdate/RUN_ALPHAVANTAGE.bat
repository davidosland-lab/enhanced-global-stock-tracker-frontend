@echo off
title Stock Analysis - Alpha Vantage (Yahoo Rate Limited)
echo ============================================================
echo    STOCK ANALYSIS - USING ALPHA VANTAGE
echo ============================================================
echo.
echo Yahoo Finance is rate limiting you (429 error)
echo Using Alpha Vantage instead - more reliable!
echo.
echo API Key: 68ZFANK047DL0KSR
echo Limits: 5 calls/minute, 500 calls/day
echo.

REM Stop any existing services
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 >nul

echo Starting Alpha Vantage server...
python app_alphavantage_primary.py

pause
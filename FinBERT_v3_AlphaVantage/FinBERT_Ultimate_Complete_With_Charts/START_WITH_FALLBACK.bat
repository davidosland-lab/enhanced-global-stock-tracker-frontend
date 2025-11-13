@echo off
echo ================================================================================
echo STARTING API WITH ALPHA VANTAGE FALLBACK
echo ================================================================================
echo.
echo This version will:
echo   1. Try Yahoo Finance first
echo   2. If that fails, use Alpha Vantage
echo   3. If both fail, show mock data so charts work
echo.

REM Kill existing Python
taskkill /F /IM python.exe 2>nul
timeout /t 2

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

python app_simple_api_with_av.py

pause
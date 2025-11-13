@echo off
echo ================================================================================
echo STARTING SIMPLE API SERVER (Compatible with finbert_charts.html)
echo ================================================================================
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul
timeout /t 2

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Starting Simple API that works with the HTML charts...
echo.

python app_simple_api.py

pause
@echo off
echo ================================================================================
echo STARTING WITH REAL DATA ONLY - NO FAKE/DEMO DATA
echo ================================================================================
echo.
echo Using:
echo   - Yahoo Finance (primary)
echo   - Alpha Vantage with your key: 68ZFANK047DL0KSR (backup)
echo   - NO FAKE/MOCK/DEMO DATA
echo.

REM Kill existing Python
taskkill /F /IM python.exe 2>nul
timeout /t 2

REM Clear cache
rmdir /s /q "%USERPROFILE%\.cache\py-yfinance" 2>nul

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

python app_real_data_only.py

pause
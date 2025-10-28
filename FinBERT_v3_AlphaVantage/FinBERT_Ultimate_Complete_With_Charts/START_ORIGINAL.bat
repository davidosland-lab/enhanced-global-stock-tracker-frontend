@echo off
echo ================================================================================
echo STARTING ORIGINAL FINBERT v3.0 WITH YOUR ALPHA VANTAGE KEY
echo ================================================================================
echo.
echo This uses the EXACT original code with only ONE change:
echo   - Added your Alpha Vantage key: 68ZFANK047DL0KSR
echo.

REM Set environment to avoid any issues
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Starting server...
echo ================================================================================
echo.

python app_finbert_ultimate_original_with_key.py

pause
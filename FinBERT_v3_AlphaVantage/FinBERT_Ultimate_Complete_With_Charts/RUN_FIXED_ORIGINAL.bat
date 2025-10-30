@echo off
echo ================================================================================
echo RUNNING FIXED ORIGINAL VERSION
echo ================================================================================
echo.

REM Kill existing Python
taskkill /F /IM python.exe 2>nul
timeout /t 2

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Starting the original code with your Alpha Vantage key...
echo This version has the bug fix already applied.
echo.

python app_finbert_ultimate_original_with_key.py

pause
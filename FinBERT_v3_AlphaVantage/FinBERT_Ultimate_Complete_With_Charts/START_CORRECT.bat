@echo off
echo ================================================================================
echo STARTING THE CORRECT FINBERT SERVER
echo ================================================================================
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul
timeout /t 2

REM Set environment
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Starting app_finbert_ultimate_original_with_key.py...
echo.
echo This should show endpoints like:
echo   /api/analyze
echo   /api/predict
echo   /api/train
echo   /api/technical
echo   /api/sentiment
echo.

python app_finbert_ultimate_original_with_key.py

pause
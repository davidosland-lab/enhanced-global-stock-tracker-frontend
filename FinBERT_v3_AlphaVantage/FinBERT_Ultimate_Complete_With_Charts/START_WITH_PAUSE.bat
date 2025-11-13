@echo off
echo ================================================================================
echo STARTING FINBERT WITH ERROR CAPTURE
echo ================================================================================
echo.

REM Clean environment
if exist ".env" del /f /q ".env"
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Starting server...
echo If it fails, the error will be shown below:
echo ================================================================================
echo.

python app_finbert_ultimate_av.py 2>&1

echo.
echo ================================================================================
echo Server stopped or failed to start.
echo Check the error message above.
echo ================================================================================
echo.
pause
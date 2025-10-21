@echo off
echo ============================================================
echo    ML STOCK PREDICTOR - FIXED VERSION
echo ============================================================
echo.

:: Clean environment
del /q .env 2>nul
del /q .flaskenv 2>nul
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

echo Starting fixed server...
echo.
echo Try these symbols that usually work:
echo   ETFs: SPY, QQQ, IWM, DIA
echo   Large Cap: MSFT, GOOGL, AMZN
echo   Australian: CBA, BHP, CSL (will add .AX)
echo.
echo ============================================================
echo Server: http://localhost:8000
echo ============================================================
echo.

python fixed_real_server.py

pause
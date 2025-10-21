@echo off
echo ============================================================
echo   ML STOCK PREDICTOR - REAL DATA SERVER
echo ============================================================
echo.
echo This server fetches REAL stock data!
echo Supports Australian stocks: CBA.AX, BHP.AX, etc.
echo.

:: Clean environment
del /q .env 2>nul
del /q .flaskenv 2>nul
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

:: Start server
echo Starting server with real Yahoo Finance data...
echo.
echo Try these symbols:
echo   Australian: CBA.AX, BHP.AX, WBC.AX, CSL.AX
echo   US Stocks: MSFT, AAPL, GOOGL, TSLA
echo.
echo ============================================================
echo Open browser: http://localhost:8000
echo ============================================================
echo.

python working_server.py

pause
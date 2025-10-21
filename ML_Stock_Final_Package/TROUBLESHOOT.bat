@echo off
echo ============================================================
echo         ML STOCK PREDICTOR - TROUBLESHOOTING TOOL
echo ============================================================
echo.

echo [1/5] Clearing Python cache...
rmdir /s /q "%LOCALAPPDATA%\py-cache" 2>nul
rmdir /s /q "__pycache__" 2>nul
del /q *.pyc 2>nul
echo       Done

echo [2/5] Clearing ML model cache...
del /q *.db 2>nul
del /q *.pkl 2>nul
echo       Done

echo [3/5] Testing Python installation...
python --version
if errorlevel 1 (
    echo       ERROR: Python not found!
    echo       Please install Python from python.org
    pause
    exit /b 1
)

echo [4/5] Testing configuration...
python -c "from config import ALPHA_VANTAGE_API_KEY; print(f'       API Key: {ALPHA_VANTAGE_API_KEY}')"
if errorlevel 1 (
    echo       ERROR: Configuration file issue!
)

echo [5/5] Testing data sources...
echo.
echo Testing Yahoo Finance...
python -c "import yfinance as yf; t=yf.Ticker('AAPL'); d=t.history(period='5d'); print(f'       Yahoo: OK - Got {len(d)} days')" 2>nul
if errorlevel 1 (
    echo       Yahoo: FAILED
) 

echo.
echo Testing Alpha Vantage...
python test_alpha_vantage.py 2>nul
if errorlevel 1 (
    echo       Alpha Vantage: FAILED or not configured
)

echo.
echo ============================================================
echo Troubleshooting complete!
echo.
echo If issues persist:
echo   1. Run: pip install -r requirements_windows_py312.txt
echo   2. Check internet connection
echo   3. Verify config.py has your API key
echo   4. Try running: python unified_ml_system.py
echo ============================================================
pause
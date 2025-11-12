@echo off
:: Quick Fix for yfinance Issues
color 0C
cls

echo ============================================================
echo  FINBERT - QUICK FIX FOR YFINANCE ISSUES
echo ============================================================
echo.

cd /d "%~dp0"

echo [STEP 1] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Virtual environment not found
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)
echo [OK] Environment activated
echo.

echo [STEP 2] Upgrading yfinance to latest version...
echo --------------------------------------------------------
echo This will fix most Yahoo Finance connection issues
echo.
pip uninstall -y yfinance
pip install yfinance --no-cache-dir
echo.
echo [OK] yfinance upgraded
echo.

echo [STEP 3] Upgrading related packages...
echo --------------------------------------------------------
pip install --upgrade requests urllib3 certifi --no-cache-dir
echo.
echo [OK] Packages upgraded
echo.

echo [STEP 4] Testing connection...
echo --------------------------------------------------------
python -c "import yfinance as yf; t=yf.Ticker('AAPL'); print('yfinance version:', yf.__version__); h=t.history(period='1d'); print('[OK] Can fetch data' if not h.empty else '[FAILED] No data')"
echo.

echo ============================================================
echo  FIX COMPLETE
echo ============================================================
echo.
echo Next steps:
echo   1. Close any running Python processes
echo   2. Run: RUN_STOCK_SCREENER_TEST.bat
echo   3. Check if errors are resolved
echo.
echo If you still see errors about indices:
echo   - Markets may be closed (weekend/holiday)
echo   - Check your internet connection
echo   - Try: DIAGNOSE_YFINANCE.bat for detailed diagnosis
echo.
pause

@echo off
REM ============================================================
REM ML STOCK PREDICTOR - FIXED FOR INVALID CRUMB ERROR
REM ============================================================
REM This script starts the fixed ML Stock Predictor server
REM with Yahoo Finance "Invalid Crumb" error workarounds
REM ============================================================

title ML Stock Predictor - Invalid Crumb Fix
color 0A
cls

echo ============================================================
echo    ML STOCK PREDICTOR - YAHOO FINANCE FIX
echo ============================================================
echo.
echo This version includes fixes for the "Invalid Crumb" error
echo.
echo Starting server setup...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM CRITICAL: Update yfinance to latest version
echo ============================================================
echo UPDATING YFINANCE TO LATEST VERSION...
echo ============================================================
echo.
pip install --upgrade yfinance
echo.
echo [OK] yfinance updated
echo.

REM Clear yfinance cache
echo Clearing yfinance cache...
python -c "import shutil, tempfile, os; cache_dir = os.path.join(tempfile.gettempdir(), 'yfinance'); shutil.rmtree(cache_dir) if os.path.exists(cache_dir) else None; print('[OK] Cache cleared')" 2>nul
echo.

REM Install other required packages
echo Installing/updating other required packages...
pip install --upgrade flask flask-cors pandas numpy requests

echo.
echo [OK] All packages installed/updated
echo.

REM Kill any existing server on port 8000
echo Checking for existing servers on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Clear the screen and show final message
cls
color 0A
echo ============================================================
echo    ML STOCK PREDICTOR - INVALID CRUMB FIX
echo ============================================================
echo.
echo FIXES APPLIED:
echo   - Multiple yfinance fallback methods
echo   - Cache clearing on each start
echo   - Session reset on failures
echo   - Alternative period formats
echo   - Threading disabled for stability
echo.
echo Server Configuration:
echo   - Port: 8000
echo   - URL: http://localhost:8000
echo   - Yahoo Finance: Primary (with fixes)
echo   - Alpha Vantage: Backup (API Key configured)
echo   - Australian stocks: Auto-detection enabled
echo.
echo ============================================================
echo.
echo Starting fixed server...
echo.
echo Once started, access the interface at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the fixed server
python server_fixed_crumb.py

REM If server exits, show message
echo.
echo ============================================================
echo Server stopped.
echo ============================================================
echo.
pause
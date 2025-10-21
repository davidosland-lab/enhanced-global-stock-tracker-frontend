@echo off
REM ============================================================
REM ML STOCK PREDICTOR - MINIMAL VERSION (NO ML DEPS)
REM ============================================================
REM Works with NumPy 2.x - No scikit-learn or xgboost needed
REM ============================================================

title ML Stock Predictor - Minimal Version
color 0A
cls

echo ============================================================
echo    ML STOCK PREDICTOR - MINIMAL VERSION
echo ============================================================
echo.
echo This version works with NumPy 2.x and doesn't need ML packages
echo Yahoo Finance and Alpha Vantage data fetching only
echo.
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

REM Install minimal requirements only
echo Installing minimal requirements...
pip install --upgrade yfinance flask flask-cors pandas requests

echo.
echo [OK] Requirements installed
echo.

REM Kill any existing server on port 8000
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Start server
cls
echo ============================================================
echo    ML STOCK PREDICTOR - MINIMAL VERSION
echo ============================================================
echo.
echo ✅ Works with NumPy 2.x (no compatibility issues)
echo ✅ No ML dependencies required
echo ✅ Yahoo Finance data fetching
echo ✅ Alpha Vantage backup
echo ✅ Australian stock auto-detection
echo.
echo Server starting at: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

python server_minimal.py

echo.
echo Server stopped.
pause
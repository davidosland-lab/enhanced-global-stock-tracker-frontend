@echo off
setlocal enabledelayedexpansion

echo =====================================================
echo     UNIFIED STOCK ANALYSIS SYSTEM LAUNCHER
echo     Windows 11 Compatible Version
echo =====================================================
echo.

REM Set UTF-8 encoding for Windows 11
chcp 65001 > nul 2>&1

REM Flask environment variable for Windows 11 compatibility
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUNBUFFERED=1

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

echo.
echo [2/3] Installing required packages...
echo This may take a few minutes on first run...
echo.

REM Install packages with error checking
pip install --quiet --upgrade pip
pip install --quiet yfinance flask flask-cors
pip install --quiet pandas numpy scikit-learn
pip install --quiet plotly requests
pip install --quiet ta-lib 2>nul || pip install --quiet ta

echo.
echo [3/3] Starting Stock Analysis System...
echo.
echo =====================================================
echo Server will start at: http://localhost:8000
echo.
echo Features:
echo - Real-time Yahoo Finance data
echo - Alpha Vantage fallback (API key integrated)
echo - Machine Learning predictions
echo - Technical indicators
echo - Candlestick charts
echo - Australian stocks support (.AX suffix)
echo.
echo Press Ctrl+C to stop the server
echo =====================================================
echo.

REM Start the Python application
python stock_analysis_unified_fixed.py

if errorlevel 1 (
    echo.
    echo =====================================================
    echo ERROR: Application failed to start
    echo.
    echo Possible causes:
    echo 1. Port 8000 is already in use
    echo 2. Missing dependencies
    echo 3. Python environment issues
    echo.
    echo Try running: pip install -r requirements.txt
    echo =====================================================
)

echo.
echo Application has stopped.
echo.
pause
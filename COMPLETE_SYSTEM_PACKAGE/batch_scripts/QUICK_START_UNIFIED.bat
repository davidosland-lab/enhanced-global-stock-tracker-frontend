@echo off
setlocal enabledelayedexpansion

:: Set console properties for better visibility
mode con cols=100 lines=40
color 0A
title Quick Start - Unified Robust Stock Analysis

cls
echo ================================================================================
echo                    UNIFIED ROBUST STOCK ANALYSIS - QUICK START
echo ================================================================================
echo.
echo This will install dependencies and start the application automatically
echo.

:: Check Python
echo [STEP 1] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo.

:: Quick install essential packages (no venv for quick start)
echo [STEP 2] Installing essential packages...
echo.
echo Installing Flask and web components...
pip install flask flask-cors --quiet --disable-pip-version-check
echo [OK] Web framework installed
echo.

echo Installing data processing libraries...
pip install pandas numpy --quiet --disable-pip-version-check
echo [OK] Data libraries installed
echo.

echo Installing market data providers...
pip install yfinance requests --quiet --disable-pip-version-check
echo [OK] Market data providers installed
echo.

:: Try to install scikit-learn, but don't fail if it doesn't work
echo Installing ML components (optional)...
pip install scikit-learn --quiet --disable-pip-version-check >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] ML predictions enabled
) else (
    echo [SKIP] ML predictions disabled (scikit-learn not available)
)
echo.

:: Start the application
echo [STEP 3] Starting the application...
echo.
echo ================================================================================
echo                              APPLICATION STARTING
echo ================================================================================
echo.
echo Server URL: http://localhost:5000
echo.
echo FEATURES:
echo   [✓] 100%% Real Market Data - NO fake/demo data
echo   [✓] Yahoo Finance with rate limiting
echo   [✓] Alpha Vantage fallback with API key
echo   [✓] Technical indicators (RSI, MACD, Bollinger Bands)
echo   [✓] Market sentiment (VIX, Treasury yields, Dollar index)
echo   [✓] Chart zoom functionality
echo   [✓] Australian stock support (.AX)
echo.
echo HOW TO USE:
echo   1. Wait for "Server running" message
echo   2. Open browser to: http://localhost:5000
echo   3. Enter any stock symbol (e.g., AAPL, MSFT, CBA)
echo   4. Click "Get Data" to fetch real market data
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

:: Check if app file exists
if not exist "app_unified_robust.py" (
    echo ERROR: app_unified_robust.py not found!
    echo.
    pause
    exit /b 1
)

:: Run the application
python app_unified_robust.py

:: Keep window open on error
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo Application stopped. Check error messages above.
    echo ================================================================================
    echo.
)

pause
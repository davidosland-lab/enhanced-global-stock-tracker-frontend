@echo off
setlocal enabledelayedexpansion

:: Set window title
title Unified Robust Stock Analysis System

echo ===============================================================================
echo UNIFIED ROBUST STOCK ANALYSIS SYSTEM
echo ===============================================================================
echo.
echo Starting the application...
echo.

:: Check if app file exists
if not exist "app_unified_robust.py" (
    echo ERROR: app_unified_robust.py not found!
    echo Please make sure the file is in the current directory.
    echo.
    pause
    exit /b 1
)

:: Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo [1/3] No virtual environment found, using global Python...
)
echo.

:: Check dependencies
echo [2/3] Checking dependencies...
python -c "import flask, pandas, yfinance, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies are missing!
    echo Please run INSTALL_UNIFIED_ROBUST.bat first
    echo.
    echo Attempting to install missing dependencies...
    pip install flask flask-cors pandas yfinance requests --quiet
    echo.
)

:: Check for scikit-learn (optional)
python -c "import sklearn" >nul 2>&1
if %errorlevel% neq 0 (
    echo NOTE: scikit-learn not found - ML predictions will be unavailable
) else (
    echo ML predictions module found
)
echo.

:: Start the application
echo [3/3] Starting the Flask server...
echo.
echo ===============================================================================
echo SERVER INFORMATION
echo ===============================================================================
echo.
echo Local URL:  http://localhost:5000
echo Network URL: http://%COMPUTERNAME%:5000
echo.
echo Features Available:
echo   - 100%% Real Market Data (NO synthetic/demo data)
echo   - Yahoo Finance with rate limiting
echo   - Alpha Vantage fallback (API key included)
echo   - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
echo   - Market sentiment (VIX, yields, dollar index)
echo   - ML predictions (if scikit-learn installed)
echo   - Chart zoom functionality
echo   - Australian stock support (.AX)
echo.
echo Press Ctrl+C to stop the server
echo ===============================================================================
echo.

:: Run the application
python app_unified_robust.py

:: If the app exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo ERROR: The application stopped unexpectedly
    echo ===============================================================================
    echo.
    echo Please check the error messages above.
    echo.
)

echo.
echo Press any key to close this window...
pause >nul
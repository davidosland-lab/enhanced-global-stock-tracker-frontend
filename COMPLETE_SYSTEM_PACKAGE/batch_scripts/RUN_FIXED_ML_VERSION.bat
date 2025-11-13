@echo off
setlocal enabledelayedexpansion

:: Set window title
title Fixed ML Stock Analysis System

echo ===============================================================================
echo UNIFIED ROBUST STOCK ANALYSIS - FIXED ML VERSION
echo ===============================================================================
echo.
echo Starting the application with fixed ML predictions...
echo.

:: Check which file to run
if exist "app_unified_robust_fixed.py" (
    set APP_FILE=app_unified_robust_fixed.py
    echo Using: app_unified_robust_fixed.py (Fixed ML Version)
) else if exist "app_unified_robust.py" (
    set APP_FILE=app_unified_robust.py
    echo Using: app_unified_robust.py
) else (
    echo ERROR: No application file found!
    echo Please ensure app_unified_robust_fixed.py or app_unified_robust.py exists
    echo.
    pause
    exit /b 1
)
echo.

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
    echo Installing missing dependencies...
    pip install flask flask-cors pandas numpy yfinance requests --quiet
    echo.
)

:: Check for scikit-learn (optional but recommended for ML)
python -c "import sklearn" >nul 2>&1
if %errorlevel% neq 0 (
    echo NOTE: scikit-learn not found - ML predictions will be limited
    echo To enable full ML features, run: pip install scikit-learn
) else (
    echo ML predictions module ready
)
echo.

:: Start the application
echo [3/3] Starting the Flask server...
echo.
echo ===============================================================================
echo FIXED ML VERSION - IMPROVEMENTS
echo ===============================================================================
echo.
echo ✓ Fixed JavaScript tab switching error
echo ✓ Improved ML model training and predictions
echo ✓ Better error handling and user feedback
echo ✓ Price ranges for multi-day predictions
echo ✓ ML status indicator in header
echo ✓ Model info display (training time, features)
echo.
echo Server URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ===============================================================================
echo.

:: Run the application
python %APP_FILE%

:: If the app exits, pause to show any error messages
if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo ERROR: The application stopped unexpectedly
    echo ===============================================================================
    echo.
)

echo.
echo Press any key to close this window...
pause >nul
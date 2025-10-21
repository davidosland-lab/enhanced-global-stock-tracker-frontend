@echo off
cls
echo ================================================================================
echo                        UNIFIED STOCK ANALYSIS SYSTEM
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Trying with --without-pip option...
        python -m venv venv --without-pip
        venv\Scripts\python.exe -m ensurepip
    )
) else (
    echo [2/4] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
python -m pip install --upgrade pip >nul 2>&1

REM Install core dependencies
echo.
echo [4/4] Installing dependencies...
echo.
echo Installing Flask and CORS...
pip install flask flask-cors >nul 2>&1

echo Installing yfinance for Yahoo data...
pip install yfinance >nul 2>&1

echo Installing pandas and numpy...
pip install "numpy<2.0" pandas >nul 2>&1

echo Installing requests for Alpha Vantage...
pip install requests >nul 2>&1

echo Installing scikit-learn for ML predictions...
pip install scikit-learn >nul 2>&1

REM Try to install TA-Lib (might fail on Windows without proper setup)
echo Installing technical indicators...
pip install TA-Lib >nul 2>&1
if errorlevel 1 (
    echo NOTE: TA-Lib installation failed - technical indicators may be limited
    echo For full functionality, install TA-Lib manually
)

echo.
echo ================================================================================
echo                           STARTING UNIFIED SYSTEM
echo ================================================================================
echo.
echo Server Configuration:
echo - URL: http://localhost:8000
echo - Yahoo Finance: Primary data source
echo - Alpha Vantage: Backup data source (API key configured)
echo - ML Predictions: Enabled
echo - Technical Analysis: Enabled
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Start the server
python unified_stock_system.py

REM If server stops, show message
echo.
echo ================================================================================
echo Server stopped.
pause
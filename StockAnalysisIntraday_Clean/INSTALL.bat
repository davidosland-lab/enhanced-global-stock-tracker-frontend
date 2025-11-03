@echo off
title Stock Analysis Installer
color 0A
cls

echo ============================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT - INSTALLER
echo ============================================================
echo.

REM Check Python installation
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://python.org
    echo.
    echo IMPORTANT: During installation, make sure to:
    echo   1. Check "Add Python to PATH"
    echo   2. Install for all users (recommended)
    echo.
    pause
    exit /b 1
)

python --version
echo Python is installed successfully!
echo.

REM Upgrade pip
echo [2/3] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install requirements
echo [3/3] Installing required packages...
echo This may take 2-3 minutes on first installation...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Some packages failed to install. Trying alternative method...
    echo ============================================================
    
    REM Install packages one by one
    pip install flask
    pip install flask-cors
    pip install yfinance
    pip install pandas
    pip install numpy
    pip install scikit-learn
    pip install requests
    pip install ta 2>nul
)

echo.
echo ============================================================
echo     INSTALLATION COMPLETE!
echo ============================================================
echo.
echo To start the application, run: START.bat
echo.
pause
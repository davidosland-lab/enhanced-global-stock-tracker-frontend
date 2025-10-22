@echo off
title Stock Analysis System Installer
color 0A

echo ========================================================
echo     STOCK ANALYSIS SYSTEM - COMPLETE INSTALLER
echo     Windows 11 Compatible Version
echo ========================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1

REM Check Python installation
echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
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

REM Create virtual environment (optional but recommended)
echo Creating virtual environment (optional)...
python -m venv venv 2>nul
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Installing required packages...
echo ========================================================

REM Upgrade pip first
python -m pip install --upgrade pip

REM Core packages
echo Installing Flask and web packages...
pip install flask flask-cors

echo Installing data packages...
pip install yfinance pandas numpy

echo Installing ML packages...
pip install scikit-learn

echo Installing visualization packages...
pip install plotly

echo Installing additional packages...
pip install requests
pip install ta 2>nul

echo.
echo ========================================================
echo Installation complete!
echo.
echo Starting Stock Analysis System...
echo Server URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================================
echo.

REM Keep window open and run the application
cmd /k python stock_analysis_unified_fixed.py
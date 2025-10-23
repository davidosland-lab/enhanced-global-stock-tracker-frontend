@echo off
cls
title Stock Tracker Pro - Complete Installation
color 0A

echo ============================================================
echo  Stock Tracker Pro - Windows 11 Installation
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/3] Python is installed
python --version
echo.

REM Install packages
echo [2/3] Installing required packages...
echo This may take a few minutes on first run...
pip install -q fastapi uvicorn yfinance pandas numpy scikit-learn requests websockets aiofiles python-multipart

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Package installation failed
    echo Trying alternative installation...
    python -m pip install fastapi uvicorn yfinance pandas numpy scikit-learn requests websockets aiofiles python-multipart
)

echo.
echo [3/3] Starting system...
echo.

REM Start the Python launcher
python start_all_services.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start system
    pause
)
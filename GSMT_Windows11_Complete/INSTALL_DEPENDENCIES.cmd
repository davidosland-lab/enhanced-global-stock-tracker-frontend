@echo off
cls
color 0E
title GSMT - Installing Required Dependencies

echo ================================================
echo  GSMT - Dependency Installation
echo  Installing Required Python Packages
echo ================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found. Installing required packages...
echo.

echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 2: Installing core dependencies...
python -m pip install fastapi uvicorn yfinance

echo.
echo Step 3: Installing additional packages...
python -m pip install python-multipart pandas numpy requests

echo.
echo Step 4: Installing optional packages (ignore errors)...
python -m pip install cachetools 2>nul

echo.
echo ================================================
echo  Installation Complete!
echo ================================================
echo.
echo All required dependencies have been installed.
echo You can now run START_LIVE_BACKEND_SIMPLE.cmd
echo.
pause
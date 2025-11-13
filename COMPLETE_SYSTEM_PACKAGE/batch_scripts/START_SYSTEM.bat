@echo off
title Complete Stock Tracker System
color 0A

echo ========================================================
echo        COMPLETE STOCK TRACKER SYSTEM STARTUP
echo                 Windows 11 Compatible
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

REM Check current directory
echo Current Directory: %CD%
echo.

REM Check if required files exist
if not exist "index.html" (
    echo ERROR: index.html not found!
    echo Please ensure you're running this from the correct directory.
    pause
    exit /b 1
)

if not exist "backend.py" (
    echo ERROR: backend.py not found!
    echo Please ensure all files are extracted properly.
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking Python packages...
pip list | findstr /i "fastapi uvicorn yfinance pandas numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install fastapi uvicorn yfinance pandas numpy scikit-learn websockets requests
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Run the Python startup script
echo.
echo Starting all services...
echo.
python start_all_services.py

REM If Python script exits, pause to show any errors
if errorlevel 1 (
    echo.
    echo ERROR: System startup failed!
    pause
)
@echo off
title Installing GSMT v9.3 Dependencies
color 0E

echo ============================================================
echo   Global Stock Market Tracker v9.3
echo   Dependency Installation
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Python detected. Installing required packages...
echo.

echo [1/8] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/8] Installing FastAPI...
pip install fastapi

echo.
echo [3/8] Installing Uvicorn server...
pip install uvicorn[standard]

echo.
echo [4/8] Installing yfinance for Yahoo Finance data...
pip install yfinance

echo.
echo [5/8] Installing pandas for data processing...
pip install pandas

echo.
echo [6/8] Installing pytz for timezone handling...
pip install pytz

echo.
echo [7/8] Installing numpy...
pip install numpy

echo.
echo [8/8] Installing cachetools for performance...
pip install cachetools

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo All dependencies have been installed successfully.
echo You can now run START_GSMT.bat to launch the application.
echo.
pause
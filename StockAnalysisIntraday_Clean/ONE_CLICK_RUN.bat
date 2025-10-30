@echo off
title Stock Analysis - One Click Run
color 0A
cls

echo ============================================================
echo     ONE-CLICK STOCK ANALYSIS SYSTEM
echo ============================================================
echo.
echo This will install dependencies (if needed) and start the app
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
)

echo Python found!
echo.

REM Install packages quietly (will skip if already installed)
echo Installing/checking packages (this may take 1-2 minutes)...
pip install flask >nul 2>&1
pip install flask-cors >nul 2>&1
pip install yfinance >nul 2>&1
pip install pandas >nul 2>&1
pip install numpy >nul 2>&1
pip install scikit-learn >nul 2>&1
pip install requests >nul 2>&1

echo.
echo Starting application...
echo.
echo ============================================================
echo Server URL: http://localhost:8000
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Set environment variables and run
set FLASK_SKIP_DOTENV=1
set PYTHONDONTWRITEBYTECODE=1

REM This keeps the window open no matter what happens
cmd /c python app.py & pause
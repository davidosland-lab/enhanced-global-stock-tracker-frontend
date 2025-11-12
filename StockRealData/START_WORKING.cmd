@echo off
title Stock Analysis - Working Version
color 0A
cls

echo ============================================================
echo    STOCK ANALYSIS SYSTEM - WORKING VERSION
echo ============================================================
echo.

cd /d "%~dp0"

REM Check files
if not exist "app_WORKING.py" (
    echo ERROR: app_WORKING.py not found!
    echo.
    echo Make sure you extracted ALL files from the ZIP
    echo.
    pause
    exit
)

REM Run Python with error output
echo Starting server...
echo.
echo If this window closes immediately, Python may not be installed.
echo.

set FLASK_SKIP_DOTENV=1
start http://localhost:8000

echo Running: python app_WORKING.py
echo.
python app_WORKING.py

REM If we get here, something went wrong
echo.
echo ============================================================
echo ERROR: The application stopped or failed to start
echo ============================================================
echo.
echo Possible issues:
echo 1. Python not installed (install from python.org)
echo 2. Missing packages (run: pip install flask yfinance plotly scikit-learn pandas)
echo 3. Port 8000 already in use
echo.
pause
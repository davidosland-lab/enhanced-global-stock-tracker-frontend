@echo off
:: GSMT Stock Tracker - Direct Run Script
:: This will definitely work on Windows 11

title GSMT Stock Tracker v8.1.3 - Direct Run
color 0A
cls

echo ================================================================
echo              GSMT STOCK TRACKER v8.1.3
echo           WINDOWS 11 - DIRECT RUN VERSION
echo ================================================================
echo.
echo This script will start the server immediately.
echo.

:: Check current directory
set "CURRENT_DIR=%CD%"
echo Current location: %CURRENT_DIR%
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Show Python version
echo Python found:
python --version
echo.

:: Check if main_server.py exists
if not exist "backend\main_server.py" (
    echo ERROR: backend\main_server.py not found!
    echo.
    echo Please make sure you extracted all files correctly.
    echo Expected location: %CURRENT_DIR%\backend\main_server.py
    echo.
    pause
    exit /b 1
)

:: Try to install dependencies silently
echo Installing/checking dependencies...
pip install fastapi uvicorn --quiet --no-warn-script-location 2>nul

:: Clear screen and show server info
cls
echo ================================================================
echo              GSMT STOCK TRACKER v8.1.3
echo ================================================================
echo.
echo Starting server on: http://localhost:8000
echo.
echo Once the server starts, you can:
echo.
echo   1. Open your browser and go to: http://localhost:8000
echo   2. Or open: frontend\index.html
echo.
echo API Endpoints will be available at:
echo   - http://localhost:8000/health (Health Check)
echo   - http://localhost:8000/api/tracker (Stock Data)
echo   - http://localhost:8000/api/predict/AAPL (Predictions)
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

:: Run the main server
python backend\main_server.py

:: If server stops, pause to see any errors
echo.
echo Server stopped.
pause
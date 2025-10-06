@echo off
cls
echo ============================================
echo   COMPLETE STOCK TRACKER - Windows 11
echo   Backend Server Launcher
echo ============================================
echo.
echo Starting server on http://localhost:8002
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [1/3] Python installation found:
python --version
echo.

echo [2/3] Installing/updating dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
echo Dependencies installed.
echo.

echo [3/3] Starting Flask backend server...
echo ============================================
echo.
echo Server is starting on: http://localhost:8002
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================
echo.

REM Start the Flask backend
python backend.py

pause
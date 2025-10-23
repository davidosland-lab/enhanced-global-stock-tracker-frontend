@echo off
echo ========================================
echo CBA Enhanced Backend Server Launcher
echo Windows 11 Optimized - Port 8002
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version

echo.
echo [2/3] Installing/Updating dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [3/3] Starting backend server on http://localhost:8002
echo.
echo ========================================
echo Server starting... Press Ctrl+C to stop
echo ========================================
echo.

REM Start the Flask backend
python backend.py

pause
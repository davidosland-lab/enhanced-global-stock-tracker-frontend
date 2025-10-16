@echo off
echo ============================================================
echo Stock Tracker V9 - Complete Edition
echo Starting all services...
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start services
echo Starting services...
python start_services.py

pause
@echo off
REM ============================================
REM ML Core Enhanced Production System
REM Quick Start Script
REM ============================================

echo.
echo ============================================
echo ML CORE ENHANCED PRODUCTION SYSTEM
echo Starting service...
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run install_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the ML Core system
echo Starting ML Core on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo ============================================
echo.

python ml_core_enhanced_production.py

echo.
echo ============================================
echo Server stopped
echo ============================================
pause
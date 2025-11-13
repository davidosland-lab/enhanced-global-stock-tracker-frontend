@echo off
REM ===================================================================
REM FinBERT v4.4 - Server Startup Script
REM ===================================================================
REM This script starts the FinBERT prediction server
REM Make sure you've run INSTALL.bat first!
REM ===================================================================

echo ========================================
echo   FinBERT v4.4 Server Startup
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [OK] Found virtual environment
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    echo Please run INSTALL.bat first!
    echo.
    pause
    exit /b 1
)

echo.
echo Starting FinBERT server...
echo.
echo Server will be available at: http://localhost:5002
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python app_finbert_v4_dev.py

pause

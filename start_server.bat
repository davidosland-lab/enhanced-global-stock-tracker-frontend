@echo off
echo ======================================================================
echo       STOCK ANALYSIS SYSTEM - SERVER LAUNCHER
echo ======================================================================
echo.
echo Starting server...
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variable to avoid UTF-8 errors
set FLASK_SKIP_DOTENV=1

REM Start the server
echo Server starting at: http://localhost:8000
echo.
echo To access the system:
echo 1. Open your browser
echo 2. Go to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================
python stock_analysis_fixed_charts.py

pause
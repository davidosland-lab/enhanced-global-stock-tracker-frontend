@echo off
echo ======================================================================
echo    STOCK ANALYSIS - COMPLETE EDITION (Yahoo + Alpha Vantage)
echo ======================================================================
echo.
echo Starting Complete Edition with Alpha Vantage integration...
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

REM Set environment variable
set FLASK_SKIP_DOTENV=1

REM Start the complete version
echo Server starting at: http://localhost:8000
echo.
echo Features:
echo - Yahoo Finance primary data source
echo - Alpha Vantage automatic fallback
echo - 12 Technical indicators
echo - Professional charts
echo.
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================
python stock_analysis_complete.py

pause
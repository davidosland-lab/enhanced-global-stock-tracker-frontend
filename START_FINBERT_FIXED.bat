@echo off
echo ========================================================
echo Starting FinBERT Ultimate Trading System v3.0 - FIXED
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Start the server
echo Starting FinBERT server...
echo.
echo The system will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app_finbert_complete_fixed.py

pause
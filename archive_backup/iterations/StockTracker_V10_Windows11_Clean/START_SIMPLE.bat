@echo off
title Stock Tracker - Simple Start
color 0A

echo ================================================
echo    STOCK TRACKER - SIMPLIFIED VERSION
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Installing required packages (this may take a few minutes)...
echo.

:: Install basic requirements
pip install fastapi uvicorn pandas numpy yfinance scikit-learn beautifulsoup4 feedparser aiohttp requests lxml > install_log.txt 2>&1

echo Packages installed.
echo.
echo Starting Stock Tracker on port 8000...
echo.

:: Start the unified backend
echo ================================================
echo    SERVER STARTING...
echo ================================================
echo.
echo The server will start in a moment.
echo Once started, your browser will open automatically.
echo.
echo To stop the server, press Ctrl+C in this window.
echo.

:: Wait a moment
timeout /t 3 /nobreak >nul

:: Start browser (will open after server starts)
start /b cmd /c "timeout /t 5 >nul && start http://localhost:8000/prediction_center_fixed.html"

:: Run the server
python unified_backend.py

pause
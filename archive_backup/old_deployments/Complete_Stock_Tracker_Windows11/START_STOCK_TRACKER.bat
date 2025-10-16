@echo off
:: Complete Stock Tracker - Desktop Launcher
:: Place this file on your Desktop for easy access

cls
color 0A
echo ============================================
echo    COMPLETE STOCK TRACKER - WINDOWS 11
echo ============================================
echo.
echo Starting Stock Tracker System...
echo.

:: Change to the correct directory
cd /d "C:\StockTrack\Complete_Stock_Tracker_Windows11"

:: Check if we're in the right directory
if not exist backend.py (
    echo ERROR: Cannot find backend.py
    echo Please ensure this script is in the correct location
    echo Expected path: C:\StockTrack\Complete_Stock_Tracker_Windows11
    pause
    exit /b 1
)

:: Start the backend server
echo [*] Starting backend server on port 8002...
echo.
echo ============================================
echo    Server Status: STARTING
echo    URL: http://localhost:8002
echo ============================================
echo.

:: Launch browser after 3 seconds
start /min cmd /c "timeout /t 3 >nul && start http://localhost:8002"

:: Run the Python backend
python backend.py

:: If the server stops, show message
echo.
echo ============================================
echo    Server has stopped
echo ============================================
pause
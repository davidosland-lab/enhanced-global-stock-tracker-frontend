@echo off
REM ====================================================================================
REM Trading System Web Control Center - Quick Start
REM ====================================================================================
REM 
REM This script starts the web control center and opens it in your default browser.
REM 
REM Usage:
REM   Double-click this file, or run from command prompt:
REM   START_WEB_CONTROL_CENTER.bat
REM 
REM ====================================================================================

echo.
echo ================================================================================
echo TRADING SYSTEM WEB CONTROL CENTER - STARTING
echo ================================================================================
echo.

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [ERROR] Flask is not installed!
    echo.
    echo Installing Flask and flask-cors...
    echo.
    pip install flask flask-cors
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install Flask. Please install manually:
        echo   pip install flask flask-cors
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Flask installed successfully!
    echo.
)

REM Check if we're in the correct directory
if not exist "web_control_center.py" (
    echo [ERROR] web_control_center.py not found in current directory!
    echo.
    echo Please run this script from the ULTIMATE_v193_COMPLETE directory.
    echo.
    pause
    exit /b 1
)

echo [OK] Starting web server...
echo.
echo Access the control panel at:
echo   Local:   http://localhost:5000
echo   Network: http://YOUR-IP:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Start the web control center
python web_control_center.py

pause

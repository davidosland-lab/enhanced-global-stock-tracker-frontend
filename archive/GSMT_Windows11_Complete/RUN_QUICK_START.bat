@echo off
:: Quick Start Script - Runs both server and opens browser

echo ============================================================
echo  GSMT Enhanced Stock Tracker - Quick Start
echo ============================================================
echo.

:: Check if installer has been run
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting server in background...
start /min cmd /c START_SERVER.bat

echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

echo Opening dashboard in browser...
start http://localhost:8000

echo.
echo ============================================================
echo  Server is running in the background
echo  Dashboard should open in your browser
echo.
echo  To stop the server, run STOP_SERVER.bat
echo ============================================================
echo.
pause
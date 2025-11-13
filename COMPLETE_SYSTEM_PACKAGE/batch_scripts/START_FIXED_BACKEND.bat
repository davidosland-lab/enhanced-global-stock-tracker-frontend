@echo off
cls
echo ============================================================
echo  Stock Tracker Pro - Fixed Backend Launcher
echo  Version 7.3 - Windows 11 Edition
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

echo Starting Complete Fixed Backend...
echo This will run both main (8002) and ML (8004) servers
echo.

REM Kill any existing Python processes on ports 8002 and 8004
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do (
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo  Starting servers...
echo ============================================================
echo.

REM Run the complete backend
python FINAL_COMPLETE_BACKEND.py

pause
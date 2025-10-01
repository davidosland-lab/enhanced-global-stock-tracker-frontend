@echo off
:: Simple CMD Launcher - Avoids PowerShell Issues
:: Just double-click this file to start!

title GSMT Stock Tracker Server

:: Force use of Command Prompt (not PowerShell)
if defined PSModulePath (
    echo Detected PowerShell environment. Switching to CMD...
    cmd /c "%~f0"
    exit
)

color 0A
cls

echo ============================================================
echo  GSMT STOCK TRACKER - QUICK START
echo ============================================================
echo.

:: Navigate to the correct directory
cd /d "C:\GSMT\GSMT_Windows11_Complete"

:: Kill existing Python processes (may fail, that's OK)
taskkill /F /IM python.exe 2>nul >nul

:: Use venv's Python directly without activation
echo Starting server (no activation needed)...
echo.
echo Server URL: http://localhost:8000
echo.
echo Testing which backend works...
echo.

:: Try test server first (most reliable)
venv\Scripts\python.exe backend\test_server.py 2>nul
if %errorlevel% equ 0 goto :END

:: Try simple backend
echo Test server didn't start, trying simple backend...
venv\Scripts\python.exe backend\simple_ml_backend.py 2>nul
if %errorlevel% equ 0 goto :END

:: Try enhanced backend
echo Simple backend didn't start, trying enhanced backend...
venv\Scripts\python.exe backend\enhanced_ml_backend.py 2>nul
if %errorlevel% equ 0 goto :END

:: If all fail, show error
echo.
echo ============================================================
echo  ERROR: Could not start any backend!
echo ============================================================
echo.
echo Please try:
echo 1. Run FIX_INSTALLATION.bat
echo 2. Or manually run in Command Prompt (not PowerShell):
echo    cd C:\GSMT\GSMT_Windows11_Complete
echo    venv\Scripts\python.exe backend\test_server.py
echo.

:END
pause
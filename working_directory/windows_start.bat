@echo off
REM ========================================
REM Stock Tracker Windows 11 Startup Script
REM ========================================

echo.
echo =====================================
echo   STOCK TRACKER - WINDOWS 11 EDITION
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python detected...

REM Navigate to script directory
cd /d "%~dp0"
echo [2/5] Working directory: %CD%

REM Install requirements
echo [3/5] Installing Python dependencies...
pip install -q -r requirements.txt 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may have failed to install
    echo Attempting to continue anyway...
)

REM Kill any existing Python process on port 8002
echo [4/5] Checking for existing services on port 8002...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Killing existing process on port 8002...
    taskkill /F /PID %%a 2>nul
)

REM Start the backend
echo [5/5] Starting backend API server...
echo.
echo =====================================
echo   BACKEND STARTING ON PORT 8002
echo =====================================
echo.
echo Backend URL: http://localhost:8002
echo.
echo Once started, open your browser and navigate to:
echo.
echo   1. Technical Analysis:
echo      file:///%CD:\=/%/modules/technical_analysis_enhanced.html
echo.
echo   2. Prediction Centre:
echo      file:///%CD:\=/%/modules/predictions/prediction_centre_advanced.html
echo.
echo   3. Desktop Version:
echo      file:///%CD:\=/%/modules/technical_analysis_desktop.html
echo.
echo   4. Diagnostic Tool:
echo      file:///%CD:\=/%/diagnostic_tool.html
echo.
echo Press Ctrl+C to stop the server
echo =====================================
echo.

REM Start the backend
python backend_fixed_v2.py

REM If backend exits, pause so user can see any errors
pause
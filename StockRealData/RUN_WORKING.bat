@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS - WORKING VERSION
echo    This version uses the simplified Yahoo Finance calls
echo ============================================================
echo.

REM Check if in correct directory
cd /d "%~dp0"
echo Working Directory: %CD%
echo.

REM Check if app_WORKING.py exists
if not exist "app_WORKING.py" (
    echo [ERROR] app_WORKING.py not found!
    echo Please ensure all files are extracted.
    pause
    exit /b 1
)

REM Use venv Python if available, otherwise system Python
if exist "venv\Scripts\python.exe" (
    echo [OK] Using virtual environment Python
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    echo [INFO] Using system Python
    set PYTHON_CMD=python
)

REM Display Python version
echo Python Version:
%PYTHON_CMD% --version
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONUNBUFFERED=1

REM Start server
echo ============================================================
echo Starting server at http://localhost:8000
echo ============================================================
echo.
echo This version WORKS because it uses simple Yahoo Finance calls
echo No complex parameters that break the API
echo.

REM Open browser after short delay
timeout /t 3 /nobreak >nul
start "" "http://localhost:8000"

REM Run the application
%PYTHON_CMD% app_WORKING.py

echo.
echo Server stopped.
pause
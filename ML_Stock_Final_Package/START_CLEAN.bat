@echo off
echo ============================================================
echo      ML STOCK PREDICTOR - CLEAN START
echo ============================================================
echo.

:: Clean up any problematic files
echo [1/4] Cleaning up problematic files...
del /q .env 2>nul
del /q .env.* 2>nul
del /q .flaskenv 2>nul
del /q *.pyc 2>nul
rmdir /s /q __pycache__ 2>nul
echo       Cleanup complete

:: Set environment to skip dotenv
echo [2/4] Setting environment...
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
echo       Environment configured

:: Check Python
echo [3/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

:: Start the simple server
echo [4/4] Starting server...
echo.
echo ============================================================
echo Server starting on http://localhost:8000
echo Press Ctrl+C to stop
echo ============================================================
echo.

python simple_server.py

echo.
echo ============================================================
echo Server stopped.
echo ============================================================
pause
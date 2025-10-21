@echo off
cls
echo ============================================================
echo ML STOCK PREDICTOR - FINAL WORKING VERSION
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing packages...
pip install flask flask-cors yfinance pandas numpy requests --no-cache-dir -q

echo.
echo ============================================================
echo STARTING SERVER...
echo ============================================================
echo.

REM Start the server
python final_working_server.py

REM If server fails, try the simple test
if %errorlevel% neq 0 (
    echo.
    echo Server failed to start. Opening simple test interface...
    start simple_test.html
)

pause
@echo off
REM ====================================================================
REM  DASHBOARD STARTER - Windows Batch File
REM  Double-click this file to start the dashboard
REM ====================================================================

echo.
echo ================================================================
echo           STARTING LIVE TRADING DASHBOARD
echo ================================================================
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check if required files exist
echo Checking required files...
if not exist "live_trading_dashboard.py" (
    echo [ERROR] live_trading_dashboard.py not found!
    echo Please make sure you're running this from the finbert_v4.4.4 directory
    echo.
    pause
    exit /b 1
)
echo [OK] live_trading_dashboard.py found

if not exist "templates\dashboard.html" (
    echo [WARNING] templates\dashboard.html not found!
    echo You may need to copy the templates folder from the deployment package
    echo.
)

if not exist "static\css\dashboard.css" (
    echo [WARNING] static\css\dashboard.css not found!
    echo You may need to copy the static folder from the deployment package
    echo.
)

REM Install dependencies
echo.
echo Installing/checking dependencies...
echo (This may take a moment on first run)
python -m pip install --quiet --upgrade pip >nul 2>&1
python -m pip install --quiet flask flask-cors pandas numpy >nul 2>&1
echo [OK] Dependencies ready
echo.

REM Start the dashboard
echo ================================================================
echo              STARTING DASHBOARD SERVER...
echo ================================================================
echo.
echo Dashboard will be available at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.
echo ----------------------------------------------------------------
echo.

python live_trading_dashboard.py

REM If we get here, the server has stopped
echo.
echo ================================================================
echo              DASHBOARD SERVER STOPPED
echo ================================================================
echo.
pause

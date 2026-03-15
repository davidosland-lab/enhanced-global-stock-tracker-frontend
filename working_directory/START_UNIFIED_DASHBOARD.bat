@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  START UNIFIED TRADING DASHBOARD
REM  Activates virtual environment and starts the dashboard
REM ═══════════════════════════════════════════════════════════════════════════

REM Change to script directory
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   STARTING UNIFIED TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Expected location: %CD%\venv\Scripts\activate.bat
    echo.
    echo Please ensure you are running this from the correct directory.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Set Keras backend
echo [2/3] Setting environment variables...
set KERAS_BACKEND=torch
echo [OK] KERAS_BACKEND=torch
echo.

REM Start dashboard
echo [3/3] Starting unified trading dashboard...
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Dashboard will open at: http://localhost:8050
echo   Press Ctrl+C to stop the dashboard
echo ───────────────────────────────────────────────────────────────────────────
echo.

python unified_trading_dashboard.py

REM If dashboard exits with error
if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   Dashboard stopped with errors
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   Dashboard stopped successfully
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

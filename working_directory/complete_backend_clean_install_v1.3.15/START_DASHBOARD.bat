@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  START DASHBOARD - Regime Intelligence Dashboard v1.3.13
REM  Use this script for regular startups (after first time setup)
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  REGIME INTELLIGENCE DASHBOARD - STARTUP
echo  Version: v1.3.13 - Complete Backend Package
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Quick check for first time setup
if not exist "requirements.txt" (
    echo ❌ ERROR: Not in the correct directory
    echo.
    echo Please navigate to the complete_backend_clean_install_v1.3.13 folder
    echo and run this script from there.
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please run FIRST_TIME_SETUP.bat to install all dependencies
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed (quick check)
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WARNING: Dependencies may not be installed
    echo.
    echo If this is your first time running, please use FIRST_TIME_SETUP.bat instead
    echo.
    echo Would you like to install dependencies now? (Y/N)
    set /p INSTALL_DEPS=
    if /i "%INSTALL_DEPS%"=="Y" (
        echo.
        echo Installing dependencies...
        pip install -r requirements.txt
        echo.
    ) else (
        echo.
        echo Continuing anyway... (errors may occur)
        echo.
    )
)

echo ───────────────────────────────────────────────────────────────────
echo DASHBOARD INFORMATION
echo ───────────────────────────────────────────────────────────────────
echo.
echo Features:
echo   • Live market regime detection (14 regime types)
echo   • Real-time market data monitoring
echo   • Sector impact visualization (8 sectors)
echo   • Cross-market features (15+ features)
echo   • Auto-refresh every 5 minutes
echo.
echo Coverage:
echo   • 720 stocks across 3 markets
echo   • Australian (ASX): 240 stocks
echo   • US (NASDAQ/NYSE): 240 stocks
echo   • UK (LSE): 240 stocks
echo.
echo Dashboard will be available at:
echo   http://localhost:5002
echo   http://127.0.0.1:5002
echo.
echo To access from other devices on your network:
echo   http://YOUR_IP_ADDRESS:5002
echo.

echo ───────────────────────────────────────────────────────────────────
echo STARTING DASHBOARD SERVER...
echo ───────────────────────────────────────────────────────────────────
echo.

REM Set environment variable to skip .env loading (prevents encoding issues)
set FLASK_SKIP_DOTENV=1

REM Check if .env file exists with proper encoding
if exist .env (
    echo ✓ Configuration file found (.env)
) else (
    echo ⚠️  No .env file found, using default settings
    echo   (This is normal and the dashboard will work fine)
)
echo.

echo Initializing components...
echo   • Market Data Fetcher
echo   • Market Regime Detector
echo   • Enhanced Data Sources
echo   • Cross-Market Features
echo.

echo Starting Flask server on port 5002...
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  DASHBOARD STARTING - DO NOT CLOSE THIS WINDOW
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Open your web browser and navigate to:
echo   http://localhost:5002
echo.
echo Press Ctrl+C to stop the dashboard server
echo.
echo ───────────────────────────────────────────────────────────────────
echo.

REM Start the dashboard using the fixed launcher
python start_dashboard_fixed.py

echo.
echo ───────────────────────────────────────────────────────────────────
echo  DASHBOARD STOPPED
echo ───────────────────────────────────────────────────────────────────
echo.
echo The dashboard has been stopped.
echo.
echo To restart, run this script again: START_DASHBOARD.bat
echo.
echo For troubleshooting, see: WINDOWS_FIX_GUIDE.md
echo.

pause

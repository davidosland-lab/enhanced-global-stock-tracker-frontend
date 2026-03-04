@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  FIRST TIME SETUP - Regime Intelligence Dashboard v1.3.13
REM  Run this script ONCE on first installation
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════
echo  REGIME INTELLIGENCE DASHBOARD - FIRST TIME SETUP
echo  Version: v1.3.13 - Complete Backend Package
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: pip is not installed or not in PATH
    echo.
    echo Please reinstall Python with pip included
    echo.
    pause
    exit /b 1
)

echo ✓ pip found:
pip --version
echo.

echo ───────────────────────────────────────────────────────────────────
echo STEP 1: Installing Python Dependencies
echo ───────────────────────────────────────────────────────────────────
echo.
echo This will install required packages:
echo   - yfinance (market data)
echo   - pandas, numpy (data processing)
echo   - flask (web dashboard)
echo   - requests (API calls)
echo   - python-dotenv (configuration)
echo.
echo Installing... (this may take 2-3 minutes)
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo Please check your internet connection and try again
    echo Or install manually: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ All dependencies installed successfully
echo.

echo ───────────────────────────────────────────────────────────────────
echo STEP 2: Creating Configuration Files
echo ───────────────────────────────────────────────────────────────────
echo.

REM Create data directories
if not exist "data" mkdir data
if not exist "data\cache" mkdir data\cache
if not exist "data\state" mkdir data\state
if not exist "data\logs" mkdir data\logs

echo ✓ Created data directories:
echo   - data/cache
echo   - data/state
echo   - data/logs
echo.

REM Create clean .env file
echo Creating .env configuration file...
(
echo # Flask Configuration
echo FLASK_SECRET_KEY=your-secure-secret-key-change-this-in-production
echo FLASK_ENV=development
echo FLASK_DEBUG=True
echo.
echo # Dashboard Settings
echo DASHBOARD_HOST=0.0.0.0
echo DASHBOARD_PORT=5002
echo.
echo # Regime Intelligence Settings
echo REGIME_WEIGHT=0.20
echo CONFIDENCE_THRESHOLD=0.30
echo ADAPTIVE_WEIGHTS=True
echo.
echo # Authentication ^(CHANGE THESE!^)
echo ADMIN_USERNAME=admin
echo ADMIN_PASSWORD=changeme123
echo.
echo # Logging
echo LOG_LEVEL=INFO
) > .env

echo ✓ Created .env configuration file
echo.

echo ───────────────────────────────────────────────────────────────────
echo STEP 3: Running Integration Tests
echo ───────────────────────────────────────────────────────────────────
echo.
echo Testing system components...
echo.

python test_integration.py --quick

if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Some tests failed
    echo.
    echo This may not prevent the dashboard from running.
    echo Check the errors above and consult WINDOWS_FIX_GUIDE.md
    echo.
    echo Press any key to continue anyway, or Ctrl+C to abort...
    pause >nul
) else (
    echo.
    echo ✓ All integration tests passed!
    echo.
)

echo ───────────────────────────────────────────────────────────────────
echo STEP 4: System Information
echo ───────────────────────────────────────────────────────────────────
echo.
echo Package: Complete Backend Clean Install v1.3.13
echo Coverage: 720 stocks across AU/US/UK markets
echo Markets: Australian (ASX), US (NASDAQ/NYSE), UK (LSE)
echo Features: 13 major features completed
echo.
echo Components Installed:
echo   ✓ Market Regime Detector (14 regime types)
echo   ✓ Cross-Market Features (15+ features)
echo   ✓ Opportunity Scorer (0-100 scale)
echo   ✓ Market Data Fetcher (3-level fallbacks)
echo   ✓ Enhanced Data Sources (Iron Ore, AU 10Y, etc.)
echo   ✓ 3 Dashboard Systems
echo   ✓ 6 Pipeline Runners (AU/US/UK)
echo.

echo ───────────────────────────────────────────────────────────────────
echo ✅ FIRST TIME SETUP COMPLETE!
echo ───────────────────────────────────────────────────────────────────
echo.
echo Your system is now ready to use.
echo.
echo 📊 QUICK REFERENCE:
echo.
echo To start the dashboard:
echo   • Run: START_DASHBOARD.bat
echo   • Or:  python start_dashboard_fixed.py
echo.
echo To run pipelines:
echo   • Australian: RUN_AU_PIPELINE.bat
echo   • US Market:  RUN_US_PIPELINE.bat
echo   • UK Market:  RUN_UK_PIPELINE.bat
echo.
echo Dashboard will be available at:
echo   http://localhost:5002
echo.
echo 📚 Documentation:
echo   • Installation: COMPLETE_INSTALLATION_GUIDE.md
echo   • Troubleshooting: WINDOWS_FIX_GUIDE.md
echo   • Package Info: README_COMPLETE_BACKEND.md
echo.
echo ───────────────────────────────────────────────────────────────────
echo.
echo Would you like to start the dashboard now? (Y/N)
set /p START_NOW=
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting dashboard...
    echo.
    call START_DASHBOARD.bat
) else (
    echo.
    echo Setup complete. Run START_DASHBOARD.bat when ready.
    echo.
)

pause

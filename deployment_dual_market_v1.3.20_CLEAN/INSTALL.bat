@echo off
REM ============================================================================
REM Dual Market Screening System - Windows Installation Script
REM Version: 1.3.20
REM Date: 2025-11-21
REM ============================================================================

echo ================================================================================
echo   DUAL MARKET SCREENING SYSTEM - INSTALLATION (Windows)
echo   Version: ASX v1.3.20 + US v1.0.0
echo ================================================================================
echo.

REM Check Python
echo [1/5] Checking system requirements...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

python --version
echo OK: Python is available

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    pause
    exit /b 1
)
echo OK: pip is available

REM Create directories
echo.
echo [2/5] Creating directory structure...
if not exist "logs\screening\us\errors" mkdir logs\screening\us\errors
if not exist "reports\us" mkdir reports\us
if not exist "data\us" mkdir data\us
echo OK: Directories created

REM Install dependencies
echo.
echo [3/5] Installing Python dependencies...
echo This may take 5-10 minutes depending on your internet speed...
echo.
echo Installing packages (this will show progress):
pip install -r requirements.txt --verbose
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    echo Troubleshooting:
    echo   1. Check internet connection
    echo   2. Try: python -m pip install --upgrade pip
    echo   3. Try: pip install -r requirements.txt --no-cache-dir
    echo.
    pause
    exit /b 1
)
echo.
echo ================================================================================
echo OK: ALL DEPENDENCIES INSTALLED SUCCESSFULLY
echo ================================================================================

REM Verify installation
echo.
echo [4/5] Verifying installation...

python -c "from models.screening.us_stock_scanner import USStockScanner; print('OK: US Stock Scanner')" 2>nul
if errorlevel 1 (
    echo ERROR: US Stock Scanner failed to import
    pause
    exit /b 1
)

python -c "from models.screening.us_market_monitor import USMarketMonitor; print('OK: US Market Monitor')" 2>nul
if errorlevel 1 (
    echo ERROR: US Market Monitor failed to import
    pause
    exit /b 1
)

python -c "from models.screening.us_market_regime_engine import USMarketRegimeEngine; print('OK: US Market Regime Engine')" 2>nul
if errorlevel 1 (
    echo ERROR: US Market Regime Engine failed to import
    pause
    exit /b 1
)

python -c "import run_screening; print('OK: Unified Launcher')" 2>nul
if errorlevel 1 (
    echo ERROR: Unified Launcher failed to import
    pause
    exit /b 1
)

echo.
echo [5/5] Running quick verification test...
echo Testing US market monitor (this will fetch live data)...
python models\screening\us_market_monitor.py
if errorlevel 1 (
    echo WARNING: Verification test had issues
    echo This may be due to network connectivity
)

echo.
echo ================================================================================
echo   INSTALLATION COMPLETE
echo ================================================================================
echo.
echo Next Steps:
echo   1. Run a quick test:
echo      python run_screening.py --market us --stocks 5
echo.
echo   2. Run full ASX pipeline:
echo      python run_screening.py --market asx
echo.
echo   3. Run full US pipeline:
echo      python run_screening.py --market us
echo.
echo   4. Run both markets (parallel):
echo      python run_screening.py --market both --parallel
echo.
echo Documentation:
echo   - DEPLOYMENT_README.md for complete guide
echo   - QUICK_START_US_PIPELINE.txt for quick reference
echo.
echo ================================================================================
echo.
pause

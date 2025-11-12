@echo off
REM ============================================================================
REM OVERNIGHT STOCK SCREENER - SIMPLE LAUNCHER
REM Run this from the COMPLETE_SYSTEM_PACKAGE directory
REM ============================================================================

echo.
echo ============================================================================
echo OVERNIGHT STOCK SCREENER - STARTING
echo ============================================================================
echo Start Time: %date% %time%
echo.

REM Check if we're in the right directory
if not exist "scripts\run_overnight_screener.py" (
    echo [ERROR] Cannot find run_overnight_screener.py
    echo [INFO] Please run this script from the COMPLETE_SYSTEM_PACKAGE directory
    echo [INFO] Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo [INFO] Please install Python 3.8+ or add it to your PATH
    echo.
    pause
    exit /b 1
)

REM Check required packages
python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] yfinance not installed
    echo [INFO] Install with: pip install yfinance pandas numpy
    echo.
    pause
    exit /b 1
)

echo [INFO] Environment OK - Starting overnight screener...
echo [INFO] This may take 2-4 hours depending on the number of stocks
echo.

REM Create directories
if not exist "logs" mkdir "logs"
if not exist "reports" mkdir "reports"
if not exist "reports\pipeline_state" mkdir "reports\pipeline_state"

REM Run screener
python -u scripts\run_overnight_screener.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo [ERROR] Screener failed
    echo ============================================================================
    echo End Time: %date% %time%
    echo.
) else (
    echo.
    echo ============================================================================
    echo [SUCCESS] Screener completed!
    echo ============================================================================
    echo End Time: %date% %time%
    echo.
    echo [INFO] Reports saved to: reports\pipeline_state\
    echo.
)

pause

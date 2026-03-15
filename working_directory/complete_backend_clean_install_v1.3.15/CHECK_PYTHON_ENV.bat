@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  Python Environment Diagnostic Tool
REM  Helps identify why dash/plotly might not be found
REM  Version: 1.0
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   PYTHON ENVIRONMENT DIAGNOSTIC
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Check Python version
echo [1/6] Checking Python version...
python --version
echo.

REM Check Python location
echo [2/6] Checking Python location...
python -c "import sys; print('Python executable:', sys.executable)"
echo.

REM Check pip location
echo [3/6] Checking pip location...
where pip
echo.

REM Check if dash is installed
echo [4/6] Checking if dash is installed...
python -c "import dash; print('Dash version:', dash.__version__)" 2>nul
if errorlevel 1 (
    echo   [X] Dash NOT installed
) else (
    echo   [OK] Dash is installed
)
echo.

REM Check if plotly is installed
echo [5/6] Checking if plotly is installed...
python -c "import plotly; print('Plotly version:', plotly.__version__)" 2>nul
if errorlevel 1 (
    echo   [X] Plotly NOT installed
) else (
    echo   [OK] Plotly is installed
)
echo.

REM Check site-packages location
echo [6/6] Checking site-packages location...
python -c "import site; print('Site-packages:', site.getsitepackages())"
echo.

echo ═══════════════════════════════════════════════════════════════════
echo   DIAGNOSIS COMPLETE
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Provide recommendations
python -c "import dash" 2>nul
if errorlevel 1 (
    echo [!] ISSUE DETECTED: Dash is not installed in the current Python environment
    echo.
    echo RECOMMENDED FIX:
    echo   1. Run: pip install dash plotly
    echo   2. Or run: INSTALL_DASHBOARD_DEPS.bat
    echo.
    echo NOTE: Make sure pip installs to the same Python that's being used
    echo       (Check Python and pip locations above)
    echo.
) else (
    echo [OK] All dependencies appear to be installed correctly!
    echo.
    echo If the dashboard still doesn't work, please check:
    echo   1. Port 8050 is not already in use
    echo   2. Firewall is not blocking localhost connections
    echo   3. Try running: python unified_trading_dashboard.py
    echo.
)

pause

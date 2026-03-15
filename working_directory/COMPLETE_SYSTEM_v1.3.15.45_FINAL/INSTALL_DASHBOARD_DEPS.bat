@echo off
REM ═══════════════════════════════════════════════════════════════════
REM  Install Dashboard Dependencies - Quick Fix
REM  Version: v1.3.15.16
REM  Date: 2026-01-16
REM ═══════════════════════════════════════════════════════════════════

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   INSTALLING DASHBOARD DEPENDENCIES
echo ═══════════════════════════════════════════════════════════════════
echo.
echo This will install:
echo   - dash (Interactive dashboards)
echo   - plotly (Interactive charts)
echo.
echo This takes about 2-3 minutes...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [OK] Using virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found, using system Python
)

echo.
echo [1/2] Installing Dash...
python -m pip install dash>=2.14.0 --quiet

echo.
echo [2/2] Installing Plotly...
python -m pip install plotly>=5.14.0 --quiet

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   INSTALLATION COMPLETE!
echo ═══════════════════════════════════════════════════════════════════
echo.
echo You can now run the Unified Trading Dashboard:
echo   - Option 7 from LAUNCH_COMPLETE_SYSTEM.bat
echo   - Or run: python unified_trading_dashboard.py
echo.
echo Dashboard will open at: http://localhost:8050
echo.

pause

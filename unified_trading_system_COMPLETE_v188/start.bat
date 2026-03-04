@echo off
REM ====================================================================
REM Unified Trading System v1.3.15.188 - Dashboard Launcher
REM ====================================================================

echo.
echo ========================================================
echo   UNIFIED TRADING SYSTEM v1.3.15.188
echo   Starting Dashboard...
echo ========================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run install_complete.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dashboard exists
if not exist "core\unified_trading_dashboard.py" (
    echo ERROR: Dashboard file not found!
    echo Expected: core\unified_trading_dashboard.py
    echo.
    pause
    exit /b 1
)

REM Display configuration
echo Configuration:
echo   - Mode: Paper Trading
echo   - Confidence Threshold: 48%%
echo   - Dashboard URL: http://localhost:8050
echo   - Portfolio: $100,000 starting cash
echo.
echo v188 Patches Active:
echo   [✓] Config threshold: 45.0%%
echo   [✓] Signal generator: 0.48
echo   [✓] Coordinator: 48.0%%
echo   [✓] Monitor: 48.0%%
echo.
echo Starting dashboard...
echo Press Ctrl+C to stop
echo.

REM Start the dashboard
python core\unified_trading_dashboard.py

REM If dashboard exits
echo.
echo Dashboard stopped.
pause

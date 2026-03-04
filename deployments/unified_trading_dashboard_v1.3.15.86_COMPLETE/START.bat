@echo off
cls
echo ===============================================================
echo     Unified Trading Dashboard v1.3.15.86
echo ===============================================================
echo.
echo Starting dashboard on http://localhost:8050
echo.

REM Set UTF-8 encoding for Python
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Set Keras backend (if using ML features)
set KERAS_BACKEND=torch

REM Start dashboard
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard failed to start!
    echo See logs\unified_trading.log for details
) else (
    echo.
    echo Dashboard stopped cleanly
)

echo.
pause

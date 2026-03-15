@echo off
echo ====================================
echo Unified Trading Dashboard v1.3.15.87
echo Starting on http://localhost:8050
echo ====================================
echo.

cd core

:: Set UTF-8 encoding
chcp 65001 > nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

:: Set Keras backend
set KERAS_BACKEND=torch

echo Starting dashboard...
echo Dashboard will be available at: http://localhost:8050
echo.
echo Press Ctrl+C to stop
echo.

:: Run dashboard
python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard stopped with errors
    echo Check logs\unified_trading.log for details
    echo.
) else (
    echo.
    echo Dashboard stopped cleanly
    echo.
)

pause

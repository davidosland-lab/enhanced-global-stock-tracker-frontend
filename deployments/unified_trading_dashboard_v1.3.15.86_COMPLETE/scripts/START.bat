@echo off
cls
echo ===============================================================
echo     Unified Trading Dashboard v1.3.15.66 FINAL
echo     Date: 2026-02-01
echo     Unicode Logging Fix
echo ===============================================================
echo.
cd /d "%~dp0"
echo Dashboard will be available at: http://localhost:8050
echo.

REM Enable UTF-8 for this session
chcp 65001 > nul

REM Set environment variables for UTF-8 encoding
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Set Keras backend
set KERAS_BACKEND=torch

REM Start the dashboard
python unified_trading_dashboard.py

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard failed to start
    echo Check the logs for details
) else (
    echo.
    echo Dashboard stopped cleanly
)

echo.
pause

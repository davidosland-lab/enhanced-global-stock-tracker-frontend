@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  START UNIFIED TRADING DASHBOARD - ULTRA SIMPLE
REM  Works with or without virtual environment
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UNIFIED TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Starting dashboard...
echo   URL: http://localhost:8050
echo   Press Ctrl+C to stop
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Set environment variable
set KERAS_BACKEND=torch

REM Start dashboard with Python
python unified_trading_dashboard.py

REM If it failed, show error
if errorlevel 1 (
    echo.
    echo [ERROR] Dashboard failed to start
    echo.
    echo Try this:
    echo   1. Open Command Prompt
    echo   2. Run: pip install dash plotly transformers keras torch
    echo   3. Run this file again
    echo.
)

pause

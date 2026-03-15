@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  START UNIFIED TRADING DASHBOARD
REM  Version: v1.3.15.66 FINAL
REM  Date: 2026-02-01
REM  Fix: Unicode logging error resolved
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║               UNIFIED TRADING DASHBOARD v1.3.15.66                        ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Starting dashboard...
echo   URL: http://localhost:8050
echo   Press Ctrl+C to stop
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Fix Unicode encoding issues in Windows console
chcp 65001 >nul 2>&1

REM Set environment variables
set KERAS_BACKEND=torch
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Start dashboard
python unified_trading_dashboard.py

REM Handle errors
if errorlevel 1 (
    echo.
    echo [ERROR] Dashboard failed to start
    echo.
    pause
) else (
    echo.
    echo [INFO] Dashboard stopped cleanly
    echo.
)

pause

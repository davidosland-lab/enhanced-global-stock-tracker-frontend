@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  UNIFIED TRADING DASHBOARD - START SCRIPT
REM  Version: v193.11.7 - Trading Loop Crash Fix
REM  Date: 2026-03-10
REM  
REM  CRITICAL FIX: Trading loop now survives exceptions
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║            UNIFIED TRADING DASHBOARD v193.11.7                            ║
echo ║                 Trading Loop Crash Fix Applied                            ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   🔧 CRITICAL FIX: Loop now survives transient errors
echo   ✅ Network timeouts won't stop trading
echo   ✅ API rate limits handled gracefully
echo   ✅ Automatic error recovery
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

REM Navigate to core directory where the dashboard is located
cd core

REM Start dashboard with the fixed paper trading coordinator
python unified_trading_dashboard.py

REM Handle errors
if errorlevel 1 (
    echo.
    echo [ERROR] Dashboard failed to start
    echo.
    echo Troubleshooting:
    echo   1. Check Python is installed: python --version
    echo   2. Check dependencies: pip install -r ../requirements.txt
    echo   3. Check logs in logs/ directory
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [INFO] Dashboard stopped cleanly
    echo.
)

pause

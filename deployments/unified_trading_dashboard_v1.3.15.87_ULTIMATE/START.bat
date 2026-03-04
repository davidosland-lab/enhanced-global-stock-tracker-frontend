@echo off
echo ==========================================
echo Unified Trading Dashboard v1.3.15.87
echo Mode: Dashboard Only (70-75%% win rate)
echo FinBERT v4.4.4: INCLUDED
echo ==========================================
echo.
echo For 75-85%% win rate, use:
echo   RUN_COMPLETE_WORKFLOW.bat
echo.

cd core

:: Set UTF-8 encoding
chcp 65001 > nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set KERAS_BACKEND=torch

echo Starting dashboard...
echo Dashboard: http://localhost:8050
echo FinBERT: Using local model (finbert_v4.4.4/)
echo.

python unified_trading_dashboard.py --symbols BHP.AX,CBA.AX,RIO.AX --capital 100000

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard stopped with errors
    echo.
) else (
    echo.
    echo Dashboard stopped cleanly
    echo.
)

pause

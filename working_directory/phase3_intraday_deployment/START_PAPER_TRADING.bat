@echo off
REM Phase 3 Paper Trading - Windows Startup
REM Quick start with default settings

echo ================================================================================
echo PHASE 3 PAPER TRADING - Starting...
echo ================================================================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs
if not exist "state" mkdir state

REM Default settings
set SYMBOLS=RIO.AX,CBA.AX,BHP.AX
set CAPITAL=100000
set CYCLES=100
set INTERVAL=60

echo Configuration:
echo   Symbols: %SYMBOLS%
echo   Capital: $%CAPITAL%
echo   Cycles: %CYCLES%
echo   Interval: %INTERVAL%s
echo.
echo Starting paper trading system...
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

python paper_trading_coordinator.py --symbols %SYMBOLS% --capital %CAPITAL% --real-signals --cycles %CYCLES% --interval %INTERVAL%

echo.
echo ================================================================================
echo Paper trading session ended
echo ================================================================================
pause

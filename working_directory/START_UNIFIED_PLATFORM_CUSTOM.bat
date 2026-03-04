@echo off
REM ====================================================================
REM  UNIFIED PLATFORM - Custom Setup
REM  Choose market and starting capital
REM ====================================================================

title Unified Trading Platform - Custom Setup

cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║      UNIFIED TRADING PLATFORM - CUSTOM CONFIGURATION           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Select market
echo Select Market:
echo   1. US Market (NYSE, NASDAQ)
echo   2. ASX Market (Australian Stock Exchange)
echo.
set /p MARKET_CHOICE="Enter choice (1 or 2): "

if "%MARKET_CHOICE%"=="1" (
    set MARKET=US
) else if "%MARKET_CHOICE%"=="2" (
    set MARKET=ASX
) else (
    echo Invalid choice, defaulting to US
    set MARKET=US
)

echo.
REM Enter capital
echo Enter Starting Capital:
echo   Examples: 50000, 100000, 250000
echo.
set /p CAPITAL="Capital: $"

if "%CAPITAL%"=="" (
    set CAPITAL=100000
    echo No input, defaulting to $100,000
)

echo.
echo ════════════════════════════════════════════════════════════════
echo Configuration:
echo   Market: %MARKET%
echo   Starting Capital: $%CAPITAL%
echo   Mode: Paper Trading (Simulated)
echo   Module: Unified All-in-One
echo   Dashboard: http://localhost:5000
echo ════════════════════════════════════════════════════════════════
echo.
echo Press any key to start...
pause >nul

cls
echo Starting Unified Trading Platform...
echo.

python unified_trading_platform.py --paper-trading --market %MARKET% --capital %CAPITAL%

pause

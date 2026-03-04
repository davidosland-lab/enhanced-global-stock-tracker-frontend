@echo off
REM Start Paper Trading System with Dashboard

echo ==========================================
echo Phase 3 Paper Trading System
echo ==========================================
echo.

REM Create necessary directories
if not exist logs mkdir logs
if not exist state mkdir state
if not exist reports mkdir reports
if not exist data mkdir data

REM Check if config exists
if not exist config\live_trading_config.json (
    echo Warning: Configuration file not found
    echo Using default configuration...
)

REM Start paper trading in background
echo 1. Starting paper trading system...
start /B python paper_trading_coordinator.py --symbols AAPL,GOOGL,MSFT,TSLA,NVDA --capital 100000 --interval 60 > logs\paper_trading.log 2>&1

echo    √ Paper trading started
echo    Logs: logs\paper_trading.log
echo.

REM Wait a moment for initial data
timeout /t 3 /nobreak >nul

REM Start dashboard
echo 2. Starting dashboard...
echo    URL: http://localhost:8050
echo.
python dashboard.py

echo.
echo √ System stopped
pause

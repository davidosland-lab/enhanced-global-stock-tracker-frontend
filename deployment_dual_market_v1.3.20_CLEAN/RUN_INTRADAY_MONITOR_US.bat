@echo off
REM ========================================================================
REM Intraday Monitoring for US Market
REM ========================================================================
REM
REM This script starts automated intraday monitoring for day trading.
REM It will rescan the market every 15 minutes during trading hours.
REM
REM Features:
REM - Auto-rescan every 15 minutes
REM - Breakout detection
REM - Real-time alerts (if configured)
REM - Auto-stop at market close
REM
REM ========================================================================

cd /d "%~dp0"

echo.
echo ================================================================================
echo INTRADAY MONITORING - US MARKET
echo ================================================================================
echo.
echo Starting automated intraday monitoring...
echo.
echo Configuration:
echo   Market: US (NYSE/NASDAQ)
echo   Rescan Interval: 15 minutes
echo   Trading Hours: 9:30 AM - 4:00 PM EST
echo.
echo Press Ctrl+C to stop monitoring
echo.
echo ================================================================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the intraday scheduler
python models\scheduling\intraday_scheduler.py --market US --interval 15

echo.
echo ================================================================================
echo Monitoring stopped
echo ================================================================================
echo.
pause

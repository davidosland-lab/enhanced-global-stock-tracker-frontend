@echo off
REM ============================================================================
REM Intraday Monitor - ASX Market
REM ============================================================================
REM 
REM This script runs the Phase 3 Intraday Rescan Monitor for ASX stocks.
REM 
REM Features:
REM - Auto-detects ASX market hours (10 AM - 4 PM AEST)
REM - Rescans every 15-30 minutes during market hours
REM - Detects breakouts and sends alerts
REM - 80-90% API cost savings via incremental scanning
REM 
REM Usage:
REM   RUN_INTRADAY_MONITOR_ASX.bat
REM 
REM Press Ctrl+C to stop monitoring
REM ============================================================================

echo ================================================================================
echo    INTRADAY MONITOR - ASX MARKET
echo ================================================================================
echo.
echo Starting intraday monitoring for ASX stocks...
echo This will scan continuously during market hours (10 AM - 4 PM AEST)
echo.
echo Features:
echo   - Auto rescan every 15-30 minutes
echo   - Real-time breakout detection
echo   - Multi-channel alerts (Email, SMS, Webhook)
echo   - 80-90%% API cost savings
echo.
echo Press Ctrl+C to stop monitoring
echo.
echo ================================================================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the intraday scheduler for ASX
python models\scheduling\intraday_scheduler.py --market ASX --interval 15

echo.
echo ================================================================================
echo    MONITORING STOPPED
echo ================================================================================
echo.
pause

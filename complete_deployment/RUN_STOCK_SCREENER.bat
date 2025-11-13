@echo off
REM ===============================================================================
REM   FinBERT v4.4.4 Alpha Vantage - Stock Screener Launcher
REM   Runs the overnight stock screening system
REM ===============================================================================

echo ================================================================================
echo   FinBERT v4.4.4 - ALPHA VANTAGE STOCK SCREENER
echo ================================================================================
echo.
echo Starting overnight stock screening system...
echo.
echo This will:
echo   1. Fetch market sentiment (ASX 200, S^&P 500, Nasdaq, Dow)
echo   2. Scan 40 stocks across 8 sectors
echo   3. Generate ensemble predictions (LSTM + Technical + Sentiment)
echo   4. Score trading opportunities
echo   5. Generate morning report (HTML)
echo.
echo Expected Duration: 8-10 minutes
echo API Calls: ~48/500 (9.6%% of daily limit)
echo.

REM Set the working directory to script location
cd /d "%~dp0"

echo ================================================================================
echo   System Information
echo ================================================================================
echo.
echo Current Directory: %CD%
echo Python Version:
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed!
    echo Please run INSTALL_DEPENDENCIES.bat first.
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo   Pre-Flight Check
echo ================================================================================
echo.

REM Check if Alpha Vantage fetcher exists
if not exist "models\screening\alpha_vantage_fetcher.py" (
    echo ❌ ERROR: alpha_vantage_fetcher.py not found!
    echo Package may be incomplete. Please re-extract the ZIP file.
    pause
    exit /b 1
)
echo ✓ Alpha Vantage fetcher found
echo.

REM Check if run script exists
if not exist "scripts\screening\run_overnight_screener.py" (
    echo ❌ ERROR: run_overnight_screener.py not found!
    echo Package may be incomplete. Please re-extract the ZIP file.
    pause
    exit /b 1
)
echo ✓ Overnight screener script found
echo.

REM Create logs directory if not exists
if not exist "logs\screening" mkdir logs\screening
echo ✓ Logs directory ready
echo.

REM Create reports directory if not exists
if not exist "reports\morning_reports" mkdir reports\morning_reports
if not exist "reports\screening_results" mkdir reports\screening_results
echo ✓ Reports directory ready
echo.

echo ================================================================================
echo   Launching Stock Screener
echo ================================================================================
echo.

REM Run the overnight screener
python scripts\screening\run_overnight_screener.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   ❌ SCREENER FAILED
    echo ================================================================================
    echo.
    echo The screener encountered an error.
    echo Check the error messages above for details.
    echo.
    echo Common Issues:
    echo   1. Missing dependencies - Run INSTALL_DEPENDENCIES.bat
    echo   2. Internet connection - Alpha Vantage API requires internet
    echo   3. API limit reached - Wait until midnight UTC
    echo.
    echo For detailed logs, check: logs\screening\
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   ✅ SCREENER COMPLETE!
echo ================================================================================
echo.
echo Check the output above for:
echo   - Number of stocks validated
echo   - API usage (should be under 500/day)
echo   - Top opportunities found
echo   - Report location (if generated)
echo.
echo Reports saved to: reports\morning_reports\
echo Results saved to: reports\screening_results\
echo.

pause

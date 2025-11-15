@echo off
title ASX Stock Scanner v4.4.4 - Overnight Pipeline
color 0A

echo ================================================================================
echo ASX OVERNIGHT STOCK SCANNER v4.4.4 - PIPELINE EXECUTION
echo ================================================================================
echo.
echo Full System Features:
echo   - 240 ASX stocks across 8 sectors
echo   - LSTM Neural Network Predictions (45%% weight)
echo   - FinBERT Sentiment Analysis (15%% weight)
echo   - Trend Analysis (25%% weight)
echo   - Technical Analysis (15%% weight)
echo   - SPI 200 Futures Monitoring
echo   - US Market Data Integration
echo   - Email Notifications (Gmail)
echo.
echo This will run comprehensive overnight analysis
echo Results will include ML predictions and sentiment scores
echo.
echo Estimated Time: 30-45 minutes
echo ================================================================================
echo.

REM Check if we're in test mode
if "%1"=="test" (
    echo [TEST MODE] Running quick scan (5 stocks per sector)
    echo.
    goto run_test
)

if "%1"=="quick" (
    echo [QUICK MODE] Running quick scan (5 stocks per sector)
    echo.
    goto run_test
)

pause

echo.
echo [Step 1/2] Checking dependencies...
echo.

REM Check if required packages are installed
python -c "import yahooquery, pandas, numpy, yfinance, pytz, schedule" 2>nul
if errorlevel 1 (
    echo ERROR: Core packages not installed!
    echo.
    echo Please run: INSTALL_DEPENDENCIES.bat
    echo Or manually install: pip install yahooquery pandas numpy yfinance pytz schedule
    echo.
    pause
    exit /b 1
)

echo Core packages: OK
echo.

REM Check optional packages
python -c "import tensorflow" 2>nul
if errorlevel 1 (
    echo WARNING: TensorFlow not installed - LSTM predictions will be unavailable
    set ML_STATUS=DISABLED
) else (
    echo LSTM packages: OK
    set ML_STATUS=ENABLED
)

python -c "import transformers" 2>nul
if errorlevel 1 (
    echo WARNING: Transformers not installed - FinBERT sentiment will be unavailable
    set FINBERT_STATUS=DISABLED
) else (
    echo FinBERT packages: OK
    set FINBERT_STATUS=ENABLED
)

echo.
echo [Step 2/2] Starting overnight pipeline...
echo.
echo LSTM Predictions: %ML_STATUS%
echo FinBERT Sentiment: %FINBERT_STATUS%
echo.
echo ================================================================================
echo.

:run_full
python run_overnight_pipeline.py

goto end

:run_test
python run_overnight_pipeline.py --mode test

:end
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo [ERROR] Pipeline execution failed!
    echo ================================================================================
    echo.
    echo Check logs for details:
    echo   - logs\screening\overnight_pipeline.log
    echo   - logs\scheduler\scheduler.log
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [SUCCESS] Pipeline execution completed!
echo ================================================================================
echo.
echo Check results:
echo   - Reports: reports\morning_reports\
echo   - Logs: logs\screening\overnight_pipeline.log
echo   - Email: Check your inbox for report delivery
echo.
pause

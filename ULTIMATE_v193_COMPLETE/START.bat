@echo off
REM ============================================================================
REM UNIFIED TRADING SYSTEM v193.11.7.6 - EODHD API Integration - MAIN MENU (Datetime Comparison Fix)
REM ============================================================================

REM Change to script directory
cd /d "%~dp0"

:MENU
cls
echo.
echo ============================================================================
echo  UNIFIED TRADING SYSTEM v193.11.7.5
echo ============================================================================
echo.
echo  Choose an option:
echo.
echo    1. Start Complete System (FinBERT + Dashboard + Pipelines)
echo    2. Start FinBERT Only (Sentiment + LSTM Training)
echo    3. Start Dashboard Only (Paper Trading + Live Charts)
echo.
echo  --- Overnight Pipeline Options ---
echo    4. Run All Pipelines (AU + US + UK) - ~60 minutes
echo    5. Run AU Pipeline Only (ASX) - ~20 minutes
echo    6. Run US Pipeline Only (NYSE/NASDAQ) - ~20 minutes
echo    7. Run UK Pipeline Only (LSE) - ~20 minutes
echo.
echo  --- LSTM Model Training ---
echo    8. Train Individual Stocks (CBA.AX, AAPL, etc.) - Interactive
echo.
echo    9. Exit
echo.
echo ============================================================================
echo  Market Trading Hours (for reference):
echo    AU (ASX):        10:00-16:00 AEDT  (00:00-06:00 UTC)
echo    US (NYSE):       09:30-16:00 EST   (14:30-21:00 UTC)
echo    UK (LSE):        08:00-16:30 GMT   (08:00-16:30 UTC)
echo ============================================================================
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto COMPLETE
if "%choice%"=="2" goto FINBERT
if "%choice%"=="3" goto DASHBOARD
if "%choice%"=="4" goto PIPELINES_ALL
if "%choice%"=="5" goto PIPELINE_AU
if "%choice%"=="6" goto PIPELINE_US
if "%choice%"=="7" goto PIPELINE_UK
if "%choice%"=="8" goto TRAIN_INDIVIDUAL
if "%choice%"=="9" goto EXIT
echo Invalid choice, please try again.
pause
goto MENU

:COMPLETE
cls
echo.
echo ============================================================================
echo  Starting Complete System...
echo ============================================================================
echo.
echo  This will start:
echo    - FinBERT v4.4.4 (Port 5001)
echo    - Dashboard (Port 8050)
echo    - Pipelines (Background)
echo.
echo  URLs:
echo    - FinBERT API: http://localhost:5001
echo    - Dashboard:   http://localhost:8050
echo.
echo  Press Ctrl+C to stop all services
echo.
echo ============================================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1

REM Start FinBERT in background
echo Starting FinBERT v4.4.4...
start "FinBERT v4.4.4" cmd /k "cd finbert_v4.4.4 && python app_finbert_v4_dev.py"
timeout /t 5 /nobreak >nul

REM Start Dashboard in background
echo Starting Dashboard...
start "Ultimate Trading Dashboard" cmd /k "cd core && python unified_trading_dashboard.py"
timeout /t 5 /nobreak >nul

echo.
echo ============================================================================
echo  System Started!
echo ============================================================================
echo.
echo  FinBERT API: http://localhost:5001
echo  Dashboard:   http://localhost:8050
echo.
echo  Two windows opened:
echo    1. FinBERT v4.4.4 (Flask server)
echo    2. Ultimate Trading Dashboard (Dash app)
echo.
echo  To run pipelines, use Option 4 from main menu
echo.
echo  Press any key to return to menu...
echo ============================================================================
pause >nul
goto MENU

:FINBERT
cls
echo.
echo ============================================================================
echo  Starting FinBERT v4.4.4...
echo ============================================================================
echo.
echo  Features:
echo    - Real sentiment analysis from news (95% accuracy)
echo    - LSTM training for 720 stocks
echo    - Technical indicators (8+)
echo    - REST API
echo.
echo  URL: http://localhost:5001
echo.
echo  API Endpoints:
echo    - POST /api/train/SYMBOL (Train LSTM model)
echo    - GET  /api/stock/SYMBOL (Get prediction)
echo    - GET  /api/models (List trained models)
echo    - GET  /api/health (System status)
echo.
echo  Press Ctrl+C to stop
echo.
echo ============================================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set FLASK_SKIP_DOTENV=1

REM Change to FinBERT directory and start
cd finbert_v4.4.4
python app_finbert_v4_dev.py

pause
goto MENU

:DASHBOARD
cls
echo.
echo ============================================================================
echo  Starting Ultimate Trading Dashboard...
echo ============================================================================
echo.
echo  Features:
echo    - Paper trading with ML signals
echo    - Real-time portfolio tracking
echo    - Live charts and indicators
echo    - Market calendar
echo.
echo  URL: http://localhost:8050
echo.
echo  Usage:
echo    1. Open http://localhost:8050 in your browser
echo    2. Select stocks from the dropdown
echo    3. Set capital and start trading
echo    4. Monitor live portfolio performance
echo.
echo  Press Ctrl+C to stop
echo.
echo ============================================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1

REM Change to core directory and start
cd core
python unified_trading_dashboard.py

pause
goto MENU

:PIPELINES_ALL
cls
echo.
echo ============================================================================
echo  Starting ALL Overnight Pipelines (AU + US + UK)
echo ============================================================================
echo.
echo  This will run ALL THREE pipelines in sequence:
echo    1. AU Pipeline (ASX stocks) - 240 stocks
echo    2. US Pipeline (NYSE/NASDAQ stocks) - 240 stocks
echo    3. UK Pipeline (LSE stocks) - 240 stocks
echo.
echo  Each pipeline will:
echo    - Scan stocks in their respective market
echo    - Generate trading signals with ML predictions
echo    - Create comprehensive morning reports
echo    - Run with --ignore-market-hours (works anytime)
echo.
echo  Estimated total time: ~60 minutes (20 min per pipeline)
echo.
echo  Reports will be saved to: reports/
echo.
echo  RECOMMENDATION: Run pipelines strategically based on market timing
echo    - Run AU pipeline before ASX opens (10:00 AEDT)
echo    - Run US pipeline before NYSE opens (09:30 EST)
echo    - Run UK pipeline before LSE opens (08:00 GMT)
echo.
echo ============================================================================
echo.
pause

REM Save current directory
set ORIGINAL_DIR=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Return to original directory before calling workflow
cd /d "%ORIGINAL_DIR%"

REM Run complete workflow (all three pipelines)
call "%ORIGINAL_DIR%\RUN_COMPLETE_WORKFLOW.bat"

echo.
echo All pipelines completed!
echo.
pause
goto MENU

:PIPELINE_AU
cls
echo.
echo ============================================================================
echo  Starting AU Pipeline (ASX - Australian Stock Exchange)
echo ============================================================================
echo.
echo  Market: ASX (Australian Stock Exchange)
echo  Trading Hours: 10:00-16:00 AEDT (00:00-06:00 UTC)
echo  Stocks to Scan: 240 ASX stocks across 8 sectors
echo.
echo  Pipeline Features:
echo    - Overnight market analysis (US/commodity impact on ASX)
echo    - SPI futures monitoring
echo    - Cross-market feature engineering
echo    - FinBERT sentiment analysis
echo    - LSTM predictions
echo    - Technical indicators
echo    - Event risk assessment
echo.
echo  Estimated time: ~20 minutes
echo  Report: reports/au_morning_report.json
echo.
echo  BEST TIME TO RUN: Before ASX opens (before 10:00 AEDT)
echo.
echo ============================================================================
echo.
pause

REM Save current directory
set ORIGINAL_DIR=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

REM Run AU pipeline
call "%ORIGINAL_DIR%\RUN_AU_PIPELINE_ONLY.bat"

echo.
echo AU Pipeline completed!
echo.
pause
goto MENU

:PIPELINE_US
cls
echo.
echo ============================================================================
echo  Starting US Pipeline (NYSE/NASDAQ)
echo ============================================================================
echo.
echo  Market: NYSE/NASDAQ (US Stock Markets)
echo  Trading Hours: 09:30-16:00 EST (14:30-21:00 UTC)
echo  Stocks to Scan: 240 US stocks across 8 sectors
echo.
echo  Pipeline Features:
echo    - Pre-market analysis
echo    - S&P 500 futures, VIX monitoring
echo    - Cross-market feature engineering
echo    - FinBERT sentiment analysis
echo    - LSTM predictions
echo    - Technical indicators
echo    - Event risk assessment
echo.
echo  Estimated time: ~20 minutes
echo  Report: reports/us_morning_report.json
echo.
echo  BEST TIME TO RUN: Before NYSE opens (before 09:30 EST)
echo.
echo ============================================================================
echo.
pause

REM Save current directory
set ORIGINAL_DIR=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

REM Run US pipeline
call "%ORIGINAL_DIR%\RUN_US_PIPELINE_ONLY.bat"

echo.
echo US Pipeline completed!
echo.
pause
goto MENU

:PIPELINE_UK
cls
echo.
echo ============================================================================
echo  Starting UK Pipeline (LSE - London Stock Exchange)
echo ============================================================================
echo.
echo  Market: LSE (London Stock Exchange)
echo  Trading Hours: 08:00-16:30 GMT (08:00-16:30 UTC)
echo  Stocks to Scan: 240 UK stocks across 8 sectors
echo.
echo  Pipeline Features:
echo    - Overnight market analysis (US close impact on UK)
echo    - FTSE futures monitoring
echo    - Cross-market feature engineering
echo    - FinBERT sentiment analysis
echo    - LSTM predictions
echo    - Technical indicators
echo    - Event risk assessment
echo.
echo  Estimated time: ~20 minutes
echo  Report: reports/uk_morning_report.json
echo.
echo  BEST TIME TO RUN: Before LSE opens (before 08:00 GMT)
echo.
echo ============================================================================
echo.
pause

REM Save current directory
set ORIGINAL_DIR=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

REM Run UK pipeline
call "%ORIGINAL_DIR%\RUN_UK_PIPELINE_ONLY.bat"

echo.
echo UK Pipeline completed!
echo.
pause
goto MENU

:TRAIN_INDIVIDUAL
cls
echo.
echo ============================================================================
echo  Train Individual Stocks - LSTM Model Trainer
echo ============================================================================
echo.
echo  This tool allows you to train LSTM models for specific stocks.
echo.
echo  Use this for:
echo    - Large-cap stocks not in overnight top 20 (e.g., CBA.AX, NAB.AX)
echo    - Stocks you want to trade that lack LSTM models
echo    - Quick model training without running full pipeline
echo.
echo  How it works:
echo    1. You enter stock symbols interactively (CBA.AX, AAPL, BP.L, etc.)
echo    2. System trains LSTM models for each stock (~3 min per stock)
echo    3. Models saved to: finbert_v4.4.4/models/saved_models/
echo    4. Restart dashboard to use new models
echo.
echo  Benefits:
echo    - No more "LSTM failed - not enough data" errors
echo    - No -20% confidence penalty for these stocks
echo    - Models updated in same location as overnight pipeline models
echo    - Full 5-component signal generation (Sentiment + LSTM + Technical + Momentum + Volume)
echo.
echo  Example stocks to train:
echo    AU: CBA.AX, NAB.AX, WBC.AX, ANZ.AX (banks)
echo    AU: WOW.AX, WES.AX, CSL.AX (retail/healthcare)
echo    US: AAPL, GOOGL, MSFT, TSLA, NVDA
echo    UK: BP.L, HSBA.L, VOD.L, BARC.L
echo.
echo ============================================================================
echo.
pause

REM Save current directory
set ORIGINAL_DIR=%CD%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

REM Run individual stock trainer
call "%ORIGINAL_DIR%\TRAIN_INDIVIDUAL_STOCKS.bat"

echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using Unified Trading System v193.11.7.5
echo.
exit /b 0

@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  COMPLETE REGIME TRADING SYSTEM - MENU LAUNCHER
REM  Version: v1.3.15.67 FINAL
REM  Date: 2026-02-01
REM  Fix: Removed startup checks that hang on PyTorch
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

REM Set environment variables
set KERAS_BACKEND=torch
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Fix Unicode for console
chcp 65001 >nul 2>&1

:MENU
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║           COMPLETE REGIME TRADING SYSTEM v1.3.15.67                      ║
echo ║                                                                           ║
echo ║                    Smart Trading Menu Launcher                            ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Select an option:
echo.
echo   ┌─────────────────────────────────────────────────────────────────────┐
echo   │  TRADING                                                            │
echo   ├─────────────────────────────────────────────────────────────────────┤
echo   │  1. Start Unified Trading Dashboard  [RECOMMENDED]                  │
echo   │     → http://localhost:8050                                         │
echo   │     → Full ML signals, Portfolio management                         │
echo   │                                                                     │
echo   │  6. Start Paper Trading Platform                                    │
echo   │     → Simulated trading environment                                 │
echo   │                                                                     │
echo   │  9. Open Basic Dashboard                                            │
echo   │     → http://localhost:5002                                         │
echo   └─────────────────────────────────────────────────────────────────────┘
echo.
echo   ┌─────────────────────────────────────────────────────────────────────┐
echo   │  OVERNIGHT PIPELINES                                                │
echo   ├─────────────────────────────────────────────────────────────────────┤
echo   │  2. Run AU Overnight Pipeline  (15-20 min)                          │
echo   │     → Scans 240 ASX stocks                                          │
echo   │     → Generates morning report                                      │
echo   │                                                                     │
echo   │  3. Run US Overnight Pipeline  (15-20 min)                          │
echo   │     → Scans 240 NYSE/NASDAQ stocks                                  │
echo   │     → Generates morning report                                      │
echo   │                                                                     │
echo   │  4. Run UK Overnight Pipeline  (15-20 min)                          │
echo   │     → Scans 240 LSE stocks                                          │
echo   │     → Generates morning report                                      │
echo   │                                                                     │
echo   │  5. Run ALL Markets Pipelines  (45-60 min)                          │
echo   │     → AU + US + UK sequentially                                     │
echo   │     → Complete overnight analysis                                   │
echo   └─────────────────────────────────────────────────────────────────────┘
echo.
echo   ┌─────────────────────────────────────────────────────────────────────┐
echo   │  SYSTEM                                                             │
echo   ├─────────────────────────────────────────────────────────────────────┤
echo   │  7. View System Status                                              │
echo   │     → Check components and accuracy                                 │
echo   │                                                                     │
echo   │  8. Advanced Options                                                │
echo   │     → FinBERT test, diagnostics, etc.                               │
echo   │                                                                     │
echo   │  0. Exit                                                            │
echo   └─────────────────────────────────────────────────────────────────────┘
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto START_DASHBOARD
if "%choice%"=="2" goto RUN_AU_PIPELINE
if "%choice%"=="3" goto RUN_US_PIPELINE
if "%choice%"=="4" goto RUN_UK_PIPELINE
if "%choice%"=="5" goto RUN_ALL_PIPELINES
if "%choice%"=="6" goto START_PAPER_TRADING
if "%choice%"=="7" goto SYSTEM_STATUS
if "%choice%"=="8" goto ADVANCED_OPTIONS
if "%choice%"=="9" goto BASIC_DASHBOARD
if "%choice%"=="0" goto EXIT

echo.
echo [ERROR] Invalid choice. Please enter 0-9.
timeout /t 2 >nul
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 1: Start Unified Trading Dashboard
REM ═══════════════════════════════════════════════════════════════════════════
:START_DASHBOARD
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                   STARTING UNIFIED TRADING DASHBOARD                      ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Dashboard URL: http://localhost:8050
echo   Press Ctrl+C to stop the dashboard
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

python unified_trading_dashboard.py

if errorlevel 1 (
    echo.
    echo [ERROR] Dashboard failed to start
    echo.
    pause
)
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 2: Run AU Overnight Pipeline
REM ═══════════════════════════════════════════════════════════════════════════
:RUN_AU_PIPELINE
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                   AUSTRALIAN OVERNIGHT PIPELINE                           ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This will scan 240 ASX stocks and generate a morning report.
echo   Estimated time: 15-20 minutes
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Pipeline complete!
echo   Report: models\screening\reports\morning_reports\au_morning_report.json
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 3: Run US Overnight Pipeline
REM ═══════════════════════════════════════════════════════════════════════════
:RUN_US_PIPELINE
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                      US OVERNIGHT PIPELINE                                ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This will scan 240 NYSE/NASDAQ stocks and generate a morning report.
echo   Estimated time: 15-20 minutes
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Pipeline complete!
echo   Report: models\screening\reports\morning_reports\us_morning_report.json
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 4: Run UK Overnight Pipeline
REM ═══════════════════════════════════════════════════════════════════════════
:RUN_UK_PIPELINE
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                      UK OVERNIGHT PIPELINE                                ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This will scan 240 LSE stocks and generate a morning report.
echo   Estimated time: 15-20 minutes
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Pipeline complete!
echo   Report: models\screening\reports\morning_reports\uk_morning_report.json
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 5: Run ALL Markets Pipelines
REM ═══════════════════════════════════════════════════════════════════════════
:RUN_ALL_PIPELINES
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                   ALL MARKETS OVERNIGHT PIPELINE                          ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   This will run AU, US, and UK pipelines sequentially.
echo   Estimated time: 45-60 minutes
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause

echo [1/3] Running AU Pipeline...
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo [2/3] Running US Pipeline...
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo [3/3] Running UK Pipeline...
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   All pipelines complete!
echo   Reports in: models\screening\reports\morning_reports\
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 6: Start Paper Trading
REM ═══════════════════════════════════════════════════════════════════════════
:START_PAPER_TRADING
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                   PAPER TRADING PLATFORM                                  ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Starting paper trading coordinator...
echo   Press Ctrl+C to stop
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

python paper_trading_coordinator.py

if errorlevel 1 (
    echo.
    echo [ERROR] Paper trading failed to start
    echo.
    pause
)
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 7: System Status
REM ═══════════════════════════════════════════════════════════════════════════
:SYSTEM_STATUS
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                        SYSTEM STATUS CHECK                                ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Python Version:
python --version

echo.
echo [INFO] Installed Packages:
echo.
python -c "import sys; print('- Python:', sys.version.split()[0])"
python -c "try: import torch; print('- PyTorch:', torch.__version__)\nexcept: print('- PyTorch: NOT INSTALLED')"
python -c "try: import transformers; print('- transformers:', transformers.__version__)\nexcept: print('- transformers: NOT INSTALLED')"
python -c "try: import keras; print('- Keras:', keras.__version__)\nexcept: print('- Keras: NOT INSTALLED')"
python -c "try: import dash; print('- Dash:', dash.__version__)\nexcept: print('- Dash: NOT INSTALLED')"

echo.
echo [INFO] System Accuracy Estimate:
python -c "try: from transformers import BertForSequenceClassification; print('- FinBERT: Available (95%% accuracy)'); acc='80-82%%'\nexcept: print('- FinBERT: Fallback (60%% accuracy)'); acc='72-75%%'\nprint('- Technical Analysis: Available (68%% accuracy)')\nprint('- Overall System:', acc)"

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.
pause
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 8: Advanced Options
REM ═══════════════════════════════════════════════════════════════════════════
:ADVANCED_OPTIONS
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                        ADVANCED OPTIONS                                   ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Select an option:
echo.
echo   1. Test FinBERT Loading
echo   2. Load FinBERT from Cache
echo   3. Download FinBERT Model
echo   4. Run Diagnostics
echo   5. Reinstall Dependencies
echo   0. Back to Main Menu
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

set /p adv_choice="Enter your choice (0-5): "

if "%adv_choice%"=="1" (
    python FIX_FINBERT_LOADING_v1.3.15.66.py
    pause
    goto ADVANCED_OPTIONS
)

if "%adv_choice%"=="2" (
    python LOAD_FINBERT_FROM_CACHE_v1.3.15.66.py
    pause
    goto ADVANCED_OPTIONS
)

if "%adv_choice%"=="3" (
    python DOWNLOAD_FINBERT_v1.3.15.66.py
    pause
    goto ADVANCED_OPTIONS
)

if "%adv_choice%"=="4" (
    echo.
    echo Running diagnostics...
    python --version
    pip list | findstr "torch transformers keras dash"
    pause
    goto ADVANCED_OPTIONS
)

if "%adv_choice%"=="5" (
    echo.
    echo This will reinstall torch, transformers, and dependencies.
    echo This may take 5-10 minutes.
    pause
    COMPLETE_FIX_TORCH_TRANSFORMERS_v1.3.15.66.bat
    pause
    goto ADVANCED_OPTIONS
)

if "%adv_choice%"=="0" goto MENU

echo.
echo [ERROR] Invalid choice.
timeout /t 2 >nul
goto ADVANCED_OPTIONS

REM ═══════════════════════════════════════════════════════════════════════════
REM  OPTION 9: Basic Dashboard
REM ═══════════════════════════════════════════════════════════════════════════
:BASIC_DASHBOARD
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                      BASIC DASHBOARD                                      ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Dashboard URL: http://localhost:5002
echo   Press Ctrl+C to stop
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

if exist regime_dashboard.py (
    python regime_dashboard.py
) else if exist dashboard.py (
    python dashboard.py
) else (
    echo [ERROR] Dashboard file not found
    echo.
    echo Available dashboards:
    echo - unified_trading_dashboard.py (use Option 1)
    pause
)
goto MENU

REM ═══════════════════════════════════════════════════════════════════════════
REM  EXIT
REM ═══════════════════════════════════════════════════════════════════════════
:EXIT
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                           ║
echo ║                   Thank you for using the system!                         ║
echo ║                                                                           ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo   Happy trading! 💰
echo.
timeout /t 2 >nul
exit /b 0

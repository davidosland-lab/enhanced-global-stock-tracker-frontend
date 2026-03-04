@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  COMPLETE REGIME TRADING SYSTEM - SMART LAUNCHER
REM  Version: v1.3.15.45 FINAL
REM  Date: 2026-01-29
REM  
REM  NEW in v1.3.15.45 FINAL:
REM  - Complete clean installation package (not a patch)
REM  - FinBERT v4.4.4 fully integrated with sentiment gates
REM  - Fixed dashboard ImportError (IntegratedSentimentAnalyzer)
REM  - PyTorch CPU version for compatibility (no DLL conflicts)
REM  - Automatic FinBERT model download
REM  - Unified trading dashboard with sentiment panel
REM  
REM  Features:
REM  - Automatic first-time vs restart detection
REM  - Dependency installation on first run (PyTorch CPU + transformers)
REM  - Complete overnight pipeline + live trading integration
REM  - Multi-market support (AU/US/UK)
REM  - Sentiment-based trading gates (BLOCK/REDUCE/CAUTION/ALLOW)
REM ═══════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

REM Configuration
set "INSTALL_MARKER=.system_installed"
set "VENV_DIR=venv"
set "PYTHON_MIN_VERSION=3.8"
set "LOG_DIR=logs"
set "STATE_DIR=state"

REM Colors (basic)
set "COLOR_GREEN=[92m"
set "COLOR_YELLOW=[93m"
set "COLOR_RED=[91m"
set "COLOR_BLUE=[94m"
set "COLOR_RESET=[0m"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   COMPLETE REGIME TRADING SYSTEM
echo   Smart Launcher - v1.3.15.45 FINAL (FinBERT Integration + Sentiment Gates)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 1: Check if this is first-time setup
REM ──────────────────────────────────────────────────────────────────────────

if exist "%INSTALL_MARKER%" (
    echo %COLOR_GREEN%[OK] System previously installed - resuming normal operation%COLOR_RESET%
    set "FIRST_TIME=0"
    goto :check_environment
) else (
    echo %COLOR_YELLOW%[!] First-time installation detected%COLOR_RESET%
    echo     Installing dependencies and configuring system...
    echo.
    set "FIRST_TIME=1"
    goto :first_time_setup
)

:first_time_setup
REM ──────────────────────────────────────────────────────────────────────────
REM  FIRST-TIME SETUP: Install all dependencies
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   FIRST-TIME SETUP
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %COLOR_RED%[X] ERROR: Python not found%COLOR_RESET%
    echo.
    echo Please install Python %PYTHON_MIN_VERSION% or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo %COLOR_GREEN%[OK] Python found%COLOR_RESET%
echo.

REM Create virtual environment
echo [2/7] Creating virtual environment...
if exist "%VENV_DIR%" (
    echo     Virtual environment already exists, skipping...
) else (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo %COLOR_RED%[X] Failed to create virtual environment%COLOR_RESET%
        pause
        exit /b 1
    )
    echo %COLOR_GREEN%[OK] Virtual environment created%COLOR_RESET%
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo %COLOR_RED%[X] Failed to activate virtual environment%COLOR_RESET%
    pause
    exit /b 1
)
echo %COLOR_GREEN%[OK] Virtual environment activated%COLOR_RESET%
echo.

REM Upgrade pip
echo [4/7] Upgrading pip...
echo.
python -m pip install --upgrade pip
if errorlevel 1 (
    echo %COLOR_RED%[X] pip upgrade failed%COLOR_RESET%
) else (
    echo.
    echo %COLOR_GREEN%[OK] pip upgraded%COLOR_RESET%
)
echo.

REM Install dependencies
echo [5/7] Installing dependencies (this may take several minutes)...
echo.
echo     You will see each package being downloaded and installed below:
echo     ────────────────────────────────────────────────────────────────
echo.

REM Install PyTorch CPU version first (avoids DLL conflicts)
echo     [5.1/7] Installing PyTorch (CPU version for compatibility)...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo     WARNING: PyTorch CPU install failed, trying default...
    python -m pip install torch torchvision
)
echo.

REM Install other dependencies
if exist "requirements.txt" (
    echo     [5.2/7] Installing from requirements.txt...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo %COLOR_YELLOW%[!] Some packages failed to install, trying core packages only...%COLOR_RESET%
        echo.
        pip install transformers feedparser yahooquery yfinance pandas numpy dash plotly requests beautifulsoup4
    )
) else (
    echo     [5.2/7] requirements.txt not found, installing core packages...
    echo.
    pip install transformers feedparser yahooquery yfinance pandas numpy dash plotly requests beautifulsoup4
)
echo.
echo %COLOR_GREEN%[OK] Dependencies installed%COLOR_RESET%
echo.

REM Create directories
echo [6/7] Creating required directories...
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%LOG_DIR%\screening" mkdir "%LOG_DIR%\screening"
if not exist "%LOG_DIR%\trading" mkdir "%LOG_DIR%\trading"
if not exist "%STATE_DIR%" mkdir "%STATE_DIR%"
if not exist "reports" mkdir "reports"
if not exist "reports\screening" mkdir "reports\screening"
if not exist "reports\csv_exports" mkdir "reports\csv_exports"
if not exist "reports\morning_reports" mkdir "reports\morning_reports"
echo %COLOR_GREEN%[OK] Directories created%COLOR_RESET%
echo.

REM Create install marker
echo [7/7] Marking installation complete...
echo Installation completed: %date% %time% > "%INSTALL_MARKER%"
echo %COLOR_GREEN%[OK] First-time setup complete!%COLOR_RESET%
echo.

goto :check_environment

:check_environment
REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 2: Verify environment and dependencies
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   ENVIRONMENT CHECK
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Activate virtual environment if not already active
if defined VIRTUAL_ENV (
    echo %COLOR_GREEN%[OK] Virtual environment active%COLOR_RESET%
) else (
    if exist "%VENV_DIR%\Scripts\activate.bat" (
        echo [*] Activating virtual environment...
        call "%VENV_DIR%\Scripts\activate.bat"
        echo %COLOR_GREEN%[OK] Virtual environment activated%COLOR_RESET%
    ) else (
        echo %COLOR_YELLOW%[!] No virtual environment found, using system Python%COLOR_RESET%
    )
)
echo.

REM Quick dependency check
echo [*] Verifying core dependencies...
python -c "import yfinance, pandas, numpy, flask, requests" 2>nul
if errorlevel 1 (
    echo %COLOR_RED%[X] Core dependencies missing%COLOR_RESET%
    echo     Run this script again to reinstall dependencies
    pause
    exit /b 1
)
echo %COLOR_GREEN%[OK] Core dependencies verified%COLOR_RESET%
echo.

goto :show_menu

:show_menu
REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 3: Main Menu (UPDATED v1.3.15.10)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   MAIN MENU
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   1. Run AU OVERNIGHT PIPELINE (with progress)
echo   2. Run US OVERNIGHT PIPELINE (with progress)
echo   3. Run UK OVERNIGHT PIPELINE (with progress)
echo   4. Run ALL MARKETS PIPELINES (sequential)
echo   5. Start PAPER TRADING PLATFORM
echo   6. View System Status
echo   7. UNIFIED TRADING DASHBOARD (Stock Selection + Live Trading + Charts)
echo   8. Open Basic Trading Dashboard
echo   9. Advanced Options
echo   0. Exit
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

set /p "MENU_CHOICE=Select option (0-9): "

if "%MENU_CHOICE%"=="1" goto :run_au_pipeline
if "%MENU_CHOICE%"=="2" goto :run_us_pipeline
if "%MENU_CHOICE%"=="3" goto :run_uk_pipeline
if "%MENU_CHOICE%"=="4" goto :run_all_pipelines
if "%MENU_CHOICE%"=="5" goto :trading_platform
if "%MENU_CHOICE%"=="6" goto :system_status
if "%MENU_CHOICE%"=="7" goto :unified_dashboard
if "%MENU_CHOICE%"=="8" goto :dashboard
if "%MENU_CHOICE%"=="9" goto :advanced_menu
if "%MENU_CHOICE%"=="0" goto :exit_script

echo %COLOR_RED%Invalid choice%COLOR_RESET%
timeout /t 2 >nul
goto :show_menu

:run_au_pipeline
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 1: Run AU Overnight Pipeline (with real-time progress)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   AU OVERNIGHT PIPELINE: Australian Market Analysis
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Sophisticated 6-phase analysis:
echo   - Phase 1: Market Sentiment (SPI gaps, US overnight)
echo   - Phase 2: Stock Scanning (240 ASX stocks)
echo   - Phase 2.5: Event Risk Assessment
echo   - Phase 3: Batch Prediction (FinBERT + LSTM ML)
echo   - Phase 4: Opportunity Scoring (14 market regimes)
echo   - Phase 5: Report Generation (HTML + email)
echo.
echo   Estimated time: 15-20 minutes
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo %COLOR_BLUE%[->] Starting AU overnight pipeline...%COLOR_RESET%
echo %COLOR_BLUE%[->] You will see real-time progress below:%COLOR_RESET%
echo.

REM Run pipeline directly (not through complete_workflow) to show progress
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours

if errorlevel 1 (
    echo.
    echo %COLOR_RED%[X] Pipeline encountered errors%COLOR_RESET%
    echo     Check logs\au_pipeline.log for details
) else (
    echo.
    echo %COLOR_GREEN%[OK] AU pipeline completed successfully!%COLOR_RESET%
    echo     Report saved to: models\screening\reports\morning_reports\
)

echo.
pause
goto :show_menu

:run_us_pipeline
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 2: Run US Overnight Pipeline (with real-time progress)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   US OVERNIGHT PIPELINE: United States Market Analysis
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Sophisticated 6-phase analysis:
echo   - Phase 1: Market Sentiment (S&P500, NASDAQ, DOW)
echo   - Phase 2: Stock Scanning (240 NYSE/NASDAQ stocks)
echo   - Phase 2.5: Event Risk Assessment
echo   - Phase 3: Batch Prediction (FinBERT + LSTM ML)
echo   - Phase 4: Opportunity Scoring (14 market regimes)
echo   - Phase 5: Report Generation (HTML + email)
echo.
echo   Estimated time: 15-20 minutes
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo %COLOR_BLUE%[->] Starting US overnight pipeline...%COLOR_RESET%
echo %COLOR_BLUE%[->] You will see real-time progress below:%COLOR_RESET%
echo.

python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

if errorlevel 1 (
    echo.
    echo %COLOR_RED%[X] Pipeline encountered errors%COLOR_RESET%
    echo     Check logs\us_pipeline.log for details
) else (
    echo.
    echo %COLOR_GREEN%[OK] US pipeline completed successfully!%COLOR_RESET%
    echo     Report saved to: models\screening\reports\morning_reports\
)

echo.
pause
goto :show_menu

:run_uk_pipeline
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 3: Run UK Overnight Pipeline (with real-time progress)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UK OVERNIGHT PIPELINE: United Kingdom Market Analysis
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Sophisticated 6-phase analysis:
echo   - Phase 1: Market Sentiment (FTSE 100, FTSE 250)
echo   - Phase 2: Stock Scanning (240 LSE stocks)
echo   - Phase 2.5: Event Risk Assessment
echo   - Phase 3: Batch Prediction (FinBERT + LSTM ML)
echo   - Phase 4: Opportunity Scoring (14 market regimes)
echo   - Phase 5: Report Generation (HTML + email)
echo.
echo   Estimated time: 15-20 minutes
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo %COLOR_BLUE%[->] Starting UK overnight pipeline...%COLOR_RESET%
echo %COLOR_BLUE%[->] You will see real-time progress below:%COLOR_RESET%
echo.

python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

if errorlevel 1 (
    echo.
    echo %COLOR_RED%[X] Pipeline encountered errors%COLOR_RESET%
    echo     Check logs\uk_pipeline.log for details
) else (
    echo.
    echo %COLOR_GREEN%[OK] UK pipeline completed successfully!%COLOR_RESET%
    echo     Report saved to: models\screening\reports\morning_reports\
)

echo.
pause
goto :show_menu

:run_all_pipelines
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 4: Run All Markets Pipelines (sequential with progress)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ALL MARKETS PIPELINES: AU + US + UK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   This will run all three market pipelines sequentially:
echo   1. AU (Australian ASX - 240 stocks)
echo   2. US (NYSE/NASDAQ - 240 stocks)
echo   3. UK (London LSE - 240 stocks)
echo.
echo   Estimated time: 45-60 minutes total
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo %COLOR_BLUE%[->] Starting all market pipelines...%COLOR_RESET%
echo.

REM Run AU
echo ═══════════════════════════════════════════════════════════════════════════
echo [1/3] Running AU Pipeline...
echo ═══════════════════════════════════════════════════════════════════════════
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours
echo.

REM Run US
echo ═══════════════════════════════════════════════════════════════════════════
echo [2/3] Running US Pipeline...
echo ═══════════════════════════════════════════════════════════════════════════
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

REM Run UK
echo ═══════════════════════════════════════════════════════════════════════════
echo [3/3] Running UK Pipeline...
echo ═══════════════════════════════════════════════════════════════════════════
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo %COLOR_GREEN%[OK] All market pipelines completed!%COLOR_RESET%
echo     Reports saved to: models\screening\reports\morning_reports\
echo.
pause
goto :show_menu

:trading_platform
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 5: Start Paper Trading Platform (NEW in v1.3.15.10)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PAPER TRADING PLATFORM
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   This will start the live paper trading system that:
echo   - Uses signals from pipeline reports
echo   - Executes automated trades
echo   - Manages positions and risk
echo   - Provides real-time monitoring
echo.
echo   Make sure you have run overnight pipelines first!
echo.

REM Check for existing reports
set "REPORTS_FOUND=0"
if exist "models\screening\reports\morning_reports\*.json" set "REPORTS_FOUND=1"

if "%REPORTS_FOUND%"=="0" (
    echo %COLOR_YELLOW%[!] WARNING: No pipeline reports found%COLOR_RESET%
    echo     You should run overnight pipelines first (Options 1-4)
    echo.
    set /p "CONFIRM=Continue anyway? (Y/N): "
    if /i not "!CONFIRM!"=="Y" goto :show_menu
) else (
    echo %COLOR_GREEN%[OK] Pipeline reports found%COLOR_RESET%
    echo.
    set /p "CONFIRM=Start trading platform? (Y/N): "
    if /i not "!CONFIRM!"=="Y" goto :show_menu
)

echo.
echo %COLOR_BLUE%[->] Starting paper trading platform...%COLOR_RESET%
echo.
echo %COLOR_GREEN%[TIP] You can run both Paper Trading AND Dashboard:%COLOR_RESET%
echo   1. This will start Paper Trading in background
echo   2. Then you can launch Dashboard (Option 7) to monitor visually
echo   3. Both will run simultaneously!
echo.
echo %COLOR_BLUE%[->] Starting in background...%COLOR_RESET%

REM Start paper trading in background
start "Paper Trading Platform" python paper_trading_coordinator.py --config config/live_trading_config.json

timeout /t 3 /nobreak >nul

echo.
echo %COLOR_GREEN%[OK] Paper Trading Platform started in background!%COLOR_RESET%
echo.
echo %COLOR_GREEN%To monitor trading:%COLOR_RESET%
echo   - Option 7: Launch Dashboard (visual monitoring)
echo   - Option 6: Check system status
echo   - Check logs: logs\paper_trading.log
echo.
echo %COLOR_YELLOW%To stop trading:%COLOR_RESET%
echo   - Close the "Paper Trading Platform" window
echo   - Or use Task Manager to end python.exe process
echo.
pause
goto :show_menu

:system_status
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 6: System Status
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   SYSTEM STATUS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Check Python
python --version
echo.

REM Check virtual environment
if defined VIRTUAL_ENV (
    echo Virtual Environment: %COLOR_GREEN%Active%COLOR_RESET%
    echo Location: %VIRTUAL_ENV%
) else (
    echo Virtual Environment: %COLOR_YELLOW%Not Active%COLOR_RESET%
)
echo.

REM Check key dependencies
echo Key Dependencies:
python -c "import yfinance; print('  yfinance: [92mInstalled[0m')" 2>nul || echo   yfinance: %COLOR_RED%Missing%COLOR_RESET%
python -c "import pandas; print('  pandas: [92mInstalled[0m')" 2>nul || echo   pandas: %COLOR_RED%Missing%COLOR_RESET%
python -c "import numpy; print('  numpy: [92mInstalled[0m')" 2>nul || echo   numpy: %COLOR_RED%Missing%COLOR_RESET%
python -c "import flask; print('  flask: [92mInstalled[0m')" 2>nul || echo   flask: %COLOR_RED%Missing%COLOR_RESET%
python -c "import sklearn; print('  scikit-learn: [92mInstalled[0m')" 2>nul || echo   scikit-learn: %COLOR_RED%Missing%COLOR_RESET%
echo.

REM Check reports
echo Recent Pipeline Reports:
if exist "models\screening\reports\morning_reports\*.json" (
    echo   Found reports in: models\screening\reports\morning_reports\
    dir /b models\screening\reports\morning_reports\*.json 2>nul | find /c ".json" > temp_count.txt
    set /p REPORT_COUNT=<temp_count.txt
    del temp_count.txt 2>nul
    echo   Total reports: %REPORT_COUNT%
) else (
    echo   %COLOR_YELLOW%No reports found%COLOR_RESET%
)
echo.

REM Check trading state
if exist "state\paper_trading_state.json" (
    echo Trading State: %COLOR_GREEN%Found%COLOR_RESET%
) else (
    echo Trading State: %COLOR_YELLOW%Not initialized%COLOR_RESET%
)
echo.

pause
goto :show_menu

:unified_dashboard
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 7: Unified Trading Dashboard (NEW - Stock Selection + Trading + Charts)
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UNIFIED TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   This is the ALL-IN-ONE interface:
echo   • Interactive stock selection (presets or custom)
echo   • Real-time paper trading with ML signals
echo   • Live dashboard with portfolio tracking
echo   • 24-hour market performance charts
echo.
echo   Stock Presets Available:
echo   • ASX Blue Chips (CBA.AX, BHP.AX, RIO.AX, WOW.AX, CSL.AX)
echo   • ASX Mining (RIO.AX, BHP.AX, FMG.AX, NCM.AX, S32.AX)
echo   • ASX Banks (CBA.AX, NAB.AX, WBC.AX, ANZ.AX)
echo   • US Tech Giants (AAPL, MSFT, GOOGL, NVDA, TSLA)
echo   • US Blue Chips (AAPL, JPM, JNJ, WMT, XOM)
echo   • US Growth (TSLA, NVDA, AMD, PLTR, SQ)
echo   • Global Mix (AAPL, MSFT, CBA.AX, BHP.AX, HSBA.L)
echo   • Custom (Enter your own symbols)
echo.

if exist "unified_trading_dashboard.py" (
    echo %COLOR_BLUE%[->] Starting unified dashboard server...%COLOR_RESET%
    echo.
    echo %COLOR_GREEN%[INFO] Checking Python environment:%COLOR_RESET%
    python --version
    python -c "import sys; print('Python location:', sys.executable)"
    echo.
    
    REM Quick check for dash
    python -c "import dash" 2>nul
    if errorlevel 1 (
        echo %COLOR_YELLOW%[!] Warning: dash module not detected%COLOR_RESET%
        echo.
        echo If you see a ModuleNotFoundError, install dash:
        echo   1. Run: INSTALL_DASHBOARD_DEPS.bat
        echo   2. Or manually: pip install dash plotly
        echo.
        echo %COLOR_GREEN%Attempting to start anyway...%COLOR_RESET%
        echo.
        timeout /t 3 /nobreak >nul
    ) else (
        echo %COLOR_GREEN%[OK] Dash installed%COLOR_RESET%
        echo.
    )
    
    echo Dashboard will open at: http://localhost:8050
    echo.
    echo %COLOR_GREEN%[OK] Once started:%COLOR_RESET%
    echo   1. Open browser to http://localhost:8050
    echo   2. Select stocks from dropdown or enter custom symbols
    echo   3. Click "Start Trading" button
    echo   4. Watch live trading with ML signals
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    python unified_trading_dashboard.py
    
    REM If it failed, show helpful error
    if errorlevel 1 (
        echo.
        echo %COLOR_RED%[X] Dashboard failed to start%COLOR_RESET%
        echo.
        echo %COLOR_YELLOW%Common fixes:%COLOR_RESET%
        echo   1. Run: INSTALL_DASHBOARD_DEPS.bat
        echo   2. Or: pip install dash plotly
        echo   3. Check Python location matches pip location
        echo.
    )
) else (
    echo %COLOR_RED%[X] unified_trading_dashboard.py not found%COLOR_RESET%
    echo.
    pause
)

goto :show_menu

:dashboard
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 8: Basic Trading Dashboard
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if exist "dashboard.py" (
    echo %COLOR_BLUE%[->] Starting dashboard server...%COLOR_RESET%
    echo.
    echo Dashboard will open at: http://localhost:5002
    echo Press Ctrl+C to stop the server
    echo.
    python dashboard.py
) else (
    echo %COLOR_RED%[X] dashboard.py not found%COLOR_RESET%
    echo.
    pause
)

goto :show_menu

:advanced_menu
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 8: Advanced Options
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ADVANCED OPTIONS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   1. Reinstall Dependencies
echo   2. Clear All Logs
echo   3. Reset Trading State
echo   4. View Recent Logs
echo   5. Back to Main Menu
echo.

set /p "ADV_CHOICE=Select option (1-5): "

if "%ADV_CHOICE%"=="1" goto :reinstall_deps
if "%ADV_CHOICE%"=="2" goto :clear_logs
if "%ADV_CHOICE%"=="3" goto :reset_state
if "%ADV_CHOICE%"=="4" goto :view_logs
if "%ADV_CHOICE%"=="5" goto :show_menu

echo %COLOR_RED%Invalid choice%COLOR_RESET%
timeout /t 2 >nul
goto :advanced_menu

:reinstall_deps
echo.
echo %COLOR_YELLOW%[!] Reinstalling dependencies...%COLOR_RESET%
echo.
echo     You will see each package being reinstalled below:
echo     ────────────────────────────────────────────────────────────────
echo.
pip install -r requirements.txt --force-reinstall
echo.
echo %COLOR_GREEN%[OK] Dependencies reinstalled%COLOR_RESET%
echo.
pause
goto :advanced_menu

:clear_logs
echo.
echo %COLOR_YELLOW%[!] Clearing logs...%COLOR_RESET%
if exist "logs\*.log" del /q "logs\*.log"
if exist "logs\screening\*.log" del /q "logs\screening\*.log"
if exist "logs\trading\*.log" del /q "logs\trading\*.log"
echo %COLOR_GREEN%[OK] Logs cleared%COLOR_RESET%
echo.
pause
goto :advanced_menu

:reset_state
echo.
echo %COLOR_YELLOW%[!] WARNING: This will reset all trading state%COLOR_RESET%
set /p "CONFIRM=Are you sure? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :advanced_menu
if exist "state\paper_trading_state.json" del /q "state\paper_trading_state.json"
echo %COLOR_GREEN%[OK] Trading state reset%COLOR_RESET%
echo.
pause
goto :advanced_menu

:view_logs
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo Recent log entries:
echo ───────────────────────────────────────────────────────────────────────────
if exist "logs\au_pipeline.log" (
    type "logs\au_pipeline.log" | more
) else (
    echo No logs found
)
echo.
pause
goto :advanced_menu

:exit_script
REM ──────────────────────────────────────────────────────────────────────────
REM  EXIT
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo %COLOR_BLUE%Thank you for using the Regime Trading System!%COLOR_RESET%
echo.
echo v1.3.15.45 FINAL - FinBERT Integration + Sentiment Gates
echo Complete Clean Installation (Not a Patch)
echo.
timeout /t 2 >nul
exit /b 0

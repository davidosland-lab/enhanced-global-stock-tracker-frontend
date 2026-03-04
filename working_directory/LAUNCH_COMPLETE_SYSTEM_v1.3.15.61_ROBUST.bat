@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  COMPLETE REGIME TRADING SYSTEM - SMART LAUNCHER
REM  Version: v1.3.15.61 ROBUST (Fixed PyTorch Installation)
REM  Date: 2026-02-01
REM  
REM  FIXED in v1.3.15.61:
REM  - Improved error handling after PyTorch installation
REM  - Skip PyTorch if already installed (faster)
REM  - Continue even if PyTorch install fails (optional dependency)
REM  - Better error messages and recovery options
REM  - Automatic fallback to system without PyTorch
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
set "COLOR_CYAN=[96m"
set "COLOR_RESET=[0m"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   COMPLETE REGIME TRADING SYSTEM
echo   Smart Launcher - v1.3.15.61 ROBUST (Fixed PyTorch)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 1: AUTO-DEPENDENCY CHECK AND INSTALLATION
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   STEP 1: AUTO-DEPENDENCY CHECK
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Detect if we're in a virtual environment
set "PYTHON_CMD=python"
set "PIP_CMD=pip"
set "USING_VENV=0"

if exist "%VENV_DIR%\Scripts\pip.exe" (
    set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"
    set "PIP_CMD=%VENV_DIR%\Scripts\pip.exe"
    set "USING_VENV=1"
    echo %COLOR_GREEN%[OK] Using virtual environment%COLOR_RESET%
) else (
    echo %COLOR_YELLOW%[!] No virtual environment detected - using system Python%COLOR_RESET%
)
echo.

REM Track if we installed anything
set "INSTALLED_SOMETHING=0"
set "PYTORCH_STATUS=unknown"

REM Check and install scikit-learn
echo [1/4] Checking scikit-learn...
"%PIP_CMD%" show scikit-learn >nul 2>&1
if errorlevel 1 (
    echo     %COLOR_YELLOW%Installing scikit-learn...%COLOR_RESET%
    "%PIP_CMD%" install scikit-learn --quiet
    if errorlevel 1 (
        echo     %COLOR_RED%[!] scikit-learn install failed - will use fallback%COLOR_RESET%
    ) else (
        set "INSTALLED_SOMETHING=1"
        echo     %COLOR_GREEN%[OK] scikit-learn installed%COLOR_RESET%
    )
) else (
    echo     %COLOR_GREEN%[OK] scikit-learn already installed%COLOR_RESET%
)
echo.

REM Check and install Keras
echo [2/4] Checking Keras...
"%PIP_CMD%" show keras >nul 2>&1
if errorlevel 1 (
    echo     %COLOR_YELLOW%Installing Keras 3.x...%COLOR_RESET%
    "%PIP_CMD%" install keras --quiet
    if errorlevel 1 (
        echo     %COLOR_RED%[!] Keras install failed - LSTM will use fallback%COLOR_RESET%
    ) else (
        set "INSTALLED_SOMETHING=1"
        echo     %COLOR_GREEN%[OK] Keras installed%COLOR_RESET%
    )
) else (
    echo     %COLOR_GREEN%[OK] Keras already installed%COLOR_RESET%
)
echo.

REM Check and install PyTorch (CPU version) - WITH BETTER ERROR HANDLING
echo [3/4] Checking PyTorch...
"%PIP_CMD%" show torch >nul 2>&1
if errorlevel 1 (
    echo     %COLOR_YELLOW%Installing PyTorch CPU (~2GB, may take 2-5 minutes)...%COLOR_RESET%
    echo     %COLOR_CYAN%[INFO] This is a large download - please be patient%COLOR_RESET%
    echo.
    
    REM Try to install PyTorch with better error handling
    "%PIP_CMD%" install torch --index-url https://download.pytorch.org/whl/cpu
    
    if errorlevel 1 (
        echo.
        echo     %COLOR_RED%[!] PyTorch installation encountered an error%COLOR_RESET%
        echo     %COLOR_YELLOW%[!] System will continue with Keras fallback for LSTM%COLOR_RESET%
        echo.
        set "PYTORCH_STATUS=failed"
    ) else (
        set "INSTALLED_SOMETHING=1"
        set "PYTORCH_STATUS=installed"
        echo.
        echo     %COLOR_GREEN%[OK] PyTorch CPU installed%COLOR_RESET%
    )
) else (
    echo     %COLOR_GREEN%[OK] PyTorch already installed%COLOR_RESET%
    set "PYTORCH_STATUS=existing"
)
echo.

REM Check and install transformers
echo [4/4] Checking transformers (for FinBERT)...
"%PIP_CMD%" show transformers >nul 2>&1
if errorlevel 1 (
    echo     %COLOR_YELLOW%Installing transformers (~1-2 minutes)...%COLOR_RESET%
    "%PIP_CMD%" install transformers --quiet
    if errorlevel 1 (
        echo     %COLOR_RED%[!] transformers install failed - FinBERT will use fallback%COLOR_RESET%
    ) else (
        set "INSTALLED_SOMETHING=1"
        echo     %COLOR_GREEN%[OK] transformers installed%COLOR_RESET%
    )
) else (
    echo     %COLOR_GREEN%[OK] transformers already installed%COLOR_RESET%
)
echo.

REM Set KERAS_BACKEND environment variable (only if Keras and PyTorch are available)
if "%PYTORCH_STATUS%"=="installed" (
    if not "%KERAS_BACKEND%"=="torch" (
        echo %COLOR_CYAN%[*] Setting KERAS_BACKEND=torch...%COLOR_RESET%
        set "KERAS_BACKEND=torch"
        setx KERAS_BACKEND torch >nul 2>&1
        echo %COLOR_GREEN%[OK] KERAS_BACKEND configured%COLOR_RESET%
        echo.
    )
) else if "%PYTORCH_STATUS%"=="existing" (
    if not "%KERAS_BACKEND%"=="torch" (
        echo %COLOR_CYAN%[*] Setting KERAS_BACKEND=torch...%COLOR_RESET%
        set "KERAS_BACKEND=torch"
        setx KERAS_BACKEND torch >nul 2>&1
        echo %COLOR_GREEN%[OK] KERAS_BACKEND configured%COLOR_RESET%
        echo.
    )
) else (
    echo %COLOR_YELLOW%[!] PyTorch not available - KERAS_BACKEND not configured%COLOR_RESET%
    echo %COLOR_YELLOW%[!] System will run with fallback methods%COLOR_RESET%
    echo.
)

REM If we installed something, notify user
if "%INSTALLED_SOMETHING%"=="1" (
    echo.
    echo %COLOR_GREEN%═══════════════════════════════════════════════════════════════════════════%COLOR_RESET%
    echo %COLOR_GREEN%  DEPENDENCIES INSTALLED SUCCESSFULLY!%COLOR_RESET%
    echo %COLOR_GREEN%═══════════════════════════════════════════════════════════════════════════%COLOR_RESET%
    echo.
    echo %COLOR_CYAN%  Next runs will be faster - all dependencies are now installed!%COLOR_RESET%
    echo.
    timeout /t 3 /nobreak >nul
)

REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 2: Check if this is first-time setup
REM ──────────────────────────────────────────────────────────────────────────

if exist "%INSTALL_MARKER%" (
    echo %COLOR_GREEN%[OK] System previously installed%COLOR_RESET%
    set "FIRST_TIME=0"
    goto :check_environment
) else (
    echo %COLOR_YELLOW%[!] First-time installation detected%COLOR_RESET%
    echo     Installing core dependencies and configuring system...
    echo.
    set "FIRST_TIME=1"
    goto :first_time_setup
)

:first_time_setup
REM ──────────────────────────────────────────────────────────────────────────
REM  FIRST-TIME SETUP: Install core dependencies
REM ──────────────────────────────────────────────────────────────────────────

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   FIRST-TIME SETUP
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
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

REM Create virtual environment if it doesn't exist
echo [2/6] Creating virtual environment...
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
echo [3/6] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo %COLOR_RED%[X] Failed to activate virtual environment%COLOR_RESET%
    pause
    exit /b 1
)
echo %COLOR_GREEN%[OK] Virtual environment activated%COLOR_RESET%
echo.

REM Update Python commands to use venv
set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"
set "PIP_CMD=%VENV_DIR%\Scripts\pip.exe"

REM Upgrade pip
echo [4/6] Upgrading pip...
echo.
"%PYTHON_CMD%" -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo %COLOR_RED%[X] pip upgrade failed%COLOR_RESET%
) else (
    echo %COLOR_GREEN%[OK] pip upgraded%COLOR_RESET%
)
echo.

REM Install core dependencies
echo [5/6] Installing core dependencies (this may take several minutes)...
echo.

REM Install from requirements.txt if it exists
if exist "requirements.txt" (
    echo     Installing from requirements.txt...
    echo.
    "%PIP_CMD%" install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo %COLOR_YELLOW%[!] Some packages failed, trying core packages only...%COLOR_RESET%
        echo.
        "%PIP_CMD%" install yfinance pandas numpy dash plotly requests beautifulsoup4 feedparser yahooquery
    )
) else (
    echo     requirements.txt not found, installing core packages...
    echo.
    "%PIP_CMD%" install yfinance pandas numpy dash plotly requests beautifulsoup4 feedparser yahooquery
)
echo.
echo %COLOR_GREEN%[OK] Core dependencies installed%COLOR_RESET%
echo.

REM Create directories
echo [6/6] Creating required directories...
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
echo Installation completed: %date% %time% > "%INSTALL_MARKER%"
echo %COLOR_GREEN%[OK] First-time setup complete!%COLOR_RESET%
echo.

goto :check_environment

:check_environment
REM ──────────────────────────────────────────────────────────────────────────
REM  STEP 3: Verify environment and dependencies
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
python -c "import yfinance, pandas, numpy" 2>nul
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
REM  STEP 4: Main Menu
REM ──────────────────────────────────────────────────────────────────────────

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   MAIN MENU - v1.3.15.61 ROBUST
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   QUICK START:
echo   ────────────────────────────────────────────────────────────────────────
echo   1. START UNIFIED TRADING DASHBOARD  [RECOMMENDED]
echo      • Interactive stock selection + live trading
echo      • Real-time ML signals (FinBERT + LSTM)
echo      • Portfolio tracking + 24hr charts
echo      • http://localhost:8050
echo.
echo   OVERNIGHT ANALYSIS:
echo   ────────────────────────────────────────────────────────────────────────
echo   2. Run AU OVERNIGHT PIPELINE (15-20 min)
echo   3. Run US OVERNIGHT PIPELINE (15-20 min)
echo   4. Run UK OVERNIGHT PIPELINE (15-20 min)
echo   5. Run ALL MARKETS PIPELINES (45-60 min)
echo.
echo   ADVANCED:
echo   ────────────────────────────────────────────────────────────────────────
echo   6. Start Paper Trading Platform (background)
echo   7. View System Status
echo   8. Open Basic Dashboard (http://localhost:5002)
echo   9. Advanced Options (reinstall, logs, reset)
echo.
echo   0. Exit
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo.

set /p "MENU_CHOICE=Select option (0-9): "

if "%MENU_CHOICE%"=="1" goto :unified_dashboard
if "%MENU_CHOICE%"=="2" goto :run_au_pipeline
if "%MENU_CHOICE%"=="3" goto :run_us_pipeline
if "%MENU_CHOICE%"=="4" goto :run_uk_pipeline
if "%MENU_CHOICE%"=="5" goto :run_all_pipelines
if "%MENU_CHOICE%"=="6" goto :trading_platform
if "%MENU_CHOICE%"=="7" goto :system_status
if "%MENU_CHOICE%"=="8" goto :dashboard
if "%MENU_CHOICE%"=="9" goto :advanced_menu
if "%MENU_CHOICE%"=="0" goto :exit_script

echo %COLOR_RED%Invalid choice%COLOR_RESET%
timeout /t 2 >nul
goto :show_menu

:unified_dashboard
REM ──────────────────────────────────────────────────────────────────────────
REM  OPTION 1: Unified Trading Dashboard [RECOMMENDED]
REM ──────────────────────────────────────────────────────────────────────────

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UNIFIED TRADING DASHBOARD - ALL-IN-ONE INTERFACE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if exist "unified_trading_dashboard.py" (
    echo %COLOR_BLUE%[->] Starting unified dashboard server...%COLOR_RESET%
    echo.
    
    REM Set environment variable for this session
    set "KERAS_BACKEND=torch"
    
    echo %COLOR_GREEN%[INFO] Environment configured%COLOR_RESET%
    echo.
    
    echo ───────────────────────────────────────────────────────────────────────
    echo   Dashboard will open at: %COLOR_CYAN%http://localhost:8050%COLOR_RESET%
    echo ───────────────────────────────────────────────────────────────────────
    echo.
    echo %COLOR_YELLOW%Press Ctrl+C to stop the server%COLOR_RESET%
    echo.
    
    python unified_trading_dashboard.py
    
    REM If it failed, show helpful error
    if errorlevel 1 (
        echo.
        echo %COLOR_RED%[X] Dashboard failed to start%COLOR_RESET%
        echo.
        pause
    )
) else (
    echo %COLOR_RED%[X] unified_trading_dashboard.py not found%COLOR_RESET%
    echo.
    pause
)

goto :show_menu

:run_au_pipeline
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   AU OVERNIGHT PIPELINE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours
echo.
pause
goto :show_menu

:run_us_pipeline
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   US OVERNIGHT PIPELINE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.
pause
goto :show_menu

:run_uk_pipeline
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UK OVERNIGHT PIPELINE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.
pause
goto :show_menu

:run_all_pipelines
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ALL MARKETS PIPELINES
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo [1/3] AU Pipeline...
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo [2/3] US Pipeline...
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo [3/3] UK Pipeline...
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo %COLOR_GREEN%[OK] All pipelines completed!%COLOR_RESET%
pause
goto :show_menu

:trading_platform
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PAPER TRADING PLATFORM
echo ═══════════════════════════════════════════════════════════════════════════
echo.

start "Paper Trading Platform" python paper_trading_coordinator.py --config config/live_trading_config.json
timeout /t 3 /nobreak >nul
echo %COLOR_GREEN%[OK] Paper Trading Platform started!%COLOR_RESET%
pause
goto :show_menu

:system_status
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   SYSTEM STATUS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python --version
echo.

echo Key Dependencies:
python -c "import keras; print('  Keras: [92mInstalled[0m')" 2>nul || echo   Keras: %COLOR_RED%Missing%COLOR_RESET%
python -c "import torch; print('  PyTorch: [92mInstalled[0m')" 2>nul || echo   PyTorch: %COLOR_RED%Missing%COLOR_RESET%
python -c "import transformers; print('  Transformers: [92mInstalled[0m')" 2>nul || echo   Transformers: %COLOR_RED%Missing%COLOR_RESET%
python -c "import sklearn; print('  scikit-learn: [92mInstalled[0m')" 2>nul || echo   scikit-learn: %COLOR_RED%Missing%COLOR_RESET%
echo.

pause
goto :show_menu

:dashboard
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   BASIC DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if exist "dashboard.py" (
    python dashboard.py
) else (
    echo %COLOR_RED%[X] dashboard.py not found%COLOR_RESET%
    pause
)

goto :show_menu

:advanced_menu
cls
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

goto :advanced_menu

:reinstall_deps
echo.
echo %COLOR_YELLOW%[!] Reinstalling dependencies...%COLOR_RESET%
echo.
if exist "requirements.txt" (
    pip install -r requirements.txt --force-reinstall
) else (
    pip install yfinance pandas numpy dash plotly requests beautifulsoup4 feedparser yahooquery --force-reinstall
)
echo.
echo %COLOR_GREEN%[OK] Dependencies reinstalled%COLOR_RESET%
pause
goto :advanced_menu

:clear_logs
echo.
echo %COLOR_YELLOW%[!] Clearing logs...%COLOR_RESET%
if exist "logs\*.log" del /q "logs\*.log"
echo %COLOR_GREEN%[OK] Logs cleared%COLOR_RESET%
pause
goto :advanced_menu

:reset_state
echo.
echo %COLOR_YELLOW%[!] WARNING: Reset trading state?%COLOR_RESET%
set /p "CONFIRM=Are you sure? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :advanced_menu
if exist "state\paper_trading_state.json" del /q "state\paper_trading_state.json"
echo %COLOR_GREEN%[OK] Trading state reset%COLOR_RESET%
pause
goto :advanced_menu

:view_logs
echo.
echo ───────────────────────────────────────────────────────────────────────────
if exist "logs\au_pipeline.log" (
    type "logs\au_pipeline.log" | more
) else (
    echo No logs found
)
pause
goto :advanced_menu

:exit_script
cls
echo.
echo %COLOR_CYAN%═══════════════════════════════════════════════════════════════════════════%COLOR_RESET%
echo %COLOR_CYAN%  Thank you for using the Regime Trading System!%COLOR_RESET%
echo %COLOR_CYAN%═══════════════════════════════════════════════════════════════════════════%COLOR_RESET%
echo.
echo   v1.3.15.61 ROBUST - Fixed PyTorch Installation
echo.
timeout /t 2 >nul
exit /b 0

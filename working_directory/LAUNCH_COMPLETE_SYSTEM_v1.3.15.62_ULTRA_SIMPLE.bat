@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  COMPLETE REGIME TRADING SYSTEM - ULTRA-SIMPLE LAUNCHER
REM  Version: v1.3.15.62 ULTRA-SIMPLE
REM  Date: 2026-02-01
REM  
REM  ULTRA-SIMPLE VERSION:
REM  - No complex dependency checking
REM  - No automatic installations during startup
REM  - Just sets environment and starts menu
REM  - Manual dependency install option in menu
REM  - Cannot crash during startup
REM ═══════════════════════════════════════════════════════════════════════════

REM Change to script directory
cd /d "%~dp0"

REM Set environment variable
set "KERAS_BACKEND=torch"

cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   COMPLETE REGIME TRADING SYSTEM
echo   Ultra-Simple Launcher - v1.3.15.62 (No Auto-Install at Startup)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo [!] No virtual environment - using system Python
)
echo.

:show_menu
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   MAIN MENU - v1.3.15.62 ULTRA-SIMPLE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   QUICK START:
echo   ────────────────────────────────────────────────────────────────────────
echo   1. START UNIFIED TRADING DASHBOARD  [QUICK - 10 seconds]
echo      Opens at: http://localhost:8050
echo.
echo   OVERNIGHT ANALYSIS:
echo   ────────────────────────────────────────────────────────────────────────
echo   2. Run AU OVERNIGHT PIPELINE (15-20 min)
echo   3. Run US OVERNIGHT PIPELINE (15-20 min)
echo   4. Run UK OVERNIGHT PIPELINE (15-20 min)
echo   5. Run ALL MARKETS PIPELINES (45-60 min)
echo.
echo   SETUP ^& ADVANCED:
echo   ────────────────────────────────────────────────────────────────────────
echo   6. Install Missing Dependencies (transformers, keras, torch, sklearn)
echo   7. Start Paper Trading Platform (background)
echo   8. View System Status
echo   9. Open Basic Dashboard (http://localhost:5002)
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
if "%MENU_CHOICE%"=="6" goto :install_deps
if "%MENU_CHOICE%"=="7" goto :trading_platform
if "%MENU_CHOICE%"=="8" goto :system_status
if "%MENU_CHOICE%"=="9" goto :dashboard
if "%MENU_CHOICE%"=="0" goto :exit_script

echo Invalid choice
timeout /t 2 >nul
goto :show_menu

:unified_dashboard
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   UNIFIED TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Starting dashboard at http://localhost:8050
echo Press Ctrl+C to stop
echo.

python unified_trading_dashboard.py

if errorlevel 1 (
    echo.
    echo [X] Dashboard failed to start
    echo.
    echo Common fixes:
    echo   1. Install dependencies: Select option 6 from main menu
    echo   2. Check if port 8050 is already in use
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
echo Starting AU pipeline...
echo.

python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo Pipeline complete
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
echo Starting US pipeline...
echo.

python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo Pipeline complete
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
echo Starting UK pipeline...
echo.

python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours

echo.
echo Pipeline complete
pause
goto :show_menu

:run_all_pipelines
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ALL MARKETS PIPELINES (45-60 minutes)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set /p "CONFIRM=Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :show_menu

echo.
echo [1/3] Running AU Pipeline...
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo [2/3] Running US Pipeline...
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo [3/3] Running UK Pipeline...
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.

echo All pipelines completed!
pause
goto :show_menu

:install_deps
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   INSTALL MISSING DEPENDENCIES
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo This will install:
echo   - transformers (for FinBERT sentiment analysis)
echo   - keras (for LSTM neural network)
echo   - torch (PyTorch CPU ~2GB - OPTIONAL, can skip)
echo   - scikit-learn (for data preprocessing)
echo.
echo Total download size: ~2.5GB (mostly PyTorch)
echo Time required: 3-7 minutes
echo.

set /p "CONFIRM=Install all dependencies? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :install_menu

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Installing dependencies...
echo ───────────────────────────────────────────────────────────────────────────
echo.

REM Determine pip command
if exist "venv\Scripts\pip.exe" (
    set "PIP_CMD=venv\Scripts\pip.exe"
) else (
    set "PIP_CMD=pip"
)

echo [1/4] Installing scikit-learn...
"%PIP_CMD%" install scikit-learn
echo.

echo [2/4] Installing keras...
"%PIP_CMD%" install keras
echo.

echo [3/4] Installing transformers...
"%PIP_CMD%" install transformers
echo.

echo [4/4] Installing PyTorch CPU (~2GB, may take 2-5 minutes)...
echo Press Ctrl+C within 5 seconds to SKIP PyTorch installation
timeout /t 5
"%PIP_CMD%" install torch --index-url https://download.pytorch.org/whl/cpu
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   Installation complete!
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Next step: Select option 1 to start trading dashboard
echo.
pause
goto :show_menu

:install_menu
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   DEPENDENCY INSTALLATION OPTIONS
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   1. Install transformers only (for FinBERT) - 2 minutes
echo   2. Install keras only (for LSTM) - 1 minute
echo   3. Install scikit-learn only - 1 minute
echo   4. Install PyTorch only (2GB) - 3-5 minutes
echo   5. Install ALL dependencies - 5-7 minutes
echo   6. Back to main menu
echo.

set /p "DEP_CHOICE=Select option (1-6): "

REM Determine pip command
if exist "venv\Scripts\pip.exe" (
    set "PIP_CMD=venv\Scripts\pip.exe"
) else (
    set "PIP_CMD=pip"
)

if "%DEP_CHOICE%"=="1" (
    echo.
    echo Installing transformers...
    "%PIP_CMD%" install transformers
    echo.
    echo Done!
    pause
    goto :install_menu
)

if "%DEP_CHOICE%"=="2" (
    echo.
    echo Installing keras...
    "%PIP_CMD%" install keras
    echo.
    echo Done!
    pause
    goto :install_menu
)

if "%DEP_CHOICE%"=="3" (
    echo.
    echo Installing scikit-learn...
    "%PIP_CMD%" install scikit-learn
    echo.
    echo Done!
    pause
    goto :install_menu
)

if "%DEP_CHOICE%"=="4" (
    echo.
    echo Installing PyTorch CPU (~2GB, may take 3-5 minutes)...
    "%PIP_CMD%" install torch --index-url https://download.pytorch.org/whl/cpu
    echo.
    echo Done!
    pause
    goto :install_menu
)

if "%DEP_CHOICE%"=="5" goto :install_deps

if "%DEP_CHOICE%"=="6" goto :show_menu

goto :install_menu

:trading_platform
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PAPER TRADING PLATFORM
echo ═══════════════════════════════════════════════════════════════════════════
echo.

start "Paper Trading Platform" python paper_trading_coordinator.py --config config/live_trading_config.json

timeout /t 3 /nobreak >nul
echo.
echo Paper Trading Platform started in background
echo.
pause
goto :show_menu

:system_status
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   SYSTEM STATUS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo Python Version:
python --version
echo.

echo Virtual Environment:
if defined VIRTUAL_ENV (
    echo   Status: Active
    echo   Location: %VIRTUAL_ENV%
) else (
    echo   Status: Not Active
)
echo.

echo Key Dependencies:
python -c "import keras; print('  Keras: Installed')" 2>nul || echo   Keras: Missing
python -c "import torch; print('  PyTorch: Installed')" 2>nul || echo   PyTorch: Missing
python -c "import transformers; print('  Transformers: Installed')" 2>nul || echo   Transformers: Missing
python -c "import sklearn; print('  scikit-learn: Installed')" 2>nul || echo   scikit-learn: Missing
echo.

echo Environment Variables:
echo   KERAS_BACKEND: %KERAS_BACKEND%
echo.

pause
goto :show_menu

:dashboard
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   BASIC DASHBOARD (http://localhost:5002)
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if exist "dashboard.py" (
    echo Starting dashboard...
    echo Press Ctrl+C to stop
    echo.
    python dashboard.py
) else (
    echo dashboard.py not found
    pause
)

goto :show_menu

:exit_script
cls
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   Thank you for using the Regime Trading System!
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   v1.3.15.62 ULTRA-SIMPLE
echo.
timeout /t 2 >nul
exit /b 0

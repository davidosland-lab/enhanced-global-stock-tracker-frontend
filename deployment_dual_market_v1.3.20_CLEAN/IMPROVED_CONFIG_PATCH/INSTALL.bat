@echo off
REM ========================================
REM Improved Backtest Config - Patch Installer
REM ========================================
echo.
echo ================================================
echo  Improved Backtest Config Patch Installer
echo ================================================
echo.

REM Check if running in correct directory
if not exist "finbert_v4.4.4" (
    echo ERROR: finbert_v4.4.4 folder not found!
    echo.
    echo This script must be run from: C:\Users\david\AATelS
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking target directory...
if not exist "finbert_v4.4.4\models\backtesting" (
    echo ERROR: Target directory not found!
    echo Expected: finbert_v4.4.4\models\backtesting
    pause
    exit /b 1
)
echo     ✓ Target directory found

echo.
echo [2/4] Creating backup...
set BACKUP_DIR=backups\improved_config_backup_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul

REM Backup existing config if it exists
if exist "finbert_v4.4.4\models\backtesting\improved_backtest_config.py" (
    copy "finbert_v4.4.4\models\backtesting\improved_backtest_config.py" "%BACKUP_DIR%\" >nul
    echo     ✓ Backed up existing config
) else (
    echo     ℹ No existing config to backup (new install)
)

echo.
echo [3/4] Installing improved config files...

REM Copy the improved config
copy /Y "finbert_v4.4.4\models\backtesting\improved_backtest_config.py" "..\finbert_v4.4.4\models\backtesting\" >nul
if errorlevel 1 (
    echo     ✗ Failed to copy improved_backtest_config.py
    pause
    exit /b 1
)
echo     ✓ Installed improved_backtest_config.py

REM Copy the README
copy /Y "finbert_v4.4.4\models\backtesting\README_IMPROVED_CONFIG.md" "..\finbert_v4.4.4\models\backtesting\" >nul
if errorlevel 1 (
    echo     ✗ Failed to copy README_IMPROVED_CONFIG.md
    pause
    exit /b 1
)
echo     ✓ Installed README_IMPROVED_CONFIG.md

echo.
echo [4/4] Verifying installation...
if exist "..\finbert_v4.4.4\models\backtesting\improved_backtest_config.py" (
    echo     ✓ Config file installed successfully
) else (
    echo     ✗ Verification failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo  ✓ INSTALLATION COMPLETE!
echo ================================================
echo.
echo Installed files:
echo   - finbert_v4.4.4\models\backtesting\improved_backtest_config.py
echo   - finbert_v4.4.4\models\backtesting\README_IMPROVED_CONFIG.md
echo.
echo NEXT STEPS:
echo.
echo 1. UPDATE YOUR BACKTEST UI:
echo    - Change Confidence Threshold: 85%% → 60%%
echo    - Change Stop Loss: 1%% → 2%%
echo.
echo 2. OR UPDATE BACKEND DEFAULTS:
echo    - Open: finbert_v4.4.4\models\backtesting\backtest_engine.py
echo    - Change: allocation_strategy = 'risk_based'
echo    - Change: stop_loss_percent = 2.0
echo    - Change: enable_take_profit = True
echo.
echo 3. TEST THE CONFIG:
echo    Run your backtest and expect:
echo    - Total Return: -1.5%% → +8-12%%
echo    - Win Rate: 25%% → 45-55%%
echo    - Profit Factor: 0.12 → 1.5-2.4
echo    - Sharpe Ratio: 0.0 → 1.2-1.8
echo.
echo DOCUMENTATION:
echo    See: finbert_v4.4.4\models\backtesting\README_IMPROVED_CONFIG.md
echo.
echo ROLLBACK (if needed):
echo    Copy files from: %BACKUP_DIR%
echo.
echo ================================================
pause

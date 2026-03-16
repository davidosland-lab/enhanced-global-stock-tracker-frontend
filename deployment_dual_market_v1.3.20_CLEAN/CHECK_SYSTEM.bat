@echo off
REM ========================================
REM System File Diagnostic Tool
REM Checks if files are latest version and in correct locations
REM ========================================

echo.
echo ====================================================================
echo  FINBERT v4.4.4 - SYSTEM FILE DIAGNOSTIC
echo ====================================================================
echo.
echo This tool checks:
echo   1. All required files exist
echo   2. Files are in correct locations
echo   3. Files have correct sizes (latest versions)
echo   4. Configuration is correct
echo.
pause

REM Verify we're in the correct directory
if not exist "finbert_v4.4.4" (
    echo.
    echo ====================================================================
    echo  ERROR: Wrong Directory!
    echo ====================================================================
    echo.
    echo This script must be run from: C:\Users\david\AATelS
    echo Current directory: %CD%
    echo.
    echo Please:
    echo   1. Open Command Prompt
    echo   2. Run: cd C:\Users\david\AATelS
    echo   3. Run: CHECK_SYSTEM.bat
    echo.
    pause
    exit /b 1
)

echo [CHECK 1/6] Directory Structure...
echo.

set ERROR_COUNT=0

if exist "finbert_v4.4.4\models\backtesting" (
    echo   [OK] finbert_v4.4.4\models\backtesting
) else (
    echo   [ERROR] finbert_v4.4.4\models\backtesting - NOT FOUND
    set /a ERROR_COUNT+=1
)

echo.
echo [CHECK 2/6] Required Files...
echo.

REM Check backtest_engine.py
if exist "finbert_v4.4.4\models\backtesting\backtest_engine.py" (
    for %%A in (finbert_v4.4.4\models\backtesting\backtest_engine.py) do (
        set SIZE=%%~zA
        if %%~zA GTR 40000 (
            echo   [OK] backtest_engine.py ^(%%~zA bytes^) - Phase 2 code present
        ) else (
            echo   [WARN] backtest_engine.py ^(%%~zA bytes^) - Too small, Phase 2 might be missing
            set /a ERROR_COUNT+=1
        )
    )
) else (
    echo   [ERROR] backtest_engine.py - NOT FOUND
    set /a ERROR_COUNT+=1
)

REM Check improved_backtest_config.py
if exist "finbert_v4.4.4\models\backtesting\improved_backtest_config.py" (
    for %%A in (finbert_v4.4.4\models\backtesting\improved_backtest_config.py) do (
        echo   [OK] improved_backtest_config.py ^(%%~zA bytes^)
    )
) else (
    echo   [WARN] improved_backtest_config.py - NOT FOUND (config patch not installed)
)

REM Check portfolio_backtester.py
if exist "finbert_v4.4.4\models\backtesting\portfolio_backtester.py" (
    echo   [OK] portfolio_backtester.py
) else (
    echo   [ERROR] portfolio_backtester.py - NOT FOUND
    set /a ERROR_COUNT+=1
)

REM Check phase1_phase2_example.py
if exist "finbert_v4.4.4\models\backtesting\phase1_phase2_example.py" (
    echo   [OK] phase1_phase2_example.py
) else (
    echo   [WARN] phase1_phase2_example.py - NOT FOUND (Phase 1 ^& 2 patch not installed)
)

echo.
echo [CHECK 3/6] Phase 2 Features in Code...
echo.

findstr /C:"enable_take_profit" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] enable_take_profit parameter found
) else (
    echo   [ERROR] enable_take_profit parameter NOT FOUND - Phase 2 missing!
    set /a ERROR_COUNT+=1
)

findstr /C:"risk_reward_ratio" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] risk_reward_ratio parameter found
) else (
    echo   [ERROR] risk_reward_ratio parameter NOT FOUND - Phase 2 missing!
    set /a ERROR_COUNT+=1
)

findstr /C:"_check_take_profits" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] _check_take_profits method found
) else (
    echo   [ERROR] _check_take_profits method NOT FOUND - Phase 2 missing!
    set /a ERROR_COUNT+=1
)

findstr /C:"_check_stop_losses" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] _check_stop_losses method found
) else (
    echo   [ERROR] _check_stop_losses method NOT FOUND - Phase 1 missing!
    set /a ERROR_COUNT+=1
)

echo.
echo [CHECK 4/6] Configuration Defaults...
echo.

REM Check allocation_strategy
findstr /N /C:"allocation_strategy: str = " finbert_v4.4.4\models\backtesting\backtest_engine.py | findstr /C:"def __init__" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    REM Found the line, now check the value
    findstr /C:"allocation_strategy: str = 'risk_based'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] allocation_strategy = 'risk_based'
    ) else (
        findstr /C:"allocation_strategy: str = 'equal'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo   [ISSUE] allocation_strategy = 'equal' ^(should be 'risk_based'^)
            echo          This is causing your poor backtest results!
            set /a ERROR_COUNT+=1
        ) else (
            echo   [WARN] allocation_strategy = unknown value
        )
    )
)

REM Check enable_take_profit
findstr /C:"enable_take_profit: bool = True" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] enable_take_profit = True
) else (
    findstr /C:"enable_take_profit: bool = False" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [ISSUE] enable_take_profit = False ^(should be True^)
        echo          Take-profit is disabled!
        set /a ERROR_COUNT+=1
    )
)

REM Check stop_loss_percent
findstr /C:"stop_loss_percent: float = 2.0" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] stop_loss_percent = 2.0
) else (
    findstr /C:"stop_loss_percent: float = 1.0" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [WARN] stop_loss_percent = 1.0 ^(recommended: 2.0^)
    ) else (
        echo   [WARN] stop_loss_percent = unknown value
    )
)

echo.
echo [CHECK 5/6] Diagnostic Tools Available...
echo.

if exist "FIX_BACKTEST_ENGINE_DEFAULTS.py" (
    echo   [OK] FIX_BACKTEST_ENGINE_DEFAULTS.py
) else (
    echo   [WARN] FIX_BACKTEST_ENGINE_DEFAULTS.py - NOT FOUND
    echo          Download from GitHub
)

if exist "DIAGNOSTIC_BACKTEST_ISSUE.py" (
    echo   [OK] DIAGNOSTIC_BACKTEST_ISSUE.py
) else (
    echo   [WARN] DIAGNOSTIC_BACKTEST_ISSUE.py - NOT FOUND
)

if exist "VERIFY_PHASE2_INSTALLATION.py" (
    echo   [OK] VERIFY_PHASE2_INSTALLATION.py
) else (
    echo   [WARN] VERIFY_PHASE2_INSTALLATION.py - NOT FOUND
)

echo.
echo [CHECK 6/6] Patch Folders...
echo.

if exist "PHASE1_PHASE2_PATCH" (
    echo   [OK] PHASE1_PHASE2_PATCH folder exists
) else (
    echo   [INFO] PHASE1_PHASE2_PATCH folder not found ^(already installed?^)
)

if exist "IMPROVED_CONFIG_PATCH" (
    echo   [OK] IMPROVED_CONFIG_PATCH folder exists
) else (
    echo   [INFO] IMPROVED_CONFIG_PATCH folder not found ^(already installed?^)
)

echo.
echo ====================================================================
echo  DIAGNOSTIC RESULTS
echo ====================================================================
echo.

if %ERROR_COUNT% EQU 0 (
    echo   STATUS: [OK] No critical issues found
    echo.
    echo   Your system appears to be configured correctly.
    echo.
    echo   If backtest still shows poor results:
    echo     1. Make sure FinBERT was restarted after patches
    echo     2. Set Confidence Threshold to 60%% ^(not 65%%^)
    echo     3. Run a fresh backtest
    echo.
) else (
    echo   STATUS: [ISSUES FOUND] %ERROR_COUNT% issue^(s^) detected
    echo.
    echo   Common issues and fixes:
    echo.
    
    findstr /C:"allocation_strategy: str = 'equal'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   ISSUE 1: allocation_strategy = 'equal'
        echo   FIX:     Run: python FIX_BACKTEST_ENGINE_DEFAULTS.py
        echo.
    )
    
    findstr /C:"enable_take_profit" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo   ISSUE 2: Phase 2 code missing
        echo   FIX:     Re-install PHASE1_PHASE2_PATCH.zip
        echo            1. Download from GitHub
        echo            2. Extract and run INSTALL.bat
        echo.
    )
)

echo ====================================================================
echo.
echo EXPECTED FILE SIZES ^(Latest Versions^):
echo   backtest_engine.py:              ~42,000 bytes
echo   portfolio_backtester.py:         ~30,000 bytes
echo   improved_backtest_config.py:     ~11,000 bytes
echo   phase1_phase2_example.py:        ~8,000 bytes
echo.
echo EXPECTED CONFIGURATION:
echo   allocation_strategy:    'risk_based'
echo   enable_take_profit:     True
echo   stop_loss_percent:      2.0
echo   risk_reward_ratio:      2.0
echo   risk_per_trade_percent: 1.0
echo   max_portfolio_heat:     6.0
echo.
echo QUICK FIXES:
echo   1. Fix defaults:        python FIX_BACKTEST_ENGINE_DEFAULTS.py
echo   2. Verify Phase 2:      python VERIFY_PHASE2_INSTALLATION.py
echo   3. Full diagnostic:     python DIAGNOSTIC_BACKTEST_ISSUE.py
echo.
echo ====================================================================
echo.

if %ERROR_COUNT% GTR 0 (
    echo RECOMMENDATION: Run the fix script to resolve issues
    echo.
    echo Command: python FIX_BACKTEST_ENGINE_DEFAULTS.py
    echo.
)

pause

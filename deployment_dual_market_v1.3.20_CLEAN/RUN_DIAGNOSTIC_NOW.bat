@echo off
REM ========================================
REM Backtest Issue - LIVE DIAGNOSTIC
REM ========================================

echo.
echo ====================================================================
echo  BACKTEST DIAGNOSTIC - LIVE ANALYSIS
echo ====================================================================
echo.
echo Issue: Backtest showing -0.86%% return after patches applied
echo Win Rate: 45.5%% (improved) but Profit Factor: 0.54 (very bad)
echo.
echo This diagnostic will identify why take-profit is not working.
echo.
pause

REM Change to project directory
cd /d %~dp0..
if not exist "finbert_v4.4.4" (
    echo ERROR: Not in correct directory!
    echo Current: %CD%
    echo Expected: C:\Users\david\AATelS
    pause
    exit /b 1
)

echo [1/5] Checking backtest_engine.py...
echo.

REM Check file exists and size
if exist "finbert_v4.4.4\models\backtesting\backtest_engine.py" (
    echo ✓ backtest_engine.py found
    for %%A in (finbert_v4.4.4\models\backtesting\backtest_engine.py) do echo   Size: %%~zA bytes
) else (
    echo ✗ backtest_engine.py NOT FOUND!
    pause
    exit /b 1
)

echo.
echo [2/5] Checking for Phase 2 features in code...
echo.

REM Check for critical Phase 2 features
findstr /C:"enable_take_profit" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ enable_take_profit found
) else (
    echo ✗ enable_take_profit NOT FOUND!
    echo   Phase 2 code is MISSING!
)

findstr /C:"risk_reward_ratio" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ risk_reward_ratio found
) else (
    echo ✗ risk_reward_ratio NOT FOUND!
)

findstr /C:"_check_take_profits" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ _check_take_profits method found
) else (
    echo ✗ _check_take_profits method NOT FOUND!
)

echo.
echo [3/5] Checking default values in __init__...
echo.

REM Extract key lines from __init__
echo Looking for default values:
echo.

findstr /N /C:"allocation_strategy: str = " finbert_v4.4.4\models\backtesting\backtest_engine.py | findstr /C:"def __init__" /C:"equal" /C:"risk_based"
findstr /N /C:"enable_take_profit: bool = " finbert_v4.4.4\models\backtesting\backtest_engine.py | findstr /C:"True" /C:"False"
findstr /N /C:"stop_loss_percent: float = " finbert_v4.4.4\models\backtesting\backtest_engine.py

echo.
echo [4/5] Analyzing current configuration...
echo.

REM Check what's currently set
findstr /C:"allocation_strategy: str = 'equal'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠ ISSUE: allocation_strategy = 'equal' ^(should be 'risk_based'^)
) else (
    findstr /C:"allocation_strategy: str = 'risk_based'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✓ allocation_strategy = 'risk_based' ^(correct^)
    ) else (
        echo ? allocation_strategy = unknown
    )
)

findstr /C:"enable_take_profit: bool = False" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠ ISSUE: enable_take_profit = False ^(should be True^)
    echo   THIS IS THE PROBLEM! Take-profit is DISABLED!
) else (
    findstr /C:"enable_take_profit: bool = True" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✓ enable_take_profit = True ^(correct^)
    ) else (
        echo ? enable_take_profit = unknown
    )
)

echo.
echo [5/5] ROOT CAUSE DIAGNOSIS
echo.
echo ====================================================================
echo.

REM Determine the issue
findstr /C:"enable_take_profit" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% NEQ 0 (
    echo ✗ CRITICAL: Phase 2 code is MISSING!
    echo.
    echo Solution:
    echo   1. Re-download PHASE1_PHASE2_PATCH.zip
    echo   2. Extract and run INSTALL.bat
    echo   3. Verify installation completes
    echo.
    goto :end
)

findstr /C:"enable_take_profit: bool = False" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠ PROBLEM FOUND: Take-profit is DISABLED in defaults!
    echo.
    echo Your results make sense now:
    echo   - Win Rate 45.5%% = Good ^(winning more often^)
    echo   - But losing money = Bad ^(losses bigger than wins^)
    echo   - Profit Factor 0.54 = Very bad ^(losing $1.85 per $1 gained^)
    echo.
    echo Why: Without take-profit:
    echo   - Wins: Small gains ^(~$500^)
    echo   - Losses: Full stop-loss ^(~$1,000^)
    echo   - Result: Win 45%% but still lose overall
    echo.
    echo Solution:
    echo   Run: FIX_BACKTEST_ENGINE_DEFAULTS.py
    echo   This will automatically enable take-profit
    echo.
    goto :end
)

findstr /C:"allocation_strategy: str = 'equal'" finbert_v4.4.4\models\backtesting\backtest_engine.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠ ISSUE: Using equal-weight allocation instead of risk-based
    echo.
    echo Solution:
    echo   Run: FIX_BACKTEST_ENGINE_DEFAULTS.py
    echo   This will change to risk-based allocation
    echo.
    goto :end
)

echo ✓ Configuration looks correct!
echo.
echo If backtest still shows poor results, check:
echo   1. UI Confidence Threshold: Must be 60%% ^(not 65%%^)
echo   2. FinBERT restart: Make sure you restarted after changes
echo   3. Cache clear: Clear any cached predictions
echo.

:end
echo ====================================================================
echo.
echo NEXT STEPS:
echo   1. Review findings above
echo   2. Run: python FIX_BACKTEST_ENGINE_DEFAULTS.py
echo   3. Restart FinBERT v4.4.4
echo   4. Set confidence to 60%%
echo   5. Re-run backtest
echo.
echo Expected results after fix:
echo   Total Return: -0.86%% → +8-12%%
echo   Profit Factor: 0.54 → 1.5-2.4
echo.
pause

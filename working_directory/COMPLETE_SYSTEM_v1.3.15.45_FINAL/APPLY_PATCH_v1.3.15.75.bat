@echo off
REM ===========================================================================
REM  MARKET CHART PATCH v1.3.15.75 - STANDALONE PYTHON SCRIPT
REM  Simple wrapper that calls a pre-written Python script
REM ===========================================================================

chcp 65001 > nul 2>&1

echo.
echo ============================================================================
echo   MARKET CHART PATCH v1.3.15.75
echo ============================================================================
echo.
echo This patch will fix the 24-Hour Market Performance Chart
echo.
pause

REM Check if Python script exists
if not exist "apply_patch_standalone.py" (
    echo.
    echo [ERROR] apply_patch_standalone.py not found!
    echo.
    echo Please make sure you have ALL THREE files in the same folder:
    echo   1. APPLY_PATCH_v1.3.15.75.bat  ^(this file^)
    echo   2. apply_patch_standalone.py
    echo   3. FIX_MARKET_CHART_v1.3.15.68.py
    echo.
    echo Current folder: %CD%
    echo.
    pause
    exit /b 1
)

REM Check if FIX file exists
if not exist "FIX_MARKET_CHART_v1.3.15.68.py" (
    echo.
    echo [ERROR] FIX_MARKET_CHART_v1.3.15.68.py not found!
    echo.
    echo Please make sure you have ALL THREE files in the same folder:
    echo   1. APPLY_PATCH_v1.3.15.75.bat  ^(this file^)
    echo   2. apply_patch_standalone.py
    echo   3. FIX_MARKET_CHART_v1.3.15.68.py
    echo.
    pause
    exit /b 1
)

REM Check if dashboard exists
if not exist "unified_trading_dashboard.py" (
    echo.
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Please run this patch from:
    echo   C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Creating backup before patching...
copy /Y "unified_trading_dashboard.py" "unified_trading_dashboard.py.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backup failed!
    pause
    exit /b 1
)
echo [OK] Backup created: unified_trading_dashboard.py.backup_*
echo.

echo [INFO] Running patch script...
echo.
python apply_patch_standalone.py
if errorlevel 1 (
    echo.
    echo [ERROR] Patch failed! Rolling back...
    for %%f in ("unified_trading_dashboard.py.backup_*") do (
        copy /Y "%%f" "unified_trading_dashboard.py" > nul 2>&1
    )
    echo [OK] Rollback complete
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   ALL DONE!
echo ============================================================================
echo.
pause

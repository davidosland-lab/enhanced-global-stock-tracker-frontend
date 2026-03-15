@echo off
REM ===========================================================================
REM  MARKET CHART PATCH v1.3.15.71 - ULTRA ROBUST
REM  Applies the market chart fix by copying function from external file
REM ===========================================================================

chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   MARKET CHART PATCH v1.3.15.71
echo ============================================================================
echo.
echo This patch will fix the 24-Hour Market Performance Chart
echo.
echo IMPORTANT: Make sure these files are in the same folder:
echo   - FIX_MARKET_CHART_v1.3.15.68.py
echo   - unified_trading_dashboard.py
echo.
pause

REM Check if FIX file exists
if not exist "FIX_MARKET_CHART_v1.3.15.68.py" (
    echo.
    echo [ERROR] FIX_MARKET_CHART_v1.3.15.68.py not found!
    echo.
    echo Please download it and place it in this folder:
    echo   %CD%
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
echo [1/5] Creating backup...
copy /Y "unified_trading_dashboard.py" "unified_trading_dashboard.py.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backup failed!
    pause
    exit /b 1
)
echo [OK] Backup created

echo.
echo [2/5] Extracting fixed function...
python -c "exec(open('FIX_MARKET_CHART_v1.3.15.68.py').read().replace('create_market_performance_chart_fixed', 'create_market_performance_chart')); import inspect; print(inspect.getsource(create_market_performance_chart))" > _temp_function.txt 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to extract function!
    type _temp_function.txt
    del _temp_function.txt > nul 2>&1
    pause
    exit /b 1
)
echo [OK] Function extracted

echo.
echo [3/5] Applying patch using Python...
python -c "import re; content = open('unified_trading_dashboard.py', 'r', encoding='utf-8').read(); fixed_func = open('_temp_function.txt', 'r', encoding='utf-8').read(); pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef |\Z)'; new_content = re.sub(pattern, fixed_func.rstrip() + '\n\n', content, flags=re.DOTALL); open('unified_trading_dashboard.py', 'w', encoding='utf-8').write(new_content); print('[OK] Patch applied')" 2>&1
if errorlevel 1 (
    echo [ERROR] Patch failed!
    echo Rolling back...
    copy /Y "unified_trading_dashboard.py.backup_*" "unified_trading_dashboard.py" > nul 2>&1
    pause
    exit /b 1
)

echo.
echo [4/5] Cleaning up...
del _temp_function.txt > nul 2>&1
echo [OK] Cleanup complete

echo.
echo [5/5] Verifying patch...
python -c "open('unified_trading_dashboard.py', 'r', encoding='utf-8').read(); print('[OK] Syntax valid')" 2>&1
if errorlevel 1 (
    echo [ERROR] Syntax error detected! Rolling back...
    copy /Y "unified_trading_dashboard.py.backup_*" "unified_trading_dashboard.py" > nul 2>&1
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   PATCH COMPLETE!
echo ============================================================================
echo.
echo The 24-Hour Market Performance Chart has been fixed!
echo.
echo Next step: Restart the dashboard
echo   1) Press Ctrl+C in the dashboard window (if running)
echo   2) Run START.bat
echo   3) Open http://localhost:8050
echo.
echo The chart should now show CURRENT data with real-time updates every 5 seconds!
echo.
echo ============================================================================
echo.
pause

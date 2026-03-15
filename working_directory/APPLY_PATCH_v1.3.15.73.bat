@echo off
REM ===========================================================================
REM  MARKET CHART PATCH v1.3.15.73 - DIRECT FILE METHOD
REM  Uses pre-written Python script for reliable patching
REM ===========================================================================

chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   MARKET CHART PATCH v1.3.15.73
echo ============================================================================
echo.
echo This patch will fix the 24-Hour Market Performance Chart
echo.
pause

REM Check if FIX file exists
if not exist "FIX_MARKET_CHART_v1.3.15.68.py" (
    echo.
    echo [ERROR] FIX_MARKET_CHART_v1.3.15.68.py not found!
    echo.
    echo Please make sure you have BOTH files in the same folder:
    echo   1. APPLY_PATCH_v1.3.15.73.bat  ^(this file^)
    echo   2. FIX_MARKET_CHART_v1.3.15.68.py
    echo.
    echo Current folder: %CD%
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
echo [2/5] Reading fixed function from FIX_MARKET_CHART_v1.3.15.68.py...
echo [OK] File found

echo.
echo [3/5] Creating patch applier script...
python -c "import sys; print('Python OK')" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

REM Create a Python script that will do the patching
echo import re > apply_patch.py
echo. >> apply_patch.py
echo # Read the fix file >> apply_patch.py
echo with open('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8') as f: >> apply_patch.py
echo     fix_content = f.read() >> apply_patch.py
echo. >> apply_patch.py
echo # Extract the fixed function (rename it) >> apply_patch.py
echo fix_content = fix_content.replace('create_market_performance_chart_fixed', 'create_market_performance_chart') >> apply_patch.py
echo. >> apply_patch.py
echo # Read dashboard >> apply_patch.py
echo with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f: >> apply_patch.py
echo     dashboard_content = f.read() >> apply_patch.py
echo. >> apply_patch.py
echo # Find and replace the old function >> apply_patch.py
echo pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\n@app\.callback|\Z)' >> apply_patch.py
echo fixed_function = re.search(r'def create_market_performance_chart\(state\):.*?(?=\nif __name__|$)', fix_content, re.DOTALL).group(0) >> apply_patch.py
echo new_dashboard = re.sub(pattern, fixed_function + '\n\n', dashboard_content, flags=re.DOTALL) >> apply_patch.py
echo. >> apply_patch.py
echo # Write back >> apply_patch.py
echo with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f: >> apply_patch.py
echo     f.write(new_dashboard) >> apply_patch.py
echo. >> apply_patch.py
echo print('[OK] Patch applied successfully!') >> apply_patch.py

echo [OK] Patch applier created

echo.
echo [4/5] Applying patch...
python apply_patch.py
if errorlevel 1 (
    echo [ERROR] Patch failed!
    echo Rolling back...
    copy /Y "unified_trading_dashboard.py.backup_*" "unified_trading_dashboard.py" > nul 2>&1
    del apply_patch.py > nul 2>&1
    pause
    exit /b 1
)

echo.
echo [5/5] Cleaning up...
del apply_patch.py > nul 2>&1
echo [OK] Cleanup complete

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
echo The chart should now show CURRENT data with real-time updates!
echo.
echo ============================================================================
echo.
pause

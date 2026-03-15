@echo off
REM ===========================================================================
REM  MARKET CHART PATCH v1.3.15.74 - FINAL WORKING VERSION
REM  Creates Python patcher with proper escaping
REM ===========================================================================

chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   MARKET CHART PATCH v1.3.15.74
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
    echo   1. APPLY_PATCH_v1.3.15.74.bat  ^(this file^)
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

REM Create the Python patcher script using a here-document style
(
echo import re
echo import sys
echo.
echo try:
echo     # Read the fix file
echo     with open('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8'^) as f:
echo         fix_content = f.read^(^)
echo.
echo     # Rename the function
echo     fix_content = fix_content.replace^('create_market_performance_chart_fixed', 'create_market_performance_chart'^)
echo.
echo     # Read dashboard
echo     with open^('unified_trading_dashboard.py', 'r', encoding='utf-8'^) as f:
echo         dashboard_content = f.read^(^)
echo.
echo     # Extract just the fixed function ^(from def to before if __name__^)
echo     pattern_extract = r'def create_market_performance_chart\(state\):.*?(?=\n\n\nif __name__|$^)'
echo     match = re.search^(pattern_extract, fix_content, re.DOTALL^)
echo     if not match:
echo         print^('[ERROR] Could not extract fixed function'^)
echo         sys.exit^(1^)
echo     fixed_function = match.group^(0^)
echo.
echo     # Find and replace old function in dashboard
echo     pattern_replace = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\n@app\.callback|\Z^)'
echo     new_dashboard = re.sub^(pattern_replace, fixed_function + '\n\n', dashboard_content, flags=re.DOTALL^)
echo.
echo     # Write back
echo     with open^('unified_trading_dashboard.py', 'w', encoding='utf-8'^) as f:
echo         f.write^(new_dashboard^)
echo.
echo     print^('[OK] Patch applied successfully!'^)
echo except Exception as e:
echo     print^(f'[ERROR] {e}'^)
echo     sys.exit^(1^)
) > apply_patch.py

if not exist apply_patch.py (
    echo [ERROR] Failed to create patch script!
    pause
    exit /b 1
)
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
echo   1) Press Ctrl+C in the dashboard window ^(if running^)
echo   2) Run START.bat
echo   3) Open http://localhost:8050
echo.
echo The chart should now show CURRENT data with real-time updates!
echo.
echo ============================================================================
echo.
pause

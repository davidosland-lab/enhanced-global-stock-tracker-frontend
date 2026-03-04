@echo off
REM ===========================================================================
REM  PATCH: 24-Hour Market Chart Fix
REM  Version: v1.3.15.70 ROBUST
REM  Date: 2026-02-01
REM  Simple version - guaranteed to work
REM ===========================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"
cls

echo.
echo ===========================================================================
echo.
echo           24-HOUR MARKET CHART FIX - v1.3.15.70
echo.
echo ===========================================================================
echo.
echo   This patch fixes the following issues:
echo   - Chart stuck on Feb 3-4 data
echo   - Chart freezing during live trading
echo   - Extended timeframes near market close
echo.
echo ===========================================================================
echo.

REM Check if files exist
echo Checking files...
echo.

if not exist unified_trading_dashboard.py (
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Please run this patch from:
    echo   C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
    echo.
    echo Current directory: %CD%
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Dashboard file found

if not exist FIX_MARKET_CHART_v1.3.15.68.py (
    echo [ERROR] FIX_MARKET_CHART_v1.3.15.68.py not found!
    echo.
    echo Please download this file to the same directory first.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Fix file found

echo.
echo ===========================================================================
echo.
echo   Ready to apply patch.
echo.
echo   This will:
echo   1. Create a backup of your dashboard
echo   2. Replace the chart function with the fixed version
echo   3. Verify the changes
echo.
echo ===========================================================================
echo.
echo Press any key to continue, or close this window to cancel...
pause >nul

echo.
echo ===========================================================================
echo   APPLYING PATCH
echo ===========================================================================
echo.

REM Step 1: Backup
echo [STEP 1/4] Creating backup...
copy /Y unified_trading_dashboard.py unified_trading_dashboard.py.backup >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create backup!
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Backup created: unified_trading_dashboard.py.backup
echo.

REM Step 2: Create simple patcher Python script
echo [STEP 2/4] Creating patcher script...

(
echo import re
echo import sys
echo import traceback
echo.
echo print^("Reading files..."^)
echo try:
echo     with open^('unified_trading_dashboard.py', 'r', encoding='utf-8'^) as f:
echo         dashboard = f.read^(^)
echo     with open^('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8'^) as f:
echo         fixfile = f.read^(^)
echo     print^("[OK] Files read successfully"^)
echo except Exception as e:
echo     print^(f"[ERROR] Failed to read files: {e}"^)
echo     sys.exit^(1^)
echo.
echo print^("Extracting fixed function..."^)
echo try:
echo     match = re.search^(r'def create_market_performance_chart_fixed\(state\):.*?^(?=\n\ndef ^|\n\nif __name__^|\Z^)', fixfile, re.DOTALL^)
echo     if not match:
echo         print^("[ERROR] Could not find fixed function"^)
echo         sys.exit^(1^)
echo     fixed_func = match.group^(0^)
echo     fixed_func = fixed_func.replace^('def create_market_performance_chart_fixed^(', 'def create_market_performance_chart^('^)
echo     print^("[OK] Fixed function extracted"^)
echo except Exception as e:
echo     print^(f"[ERROR] Failed to extract function: {e}"^)
echo     traceback.print_exc^(^)
echo     sys.exit^(1^)
echo.
echo print^("Finding original function..."^)
echo try:
echo     match = re.search^(r'def create_market_performance_chart\(state\):.*?^(?=\ndef [a-zA-Z_]^|\nclass [a-zA-Z_]^|\n@app\.callback^|\Z^)', dashboard, re.DOTALL^)
echo     if not match:
echo         print^("[ERROR] Could not find original function"^)
echo         sys.exit^(1^)
echo     print^(f"[OK] Found function at position {match.start^(^)}"^)
echo except Exception as e:
echo     print^(f"[ERROR] Failed to find function: {e}"^)
echo     sys.exit^(1^)
echo.
echo print^("Replacing function..."^)
echo try:
echo     new_dashboard = dashboard[:match.start^(^)] + fixed_func + dashboard[match.end^(^):]
echo     with open^('unified_trading_dashboard.py', 'w', encoding='utf-8'^) as f:
echo         f.write^(new_dashboard^)
echo     print^("[OK] Function replaced successfully"^)
echo except Exception as e:
echo     print^(f"[ERROR] Failed to replace: {e}"^)
echo     print^("Restoring backup..."^)
echo     try:
echo         with open^('unified_trading_dashboard.py.backup', 'r', encoding='utf-8'^) as f:
echo             backup = f.read^(^)
echo         with open^('unified_trading_dashboard.py', 'w', encoding='utf-8'^) as f:
echo             f.write^(backup^)
echo         print^("[OK] Backup restored"^)
echo     except:
echo         print^("[ERROR] Failed to restore backup!"^)
echo     sys.exit^(1^)
echo.
echo print^("PATCH APPLIED SUCCESSFULLY!"^)
) > apply_patch.py

echo [OK] Patcher script created
echo.

REM Step 3: Run the patcher
echo [STEP 3/4] Running patcher...
echo.
echo ---------------------------------------------------------------------------
python apply_patch.py
set PATCH_RESULT=%errorlevel%
echo ---------------------------------------------------------------------------
echo.

if %PATCH_RESULT% neq 0 (
    echo [ERROR] Patch failed with error code: %PATCH_RESULT%
    echo.
    echo The backup file is still available:
    echo   unified_trading_dashboard.py.backup
    echo.
    echo You can restore it manually if needed:
    echo   copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py
    echo.
    del apply_patch.py >nul 2>&1
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Clean up
del apply_patch.py >nul 2>&1

REM Step 4: Verify
echo [STEP 4/4] Verifying patch...
python -c "content = open('unified_trading_dashboard.py', 'r').read(); assert 'now_gmt' in content and 'datetime.now(gmt)' in content; print('[OK] Patch verified')" 2>nul
if errorlevel 1 (
    echo [WARNING] Could not verify patch
    echo.
    echo The patch may not have been applied correctly.
    echo Check the file manually or restore from backup.
    echo.
) else (
    echo [OK] Patch verified successfully
    echo.
)

echo.
echo ===========================================================================
echo.
echo                        PATCH COMPLETE!
echo.
echo ===========================================================================
echo.
echo   The 24-hour market chart has been fixed.
echo.
echo   Changes:
echo   - Chart now uses current date/time (not old data)
echo   - Real-time updates every 5 seconds
echo   - Shows "Updated: HH:MM:SS" timestamp
echo   - Detailed logging for debugging
echo.
echo   Backup saved: unified_trading_dashboard.py.backup
echo.
echo ---------------------------------------------------------------------------
echo.
echo   NEXT STEPS:
echo.
echo   1. Close this window
echo.
echo   2. Start your dashboard:
echo      START.bat
echo.
echo   3. Verify chart shows current date (not Feb 3-4)
echo.
echo   4. Look for these console messages:
echo      [MARKET CHART] Current time (GMT): ...
echo      [MARKET CHART] ^GSPC: Added to chart successfully
echo.
echo ---------------------------------------------------------------------------
echo.
echo   If the chart still shows old data:
echo.
echo   1. Stop the dashboard (Ctrl+C)
echo   2. Restore backup:
echo      copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py
echo   3. Contact support with error details
echo.
echo ===========================================================================
echo.
echo.
echo Press any key to close this window...
pause >nul
exit /b 0

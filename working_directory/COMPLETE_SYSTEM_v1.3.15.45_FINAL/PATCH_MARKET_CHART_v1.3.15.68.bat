@echo off
REM ===========================================================================
REM  PATCH: 24-Hour Market Chart Fix
REM  Version: v1.3.15.68
REM  Date: 2026-02-01
REM  Fixes: Chart freezing, old data (Feb 3-4), extended timeframes
REM ===========================================================================

cd /d "%~dp0"
cls

echo.
echo ===========================================================================
echo.
echo           24-HOUR MARKET CHART FIX - v1.3.15.68
echo.
echo ===========================================================================
echo.
echo   This patch fixes the following issues:
echo   - Chart stuck on Feb 3-4 data
echo   - Chart freezing during live trading
echo   - Extended timeframes near market close
echo   - No real-time updates
echo.
echo   Root Cause: Using old data date instead of current time
echo   Solution: Always use datetime.now(GMT) for date logic
echo.
echo ===========================================================================
echo.
echo   IMPORTANT: This will modify unified_trading_dashboard.py
echo.
echo   A backup will be created: unified_trading_dashboard.py.backup
echo.
echo ---------------------------------------------------------------------------
echo.

pause

REM Check if we're in the right directory
if not exist unified_trading_dashboard.py (
    echo.
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Please run this patch from:
    echo   C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo.
echo [1/5] Creating backup...
copy /Y unified_trading_dashboard.py unified_trading_dashboard.py.backup >nul
if errorlevel 1 (
    echo [ERROR] Failed to create backup!
    pause
    exit /b 1
)
echo [OK] Backup created: unified_trading_dashboard.py.backup
echo.

echo [2/5] Checking if FIX_MARKET_CHART_v1.3.15.68.py exists...
if not exist FIX_MARKET_CHART_v1.3.15.68.py (
    echo [ERROR] Fix file not found!
    echo.
    echo Please download FIX_MARKET_CHART_v1.3.15.68.py to this directory first.
    echo.
    pause
    exit /b 1
)
echo [OK] Fix file found
echo.

echo [3/5] Applying patch...
echo.
echo This will replace the create_market_performance_chart function
echo in unified_trading_dashboard.py
echo.

REM Use Python to apply the patch
python -c "import sys; print('[INFO] Python available:', sys.version.split()[0])"
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo.
echo Executing patch script...
echo.

python << EOF
import re
import sys

print("[INFO] Reading original dashboard file...")
try:
    with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
        original_content = f.read()
    print("[OK] Original file loaded")
except Exception as e:
    print(f"[ERROR] Failed to read original file: {e}")
    sys.exit(1)

print("[INFO] Reading fix file...")
try:
    with open('FIX_MARKET_CHART_v1.3.15.68.py', 'r', encoding='utf-8') as f:
        fix_content = f.read()
    print("[OK] Fix file loaded")
except Exception as e:
    print(f"[ERROR] Failed to read fix file: {e}")
    sys.exit(1)

# Extract the fixed function from the fix file
print("[INFO] Extracting fixed function...")
fixed_function_match = re.search(
    r'def create_market_performance_chart_fixed\(state\):.*?(?=\n\ndef |\n\nif __name__|\Z)',
    fix_content,
    re.DOTALL
)

if not fixed_function_match:
    print("[ERROR] Could not extract fixed function from fix file!")
    sys.exit(1)

fixed_function = fixed_function_match.group(0)
# Rename the function back to original name
fixed_function = fixed_function.replace('def create_market_performance_chart_fixed(', 
                                       'def create_market_performance_chart(')
print("[OK] Fixed function extracted")

# Find and replace the old function in the original file
print("[INFO] Locating original function...")
original_function_pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\n@app\.callback|\Z)'

match = re.search(original_function_pattern, original_content, re.DOTALL)
if not match:
    print("[ERROR] Could not find original function in dashboard!")
    sys.exit(1)

print(f"[OK] Found original function at position {match.start()}")

# Replace the function
print("[INFO] Replacing function...")
new_content = original_content[:match.start()] + fixed_function + original_content[match.end():]

# Write the patched file
print("[INFO] Writing patched file...")
try:
    with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("[OK] Patched file written successfully")
except Exception as e:
    print(f"[ERROR] Failed to write patched file: {e}")
    print("[INFO] Restoring backup...")
    try:
        with open('unified_trading_dashboard.py.backup', 'r', encoding='utf-8') as f:
            backup = f.read()
        with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
            f.write(backup)
        print("[OK] Backup restored")
    except:
        print("[ERROR] Failed to restore backup!")
    sys.exit(1)

print()
print("=" * 70)
print("[SUCCESS] Patch applied successfully!")
print("=" * 70)
EOF

if errorlevel 1 (
    echo.
    echo [ERROR] Patch failed!
    echo.
    echo The original file has been preserved.
    echo You can manually restore the backup if needed:
    echo   copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Verifying patch...
python -c "with open('unified_trading_dashboard.py', 'r') as f: content = f.read(); assert 'datetime.now(gmt)' in content and 'now_gmt' in content, 'Patch verification failed'; print('[OK] Patch verified - new code detected')"
if errorlevel 1 (
    echo [ERROR] Patch verification failed!
    echo Restoring backup...
    copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py >nul
    echo [OK] Backup restored
    pause
    exit /b 1
)
echo.

echo [5/5] Testing patched dashboard (quick syntax check)...
python -m py_compile unified_trading_dashboard.py 2>nul
if errorlevel 1 (
    echo [WARNING] Syntax check failed - there may be an issue
    echo.
    echo To restore backup:
    echo   copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py
    echo.
) else (
    echo [OK] Syntax check passed
)

echo.
echo ===========================================================================
echo.
echo                        PATCH COMPLETE!
echo.
echo ===========================================================================
echo.
echo   Changes applied:
echo   - Fixed date logic (now uses current time, not old data date)
echo   - Added real-time updates with 1d/5m intervals
echo   - Improved timezone handling for all markets
echo   - Added detailed logging for debugging
echo   - Chart now shows "Updated: HH:MM:SS" timestamp
echo.
echo   Backup saved: unified_trading_dashboard.py.backup
echo.
echo ---------------------------------------------------------------------------
echo.
echo   NEXT STEPS:
echo.
echo   1. Restart your dashboard:
echo      START.bat
echo.
echo   2. Check the console logs for "[MARKET CHART]" messages
echo.
echo   3. Verify the chart shows current date (not Feb 3-4!)
echo.
echo   4. Watch for real-time updates every 5 seconds
echo.
echo ---------------------------------------------------------------------------
echo.
echo   If you have issues, restore the backup:
echo      copy /Y unified_trading_dashboard.py.backup unified_trading_dashboard.py
echo.
echo ===========================================================================
echo.

pause
exit /b 0

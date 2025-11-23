@echo off
REM ============================================================================
REM CODE VERSION VERIFICATION - Dual Market Screening System v1.3.20.1
REM ============================================================================
REM
REM This script verifies that you're running the latest code version by
REM checking for specific fixes in key files.
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   CODE VERSION VERIFICATION - v1.3.20.1
echo ============================================================================
echo.

set "ERRORS=0"
set "WARNINGS=0"

REM Check 1: US Pipeline CSV Export Fix
echo [CHECK 1/4] Verifying US Pipeline CSV Export Fix...
findstr /C:"us_sentiment" models\screening\us_overnight_pipeline.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ FAIL: US Pipeline CSV export fix NOT found
    echo   Expected: 'us_sentiment' in us_overnight_pipeline.py
    set /a ERRORS+=1
) else (
    findstr /C:"export_screening_results(scored_stocks, sentiment)" models\screening\us_overnight_pipeline.py >nul 2>&1
    if not errorlevel 1 (
        echo   ❌ FAIL: OLD CODE detected - still using 'sentiment' instead of 'us_sentiment'
        set /a ERRORS+=1
    ) else (
        echo   ✓ PASS: US Pipeline CSV export fix verified
    )
)

echo.

REM Check 2: HMM Covariance Fix
echo [CHECK 2/4] Verifying HMM Covariance Fix...
findstr /C:"StandardScaler" models\screening\us_market_regime_engine.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ FAIL: HMM scaling fix NOT found
    echo   Expected: 'StandardScaler' in us_market_regime_engine.py
    set /a ERRORS+=1
) else (
    findstr /C:"covariance_type=\"diag\"" models\screening\us_market_regime_engine.py >nul 2>&1
    if errorlevel 1 (
        echo   ⚠️  WARNING: HMM may still use 'full' covariance (should be 'diag')
        set /a WARNINGS+=1
    ) else (
        echo   ✓ PASS: HMM covariance fix verified
    )
)

echo.

REM Check 3: Python Cache
echo [CHECK 3/4] Checking for Python cache files...
set "CACHE_FOUND=0"
for /r . %%d in (__pycache__) do (
    if exist "%%d" (
        set "CACHE_FOUND=1"
    )
)

if !CACHE_FOUND!==1 (
    echo   ⚠️  WARNING: Python cache found - may cause old code to run
    echo   Run CLEAR_PYTHON_CACHE.bat to fix this
    set /a WARNINGS+=1
) else (
    echo   ✓ PASS: No Python cache files found
)

echo.

REM Check 4: Email Notification Fix (ASX)
echo [CHECK 4/4] Verifying ASX Email Notification...
findstr /C:"self.notifier.send_morning_report(" models\screening\overnight_pipeline.py >nul 2>&1
if errorlevel 1 (
    echo   ❌ FAIL: Email notification code not found
    set /a ERRORS+=1
) else (
    REM Check for double parentheses (common error)
    findstr /C:"self.notifier.send_morning_report()(" models\screening\overnight_pipeline.py >nul 2>&1
    if not errorlevel 1 (
        echo   ❌ FAIL: Double parentheses detected in email notification
        set /a ERRORS+=1
    ) else (
        echo   ✓ PASS: Email notification code looks correct
    )
)

echo.
echo ============================================================================
echo   VERIFICATION RESULTS
echo ============================================================================
echo.
echo   Critical Errors: %ERRORS%
echo   Warnings: %WARNINGS%
echo.

if %ERRORS% GTR 0 (
    echo   ❌ CODE VERSION IS OUT OF DATE OR CORRUPTED
    echo.
    echo   ACTION REQUIRED:
    echo   1. Re-extract the latest deployment package
    echo   2. Run CLEAR_PYTHON_CACHE.bat
    echo   3. Run this verification again
    echo.
    exit /b 1
) else if %WARNINGS% GTR 0 (
    echo   ⚠️  WARNINGS DETECTED - Review Above
    echo.
    echo   RECOMMENDED ACTIONS:
    if !CACHE_FOUND!==1 (
        echo   - Run CLEAR_PYTHON_CACHE.bat to remove old cache files
    )
    echo   - Review the warnings above
    echo   - Run QUICK TEST.bat to verify functionality
    echo.
    exit /b 0
) else (
    echo   ✅ ALL CHECKS PASSED
    echo.
    echo   Your code version is up to date with v1.3.20.1
    echo   You can proceed with running the screening system.
    echo.
    echo   Next Steps:
    echo   1. Run "QUICK TEST.bat" to verify functionality
    echo   2. Or run "RUN_BOTH_MARKETS.bat" for full screening
    echo.
    exit /b 0
)

pause

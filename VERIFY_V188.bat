@echo off
REM ====================================================================
REM v188 Verification Script
REM Checks if v188 patches are applied correctly
REM ====================================================================

echo.
echo ========================================================
echo   v188 PATCH VERIFICATION
echo ========================================================
echo.

set PASS=0
set FAIL=0

REM Check 1: Config file
echo [1/4] Checking config\live_trading_config.json...
findstr /C:"\"confidence_threshold\": 45.0" config\live_trading_config.json >nul 2>&1
if %errorlevel% equ 0 (
    echo   [PASS] Config threshold = 45.0
    set /a PASS+=1
) else (
    echo   [FAIL] Config threshold NOT 45.0
    set /a FAIL+=1
)

REM Check 2: Signal generator
echo.
echo [2/4] Checking ml_pipeline\swing_signal_generator.py...
findstr /C:"CONFIDENCE_THRESHOLD = 0.48" ml_pipeline\swing_signal_generator.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   [PASS] Signal generator = 0.48
    set /a PASS+=1
) else (
    echo   [FAIL] Signal generator NOT 0.48
    set /a FAIL+=1
)

REM Check 3: Paper trading coordinator
echo.
echo [3/4] Checking core\paper_trading_coordinator.py...
findstr /C:"else 48.0" core\paper_trading_coordinator.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   [PASS] Coordinator fallback = 48.0
    set /a PASS+=1
) else (
    echo   [FAIL] Coordinator fallback NOT 48.0
    set /a FAIL+=1
)

REM Check 4: Opportunity monitor
echo.
echo [4/4] Checking core\opportunity_monitor.py...
findstr /C:"confidence_threshold: float = 48.0" core\opportunity_monitor.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   [PASS] Monitor threshold = 48.0
    set /a PASS+=1
) else (
    echo   [FAIL] Monitor threshold NOT 48.0
    set /a FAIL+=1
)

REM Summary
echo.
echo ========================================================
if %FAIL% equ 0 (
    echo   VERIFICATION COMPLETE: ALL CHECKS PASSED
    echo   v188 patches are correctly applied!
    echo.
    echo   Your system should now:
    echo   - Accept trades at 48%% confidence or higher
    echo   - Show "PASS" for 52%%, 53%%, 54%% confidence trades
    echo   - No longer block trades at 65%%
) else (
    echo   VERIFICATION FAILED: %FAIL% check(s) failed
    echo   v188 patches are NOT fully applied
    echo.
    echo   Please run: APPLY_V188_INPLACE.bat
)
echo ========================================================
echo.
pause

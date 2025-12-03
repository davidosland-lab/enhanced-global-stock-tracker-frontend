@echo off
REM =====================================================================
REM TELEGRAM TEST COMMANDS - Quick Reference
REM =====================================================================

echo.
echo ========================================================================
echo    TELEGRAM SETUP VERIFICATION TESTS
echo ========================================================================
echo.

REM Check if we're in the right directory
if not exist "..\models\notifications\telegram_notifier.py" (
    echo ERROR: Must run from C:\Users\david\AATelS directory
    echo Current location: %CD%
    echo.
    pause
    exit /b 1
)

echo Test 1: Check credentials file
echo ========================================================================
cd ..
if exist telegram.env (
    echo ✓ telegram.env found
    type telegram.env
) else (
    echo ✗ telegram.env NOT FOUND
    echo Please run SETUP_TELEGRAM.bat first
    pause
    exit /b 1
)
echo.

echo Test 2: Check configuration
echo ========================================================================
findstr /C:"telegram_notifications" models\config\screening_config.json >nul 2>&1
if errorlevel 0 (
    echo ✓ telegram_notifications found in config
) else (
    echo ⚠ telegram_notifications not found in config
    echo This is OK if you manually configured it
)
echo.

echo Test 3: Run full test script
echo ========================================================================
echo Running comprehensive tests...
echo.
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
if errorlevel 1 (
    echo.
    echo ✗ Tests failed - see output above
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    TESTS COMPLETE
echo ========================================================================
echo.
echo Next steps:
echo   1. Check your Telegram app for test messages
echo   2. Run pipeline test: python models\screening\us_overnight_pipeline.py --test-mode
echo.
pause

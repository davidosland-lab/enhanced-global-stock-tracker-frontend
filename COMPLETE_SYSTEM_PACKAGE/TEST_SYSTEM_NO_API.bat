@echo off
REM ============================================================================
REM Test System Without API Calls
REM This tests all components without hitting Yahoo Finance rate limits
REM ============================================================================

echo.
echo ============================================================================
echo SYSTEM TEST - NO API CALLS
echo ============================================================================
echo.

REM Check if we're in the right directory
if not exist "models\screening" (
    echo [ERROR] Please run from COMPLETE_SYSTEM_PACKAGE directory
    pause
    exit /b 1
)

REM Run the Python test script
python test_components.py

if errorlevel 1 (
    echo.
    echo [ERROR] Test failed
    pause
    exit /b 1
)

echo.
pause

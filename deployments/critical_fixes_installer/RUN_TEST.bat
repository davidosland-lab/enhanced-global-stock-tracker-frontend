@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM Critical Fixes - Pipeline Test Script
REM ============================================================================
REM
REM This script tests the installed fixes by running a quick 5-stock test.
REM
REM Expected output:
REM   [✓] [1/5] Processed JPM - Prediction: HOLD (Confidence: 24%)
REM   [✓] [2/5] Processed BAC - Prediction: HOLD (Confidence: 24%)
REM   [✓] [3/5] Processed WFC - Prediction: HOLD (Confidence: 24%)
REM   [✓] [4/5] Processed C   - Prediction: HOLD (Confidence: 24%)
REM   [✓] [5/5] Processed GS  - Prediction: HOLD (Confidence: 24%)
REM   [OK] Batch prediction complete: 5/5 results ✅
REM   
REM   TOP OPPORTUNITIES
REM   1. C     | Score: 52.2/100 | Signal: HOLD | Conf: 24.0%
REM   ...
REM   
REM   [SUCCESS] Complete pipeline executed successfully
REM
REM ============================================================================

echo.
echo ============================================================================
echo                    CRITICAL FIXES - PIPELINE TEST
echo ============================================================================
echo.

REM Get installation directory
set /p "INSTALL_DIR=Enter Unified Trading Dashboard installation directory: " || set INSTALL_DIR=

if "%INSTALL_DIR%"=="" (
    echo [ERROR] No installation directory specified.
    echo.
    pause
    exit /b 1
)

REM Remove quotes if present
set INSTALL_DIR=%INSTALL_DIR:"=%

REM Verify directory exists
if not exist "%INSTALL_DIR%" (
    echo [ERROR] Directory does not exist: %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

echo [INFO] Installation directory: %INSTALL_DIR%
echo.

REM Verify test script exists
if not exist "%INSTALL_DIR%\scripts\run_us_full_pipeline.py" (
    echo [ERROR] Test script not found: scripts\run_us_full_pipeline.py
    echo.
    echo Please verify the installation directory is correct.
    pause
    exit /b 1
)

echo [INFO] Test script found.
echo.

echo ============================================================================
echo                          RUNNING PIPELINE TEST
echo ============================================================================
echo.
echo This will take approximately 2 minutes...
echo.
echo Expected results:
echo   - 5 stocks processed (JPM, BAC, WFC, C, GS)
echo   - All predictions: HOLD with confidence ~24%%
echo   - No KeyError or UnicodeError messages
echo   - Top opportunities displayed
echo   - Clean console output
echo.
pause
echo.

cd /d "%INSTALL_DIR%"

echo [INFO] Running US pipeline test with 5 stocks...
echo.
python scripts\run_us_full_pipeline.py --mode test

echo.
echo ============================================================================
echo                          TEST COMPLETE
echo ============================================================================
echo.

REM Check error level
if errorlevel 1 (
    echo [WARNING] Test may have encountered errors.
    echo.
    echo Troubleshooting:
    echo   1. Check if all 4 fixes are installed correctly
    echo   2. Verify Python environment is activated
    echo   3. Check logs: logs\us_full_pipeline.log
    echo   4. Review error messages above
    echo.
) else (
    echo [SUCCESS] Test completed successfully!
    echo.
    echo If you see the following in the output above:
    echo   - [✓] for all 5 stocks (JPM, BAC, WFC, C, GS)
    echo   - "Batch prediction complete: 5/5 results"
    echo   - TOP OPPORTUNITIES section with 5 entries
    echo   - No KeyError or UnicodeError messages
    echo.
    echo Then all fixes are working correctly!
    echo.
)

echo Press any key to exit...
pause >NUL

endlocal
exit /b 0

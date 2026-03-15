@echo off
REM ========================================================================
REM v188 Comprehensive Confidence Threshold Fix - Batch Launcher
REM ========================================================================
REM
REM This batch file applies the v188 patch to fix confidence threshold
REM blocking issues (52%/65% -> 48%).
REM
REM Usage: Double-click this file or run from command prompt
REM ========================================================================

echo.
echo ======================================================================
echo v188 COMPREHENSIVE CONFIDENCE THRESHOLD FIX
echo ======================================================================
echo.
echo This will patch 4 files to lower confidence threshold to 48%%
echo.
echo Files to be patched:
echo   - config\live_trading_config.json
echo   - ml_pipeline\swing_signal_generator.py
echo   - core\paper_trading_coordinator.py
echo   - core\opportunity_monitor.py
echo.
echo Press Ctrl+C to cancel, or
pause

REM Check if Python is available
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and added to PATH
    echo.
    pause
    exit /b 1
)

REM Check if patch script exists
if not exist "APPLY_V188_COMPREHENSIVE_FIX.py" (
    echo.
    echo ERROR: APPLY_V188_COMPREHENSIVE_FIX.py not found
    echo Please ensure the patch script is in the current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Run the Python patch script
echo.
echo Running patch script...
echo.
python APPLY_V188_COMPREHENSIVE_FIX.py

REM Check if patch was successful
if errorlevel 1 (
    echo.
    echo ======================================================================
    echo PATCH FAILED
    echo ======================================================================
    echo.
    echo Please check the error messages above and try again.
    echo.
    pause
    exit /b 1
)

REM Success message
echo.
echo ======================================================================
echo PATCH COMPLETED SUCCESSFULLY
echo ======================================================================
echo.
echo Next steps:
echo   1. Restart the dashboard
echo   2. Monitor for trades with 48-65%% confidence passing
echo.
echo To start dashboard, run:
echo   python core\unified_trading_dashboard.py
echo.
echo Or use the dashboard startup script if available.
echo.
pause

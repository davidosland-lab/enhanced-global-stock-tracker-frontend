@echo off
REM ====================================================================
REM v188 In-Place Patch for COMPLETE Trading System
REM Modifies ONLY 4 files - Preserves FinBERT, pipelines, all features
REM ====================================================================

echo.
echo ========================================================
echo   v188 CONFIDENCE THRESHOLD PATCH - IN-PLACE UPDATE
echo ========================================================
echo.
echo This patch modifies ONLY 4 files in your existing system:
echo   1. config\live_trading_config.json
echo   2. ml_pipeline\swing_signal_generator.py
echo   3. core\paper_trading_coordinator.py
echo   4. core\opportunity_monitor.py
echo.
echo ALL OTHER FILES REMAIN UNCHANGED:
echo   - finbert_v4.4.4\ folder (kept as-is)
echo   - pipelines\ folder (kept as-is)
echo   - All scripts and batch files (kept as-is)
echo   - All documentation (kept as-is)
echo   - venv\ (kept as-is)
echo.
pause

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

REM Check directory structure
if not exist "config\" (
    echo.
    echo ERROR: config\ folder not found
    echo Please run this script from the root of your trading system:
    echo   C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE\
    pause
    exit /b 1
)

if not exist "core\" (
    echo.
    echo ERROR: core\ folder not found
    echo Please run this script from the correct directory
    pause
    exit /b 1
)

if not exist "finbert_v4.4.4\" (
    echo.
    echo WARNING: finbert_v4.4.4\ folder not found
    echo This is expected if FinBERT is in a different location
    echo.
)

if not exist "pipelines\" (
    echo.
    echo WARNING: pipelines\ folder not found
    echo This may indicate you're in the wrong directory
    echo.
    pause
)

REM Run the patch script
echo.
echo Running v188 patch...
echo.
python APPLY_V188_INPLACE_PATCH.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   v188 PATCH COMPLETE
    echo ========================================================
    echo.
    echo Your complete system is now updated with v188 patches.
    echo All other components remain unchanged.
    echo.
    echo Next steps:
    echo   1. Stop the dashboard if running (Ctrl+C)
    echo   2. Restart: python core\unified_trading_dashboard.py
    echo   3. Verify 48%% confidence threshold is active
    echo   4. Check trades with 52-54%% confidence now PASS
    echo.
) else (
    echo.
    echo ========================================================
    echo   PATCH FAILED
    echo ========================================================
    echo.
    echo Please check the errors above and try again.
    echo Backups have been created for any modified files.
    echo.
)

pause

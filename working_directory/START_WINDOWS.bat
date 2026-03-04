@echo off
REM Phase 3 Trading System - Windows Startup Script
REM Version: 1.3.2 FINAL
REM Date: December 26, 2024

echo ================================================================================
echo PHASE 3 REAL-TIME TRADING SYSTEM - Windows Setup
echo ================================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)

echo [1/5] Creating required directories...
if not exist "logs" mkdir logs
if not exist "state" mkdir state
if not exist "config" mkdir config
if not exist "phase3_intraday_deployment\logs" mkdir phase3_intraday_deployment\logs
if not exist "phase3_intraday_deployment\state" mkdir phase3_intraday_deployment\state
echo    ✓ Directories created

echo.
echo [2/5] Testing ML Stack...
python test_ml_stack.py
if errorlevel 1 (
    echo.
    echo [WARNING] ML stack test failed. Check dependencies.
    echo          Install missing packages with:
    echo          pip install torch keras optree absl-py h5py ml-dtypes namex
    echo          pip install transformers sentencepiece xgboost lightgbm catboost
    pause
)

echo.
echo [3/5] System Status:
echo    ✓ Python: Available
echo    ✓ Directories: Created
echo    ✓ ML Stack: Check above for status
echo.

echo ================================================================================
echo READY TO START PAPER TRADING
echo ================================================================================
echo.
echo You can now start paper trading with:
echo.
echo   cd phase3_intraday_deployment
echo   python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals --cycles 100 --interval 60
echo.
echo Or use the quick start script:
echo   cd phase3_intraday_deployment
echo   start_system.bat
echo.
echo ================================================================================
pause

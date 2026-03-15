@echo off
REM ============================================================================
REM US MARKET COMPLETE PIPELINE - WINDOWS LAUNCHER
REM ============================================================================
REM
REM Features:
REM   - Original sophistication (FinBERT, LSTM, Event Risk Guard)
REM   - NEW regime intelligence (14 regimes, 15+ cross-market features)
REM   - 240 stocks (8 sectors x 30 stocks)
REM   - Morning report with email alerts
REM
REM This script runs the complete US Market overnight screening pipeline
REM combining all sophisticated features from the original system with
REM new market regime intelligence.
REM
REM ============================================================================

echo.
echo ===========================================================================
echo US MARKET COMPLETE PIPELINE v1.3.13
echo ===========================================================================
echo.
echo Market: NYSE / NASDAQ
echo Features: FinBERT + LSTM + Event Risk Guard + Regime Intelligence
echo Expected Stocks: 240 (8 sectors x 30 stocks)
echo.
echo ===========================================================================
echo.

REM ============================================================================
REM CONFIGURATION
REM ============================================================================

REM Choose your mode:
REM   1. full-scan  = Scan all 240 stocks (8 sectors x 30)
REM   2. preset     = Use predefined stock list
REM   3. test       = Quick test with 5 stocks
set MODE=full-scan

REM If using preset mode, choose preset:
REM   "US Tech Giants", "US Banks", "US Healthcare", "US Energy"
REM   "Magnificent 7", "S&P 500 Top 10"
set PRESET=US Tech Giants

REM Initial capital (USD)
set CAPITAL=100000

REM Feature toggles
set USE_REGIME=true
set USE_ORIGINAL=true

REM ============================================================================
REM PRE-FLIGHT CHECKS
REM ============================================================================

echo [CHECK] Verifying Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python 3.8 or later.
    echo.
    pause
    exit /b 1
)
echo [OK] Python found

echo.
echo [CHECK] Verifying pipeline script...
if not exist "run_us_full_pipeline.py" (
    echo [ERROR] run_us_full_pipeline.py not found!
    echo Please ensure you're in the correct directory.
    echo.
    pause
    exit /b 1
)
echo [OK] Pipeline script found

echo.
echo ===========================================================================
echo PIPELINE CONFIGURATION
echo ===========================================================================
echo.
echo Mode:            %MODE%
if "%MODE%"=="preset" echo Preset:          %PRESET%
echo Initial Capital: $%CAPITAL% USD
echo Regime Intel:    %USE_REGIME%
echo Original Modules: %USE_ORIGINAL%
echo.
echo ===========================================================================
echo.

REM ============================================================================
REM RUN PIPELINE
REM ============================================================================

echo [STARTING] US Market Complete Pipeline...
echo.
echo Press Ctrl+C to stop the pipeline at any time
echo.
echo ===========================================================================
echo.

REM Build command based on mode
if "%MODE%"=="full-scan" (
    set CMD=python run_us_full_pipeline.py --full-scan --capital %CAPITAL%
) else if "%MODE%"=="preset" (
    set CMD=python run_us_full_pipeline.py --preset "%PRESET%" --capital %CAPITAL%
) else if "%MODE%"=="test" (
    set CMD=python run_us_full_pipeline.py --mode test --capital %CAPITAL%
) else (
    echo [ERROR] Invalid MODE setting: %MODE%
    echo Please set MODE to: full-scan, preset, or test
    pause
    exit /b 1
)

REM Add feature flags
if "%USE_REGIME%"=="false" (
    set CMD=%CMD% --no-regime
)
if "%USE_ORIGINAL%"=="false" (
    set CMD=%CMD% --no-original
)

REM Always ignore market hours for overnight run
set CMD=%CMD% --ignore-market-hours

REM Execute the pipeline
echo Command: %CMD%
echo.
%CMD%

REM ============================================================================
REM POST-EXECUTION
REM ============================================================================

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===========================================================================
    echo PIPELINE COMPLETE - SUCCESS
    echo ===========================================================================
    echo.
    echo Report should be in: reports/screening/
    echo Log file: logs/us_full_pipeline.log
    echo CSV exports: reports/csv_exports/
    echo.
) else (
    echo.
    echo ===========================================================================
    echo PIPELINE FAILED
    echo ===========================================================================
    echo.
    echo Please check logs/us_full_pipeline.log for errors
    echo.
)

echo ===========================================================================
echo.
pause

@echo off
REM ============================================================================
REM AU MARKET COMPLETE PIPELINE - WINDOWS LAUNCHER
REM ============================================================================
REM
REM Features:
REM   - Original sophistication (FinBERT, LSTM, Event Risk Guard)
REM   - NEW regime intelligence (14 regimes, 15+ cross-market features)
REM   - 240 stocks (8 sectors x 30 stocks)
REM   - Morning report with email alerts
REM
REM This script runs the complete Australian Market overnight screening pipeline
REM combining all sophisticated features from the original system with
REM new market regime intelligence.
REM
REM ============================================================================

echo.
echo ===========================================================================
echo AU MARKET COMPLETE PIPELINE v1.3.13
echo ===========================================================================
echo.
echo Market: ASX (Australian Securities Exchange)
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
REM   3. custom     = Specify symbols manually
set MODE=full-scan

REM If using preset mode, choose preset:
REM   "ASX Blue Chips", "ASX Banks", "ASX Mining", "ASX Energy"
REM   "ASX Healthcare", "ASX Retail", "ASX Top 20"
set PRESET=ASX Blue Chips

REM If using custom mode, specify symbols (comma-separated)
set SYMBOLS=CBA.AX,BHP.AX,RIO.AX,CSL.AX

REM Initial capital (AUD)
set CAPITAL=100000

REM Feature toggles
set USE_REGIME=true

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
if not exist "run_au_pipeline_v1.3.13.py" (
    echo [ERROR] run_au_pipeline_v1.3.13.py not found!
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
if "%MODE%"=="custom" echo Symbols:         %SYMBOLS%
echo Initial Capital: $%CAPITAL% AUD
echo Regime Intel:    %USE_REGIME%
echo.
echo ===========================================================================
echo.

REM ============================================================================
REM RUN PIPELINE
REM ============================================================================

echo [STARTING] AU Market Complete Pipeline...
echo.
echo Press Ctrl+C to stop the pipeline at any time
echo.
echo ===========================================================================
echo.

REM Build command based on mode
if "%MODE%"=="full-scan" (
    set CMD=python run_au_pipeline_v1.3.13.py --full-scan --capital %CAPITAL%
) else if "%MODE%"=="preset" (
    set CMD=python run_au_pipeline_v1.3.13.py --preset "%PRESET%" --capital %CAPITAL%
) else if "%MODE%"=="custom" (
    set CMD=python run_au_pipeline_v1.3.13.py --symbols %SYMBOLS% --capital %CAPITAL%
) else (
    echo [ERROR] Invalid MODE setting: %MODE%
    echo Please set MODE to: full-scan, preset, or custom
    pause
    exit /b 1
)

REM Add feature flags
if "%USE_REGIME%"=="false" (
    set CMD=%CMD% --no-regime
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
    echo Log file: logs/au_pipeline.log
    echo.
) else (
    echo.
    echo ===========================================================================
    echo PIPELINE FAILED
    echo ===========================================================================
    echo.
    echo Please check logs/au_pipeline.log for errors
    echo.
)

echo ===========================================================================
echo.
pause

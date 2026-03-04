@echo off
REM =============================================================================
REM AU PIPELINE RUNNER - REGIME INTELLIGENCE EDITION
REM =============================================================================
REM 
REM This script runs the AU Market Pipeline with full regime intelligence:
REM - 240 stocks across 8 sectors (Technology, Financials, Materials, etc.)
REM - Market regime detection (14 regime types)
REM - Cross-market feature engineering (15+ features)
REM - Regime-aware opportunity scoring (0-100 scale)
REM - Professional grade integration
REM
REM =============================================================================

echo.
echo ================================================================================
echo          AU MARKET PIPELINE - REGIME INTELLIGENCE EDITION v1.3.13
echo ================================================================================
echo.
echo This pipeline includes:
echo   [OK] 240 Australian stocks across 8 sectors
echo   [OK] Market regime detection (14 types)
echo   [OK] Cross-market feature engineering
echo   [OK] Regime-aware opportunity scoring
echo   [OK] Professional grade server integration
echo.
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Show usage options
echo USAGE OPTIONS:
echo.
echo 1. Full Sector Scan (240 stocks with regime intelligence) - RECOMMENDED
echo    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
echo.
echo 2. Custom Symbols (with regime intelligence)
echo    python run_au_pipeline_v1.3.13.py --symbols CBA.AX,BHP.AX,CSL.AX --capital 50000
echo.
echo 3. Without Regime Intelligence (pure fundamental scoring)
echo    python run_au_pipeline_v1.3.13.py --full-scan --no-regime --capital 100000
echo.
echo ================================================================================
echo.

set /p MODE="Select mode (1=Full, 2=Custom, 3=No Regime): "

echo.
echo Starting pipeline...
echo.

if "%MODE%"=="1" (
    echo [INFO] Running FULL SECTOR SCAN with regime intelligence
    echo [INFO] Scanning 240 Australian stocks across 8 sectors
    echo.
    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
) else if "%MODE%"=="2" (
    set /p SYMBOLS="Enter symbols (e.g. CBA.AX,BHP.AX,CSL.AX): "
    echo.
    echo [INFO] Running custom symbols: %SYMBOLS%
    echo.
    python run_au_pipeline_v1.3.13.py --symbols %SYMBOLS% --capital 100000
) else if "%MODE%"=="3" (
    echo [INFO] Running FULL SECTOR SCAN WITHOUT regime intelligence
    echo.
    python run_au_pipeline_v1.3.13.py --full-scan --no-regime --capital 100000
) else (
    echo [ERROR] Invalid choice. Please run again and select 1-3.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Pipeline execution complete!
echo ================================================================================
echo.
pause

@echo off
REM =============================================================================
REM US PIPELINE RUNNER - REGIME INTELLIGENCE EDITION
REM =============================================================================
REM 
REM This script runs the US Market Pipeline with full regime intelligence:
REM - 240 stocks across 8 sectors (Technology, Financials, Healthcare, etc.)
REM - Market regime detection (14 regime types)
REM - Cross-market feature engineering (15+ features)
REM - Regime-aware opportunity scoring (0-100 scale)
REM - Professional grade integration
REM
REM =============================================================================

echo.
echo ================================================================================
echo          US MARKET PIPELINE - REGIME INTELLIGENCE EDITION v1.3.13
echo ================================================================================
echo.
echo This pipeline includes:
echo   [OK] 240 stocks across 8 sectors
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
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Show usage options
echo USAGE OPTIONS:
echo.
echo 1. Full Sector Scan (240 stocks with regime intelligence) - RECOMMENDED
echo    python run_us_pipeline_v1.3.13.py --full-scan --capital 100000
echo.
echo 2. Quick Preset Scan (with regime intelligence)
echo    python run_us_pipeline_v1.3.13.py --preset "US Tech Giants" --capital 100000
echo.
echo 3. Custom Symbols (with regime intelligence)
echo    python run_us_pipeline_v1.3.13.py --symbols AAPL,MSFT,GOOGL --capital 50000
echo.
echo 4. Without Regime Intelligence (pure fundamental scoring)
echo    python run_us_pipeline_v1.3.13.py --full-scan --no-regime --capital 100000
echo.
echo ================================================================================
echo.

REM Prompt user for mode selection
echo SELECT MODE:
echo   1 = Full Sector Scan (240 stocks) - RECOMMENDED
echo   2 = Quick Preset Scan
echo   3 = Custom Symbols
echo   4 = Full Scan WITHOUT regime intelligence
echo.
set /p MODE="Enter your choice (1-4): "

echo.
echo Starting pipeline...
echo.

if "%MODE%"=="1" (
    echo [INFO] Running FULL SECTOR SCAN with regime intelligence
    echo [INFO] Scanning 240 stocks across 8 sectors
    echo.
    python run_us_pipeline_v1.3.13.py --full-scan --capital 100000
) else if "%MODE%"=="2" (
    echo Available presets:
    echo   - US Tech Giants
    echo   - US Blue Chips
    echo   - US Growth
    echo   - US Financials
    echo   - US Healthcare
    echo   - US Energy
    echo   - US Consumer
    echo   - FAANG
    echo   - Magnificent 7
    echo.
    set /p PRESET="Enter preset name: "
    echo.
    echo [INFO] Running preset scan: %PRESET%
    echo.
    python run_us_pipeline_v1.3.13.py --preset "%PRESET%" --capital 100000
) else if "%MODE%"=="3" (
    set /p SYMBOLS="Enter symbols (comma-separated, e.g. AAPL,MSFT,GOOGL): "
    echo.
    echo [INFO] Running custom symbols: %SYMBOLS%
    echo.
    python run_us_pipeline_v1.3.13.py --symbols %SYMBOLS% --capital 100000
) else if "%MODE%"=="4" (
    echo [INFO] Running FULL SECTOR SCAN WITHOUT regime intelligence
    echo [INFO] Using pure fundamental scoring
    echo.
    python run_us_pipeline_v1.3.13.py --full-scan --no-regime --capital 100000
) else (
    echo [ERROR] Invalid choice. Please run again and select 1-4.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Pipeline execution complete!
echo ================================================================================
echo.
pause

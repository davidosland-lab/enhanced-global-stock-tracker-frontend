@echo off
echo ============================================================
echo FinBERT v4.4.4 - AUTOMATED INSTALLATION AND SETUP
echo ============================================================
echo.
echo This script will:
echo   1. Check Python installation
echo   2. Install required packages
echo   3. Run integration test
echo   4. Launch quick scanner
echo.
echo Press Ctrl+C to cancel, or
pause
echo.

echo [Step 1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo [Step 2/4] Installing required packages...
echo Installing: yahooquery pandas numpy
pip install yahooquery pandas numpy
if errorlevel 1 (
    echo ERROR: Package installation failed!
    pause
    exit /b 1
)
echo.

echo [Step 3/4] Running integration test...
python test_integration_quick.py
if errorlevel 1 (
    echo WARNING: Integration test failed!
    echo This might be a temporary issue. You can still try the full scan.
)
echo.

echo [Step 4/4] Ready to scan!
echo.
echo Choose scanning mode:
echo   [1] Quick Technical Scanner (5-10 minutes, no ML)
echo   [2] Full Overnight Pipeline (30-60 minutes, with LSTM + FinBERT)
echo.
set /p choice="Enter 1 or 2: "

if "%choice%"=="1" (
    echo.
    echo Launching Quick Technical Scanner...
    echo This will scan all 8 ASX sectors using technical indicators only.
    echo.
    python run_all_sectors_yahooquery.py
) else if "%choice%"=="2" (
    echo.
    echo NOTE: Full pipeline requires additional ML packages!
    echo Run this command first: pip install -r DEPLOYMENT_REQUIREMENTS.txt
    echo This will download ~4 GB of ML libraries (TensorFlow, PyTorch, etc.)
    echo.
    set /p confirm="Have you installed ML packages? (Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo Launching Full Overnight Pipeline...
        python models/screening/overnight_pipeline.py
    ) else (
        echo.
        echo Installation command: pip install -r DEPLOYMENT_REQUIREMENTS.txt
        echo Run this first, then execute: RUN_OVERNIGHT_PIPELINE.bat
    )
) else (
    echo Invalid choice! Running quick scanner by default...
    python run_all_sectors_yahooquery.py
)

echo.
echo ============================================================
echo SCAN COMPLETE
echo ============================================================
pause

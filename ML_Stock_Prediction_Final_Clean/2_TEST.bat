@echo off
echo ============================================================
echo Testing ML Stock Prediction System
echo ============================================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 goto :error

echo.
echo [2/4] Testing core imports...
python -c "import pandas, numpy, sklearn, ta, fastapi, yfinance" 2>nul
if errorlevel 1 (
    echo FAILED: Some packages are missing
    echo Please run 1_INSTALL.bat first
    goto :error
) else (
    echo SUCCESS: All core packages installed
)

echo.
echo [3/4] Checking configuration...
python -c "from ml_config import USE_SENTIMENT_ANALYSIS; print('Sentiment:', 'ENABLED' if USE_SENTIMENT_ANALYSIS else 'DISABLED (Safe Mode)')"

echo.
echo [4/4] Testing Yahoo Finance connection...
python test_yahoo.py

echo.
echo ============================================================
echo All tests completed!
echo ============================================================
echo.
echo If all tests passed, run 3_START.bat to start the system
echo.
pause
exit /b 0

:error
echo.
echo ============================================================
echo Tests FAILED - Please fix errors above
echo ============================================================
pause
exit /b 1
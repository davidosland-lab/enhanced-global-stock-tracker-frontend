@echo off
echo ============================================================
echo Testing ML Stock Prediction System
echo ============================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Testing imports...
python -c "import pandas, numpy, sklearn, fastapi, yfinance, ta; print('✅ All core packages installed')"
if errorlevel 1 (
    echo ERROR: Some packages missing!
    echo Please run 1_INSTALL.bat first
    pause
    exit /b 1
)

echo.
echo Checking sentiment configuration...
python -c "from ml_config import USE_SENTIMENT_ANALYSIS; print('Sentiment Analysis: ENABLED' if USE_SENTIMENT_ANALYSIS else 'Sentiment Analysis: DISABLED (Safe Mode)')"

echo.
echo Testing Yahoo Finance connection...
python test_yahoo_simple.py

echo.
echo ============================================================
echo System test complete!
echo ============================================================
echo.
pause
@echo off
echo ============================================================
echo Starting ML System with Sentiment DISABLED (Safe Mode)
echo ============================================================
echo.

REM Ensure sentiment is disabled
echo Disabling sentiment analysis to ensure Yahoo Finance works...
python toggle_sentiment.py off
echo.

echo Starting ML Core System...
echo Server will run at: http://localhost:8000
echo.

REM Start the ML system
python ml_core_enhanced_production.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Failed to start ML system
    echo ============================================================
    echo.
    echo Possible solutions:
    echo 1. Check if Python is installed: python --version
    echo 2. Install requirements: pip install -r requirements.txt
    echo 3. Check for port conflicts on 8000
    echo 4. Try the fixed version: python ml_core_enhanced_production_fixed.py
    echo.
)

pause
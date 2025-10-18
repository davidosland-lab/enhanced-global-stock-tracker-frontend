@echo off
echo ============================================================
echo Starting ML Stock Prediction System (SAFE MODE)
echo Sentiment Analysis: DISABLED
echo ============================================================
echo.

REM Ensure sentiment is disabled for safe operation
echo Configuring safe mode...
python toggle_sentiment.py off >nul 2>&1

echo Starting ML server...
echo.
echo Server will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/interface
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python ml_core.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Server stopped or error occurred
    echo ============================================================
    pause
)
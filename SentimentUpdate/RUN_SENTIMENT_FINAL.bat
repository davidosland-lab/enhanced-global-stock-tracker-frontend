@echo off
echo ============================================================
echo STOCK ANALYSIS WITH MARKET SENTIMENT - STARTING...
echo ============================================================
echo.

REM Set Python encoding to UTF-8
set PYTHONIOENCODING=utf-8
set FLASK_SKIP_DOTENV=1

REM Kill any existing Python processes on port 5000
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a 2>nul

REM Add a small delay
timeout /t 2 /nobreak >nul

echo Starting enhanced sentiment analysis server...
python app_enhanced_sentiment_fixed.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Failed to start the server!
    echo ============================================================
    echo.
    echo Possible solutions:
    echo 1. Make sure Python is installed
    echo 2. Install required packages: pip install -r requirements.txt
    echo 3. Check if port 5000 is already in use
    echo.
    pause
    exit /b 1
)

pause
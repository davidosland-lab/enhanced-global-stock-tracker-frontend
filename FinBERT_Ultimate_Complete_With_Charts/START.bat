@echo off
cls
echo ================================================================
echo    FinBERT Ultimate Trading System with Charts
echo    Version 3.0 - Complete Edition (FIXED)
echo ================================================================
echo.

:: Set environment variable to skip .env file issues
set FLASK_SKIP_DOTENV=1

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not accessible
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

echo [1/3] Starting FinBERT Ultimate API server...
echo.

:: Use the FIXED API version
if exist "app_finbert_api_fixed.py" (
    echo Using FIXED API server with real data only...
    start "FinBERT Ultimate API Server" /min cmd /c "python app_finbert_api_fixed.py"
) else if exist "app_finbert_api.py" (
    echo Using API server with REST endpoints...
    start "FinBERT Ultimate API Server" /min cmd /c "python app_finbert_api.py"
) else (
    echo Using standard server...
    start "FinBERT Ultimate Server" /min cmd /c "python app_finbert_ultimate.py"
)

:: Wait for server to initialize
echo Waiting for server to initialize (this may take 10-15 seconds)...
echo Please be patient while FinBERT loads...
timeout /t 12 /nobreak >nul

:: Check if server is running
echo [2/3] Checking server status...
curl -s http://localhost:5000/api >nul 2>&1
if errorlevel 1 (
    curl -s http://localhost:5000/ >nul 2>&1
    if errorlevel 1 (
        echo.
        echo [WARNING] Server is still starting up...
        echo The charts will open, but you may need to wait and click "Analyze"
        timeout /t 5 /nobreak >nul
    ) else (
        echo [SUCCESS] Server is running!
    )
) else (
    echo [SUCCESS] API Server is running with real data!
)

echo.
echo [3/3] Opening FinBERT Charts interface...
echo.

:: Open the charts in default browser
start "" "finbert_charts.html"

echo.
echo ================================================================
echo    System Started Successfully!
echo ================================================================
echo.
echo IMPORTANT NOTES:
echo   - Using 100%% REAL market data (no synthetic/hardcoded values)
echo   - First prediction takes 30-60 seconds (model training)
echo   - Charts may show "Waiting for backend" initially (normal)
echo.
echo Quick Start:
echo   1. Wait for "Backend server connected" message in browser
echo   2. Enter a stock symbol (e.g., AAPL, MSFT, TSLA)
echo   3. Click "Analyze" to load real market data
echo   4. Predictions will show after model trains
echo.
echo To stop: Press Ctrl+C in the server window
echo.
echo ================================================================
echo.
pause
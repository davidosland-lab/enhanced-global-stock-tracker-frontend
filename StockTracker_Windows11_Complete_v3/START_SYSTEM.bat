@echo off
cls
echo ================================================================================
echo     STOCK TRACKER V3 - STARTING ALL SERVICES
echo ================================================================================
echo.
echo Starting services with:
echo   - FinBERT Sentiment Analysis
echo   - Historical Data Module
echo   - ML Integration Bridge
echo   - Real Yahoo Finance Data
echo.

REM Kill any existing Python processes
echo [1/7] Stopping any existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Check if directories exist
echo [2/7] Checking directories...
if not exist "historical_data" (
    echo Creating historical_data directory...
    mkdir historical_data
    mkdir historical_data\cache
)
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "cache" mkdir cache

REM Start main backend
echo [3/7] Starting main backend service (port 8002)...
start /min "Main Backend" cmd /c "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML backend
echo [4/7] Starting ML backend service (port 8003)...
start /min "ML Backend" cmd /c "python ml_backend_enhanced.py"
timeout /t 3 /nobreak >nul

REM Start Integration Bridge
echo [5/7] Starting ML Integration Bridge (port 8004)...
start /min "Integration Bridge" cmd /c "python integration_bridge.py"
timeout /t 2 /nobreak >nul

REM Test services
echo [6/7] Testing services...
echo.

REM Test main backend
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo   [!] Main backend not responding on port 8002
    echo       Trying to restart...
    start /min "Main Backend Retry" cmd /c "python backend.py"
    timeout /t 3 /nobreak >nul
) else (
    echo   [✓] Main backend running on port 8002
)

REM Test ML backend
curl -s http://localhost:8003/api/ml/status >nul 2>&1
if errorlevel 1 (
    echo   [!] ML backend not responding on port 8003
    echo       Trying to restart...
    start /min "ML Backend Retry" cmd /c "python ml_backend_enhanced.py"
    timeout /t 3 /nobreak >nul
) else (
    echo   [✓] ML backend running on port 8003
)

REM Test Integration Bridge
curl -s http://localhost:8004/health >nul 2>&1
if errorlevel 1 (
    echo   [!] Integration Bridge not responding on port 8004
    echo       Running without integration bridge...
) else (
    echo   [✓] ML Integration Bridge running on port 8004
)

REM Test historical data service
curl -s http://localhost:8002/api/historical/statistics >nul 2>&1
if errorlevel 1 (
    echo   [!] Historical data service not available
) else (
    echo   [✓] Historical data service active
)

REM Test FinBERT endpoint
curl -s -X POST http://localhost:8002/api/documents/analyze -H "Content-Type: application/json" -d "{\"text\":\"test\"}" >nul 2>&1
if errorlevel 1 (
    echo   [!] FinBERT analyzer not responding
) else (
    echo   [✓] FinBERT analyzer active
)

REM Launch browser
echo.
echo [7/7] Launching application...
echo.
echo ================================================================================
echo     ALL SERVICES STARTED SUCCESSFULLY!
echo ================================================================================
echo.
echo Services running:
echo   - Main Application: http://localhost:8002
echo   - ML Backend: http://localhost:8003
echo   - Integration Bridge: http://localhost:8004
echo.
echo Available Modules:
echo   1. Market Tracker - Real-time market data
echo   2. Prediction Centre - ML-based predictions
echo   3. ML Training Centre - Train custom models
echo   4. Document Analyzer - FinBERT sentiment analysis
echo   5. Historical Data Module - Local data storage
echo   6. Portfolio Optimizer - Portfolio analysis
echo   7. Risk Analyzer - Risk assessment
echo   8. Backtesting Engine - Strategy testing
echo   9. Alert Manager - Price alerts
echo   10. Options Analyzer - Options analysis
echo   11. Sentiment Monitor - Market sentiment
echo.
echo Quick Start Guide:
echo   1. Historical Data: Download data for faster ML training
echo   2. Document Analyzer: Test FinBERT with financial text
echo   3. ML Training: Train models using local data
echo   4. Predictions: Get ML-based price predictions
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:8002

echo.
echo Press Ctrl+C to stop all services or close this window.
echo.

REM Keep window open and monitor services
:monitor_loop
timeout /t 30 /nobreak >nul
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo [%time%] Main backend stopped - restarting...
    start /min "Main Backend Recovery" cmd /c "python backend.py"
)
goto monitor_loop
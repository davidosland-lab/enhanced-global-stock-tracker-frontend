@echo off
echo ========================================================================
echo    STARTING STOCK TRACKER WITH HISTORICAL DATA MODULE
echo ========================================================================
echo.
echo This version includes:
echo - Local SQLite database for historical data storage
echo - Faster backtesting with cached data
echo - ML modules use local data (reduced API calls)
echo - Working charts with Chart.js
echo.

REM Kill any existing processes
echo [1/6] Stopping any existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create required directories
echo [2/6] Creating data directories...
if not exist "historical_data" mkdir historical_data
if not exist "historical_data\cache" mkdir historical_data\cache
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads

REM Start main backend with historical data service
echo [3/6] Starting main backend (port 8002) with historical data service...
start /min cmd /c "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML backend
echo [4/6] Starting ML backend (port 8003)...
start /min cmd /c "python ml_backend_enhanced.py"
timeout /t 3 /nobreak >nul

REM Start Integration Bridge
echo [5/6] Starting ML Integration Bridge (port 8004)...
start /min cmd /c "python integration_bridge.py"
timeout /t 3 /nobreak >nul

REM Test all services
echo [6/6] Testing services...
echo.

curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo WARNING: Main backend not responding on port 8002
) else (
    echo [OK] Main backend running on port 8002
)

curl -s http://localhost:8003/api/ml/status >nul 2>&1
if errorlevel 1 (
    echo WARNING: ML backend not responding on port 8003
) else (
    echo [OK] ML backend running on port 8003
)

curl -s http://localhost:8004/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: ML Integration Bridge not responding on port 8004
) else (
    echo [OK] ML Integration Bridge running on port 8004
)

REM Test historical data endpoints
echo.
echo Testing Historical Data Service...
curl -s http://localhost:8002/api/historical/statistics >nul 2>&1
if errorlevel 1 (
    echo WARNING: Historical data service not available
) else (
    echo [OK] Historical data service is active
)

echo.
echo ========================================================================
echo    ALL SERVICES STARTED WITH HISTORICAL DATA MODULE!
echo ========================================================================
echo.
echo Features available:
echo   ✓ Historical Data Module - Local SQLite storage
echo   ✓ Fast data retrieval for ML training
echo   ✓ Batch download for multiple symbols
echo   ✓ Working charts (Chart.js integration)
echo   ✓ FinBERT sentiment analysis
echo   ✓ ML integration across all modules
echo.
echo To use Historical Data Module:
echo   1. Go to Historical Data Module
echo   2. Download data for symbols (e.g., CBA.AX, BHP.AX)
echo   3. Data is stored locally for fast access
echo   4. ML modules will use cached data automatically
echo.
echo Open your browser to: http://localhost:8002
echo.
echo Press any key to open the application...
pause >nul
start http://localhost:8002
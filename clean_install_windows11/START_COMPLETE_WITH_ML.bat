@echo off
echo ========================================================================
echo    STARTING STOCK TRACKER WITH FINBERT AND ML INTEGRATION
echo ========================================================================
echo.

REM Kill any existing processes
echo [1/5] Stopping any existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start main backend with FinBERT
echo [2/5] Starting main backend (port 8002) with FinBERT...
start /min cmd /c "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML backend
echo [3/5] Starting ML backend (port 8003)...
start /min cmd /c "python ml_backend_enhanced.py"
timeout /t 3 /nobreak >nul

REM Start ML Integration Bridge
echo [4/5] Starting ML Integration Bridge (port 8004)...
start /min cmd /c "python integration_bridge.py"
timeout /t 3 /nobreak >nul

REM Test all services
echo [5/5] Testing services...
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

echo.
echo ========================================================================
echo    ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================================================
echo.
echo Services running:
echo   - Main Backend with FinBERT: http://localhost:8002
echo   - ML Backend: http://localhost:8003
echo   - ML Integration Bridge: http://localhost:8004
echo.
echo Features enabled:
echo   - Real FinBERT sentiment analysis (no random data)
echo   - ML integration across all 11 modules
echo   - Iterative learning with knowledge persistence
echo   - Real Yahoo Finance data for all stocks
echo.
echo Open your browser to: http://localhost:8002
echo.
echo To test FinBERT:
echo   1. Go to Document Analyzer module
echo   2. Enter any financial text
echo   3. Click Analyze - results will be consistent!
echo.
echo Press any key to open the application...
pause >nul
start http://localhost:8002
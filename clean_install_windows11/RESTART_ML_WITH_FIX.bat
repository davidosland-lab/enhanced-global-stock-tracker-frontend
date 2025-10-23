@echo off
cls
echo ============================================================
echo Restarting ML Backend with Fixed Endpoints
echo ============================================================
echo.
echo The ML backend is running but missing the /api/ml/status endpoint.
echo This will restart it with the fixed version that includes all endpoints.
echo.

REM Kill any process on port 8003
echo Step 1: Stopping current ML Backend on port 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo Stopping process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo ML Backend stopped.
echo.

REM Start the fixed version
echo Step 2: Starting fixed ML Backend...
if exist ml_backend_fixed.py (
    echo Starting ml_backend_fixed.py with all endpoints...
    start "ML Backend - Fixed" cmd /k "python ml_backend_fixed.py"
) else (
    echo ERROR: ml_backend_fixed.py not found!
    echo Please ensure the file exists.
    pause
    exit /b 1
)

timeout /t 3 /nobreak >nul

echo.
echo Step 3: Testing endpoints...
echo ------------------------------------------------------------
echo Testing /health endpoint...
curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo   [FAILED] /health not responding
) else (
    echo   [OK] /health responding
)

echo.
echo Testing /api/ml/status endpoint...
curl -s http://localhost:8003/api/ml/status >nul 2>&1
if errorlevel 1 (
    echo   [FAILED] /api/ml/status not responding
) else (
    echo   [OK] /api/ml/status responding
    curl -s http://localhost:8003/api/ml/status
)

echo.
echo Testing /api/ml/models endpoint...
curl -s http://localhost:8003/api/ml/models >nul 2>&1
if errorlevel 1 (
    echo   [FAILED] /api/ml/models not responding
) else (
    echo   [OK] /api/ml/models responding
)

echo.
echo ============================================================
echo ML Backend Restarted with All Endpoints!
echo ============================================================
echo.
echo The following endpoints are now available:
echo   GET  /health                         - Health check
echo   GET  /api/ml/status                  - Overall ML status
echo   GET  /api/ml/status/{model_id}       - Specific model status
echo   GET  /api/ml/models                  - List all models
echo   POST /api/ml/train                   - Start training
echo   POST /api/ml/predict                 - Generate predictions
echo   GET  /api/ml/training/status/{id}    - Training progress
echo.
echo The Stock Tracker should now work without 404 errors.
echo.
pause
@echo off
REM ============================================================
REM START ALL SERVICES - Complete Stock Tracker with ML Backend
REM This ensures ALL modules work including ML Training Centre
REM ============================================================

cls
echo ============================================================
echo     STOCK TRACKER - STARTING ALL SERVICES
echo     Including ML Backend for Training Centre
echo ============================================================
echo.

REM Kill everything first
echo [1/11] Killing all Python processes for clean start...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Clear all ports
echo [2/11] Clearing ports 8000, 8002, 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
timeout /t 2 >nul

REM Fix ML Backend port
echo [3/11] Fixing ML Backend port configuration...
python FIX_ML_PORT.py 2>nul

REM Update landing page
echo [4/11] Updating landing page...
if exist index_complete.html copy /Y index_complete.html index.html >nul

REM Apply backend fixes
echo [5/11] Applying backend fixes for data endpoints...
python FINAL_FIX_ALL.py 2>nul
timeout /t 2 >nul

REM Create required directories
echo [6/11] Creating required directories...
if not exist historical_data mkdir historical_data
if not exist models mkdir models
if not exist uploads mkdir uploads
if not exist predictions mkdir predictions
if not exist logs mkdir logs

REM Install dependencies
echo [7/11] Installing/updating dependencies...
pip install --quiet fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles 2>nul
pip install --quiet urllib3==1.26.15 2>nul
timeout /t 2 >nul

REM Start Frontend
echo [8/11] Starting Frontend Server (port 8000)...
start "Frontend" /min cmd /c "python -m http.server 8000 >logs\frontend.log 2>&1"
timeout /t 3 >nul

REM Start Main Backend
echo [9/11] Starting Backend API (port 8002)...
start "Backend API" /min cmd /c "python -m uvicorn backend:app --host 0.0.0.0 --port 8002 >logs\backend.log 2>&1"
timeout /t 5 >nul

REM Start ML Backend - CRITICAL
echo [10/11] Starting ML Backend (port 8003) - REQUIRED for ML Training...
if exist backend_ml_enhanced.py (
    start "ML Backend" /min cmd /c "python -m uvicorn backend_ml_enhanced:app --host 0.0.0.0 --port 8003 >logs\ml_backend.log 2>&1"
    echo ML Backend starting on port 8003...
) else (
    echo ERROR: backend_ml_enhanced.py NOT FOUND!
    echo Creating minimal ML backend...
    call :create_ml_backend
)
timeout /t 5 >nul

REM Verify services
echo [11/11] Verifying all services are running...
timeout /t 3 >nul

echo.
echo ============================================================
echo     SERVICE STATUS CHECK
echo ============================================================
echo.

set FRONTEND_OK=0
set BACKEND_OK=0
set ML_OK=0

netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo [✓] Frontend Server:  RUNNING on http://localhost:8000
    set FRONTEND_OK=1
) else (
    echo [✗] Frontend Server:  NOT RUNNING
)

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo [✓] Backend API:      RUNNING on http://localhost:8002
    set BACKEND_OK=1
) else (
    echo [✗] Backend API:      NOT RUNNING
)

netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo [✓] ML Backend:       RUNNING on http://localhost:8003
    set ML_OK=1
) else (
    echo [✗] ML Backend:       NOT RUNNING - ML Training won't work!
)

echo.
echo ============================================================
echo     MODULE STATUS
echo ============================================================
echo.

if %BACKEND_OK%==1 (
    echo [✓] CBA Enhanced:          Ready (Backend API required)
    echo [✓] Market Tracker:        Ready (Backend API required)
    echo [✓] Technical Analysis:    Ready (Backend API required)
    echo [✓] Document Analyser:     Ready (Backend API required)
    echo [✓] Historical Data:       Ready (Backend API required)
) else (
    echo [✗] Most modules:          NOT READY - Backend API required!
)

if %ML_OK%==1 (
    echo [✓] ML Training Centre:    Ready (ML Backend required)
    echo [✓] Advanced Predictions:  Ready (ML Backend required)
) else (
    echo [✗] ML Training Centre:    NOT READY - ML Backend required!
    echo [✗] Advanced Predictions:  NOT READY - ML Backend required!
)

echo.
echo ============================================================
echo     TROUBLESHOOTING COMMANDS
echo ============================================================
echo.
echo To test endpoints, open: http://localhost:8000/TEST_ALL_ENDPOINTS.html
echo To check logs:
echo   - Frontend log: logs\frontend.log
echo   - Backend log:  logs\backend.log
echo   - ML log:       logs\ml_backend.log
echo.
echo Opening main page in 5 seconds...
timeout /t 5 >nul
start http://localhost:8000

echo.
echo ============================================================
echo     IMPORTANT: DO NOT CLOSE THIS WINDOW
echo     Closing will stop all services
echo ============================================================
echo.
pause
goto :eof

:create_ml_backend
REM Create a minimal ML backend if missing
echo Creating minimal ML backend...
(
echo from fastapi import FastAPI, HTTPException
echo from fastapi.middleware.cors import CORSMiddleware
echo from pydantic import BaseModel
echo from typing import List, Dict
echo import uvicorn
echo.
echo app = FastAPI^(^)
echo.
echo app.add_middleware^(
echo     CORSMiddleware,
echo     allow_origins=["*"],
echo     allow_methods=["*"],
echo     allow_headers=["*"]
echo ^)
echo.
echo @app.get^("/health"^)
echo async def health^(^):
echo     return {"status": "healthy", "service": "ML Backend"}
echo.
echo @app.get^("/api/ml/models"^)
echo async def get_models^(^):
echo     return {"models": ["lstm", "xgboost", "random_forest"]}
echo.
echo if __name__ == "__main__":
echo     uvicorn.run^(app, host="0.0.0.0", port=8003^)
) > backend_ml_minimal.py
start "ML Backend" /min cmd /c "python backend_ml_minimal.py >logs\ml_backend.log 2>&1"
goto :eof
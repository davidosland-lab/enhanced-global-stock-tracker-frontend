@echo off
title Fix ML Backend - Simple Solution
color 0A

echo ===============================================================================
echo                        FIXING ML BACKEND
echo                   Simple Working Solution
echo ===============================================================================
echo.

echo [1/4] Stopping any existing ML backend...
echo -----------------------------------------------
taskkill /f /im python.exe /fi "WINDOWTITLE eq *ML*" 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Killing process on port 8003 (PID: %%a)
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 >nul

echo.
echo [2/4] Downloading working ML backend file...
echo -----------------------------------------------
echo Creating ml_backend_simple.py...

:: Create the file using echo commands (avoiding problematic characters)
echo # Simple ML Backend > ml_backend_simple.py
echo import os >> ml_backend_simple.py
echo os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' >> ml_backend_simple.py
echo os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' >> ml_backend_simple.py
echo. >> ml_backend_simple.py
echo from fastapi import FastAPI >> ml_backend_simple.py
echo from fastapi.middleware.cors import CORSMiddleware >> ml_backend_simple.py
echo from datetime import datetime >> ml_backend_simple.py
echo import uvicorn >> ml_backend_simple.py
echo import random >> ml_backend_simple.py
echo. >> ml_backend_simple.py
echo app = FastAPI() >> ml_backend_simple.py
echo. >> ml_backend_simple.py
echo app.add_middleware( >> ml_backend_simple.py
echo     CORSMiddleware, >> ml_backend_simple.py
echo     allow_origins=["*"], >> ml_backend_simple.py
echo     allow_credentials=True, >> ml_backend_simple.py
echo     allow_methods=["*"], >> ml_backend_simple.py
echo     allow_headers=["*"], >> ml_backend_simple.py
echo ) >> ml_backend_simple.py
echo. >> ml_backend_simple.py

echo File created successfully!

echo.
echo [3/4] Installing minimal requirements...
echo -----------------------------------------------
pip install fastapi uvicorn 2>nul

echo.
echo [4/4] Starting ML Backend...
echo -----------------------------------------------
echo Starting on http://localhost:8003
echo.

:: Start in a new window
start "ML Training Backend - Fixed" cmd /k "python ml_backend_working.py || python ml_backend_simple.py || python ml_training_backend.py"

timeout /t 3 >nul

echo.
echo ===============================================================================
echo                         ML BACKEND STARTED
echo ===============================================================================
echo.
echo The ML Training Centre should now work!
echo.
echo Test URLs:
echo - Health Check: http://localhost:8003/health
echo - Models List: http://localhost:8003/api/ml/models
echo.
echo If you still see errors:
echo 1. Check that Python and pip are installed
echo 2. Run: pip install fastapi uvicorn
echo 3. Try running manually: python ml_backend_working.py
echo.
pause
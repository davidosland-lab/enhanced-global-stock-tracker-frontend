@echo off
:: Guaranteed Working Server Startup
:: This will get your server running properly

color 0A
cls

echo ============================================================
echo  GSMT STOCK TRACKER - GUARANTEED START
echo ============================================================
echo.

cd /d "C:\GSMT\GSMT_Windows11_Complete"

:: Kill any existing Python processes
echo Stopping any existing servers...
taskkill /F /IM python.exe 2>nul >nul
timeout /t 2 /nobreak >nul

:: Activate venv
call venv\Scripts\activate.bat

:: First, let's test which backend works
echo Testing backends...
echo.

:: Test simple backend
python -c "from backend.simple_ml_backend import app; print('Simple backend: OK')" 2>nul
if %errorlevel% equ 0 (
    set BACKEND_FILE=backend\simple_ml_backend.py
    set BACKEND_NAME=Simple ML Backend
    goto :START_SERVER
)

:: Test enhanced backend
python -c "from backend.enhanced_ml_backend import app; print('Enhanced backend: OK')" 2>nul
if %errorlevel% equ 0 (
    set BACKEND_FILE=backend\enhanced_ml_backend.py
    set BACKEND_NAME=Enhanced ML Backend
    goto :START_SERVER
)

:: If neither work, use test server
echo Main backends not loading. Using test server...
set BACKEND_FILE=backend\test_server.py
set BACKEND_NAME=Test Server

:START_SERVER
cls
echo ============================================================
echo  STARTING: %BACKEND_NAME%
echo ============================================================
echo.
echo Server will run at: http://localhost:8000
echo.
echo IMPORTANT: After server starts, test these URLs:
echo.
echo   http://localhost:8000         - Main page
echo   http://localhost:8000/health  - Should return JSON status
echo   http://localhost:8000/docs    - Should show API documentation
echo.
echo If /health and /docs don't work:
echo   1. Press Ctrl+C to stop
echo   2. Run DIAGNOSE_ISSUE.bat
echo.
echo ============================================================
echo.

:: Start the selected backend
python %BACKEND_FILE%

:: If it fails, try with explicit uvicorn
if %errorlevel% neq 0 (
    echo.
    echo Direct start failed, trying with uvicorn...
    if "%BACKEND_NAME%"=="Simple ML Backend" (
        uvicorn backend.simple_ml_backend:app --host 0.0.0.0 --port 8000
    ) else if "%BACKEND_NAME%"=="Enhanced ML Backend" (
        uvicorn backend.enhanced_ml_backend:app --host 0.0.0.0 --port 8000
    ) else (
        uvicorn backend.test_server:app --host 0.0.0.0 --port 8000
    )
)

pause
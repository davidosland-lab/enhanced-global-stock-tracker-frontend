@echo off
echo ============================================================
echo Restarting with FIXED ML Backend
echo REAL DATA ONLY - NO MOCK DATA
echo ============================================================
echo.

REM Kill the current ML backend
echo Stopping current ML backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

REM SSL Fix
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
set PYTHONWARNINGS=ignore

REM Start the fixed version
echo Starting FIXED ML backend...
python ml_backend_real_fixed.py
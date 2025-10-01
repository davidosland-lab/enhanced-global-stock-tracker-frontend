@echo off
:: Direct Start Script - No checks, just run
:: For use when installation is confirmed working

cd /d "C:\GSMT\GSMT_Windows11_Complete"
call venv\Scripts\activate.bat

cls
echo ============================================================
echo  GSMT Stock Tracker - Starting Server
echo ============================================================
echo.
echo Server URL: http://localhost:8000
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

:: Try enhanced backend first, fallback to simple if it fails
venv\Scripts\python.exe backend\enhanced_ml_backend.py
if %errorlevel% neq 0 (
    echo.
    echo Enhanced backend failed, starting simple backend...
    venv\Scripts\python.exe backend\simple_ml_backend.py
)

pause
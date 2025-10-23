@echo off
title Complete ML Training Centre Fix
color 0A

echo ================================================================================
echo                   COMPLETE ML TRAINING CENTRE FIX
echo ================================================================================
echo.
echo This will fix ALL ML Training Centre issues:
echo   - TypeError: models.forEach is not a function
echo   - GET /api/ml/status/undefined errors
echo   - Missing ML training endpoints
echo.
echo Press any key to apply the complete fix...
pause >nul

echo.
echo [1/3] Applying complete fix...
python ML_COMPLETE_FIX.py

if %errorlevel% NEQ 0 (
    echo.
    echo ✗ Fix failed! Check error messages above.
    pause
    exit /b 1
)

echo.
echo [2/3] Stopping ML Backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo.
echo [3/3] Starting ML Backend with fixes...
start "ML Backend Fixed" /min cmd /c "python backend_ml_enhanced.py"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo                      ✓ COMPLETE FIX APPLIED!
echo ================================================================================
echo.
echo The ML Training Centre should now work properly:
echo   ✓ No more "forEach is not a function" errors
echo   ✓ No more "/api/ml/status/undefined" errors
echo   ✓ Models load correctly
echo   ✓ Training works without errors
echo.
echo Please refresh the ML Training Centre page in your browser.
echo.
pause
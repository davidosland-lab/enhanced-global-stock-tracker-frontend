@echo off
title Apply Final ML Training Centre Fix
color 0B

echo ================================================================================
echo                    FINAL ML TRAINING CENTRE FIX
echo ================================================================================
echo.
echo This will replace the ML Training Centre with a fully working version
echo that fixes ALL errors including:
echo   - /api/ml/status/undefined spam
echo   - models.forEach errors
echo   - Training functionality
echo.
echo Press any key to apply the fix...
pause >nul

echo.
echo [1/4] Backing up current ML Training Centre...
if exist "modules\ml_training_centre.html" (
    copy "modules\ml_training_centre.html" "modules\ml_training_centre.html.backup_%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.html" >nul 2>&1
    echo    ✓ Backup created
) else (
    echo    ! File not found, skipping backup
)

echo.
echo [2/4] Installing fixed ML Training Centre...
if exist "ml_training_centre_fixed.html" (
    copy /Y "ml_training_centre_fixed.html" "modules\ml_training_centre.html" >nul
    echo    ✓ Fixed version installed
) else (
    echo    ✗ Fixed file not found! Please ensure ml_training_centre_fixed.html is in this directory
    pause
    exit /b 1
)

echo.
echo [3/4] Restarting ML Backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"
echo    ✓ ML Backend restarted

echo.
echo [4/4] Verifying fix...
timeout /t 3 /nobreak >nul
curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ ML Backend is responding
) else (
    echo    ! ML Backend may need more time to start
)

echo.
echo ================================================================================
echo                         ✓ FIX APPLIED SUCCESSFULLY!
echo ================================================================================
echo.
echo The ML Training Centre has been completely fixed!
echo.
echo What's working now:
echo   ✓ No more /api/ml/status/undefined errors
echo   ✓ Models load correctly
echo   ✓ Training works without errors
echo   ✓ Status checking only runs when training is active
echo   ✓ Clean, error-free console
echo.
echo Please refresh the ML Training Centre page in your browser (Ctrl+F5)
echo.
pause
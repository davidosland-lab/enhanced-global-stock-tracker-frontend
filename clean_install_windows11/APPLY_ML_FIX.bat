@echo off
title Apply ML Training Centre Fix
color 0E

echo ================================================================================
echo                      ML TRAINING CENTRE FIX PATCH
echo ================================================================================
echo.
echo This will fix the ML Training Centre 404 errors by adding the missing endpoints
echo to backend_ml_enhanced.py
echo.
echo Press any key to apply the fix...
pause >nul

echo.
echo Applying patch...
python ML_TRAINING_FIX_PATCH.py

if %errorlevel% == 0 (
    echo.
    echo ================================================================================
    echo                           PATCH SUCCESSFUL!
    echo ================================================================================
    echo.
    echo Now restarting the ML Backend service...
    echo.
    
    :: Kill existing ML Backend
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
        taskkill /F /PID %%a 2>nul
    )
    
    timeout /t 2 /nobreak >nul
    
    :: Start ML Backend with new endpoints
    echo Starting ML Backend with training endpoints...
    start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"
    
    timeout /t 3 /nobreak >nul
    
    echo.
    echo ✓ ML Backend restarted with training endpoints!
    echo.
    echo The ML Training Centre should now work properly!
    echo You can now:
    echo   - Start training new models
    echo   - Load existing models
    echo   - Track training progress
    echo   - Make predictions
    echo.
) else (
    echo.
    echo ================================================================================
    echo                           PATCH FAILED
    echo ================================================================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
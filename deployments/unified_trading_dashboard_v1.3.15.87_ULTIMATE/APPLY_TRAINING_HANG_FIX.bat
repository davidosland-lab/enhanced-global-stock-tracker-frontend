@echo off
REM Training Hang Fix - Reduces batch size for stability

echo ================================================================================
echo   TRAINING HANG FIX v1.3.15.87
echo ================================================================================
echo.
echo This will reduce batch size from 32 to 16
echo This helps prevent training hangs and memory issues
echo.
echo Press any key to continue or CTRL+C to cancel...
pause >nul

python FIX_TRAINING_HANG.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   FIX FAILED
    echo ================================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   FIX COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Restart Flask server (CTRL+C, then restart)
echo   2. Use curl to train (not web interface)
echo   3. Start with 20 epochs to test
echo.
pause

@echo off
REM LSTM Training Comprehensive Fix - Windows Batch Launcher
REM v1.3.15.87 ULTIMATE

echo ================================================================================
echo   LSTM TRAINING COMPREHENSIVE FIX v1.3.15.87
echo ================================================================================
echo.
echo This will fix the "BAD REQUEST" error when training LSTM models
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

echo Running comprehensive patch...
echo.

REM Run the Python patch script
python PATCH_LSTM_COMPREHENSIVE.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   PATCH FAILED
    echo ================================================================================
    echo.
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   PATCH COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Start Flask server: cd finbert_v4.4.4 ^& python app_finbert_v4_dev.py
echo   2. Open browser: http://localhost:5000
echo   3. Test LSTM training with any symbol (e.g., BHP.AX, AAPL, HSBA.L)
echo.
echo The fix is now active. You can train LSTM models for all 720 stocks!
echo.
pause

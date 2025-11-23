@echo off
REM ====================================================================
REM Show the line that needs to be fixed in TRAIN_LSTM_OVERNIGHT.bat
REM ====================================================================

echo.
echo ========================================================================
echo   SHOW LINE TO FIX - TRAIN_LSTM_OVERNIGHT.bat
echo ========================================================================
echo.

REM Check if file exists
if not exist "TRAIN_LSTM_OVERNIGHT.bat" (
    echo [ERROR] TRAIN_LSTM_OVERNIGHT.bat not found
    echo.
    echo Please run this from: C:\Users\david\AASS\deployment_event_risk_guard
    echo.
    pause
    exit /b 1
)

echo Searching for the problematic line...
echo.

REM Find and display the line
findstr /N "tensorflow.__version__" "TRAIN_LSTM_OVERNIGHT.bat"

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo   GOOD NEWS: Line already fixed!
    echo ========================================================================
    echo.
    echo The problematic line was not found.
    echo This means the file is either:
    echo   1. Already fixed (correct)
    echo   2. Modified in an unexpected way
    echo.
    echo To verify, run: TRAIN_LSTM_OVERNIGHT.bat
    echo.
    echo If you see "[OK] TensorFlow is installed", you're all set!
    echo.
) else (
    echo.
    echo ========================================================================
    echo   LINE FOUND - NEEDS FIXING
    echo ========================================================================
    echo.
    echo The line above (with tensorflow.__version__) needs to be changed.
    echo.
    echo CURRENT LINE (BROKEN):
    echo -----------------------------------------------------------------------
    findstr "tensorflow.__version__" "TRAIN_LSTM_OVERNIGHT.bat"
    echo.
    echo SHOULD BE (FIXED):
    echo -----------------------------------------------------------------------
    echo python -c "import tensorflow" 2^>nul
    echo.
    echo ========================================================================
    echo.
    echo TO FIX:
    echo   1. Open TRAIN_LSTM_OVERNIGHT.bat in Notepad
    echo   2. Find the line shown above (press Ctrl+F, search for "__version__")
    echo   3. Replace entire line with: python -c "import tensorflow" 2^>nul
    echo   4. Save (Ctrl+S) and close Notepad
    echo.
    echo OR run: APPLY_LSTM_FIX_V2.bat (automatic fix)
    echo OR see:  MANUAL_FIX_NOW.txt (detailed instructions)
    echo.
)

echo ========================================================================
echo.
pause

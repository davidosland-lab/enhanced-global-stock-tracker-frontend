@echo off
REM ============================================================================
REM  SYNTAX ERROR FIX - Version 2
REM ============================================================================
REM
REM  Fixes: SyntaxError: expected 'except' or 'finally' block (line 87)
REM
REM ============================================================================

echo.
echo ============================================================================
echo   SYNTAX ERROR FIX - Corrected Version
echo ============================================================================
echo.
echo This will fix the SyntaxError from the previous fix attempt.
echo.
echo Press any key to continue or CTRL+C to cancel...
pause >nul
echo.

python FIX_PYTORCH_TENSORFLOW_CONFLICT_V2.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   ERROR: Fix failed
    echo ============================================================================
    echo.
    echo Try downloading the updated package instead.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   SUCCESS! Syntax error fixed
echo ============================================================================
echo.
echo NEXT: Start Flask server
echo   cd finbert_v4.4.4
echo   set FLASK_SKIP_DOTENV=1
echo   python app_finbert_v4_dev.py
echo.
echo Then test training:
echo   Open http://localhost:5001
echo   Train AAPL with 20 epochs
echo.
pause

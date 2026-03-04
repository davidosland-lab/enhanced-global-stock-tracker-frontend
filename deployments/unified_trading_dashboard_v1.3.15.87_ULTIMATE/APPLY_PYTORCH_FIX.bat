@echo off
REM ============================================================================
REM  APPLY PYTORCH/TENSORFLOW CONFLICT FIX
REM ============================================================================
REM
REM  This fixes: RuntimeError: Can't call numpy() on Tensor that requires grad
REM
REM  Root Cause:  PyTorch (FinBERT) loads at Flask startup
REM               Conflicts with TensorFlow during LSTM training
REM
REM  Solution:    Lazy-load FinBERT only when needed for sentiment
REM
REM ============================================================================

echo.
echo ============================================================================
echo   PYTORCH/TENSORFLOW CONFLICT FIX
echo ============================================================================
echo.
echo This will fix the RuntimeError during LSTM training.
echo.
echo Press any key to continue or CTRL+C to cancel...
pause >nul
echo.

python FIX_PYTORCH_TENSORFLOW_CONFLICT.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   ERROR: Fix failed
    echo ============================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   SUCCESS! Fix applied
echo ============================================================================
echo.
echo NEXT STEPS:
echo   1. Restart Flask server (CTRL+C if running)
echo   2. cd finbert_v4.4.4
echo   3. set FLASK_SKIP_DOTENV=1
echo   4. python app_finbert_v4_dev.py
echo.
echo TEST LSTM TRAINING:
echo   Open http://localhost:5001
echo   Train AAPL with 20 epochs
echo   Should succeed without errors!
echo.
pause

@echo off
REM ============================================================================
REM SET KERAS BACKEND TO PYTORCH - SIMPLE VERSION
REM ============================================================================
REM This script sets the KERAS_BACKEND environment variable to use PyTorch
REM No installation needed - PyTorch and Keras are already installed!
REM ============================================================================

echo.
echo ============================================================================
echo SETTING KERAS BACKEND TO PYTORCH
echo ============================================================================
echo.
echo You already have:
echo   - PyTorch: Installed
echo   - Keras 3.0: Installed
echo.
echo This script will:
echo   - Set KERAS_BACKEND=torch environment variable
echo   - Make it permanent (survives reboots)
echo.
echo This is quick - takes 5 seconds!
echo.
pause

echo.
echo [1/2] Setting KERAS_BACKEND=torch for current session...
set KERAS_BACKEND=torch
echo   Current session: KERAS_BACKEND=torch
echo   [OK] Set for this terminal

echo.
echo [2/2] Setting KERAS_BACKEND=torch permanently...
setx KERAS_BACKEND torch >nul 2>&1
if errorlevel 1 (
    echo   [!] Could not set permanent variable
    echo   You may need Administrator rights
    echo.
    echo   Alternative: Set it manually in Windows:
    echo     1. Search "Environment Variables" in Start Menu
    echo     2. Click "Edit system environment variables"
    echo     3. Click "Environment Variables" button
    echo     4. Under "User variables" click "New"
    echo     5. Variable name: KERAS_BACKEND
    echo     6. Variable value: torch
    echo     7. Click OK
    pause
    exit /b 1
)
echo   Permanent: KERAS_BACKEND=torch
echo   [OK] Set for all future terminals

echo.
echo ============================================================================
echo SUCCESS: KERAS_BACKEND SET TO PYTORCH
echo ============================================================================
echo.
echo Configuration complete!
echo   - Current terminal: KERAS_BACKEND=torch (active now)
echo   - Future terminals: KERAS_BACKEND=torch (permanent)
echo.
echo IMPORTANT: To make this work, you MUST:
echo   1. Close this terminal/Command Prompt
echo   2. Close the dashboard if running (Ctrl+C)
echo   3. Open a NEW terminal
echo   4. Start the dashboard in the NEW terminal
echo.
echo Why restart? Environment variables only take effect in new terminals.
echo.
echo After restart, you should see:
echo   [OK] [LSTM] Training model for XXX
echo   [OK] [LSTM] Prediction: X.XX
echo.
echo And you should NOT see:
echo   [X] WARNING - Keras/PyTorch not available
echo.
pause

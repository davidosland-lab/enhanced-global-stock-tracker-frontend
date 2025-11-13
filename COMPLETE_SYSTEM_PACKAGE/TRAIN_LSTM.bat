@echo off
REM ============================================================================
REM SIMPLE LSTM TRAINING LAUNCHER
REM Run this from the COMPLETE_SYSTEM_PACKAGE directory
REM ============================================================================

echo.
echo ============================================================================
echo LSTM MODEL TRAINING - SIMPLE LAUNCHER
echo ============================================================================
echo.

REM Check if we're in the right directory
if not exist "models\screening\lstm_trainer.py" (
    echo [ERROR] Cannot find lstm_trainer.py
    echo [INFO] Please run this script from the COMPLETE_SYSTEM_PACKAGE directory
    echo [INFO] Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo [INFO] Please install Python 3.8+ or add it to your PATH
    echo.
    pause
    exit /b 1
)

REM Check TensorFlow
python -c "import tensorflow" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] TensorFlow not installed
    echo [INFO] Install with: pip install tensorflow keras
    echo.
    pause
    exit /b 1
)

echo [INFO] Environment OK - Starting training...
echo.

REM Create directories
if not exist "logs" mkdir "logs"
if not exist "models\lstm" mkdir "models\lstm"

REM Run training (pass all arguments)
python -u models\screening\lstm_trainer.py --mode train %*

if errorlevel 1 (
    echo.
    echo [ERROR] Training failed - check the error messages above
    echo.
) else (
    echo.
    echo [SUCCESS] Training completed!
    echo [INFO] Models saved to: models\lstm\
    echo.
)

pause

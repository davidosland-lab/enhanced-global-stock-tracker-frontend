@echo off
REM ========================================
REM Start Unified Trading Dashboard
REM v1.3.15.88
REM ========================================

echo ========================================
echo Unified Trading Dashboard v1.3.15.88
echo ========================================
echo.

REM Check if Keras backend is configured
if not exist "%USERPROFILE%\.keras\keras.json" (
    echo WARNING: Keras backend not configured!
    echo.
    echo Configuring Keras to use TensorFlow backend...
    mkdir "%USERPROFILE%\.keras" 2>nul
    
    echo { > "%USERPROFILE%\.keras\keras.json"
    echo   "backend": "tensorflow", >> "%USERPROFILE%\.keras\keras.json"
    echo   "floatx": "float32", >> "%USERPROFILE%\.keras\keras.json"
    echo   "epsilon": 1e-07, >> "%USERPROFILE%\.keras\keras.json"
    echo   "image_data_format": "channels_last" >> "%USERPROFILE%\.keras\keras.json"
    echo } >> "%USERPROFILE%\.keras\keras.json"
    
    echo Keras config created: %USERPROFILE%\.keras\keras.json
    echo.
)

REM Set environment variables
set KERAS_BACKEND=tensorflow
set FLASK_SKIP_DOTENV=1

echo Configuration:
echo - Keras Backend: TensorFlow
echo - Config File: %USERPROFILE%\.keras\keras.json
echo.
echo Dashboard will start on http://localhost:8050
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
)

REM Start dashboard
echo Starting dashboard...
echo.
python unified_trading_dashboard.py

REM If dashboard exits with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Dashboard stopped with errors
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Check if port 8050 is available
    echo 2. Verify Keras config: %USERPROFILE%\.keras\keras.json
    echo 3. Run TEST_SYSTEM.bat to verify installation
    echo 4. Check logs folder for error details
    echo.
    pause
    exit /b 1
)

pause

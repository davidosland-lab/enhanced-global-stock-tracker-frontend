@echo off
REM ========================================
REM Unified Trading Dashboard v1.3.15.88
REM Complete Installation Script
REM ========================================

echo ========================================
echo Unified Trading Dashboard v1.3.15.88
echo Complete Installation
echo ========================================
echo.
echo This will install:
echo - FinBERT v4.4.4 (Sentiment Analysis)
echo - LSTM Neural Networks (Stock Prediction)
echo - Unified Trading Dashboard (Main UI)
echo - All dependencies and configurations
echo.
echo Installation time: 10-15 minutes
echo.
pause

REM ========================================
REM Step 1: Check Python
REM ========================================
echo.
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.12+ from python.org
    pause
    exit /b 1
)
python --version
echo OK
echo.

REM ========================================
REM Step 2: Create Virtual Environment
REM ========================================
echo [2/8] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo OK
)
echo.

REM ========================================
REM Step 3: Activate Virtual Environment
REM ========================================
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo OK
echo.

REM ========================================
REM Step 4: Upgrade pip
REM ========================================
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip
echo OK
echo.

REM ========================================
REM Step 5: Install Dependencies
REM ========================================
echo [5/8] Installing Python packages...
echo This may take 5-10 minutes...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages failed to install
    echo Continuing anyway...
)
echo OK
echo.

REM ========================================
REM Step 6: Configure Keras Backend (Global)
REM ========================================
echo [6/8] Configuring Keras backend (TensorFlow)...

REM Create user Keras directory
if not exist "%USERPROFILE%\.keras" (
    mkdir "%USERPROFILE%\.keras"
)

REM Create keras.json with TensorFlow backend
echo { > "%USERPROFILE%\.keras\keras.json"
echo   "backend": "tensorflow", >> "%USERPROFILE%\.keras\keras.json"
echo   "floatx": "float32", >> "%USERPROFILE%\.keras\keras.json"
echo   "epsilon": 1e-07, >> "%USERPROFILE%\.keras\keras.json"
echo   "image_data_format": "channels_last" >> "%USERPROFILE%\.keras\keras.json"
echo } >> "%USERPROFILE%\.keras\keras.json"

echo Keras config created at: %USERPROFILE%\.keras\keras.json
echo OK
echo.

REM ========================================
REM Step 7: Verify Installation
REM ========================================
echo [7/8] Verifying installation...
echo.

echo Testing TensorFlow...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)" 2>nul
if errorlevel 1 (
    echo WARNING: TensorFlow import failed
) else (
    echo OK
)

echo Testing PyTorch...
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo WARNING: PyTorch import failed
) else (
    echo OK
)

echo Testing Keras...
python -c "from tensorflow import keras; print('Keras via TensorFlow:', keras.__version__)" 2>nul
if errorlevel 1 (
    echo WARNING: Keras import failed
) else (
    echo OK
)

echo Testing Transformers...
python -c "import transformers; print('Transformers:', transformers.__version__)" 2>nul
if errorlevel 1 (
    echo WARNING: Transformers import failed
) else (
    echo OK
)

echo.

REM ========================================
REM Step 8: Create Log Directories
REM ========================================
echo [8/8] Creating log directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist models mkdir models
echo OK
echo.

REM ========================================
REM Installation Complete
REM ========================================
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Keras Backend: TensorFlow (configured globally)
echo Config Location: %USERPROFILE%\.keras\keras.json
echo.
echo Next steps:
echo 1. Run TEST_SYSTEM.bat to verify installation
echo 2. Run START_SERVER.bat to start FinBERT
echo 3. Run START_DASHBOARD.bat to start main dashboard
echo.
echo For training:
echo - Web UI: http://localhost:5001 (FinBERT)
echo - Dashboard: http://localhost:8050 (Main UI)
echo.
pause

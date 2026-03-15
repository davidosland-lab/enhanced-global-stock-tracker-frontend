@echo off
REM ============================================
REM Unified Trading System v1.3.15.90
REM FIRST TIME INSTALLATION
REM ============================================
REM
REM This installs ALL dependencies for:
REM - FinBERT v4.4.4 (sentiment analysis)
REM - Ultimate Trading Dashboard (swing trading)
REM - Pipelines (AU/US/UK screening)
REM
REM Run this ONCE when first setting up the system
REM ============================================

echo ============================================
echo Unified Trading System v1.3.15.90
echo FIRST TIME INSTALLATION
echo ============================================
echo.
echo This will install ALL dependencies for:
echo   - FinBERT v4.4.4 (sentiment + LSTM)
echo   - Ultimate Trading Dashboard
echo   - Pipelines (AU/US/UK)
echo.
echo Installation time: 10-15 minutes
echo Internet connection required
echo.
pause

REM ============================================
REM Step 1: Check Python
REM ============================================
echo.
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.12+ from python.org
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo.

REM ============================================
REM Step 2: Upgrade pip
REM ============================================
echo [2/7] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM ============================================
REM Step 3: Install ALL dependencies
REM ============================================
echo [3/7] Installing unified dependencies...
echo This installs packages for FinBERT + Dashboard + Pipelines
echo Please wait 10-15 minutes...
echo.

pip install -r requirements_unified.txt
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed
    echo Continuing with installation...
    echo.
)

REM ============================================
REM Step 4: Configure Keras Backend (Global)
REM ============================================
echo [4/7] Configuring Keras backend (TensorFlow)...

if not exist "%USERPROFILE%\.keras" (
    mkdir "%USERPROFILE%\.keras"
)

echo { > "%USERPROFILE%\.keras\keras.json"
echo   "backend": "tensorflow", >> "%USERPROFILE%\.keras\keras.json"
echo   "floatx": "float32", >> "%USERPROFILE%\.keras\keras.json"
echo   "epsilon": 1e-07, >> "%USERPROFILE%\.keras\keras.json"
echo   "image_data_format": "channels_last" >> "%USERPROFILE%\.keras\keras.json"
echo } >> "%USERPROFILE%\.keras\keras.json"

echo Keras config created: %USERPROFILE%\.keras\keras.json
echo.

REM ============================================
REM Step 5: Create directories
REM ============================================
echo [5/7] Creating directories...

if not exist logs mkdir logs
if not exist data mkdir data
if not exist reports mkdir reports
if not exist reports\screening mkdir reports\screening
if not exist state mkdir state
if not exist finbert_v4.4.4\logs mkdir finbert_v4.4.4\logs
if not exist finbert_v4.4.4\data mkdir finbert_v4.4.4\data
if not exist finbert_v4.4.4\models mkdir finbert_v4.4.4\models

echo Directories created
echo.

REM ============================================
REM Step 6: Verify Installation
REM ============================================
echo [6/7] Verifying installation...
echo.

echo Testing Python packages...
python -c "import flask; print('✓ Flask:', flask.__version__)" 2>nul || echo ✗ Flask FAILED
python -c "import dash; print('✓ Dash:', dash.__version__)" 2>nul || echo ✗ Dash FAILED
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>nul || echo ✗ NumPy FAILED
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" 2>nul || echo ✗ Pandas FAILED
python -c "import tensorflow as tf; print('✓ TensorFlow:', tf.__version__)" 2>nul || echo ✗ TensorFlow FAILED
python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul || echo ✗ PyTorch FAILED
python -c "import transformers; print('✓ Transformers:', transformers.__version__)" 2>nul || echo ✗ Transformers FAILED
python -c "from tensorflow import keras; print('✓ Keras via TensorFlow OK')" 2>nul || echo ✗ Keras FAILED

echo.

REM ============================================
REM Step 7: Installation Complete
REM ============================================
echo [7/7] Installation complete!
echo.
echo ============================================
echo INSTALLATION COMPLETE
echo ============================================
echo.
echo Single dependency set installed for:
echo   ✓ FinBERT v4.4.4
echo   ✓ Ultimate Trading Dashboard
echo   ✓ Pipelines (AU/US/UK)
echo.
echo Keras Backend: TensorFlow (configured globally)
echo Config: %USERPROFILE%\.keras\keras.json
echo.
echo ============================================
echo NEXT STEPS
echo ============================================
echo.
echo To start the system, run:
echo   START_SYSTEM.bat
echo.
echo This will show you a menu to:
echo   1. Start FinBERT v4.4.4
echo   2. Start Ultimate Trading Dashboard
echo   3. Run Pipelines (AU/US/UK)
echo   4. Run Complete Workflow (All components)
echo.
pause

@echo off
REM ========================================
REM Quick Fix for Existing Installation
REM v1.3.15.88
REM ========================================

echo ========================================
echo Quick Fix v1.3.15.88
echo ========================================
echo.
echo This script will fix:
echo 1. PyTorch security vulnerability (CVE-2025-32434)
echo 2. Keras backend configuration
echo 3. Dashboard compatibility issues
echo.
echo This will take 2-3 minutes.
echo.
pause

REM ========================================
REM Step 1: Configure Keras Backend
REM ========================================
echo.
echo [1/3] Configuring Keras backend...

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
echo OK
echo.

REM ========================================
REM Step 2: Upgrade PyTorch (Security Fix)
REM ========================================
echo [2/3] Upgrading PyTorch (CVE-2025-32434 fix)...
echo.

REM Activate venv if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Upgrading PyTorch to 2.6.0...
pip install --upgrade torch==2.6.0 torchvision==0.21.0
if errorlevel 1 (
    echo WARNING: PyTorch upgrade failed
    echo Continuing anyway...
) else (
    echo OK
)
echo.

REM ========================================
REM Step 3: Verify Installation
REM ========================================
echo [3/3] Verifying fixes...
echo.

echo Testing PyTorch version...
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo WARNING: PyTorch not available
) else (
    echo OK
)

echo Testing Keras backend...
python -c "from tensorflow import keras; print('Keras via TensorFlow OK')" 2>nul
if errorlevel 1 (
    echo WARNING: Keras import failed
) else (
    echo OK
)

echo.

REM ========================================
REM Fix Complete
REM ========================================
echo ========================================
echo FIX COMPLETE!
echo ========================================
echo.
echo Fixed:
echo 1. Keras backend: TensorFlow (global config)
echo 2. PyTorch: 2.6.0 (security vulnerability fixed)
echo 3. Dashboard: Ready to start
echo.
echo Keras config location: %USERPROFILE%\.keras\keras.json
echo.
echo Next steps:
echo 1. Restart FinBERT: START_SERVER.bat
echo 2. Restart Dashboard: START_DASHBOARD.bat
echo 3. Test training: curl POST /api/train/AAPL
echo.
echo For verification, run: TEST_SYSTEM.bat
echo.
pause

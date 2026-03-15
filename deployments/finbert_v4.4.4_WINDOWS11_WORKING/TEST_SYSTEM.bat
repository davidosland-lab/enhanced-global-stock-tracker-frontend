@echo off
echo ========================================
echo FinBERT v4.4.4 - System Test
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/5] Testing Python Installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo OK
echo.

echo [2/5] Testing TensorFlow...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
if errorlevel 1 (
    echo ERROR: TensorFlow import failed!
    pause
    exit /b 1
)
echo OK
echo.

echo [3/5] Testing PyTorch...
python -c "import torch; print('PyTorch:', torch.__version__)"
if errorlevel 1 (
    echo ERROR: PyTorch import failed!
    pause
    exit /b 1
)
echo OK
echo.

echo [4/5] Testing Transformers (FinBERT)...
python -c "import transformers; print('Transformers:', transformers.__version__)"
if errorlevel 1 (
    echo ERROR: Transformers import failed!
    pause
    exit /b 1
)
echo OK
echo.

echo [5/5] Testing Keras Backend...
python -c "import tensorflow as tf; from tensorflow import keras; print('Keras via TensorFlow:', keras.__version__)"
if errorlevel 1 (
    echo ERROR: Keras import failed!
    pause
    exit /b 1
)
echo OK
echo.

echo ========================================
echo ALL TESTS PASSED!
echo ========================================
echo.
echo System is ready for use!
echo.
echo Next steps:
echo 1. Run START_SERVER.bat
echo 2. Open http://localhost:5001
echo 3. Train your first model (AAPL recommended)
echo.
pause

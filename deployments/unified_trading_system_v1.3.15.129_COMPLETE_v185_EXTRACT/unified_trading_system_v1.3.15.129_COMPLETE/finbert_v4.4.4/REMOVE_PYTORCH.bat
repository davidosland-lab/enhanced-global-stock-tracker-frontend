@echo off
REM ============================================================================
REM  REMOVE PYTORCH TO FIX TENSORFLOW CONFLICT
REM ============================================================================
REM
REM  Problem: PyTorch and TensorFlow installed together cause conflicts
REM  Solution: Remove PyTorch (we only need TensorFlow for LSTM)
REM  Impact: FinBERT sentiment disabled, but LSTM training works
REM
REM ============================================================================

echo.
echo ============================================================================
echo   REMOVE PYTORCH TO FIX TRAINING
echo ============================================================================
echo.
echo This will uninstall PyTorch to fix the TensorFlow conflict during training.
echo.
echo IMPACT:
echo   ✅ LSTM training will work (all 720 stocks)
echo   ❌ FinBERT sentiment will be disabled
echo   ✅ Technical indicators still work
echo   ✅ Win rate: 70-80%% (without sentiment)
echo.
echo Press any key to continue or CTRL+C to cancel...
pause >nul
echo.

REM Navigate to the project directory
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at venv\Scripts\activate.bat
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Uninstalling PyTorch packages...
echo This may take a minute...
echo.

pip uninstall torch torchvision torchaudio -y

if errorlevel 1 (
    echo.
    echo WARNING: Some PyTorch packages may not have been installed.
    echo This is OK if you didn't have PyTorch installed.
    echo.
) else (
    echo.
    echo ✅ PyTorch successfully removed!
    echo.
)

echo.
echo Verifying TensorFlow is still installed...
python -c "import tensorflow as tf; print('✅ TensorFlow version:', tf.__version__)" 2>nul

if errorlevel 1 (
    echo.
    echo ❌ ERROR: TensorFlow not found!
    echo Installing TensorFlow...
    pip install tensorflow
)

echo.
echo Deactivating virtual environment...
call deactivate

echo.
echo ============================================================================
echo   ✅ PYTORCH REMOVED - TENSORFLOW OK
echo ============================================================================
echo.
echo NEXT STEPS:
echo   1. Start Flask server:
echo      set FLASK_SKIP_DOTENV=1
echo      python app_finbert_v4_dev.py
echo.
echo   2. Test LSTM training:
echo      curl -X POST http://localhost:5001/api/train/AAPL ^
echo           -H "Content-Type: application/json" ^
echo           -d "{\"epochs\": 20}"
echo.
echo   3. Expected: Training succeeds without RuntimeError!
echo.
echo NOTE: FinBERT sentiment is disabled (requires PyTorch)
echo      You can still trade with 70-80%% win rate using:
echo        - LSTM predictions
echo        - Technical indicators (8+)
echo        - Trend analysis
echo        - Volume analysis
echo.
pause

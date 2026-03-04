@echo off
REM ============================================================================
REM  FinBERT v4.4.4 - Windows 11 Installation Script
REM  Python 3.12 Compatible - Tested February 2026
REM ============================================================================

echo.
echo ============================================================================
echo   FinBERT v4.4.4 Installation for Windows 11
echo ============================================================================
echo.
echo This will install FinBERT v4.4.4 with:
echo   - TensorFlow 2.16.1 (LSTM training)
echo   - PyTorch 2.2.0 (FinBERT sentiment)
echo   - All required dependencies
echo.
echo Requirements:
echo   - Python 3.12 (must be in PATH)
echo   - Internet connection
echo.
pause

echo.
echo ============================================================================
echo   Step 1: Checking Python version
echo ============================================================================
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.12 and add to PATH
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   Step 2: Upgrading pip
echo ============================================================================
python -m pip install --upgrade pip

echo.
echo ============================================================================
echo   Step 3: Installing dependencies
echo ============================================================================
echo This may take 5-10 minutes...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   ERROR: Installation failed
    echo ============================================================================
    echo.
    echo Please check the error messages above and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   Step 4: Configuring Keras backend
echo ============================================================================
echo Creating Keras configuration...

if not exist "%USERPROFILE%\.keras" mkdir "%USERPROFILE%\.keras"
copy /Y keras.json "%USERPROFILE%\.keras\keras.json" >nul

echo ✓ Keras configured to use TensorFlow backend

echo.
echo ============================================================================
echo   Step 5: Creating directories
echo ============================================================================

if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "logs\screening" mkdir logs\screening
if not exist "logs\screening\us" mkdir "logs\screening\us"
if not exist "logs\screening\au" mkdir "logs\screening\au"
if not exist "logs\screening\uk" mkdir "logs\screening\uk"
if not exist "reports" mkdir reports
if not exist "data" mkdir data

echo ✓ Directories created

echo.
echo ============================================================================
echo   Step 6: Verifying installation
echo ============================================================================

python -c "import tensorflow as tf; print('✓ TensorFlow:', tf.__version__)"
python -c "import torch; print('✓ PyTorch:', torch.__version__)"
python -c "import transformers; print('✓ Transformers:', transformers.__version__)"
python -c "import flask; print('✓ Flask:', flask.__version__)"

echo.
echo ============================================================================
echo   ✅ INSTALLATION COMPLETE!
echo ============================================================================
echo.
echo Next steps:
echo   1. Run START_SERVER.bat to start the Flask server
echo   2. Open http://localhost:5001 in your browser
echo   3. Train your first LSTM model for a stock (e.g., AAPL)
echo.
echo To train a model:
echo   - Web UI: Open http://localhost:5001, enter symbol, click Train
echo   - Command line: python models\train_lstm.py --symbol AAPL --epochs 50
echo.
echo Documentation:
echo   - README.md - Quick start guide
echo   - TRAINING_GUIDE.md - LSTM training instructions
echo.
pause

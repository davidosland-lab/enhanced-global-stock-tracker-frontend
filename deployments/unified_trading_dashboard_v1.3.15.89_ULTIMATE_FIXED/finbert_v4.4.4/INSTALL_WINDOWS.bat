@echo off
REM ========================================
REM FinBERT v4.4.4 - Windows Installation
REM Fixed for Windows 11 (No Build Tools)
REM ========================================

echo ============================================================================
echo   FinBERT v4.4.4 Installation for Windows 11 (FIXED)
echo ============================================================================
echo.
echo This will install FinBERT v4.4.4 with:
echo   - TensorFlow 2.16.1 (LSTM training)
echo   - PyTorch 2.6.0 (FinBERT sentiment - SECURITY FIX)
echo   - Pre-built packages (NO build tools required)
echo.
echo Requirements:
echo   - Python 3.12 (must be in PATH)
echo   - Internet connection
echo.
pause

REM ========================================
REM Step 1: Check Python
REM ========================================
echo.
echo ============================================================================
echo   Step 1: Checking Python version
echo ============================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.12 from python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo.

REM ========================================
REM Step 2: Upgrade pip
REM ========================================
echo ============================================================================
echo   Step 2: Upgrading pip
echo ============================================================================
python -m pip install --upgrade pip
echo.

REM ========================================
REM Step 3: Install packages with pre-built wheels
REM ========================================
echo ============================================================================
echo   Step 3: Installing dependencies (pre-built packages)
echo ============================================================================
echo This may take 5-10 minutes...
echo.

REM Install packages that have pre-built wheels
echo Installing core packages...
pip install Flask==3.0.0 Flask-CORS==4.0.0 Werkzeug==3.0.0 python-dotenv==1.0.0
if errorlevel 1 (
    echo WARNING: Some core packages failed to install
)
echo.

echo Installing data processing packages...
pip install "numpy>=1.26.0" "pandas>=2.2.0" python-dateutil==2.8.2
if errorlevel 1 (
    echo WARNING: Some data packages failed to install
)
echo.

echo Installing market data and web scraping...
pip install "yfinance>=0.2.28" "beautifulsoup4>=4.12.0" "lxml>=4.9.0" "aiohttp>=3.9.0" "requests>=2.31.0"
if errorlevel 1 (
    echo WARNING: Some web packages failed to install
)
echo.

echo Installing TensorFlow...
pip install tensorflow==2.16.1
if errorlevel 1 (
    echo ERROR: TensorFlow installation failed
    echo This is critical - please check your internet connection
    pause
    exit /b 1
)
echo.

echo Installing PyTorch (SECURITY FIX: 2.6.0)...
pip install "torch>=2.6.0" "torchvision>=0.21.0"
if errorlevel 1 (
    echo ERROR: PyTorch installation failed
    echo Trying alternative installation method...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
)
echo.

echo Installing transformers and ML utilities...
pip install "transformers>=4.36.0" "sentencepiece>=0.1.99" "scikit-learn>=1.3.0"
if errorlevel 1 (
    echo WARNING: Some ML packages failed to install
)
echo.

echo Installing API utilities...
pip install "urllib3>=1.26.0,<2.0.0" "websockets>=11.0.0" "python-multipart>=0.0.9"
echo.

REM ========================================
REM Step 4: Configure Keras Backend
REM ========================================
echo ============================================================================
echo   Step 4: Configuring Keras backend (TensorFlow)
echo ============================================================================

if not exist "%USERPROFILE%\.keras" (
    mkdir "%USERPROFILE%\.keras"
)

echo { > "%USERPROFILE%\.keras\keras.json"
echo   "backend": "tensorflow", >> "%USERPROFILE%\.keras\keras.json"
echo   "floatx": "float32", >> "%USERPROFILE%\.keras\keras.json"
echo   "epsilon": 1e-07, >> "%USERPROFILE%\.keras\keras.json"
echo   "image_data_format": "channels_last" >> "%USERPROFILE%\.keras\keras.json"
echo } >> "%USERPROFILE%\.keras\keras.json"

echo Keras config created at: %USERPROFILE%\.keras\keras.json
echo.

REM ========================================
REM Step 5: Create directories
REM ========================================
echo ============================================================================
echo   Step 5: Creating directories
echo ============================================================================
if not exist logs mkdir logs
if not exist data mkdir data
if not exist models mkdir models
echo Directories created.
echo.

REM ========================================
REM Step 6: Verify Installation
REM ========================================
echo ============================================================================
echo   Step 6: Verifying installation
echo ============================================================================
echo.

echo Testing TensorFlow...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: TensorFlow import failed!
    set INSTALL_ERROR=1
) else (
    echo OK
)

echo Testing PyTorch...
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: PyTorch import failed!
    set INSTALL_ERROR=1
) else (
    echo OK
)

echo Testing Transformers...
python -c "import transformers; print('Transformers:', transformers.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: Transformers import failed!
    set INSTALL_ERROR=1
) else (
    echo OK
)

echo Testing Keras...
python -c "from tensorflow import keras; print('Keras via TensorFlow OK')" 2>nul
if errorlevel 1 (
    echo ERROR: Keras import failed!
    set INSTALL_ERROR=1
) else (
    echo OK
)

echo.

REM ========================================
REM Installation Complete
REM ========================================
if defined INSTALL_ERROR (
    echo ============================================================================
    echo   WARNING: Installation completed with errors
    echo ============================================================================
    echo.
    echo Some packages failed to install. Please check the errors above.
    echo.
    echo Common issues:
    echo   1. Internet connection problems
    echo   2. Python not properly added to PATH
    echo   3. Antivirus blocking downloads
    echo.
    echo You can try running this script again.
    echo.
) else (
    echo ============================================================================
    echo   Installation complete!
    echo ============================================================================
    echo.
    echo Keras Backend: TensorFlow (configured globally)
    echo Config Location: %USERPROFILE%\.keras\keras.json
    echo.
    echo Next steps:
    echo   1. Run START_SERVER.bat to start FinBERT
    echo   2. Open http://localhost:5001 in your browser
    echo   3. Train your first model (AAPL recommended)
    echo.
    echo For training:
    echo   - Web UI: http://localhost:5001
    echo   - Command: curl -X POST http://localhost:5001/api/train/AAPL
    echo.
)

pause

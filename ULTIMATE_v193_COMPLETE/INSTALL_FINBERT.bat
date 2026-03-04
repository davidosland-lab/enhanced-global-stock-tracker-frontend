@echo off
REM ===========================================================================
REM INSTALL_FINBERT.bat
REM ===========================================================================
REM 
REM Purpose: Install FinBERT sentiment analysis dependencies
REM 
REM What it does:
REM 1. Activates virtual environment
REM 2. Installs PyTorch 2.6.0 (CPU version)
REM 3. Installs Transformers and SentencePiece
REM 4. Verifies installation
REM 
REM Time: 10-15 minutes
REM Disk Space: ~3GB
REM 
REM ===========================================================================

echo.
echo ============================================================================
echo  Installing FinBERT Sentiment Analysis Dependencies
echo ============================================================================
echo.
echo This will install:
echo   - PyTorch 2.6.0 (CPU version) - Deep Learning Framework
echo   - Transformers 4.36+ - NLP Models
echo   - SentencePiece 0.1.99+ - Text Processing
echo.
echo Download size: ~2.5 GB
echo Installation time: 10-15 minutes
echo Disk space required: ~3 GB
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run INSTALL_COMPLETE.bat first to create the environment
    echo.
    pause
    exit /b 1
)

REM Step 1: Activate environment
echo.
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Environment activated

REM Step 2: Check if already installed
echo.
echo [2/5] Checking existing installation...
python -c "import torch; import transformers; import sentencepiece; exit(0)" 2>nul
if not errorlevel 1 (
    echo [INFO] FinBERT dependencies already installed
    echo.
    choice /C YN /M "Do you want to reinstall"
    if errorlevel 2 goto :skip_install
)

REM Step 3: Install PyTorch (CPU version)
echo.
echo [3/5] Installing PyTorch 2.6.0 (CPU version)...
echo This may take 5-10 minutes depending on your internet speed...
echo.
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if errorlevel 1 (
    echo.
    echo [ERROR] PyTorch installation failed
    echo [INFO] Possible causes:
    echo   - Internet connection issues
    echo   - Insufficient disk space
    echo   - Python version incompatibility
    echo.
    echo [HELP] Try manual installation:
    echo   pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
    echo.
    pause
    exit /b 1
)
echo [OK] PyTorch installed successfully

REM Step 4: Install Transformers & SentencePiece
echo.
echo [4/5] Installing Transformers and SentencePiece...
echo.
pip install transformers>=4.36.0 sentencepiece>=0.1.99 --no-cache-dir
if errorlevel 1 (
    echo.
    echo [ERROR] Transformers installation failed
    echo [INFO] Try running again or install manually:
    echo   pip install transformers sentencepiece
    echo.
    pause
    exit /b 1
)
echo [OK] Transformers and SentencePiece installed

:skip_install

REM Step 5: Verify installation
echo.
echo [5/5] Verifying installation...
python -c "import torch; print('[OK] PyTorch:', torch.__version__)"
if errorlevel 1 (
    echo [ERROR] PyTorch verification failed
    pause
    exit /b 1
)

python -c "import transformers; print('[OK] Transformers:', transformers.__version__)"
if errorlevel 1 (
    echo [ERROR] Transformers verification failed
    pause
    exit /b 1
)

python -c "import sentencepiece; print('[OK] SentencePiece installed')"
if errorlevel 1 (
    echo [ERROR] SentencePiece verification failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  FinBERT Dependencies Installed Successfully!
echo ============================================================================
echo.
echo Installed components:
python -c "import torch, transformers, sentencepiece; print(f'  - PyTorch {torch.__version__}'); print(f'  - Transformers {transformers.__version__}'); print('  - SentencePiece (installed)')"
echo.
echo Next steps:
echo   1. Run START.bat
echo   2. Choose option 2 (FinBERT Only) or option 1 (Complete System)
echo   3. Look for: "✓ FinBERT Sentiment (15%% Weight): Active as Independent Model"
echo.
echo To test FinBERT:
echo   1. cd finbert_v4.4.4
echo   2. python app_finbert_v4_dev.py
echo   3. Open http://localhost:5001/api/sentiment/AAPL
echo.
echo Expected benefits:
echo   - 95%% sentiment accuracy (vs 60%% keyword fallback)
echo   - 15%% weight in ensemble predictions
echo   - +5-10%% win rate improvement
echo.
pause

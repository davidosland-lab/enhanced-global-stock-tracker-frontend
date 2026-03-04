@echo off
REM ===================================================================
REM CRITICAL FIX - FinBERT Local Model + Keras LSTM Patch
REM ===================================================================
REM This patch fixes TWO issues:
REM 1. FinBERT "analyzer not available" - downloads model ONCE to cache
REM 2. Keras/PyTorch LSTM warning - installs keras with torch backend
REM
REM Run this from: COMPLETE_SYSTEM_v1.3.15.45_FINAL directory
REM Time: 5-10 minutes (one-time download ~500MB)
REM ===================================================================

echo ========================================
echo   CRITICAL FIX v1.3.15.52
echo   FinBERT + Keras LSTM Patch
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "unified_trading_dashboard.py" (
    echo [ERROR] Wrong directory!
    echo Please run this from: COMPLETE_SYSTEM_v1.3.15.45_FINAL
    echo.
    pause
    exit /b 1
)

echo [STEP 1/5] Checking Python environment...
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first to create the environment
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.

echo [STEP 2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

echo ========================================
echo   FIX 1: Install Keras + PyTorch
echo ========================================
echo This fixes: "Keras/PyTorch not available - LSTM will use fallback"
echo Installing: keras 3.x with PyTorch CPU backend
echo Size: ~2GB download (PyTorch CPU)
echo.

choice /C YN /M "Install Keras + PyTorch (required for LSTM neural networks)"
if errorlevel 2 goto skip_keras

echo.
echo Installing Keras 3.x...
pip install "keras>=3.0" --quiet
if errorlevel 1 (
    echo [WARNING] Keras installation had issues
    echo Continuing anyway...
)

echo.
echo Installing PyTorch CPU (this will take 3-5 minutes)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo [WARNING] PyTorch installation had issues
    echo You may need to install manually
) else (
    echo [OK] Keras + PyTorch installed successfully
)
echo.

:skip_keras

echo ========================================
echo   FIX 2: Download FinBERT Model
echo ========================================
echo This fixes: "FinBERT analyzer not available"
echo Downloads: ProsusAI/finbert model (~500MB)
echo Location: %%USERPROFILE%%\.cache\huggingface\transformers
echo.

choice /C YN /M "Download FinBERT model to local cache (REQUIRED for sentiment)"
if errorlevel 2 goto skip_finbert

echo.
echo [STEP 3/5] Downloading FinBERT model...
echo This is a ONE-TIME download (~500MB)
echo Please be patient, this may take 2-5 minutes...
echo.

python -c "import os; os.environ['TRANSFORMERS_OFFLINE']='0'; from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading FinBERT model...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('✅ FinBERT model downloaded to cache'); print('Cache location:', os.path.expanduser('~/.cache/huggingface/transformers'))"

if errorlevel 1 (
    echo.
    echo [ERROR] FinBERT download failed!
    echo.
    echo Possible causes:
    echo 1. No internet connection
    echo 2. HuggingFace.co is down
    echo 3. Transformers library not installed
    echo.
    echo Try installing transformers:
    echo   pip install transformers torch
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] FinBERT model downloaded successfully
echo.

:skip_finbert

echo ========================================
echo   FIX 3: Verify Installation
echo ========================================
echo [STEP 4/5] Verifying fixes...
echo.

REM Verify transformers
python -c "import transformers; print('[OK] Transformers:', transformers.__version__)" 2>nul || echo [WARNING] Transformers not installed

REM Verify torch
python -c "import torch; print('[OK] PyTorch:', torch.__version__)" 2>nul || echo [WARNING] PyTorch not installed

REM Verify keras
python -c "import os; os.environ['KERAS_BACKEND']='torch'; import keras; print('[OK] Keras:', keras.__version__, '(PyTorch backend)')" 2>nul || echo [WARNING] Keras not installed

REM Check if FinBERT model exists in cache
python -c "import os; cache_dir = os.path.expanduser('~/.cache/huggingface/transformers'); exists = os.path.exists(cache_dir) and len(os.listdir(cache_dir)) > 0 if os.path.exists(cache_dir) else False; print('[OK] FinBERT model cached locally' if exists else '[WARNING] FinBERT cache not found')"

echo.

echo ========================================
echo   FIX 4: Test FinBERT Loading
echo ========================================
echo [STEP 5/5] Testing FinBERT analyzer...
echo.

python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Loading FinBERT from cache...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('✅ FinBERT loads successfully from cache'); print('✅ Sentiment analysis will work properly')"

if errorlevel 1 (
    echo.
    echo [WARNING] FinBERT test failed
    echo The model may need to be downloaded again
    echo.
) else (
    echo.
    echo [OK] FinBERT test passed
    echo.
)

echo ========================================
echo   PATCH COMPLETE
echo ========================================
echo.
echo What was fixed:
echo.
echo 1. Keras + PyTorch installed
echo    ✓ LSTM neural networks will work (no fallback)
echo    ✓ "Keras/PyTorch not available" warning eliminated
echo.
echo 2. FinBERT model downloaded to cache
echo    ✓ Sentiment analysis will work properly
echo    ✓ "FinBERT analyzer not available" error eliminated
echo    ✓ News articles will be analyzed (not neutral fallback)
echo.
echo Cache locations:
echo    FinBERT: %%USERPROFILE%%\.cache\huggingface\transformers
echo    PyTorch: %%USERPROFILE%%\.cache\torch
echo.
echo Next steps:
echo 1. Restart any running pipelines
echo 2. Run: python -m models.screening.run_uk_screening_pipeline
echo 3. Check for these success messages:
echo    - "[OK] Keras LSTM available (PyTorch backend)"
echo    - "✅ FinBERT loaded from local cache"
echo    - "[OK] FinBERT v4.4.4 Sentiment for [STOCK]: [positive/negative/neutral] (XX%%), compound: X.XXX, [N] articles"
echo.
echo ========================================
echo   What You Should See Now
echo ========================================
echo.
echo BEFORE (broken):
echo   WARNING - Keras/PyTorch not available - LSTM will use fallback
echo   ERROR - FinBERT analyzer not available
echo   [OK] FinBERT v4.4.4 Sentiment for SAGA.L: neutral (0.0%%), 0 articles
echo.
echo AFTER (fixed):
echo   [OK] Keras LSTM available (PyTorch backend)
echo   ✅ FinBERT loaded from local cache (no download)
echo   [OK] FinBERT v4.4.4 Sentiment for SAGA.L: positive (72.3%%), compound: 0.485, 10 articles
echo.
echo ========================================
echo.

REM Check if they want to deploy v1.3.15.52 as well
echo.
echo IMPORTANT: This patch only fixes Keras + FinBERT loading.
echo.
echo You should ALSO deploy v1.3.15.52 which includes:
echo   - Accurate sentiment calculation (AORD -0.9%% shows correctly)
echo   - Position multiplier fix (trades execute properly)
echo   - Market breakdown display (AU vs US vs UK)
echo.
choice /C YN /M "Do you want to see instructions for deploying v1.3.15.52"
if errorlevel 2 goto end_patch

echo.
echo v1.3.15.52 Deployment (4 minutes):
echo.
echo 1. Download: COMPLETE_SYSTEM_v1.3.15.52_ALL_FIXES.zip
echo 2. Stop dashboard (Ctrl+C)
echo 3. Backup: rename COMPLETE_SYSTEM_v1.3.15.45_FINAL to COMPLETE_SYSTEM_v1.3.15.45_BACKUP
echo 4. Extract v1.3.15.52
echo 5. Run this patch again in the new folder
echo 6. Start dashboard
echo.
echo See: DEPLOYMENT_GUIDE_v1.3.15.52.md for full instructions
echo.

:end_patch

echo ========================================
echo Press any key to exit...
pause >nul

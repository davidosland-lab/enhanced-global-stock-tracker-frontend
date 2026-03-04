@echo off
REM ============================================================================
REM DOWNLOAD FINBERT LOCAL - ONE-TIME SETUP (IMPROVED)
REM ============================================================================
REM This script downloads FinBERT model once to local cache AND configures
REM the system to use OFFLINE MODE (no HuggingFace checks on every load)
REM 
REM Expected: 500MB download, 2-3 minutes first time
REM After: Instant startup (10-15 seconds), full FinBERT accuracy, NO NETWORK CALLS
REM ============================================================================

echo.
echo ============================================================================
echo DOWNLOADING FINBERT MODEL TO LOCAL CACHE + OFFLINE MODE SETUP
echo ============================================================================
echo.
echo This will:
echo   1. Download FinBERT (~500MB) ONCE to your local cache
echo   2. Configure system for OFFLINE MODE (no HuggingFace checks)
echo   3. Set environment variables for instant loading
echo.
echo Expected time: 2-3 minutes (one-time only)
echo Future runs: Instant load, NO network calls
echo.
pause

echo.
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure you're running this from COMPLETE_SYSTEM_v1.3.15.45_FINAL directory
    pause
    exit /b 1
)

echo.
echo [2/5] Installing required dependencies...
pip install --quiet transformers>=4.30.0 torch>=2.0.0
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection
    pause
    exit /b 1
)

echo.
echo [3/5] Downloading FinBERT model to local cache...
echo This may take 2-3 minutes...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading FinBERT...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('SUCCESS: FinBERT downloaded to cache')"
if errorlevel 1 (
    echo ERROR: Failed to download FinBERT
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo [4/5] Setting environment variables for OFFLINE MODE...
REM Set for current session
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1
echo Current session: TRANSFORMERS_OFFLINE=1
echo Current session: HF_HUB_OFFLINE=1

REM Set permanently for user
setx TRANSFORMERS_OFFLINE 1 >nul 2>&1
setx HF_HUB_OFFLINE 1 >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not set permanent environment variables
    echo System will still work but may check HuggingFace on each load
) else (
    echo Permanent: TRANSFORMERS_OFFLINE=1
    echo Permanent: HF_HUB_OFFLINE=1
)

echo.
echo [5/5] Verifying FinBERT installation in OFFLINE MODE...
python -c "import os; os.environ['TRANSFORMERS_OFFLINE']='1'; os.environ['HF_HUB_OFFLINE']='1'; from transformers import AutoTokenizer, AutoModelForSequenceClassification; import torch; print('Loading in OFFLINE MODE...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert', local_files_only=True); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert', local_files_only=True); model.eval(); inputs = tokenizer('Test', return_tensors='pt', max_length=512, truncation=True, padding=True); with torch.no_grad(): outputs = model(**inputs); print('SUCCESS: FinBERT works in OFFLINE MODE (no network calls)')"
if errorlevel 1 (
    echo ERROR: FinBERT verification failed
    echo It may still work online but not in offline mode
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS: FINBERT INSTALLED + OFFLINE MODE CONFIGURED
echo ============================================================================
echo.
echo FinBERT is now cached locally and configured for OFFLINE MODE.
echo.
echo What changed:
echo   - FinBERT model downloaded to: %%USERPROFILE%%\.cache\huggingface
echo   - Environment variables set: TRANSFORMERS_OFFLINE=1, HF_HUB_OFFLINE=1
echo   - No more HuggingFace network checks on startup
echo.
echo Expected behavior:
echo   - First dashboard start: 10-15 seconds (loads from cache)
echo   - No httpx requests to huggingface.co in console
echo   - Full FinBERT accuracy (95%%)
echo.
echo NOTE: You must RESTART your command prompt for environment variables to take effect.
echo      Or the dashboard will automatically use offline mode if run from this window.
echo.
echo Next steps:
echo   1. Close this window and open a NEW command prompt (for env vars)
echo   2. Run INSTALL_KERAS_LSTM.bat (optional - for LSTM predictions)
echo   3. Start the dashboard normally
echo   4. Verify NO httpx requests appear in console
echo.
pause

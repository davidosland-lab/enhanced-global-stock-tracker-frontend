@echo off
REM ============================================================================
REM DOWNLOAD FINBERT LOCAL - ONE-TIME SETUP
REM ============================================================================
REM This script downloads FinBERT model once to local cache
REM Future runs will use the cached model (no more downloads)
REM 
REM Expected: 500MB download, 2-3 minutes first time
REM After: Instant startup, full FinBERT accuracy
REM ============================================================================

echo.
echo ============================================================================
echo DOWNLOADING FINBERT MODEL TO LOCAL CACHE
echo ============================================================================
echo.
echo This will download FinBERT (~500MB) ONCE to your local cache.
echo Future runs will load instantly from cache.
echo.
echo Expected time: 2-3 minutes (one-time only)
echo.
pause

echo.
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure you're running this from COMPLETE_SYSTEM_v1.3.15.45_FINAL directory
    pause
    exit /b 1
)

echo.
echo [2/4] Installing required dependencies...
pip install --quiet transformers>=4.30.0 torch>=2.0.0
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection
    pause
    exit /b 1
)

echo.
echo [3/4] Downloading FinBERT model to local cache...
echo This may take 2-3 minutes...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading FinBERT...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('SUCCESS: FinBERT downloaded to cache')"
if errorlevel 1 (
    echo ERROR: Failed to download FinBERT
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying FinBERT installation...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; import torch; tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); model.eval(); inputs = tokenizer('Test', return_tensors='pt', max_length=512, truncation=True, padding=True); with torch.no_grad(): outputs = model(**inputs); print('SUCCESS: FinBERT is working correctly')"
if errorlevel 1 (
    echo ERROR: FinBERT verification failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS: FINBERT DOWNLOADED AND VERIFIED
echo ============================================================================
echo.
echo FinBERT is now cached locally and ready to use.
echo Future dashboard starts will load FinBERT instantly from cache.
echo.
echo Next steps:
echo   1. Run INSTALL_KERAS_LSTM.bat (optional - for LSTM predictions)
echo   2. Start the dashboard normally
echo   3. FinBERT will load in 10-15 seconds from cache
echo.
pause

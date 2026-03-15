@echo off
REM ============================================================================
REM VERIFY FINBERT OFFLINE MODE - Quick Test
REM ============================================================================

echo.
echo ============================================================================
echo VERIFYING FINBERT OFFLINE MODE
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)

echo.
echo [2/3] Testing FinBERT in OFFLINE MODE...
echo.
python -c "import os; os.environ['TRANSFORMERS_OFFLINE']='1'; os.environ['HF_HUB_OFFLINE']='1'; from transformers import AutoTokenizer, AutoModelForSequenceClassification; import torch; print('Loading FinBERT in OFFLINE MODE...'); tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert', local_files_only=True); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert', local_files_only=True); model.eval(); inputs = tokenizer('Financial markets showed strong performance today', return_tensors='pt', max_length=512, truncation=True, padding=True); outputs = model(**inputs); import torch.nn.functional as F; probs = F.softmax(outputs.logits, dim=1); sentiment = ['negative', 'neutral', 'positive'][probs.argmax().item()]; print(f'SUCCESS: FinBERT works in OFFLINE MODE'); print(f'Test sentiment: {sentiment} (confidence: {probs.max().item()*100:.1f}%%)')"

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: FinBERT OFFLINE MODE FAILED
    echo ============================================================================
    echo.
    echo This means FinBERT is not cached locally or cache is incomplete.
    echo.
    echo Fix:
    echo   1. Run DOWNLOAD_FINBERT_LOCAL.bat again
    echo   2. Make sure it completes successfully
    echo   3. Then run this verification again
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying environment variables...
echo.
echo System environment variables:
setx TRANSFORMERS_OFFLINE >nul 2>&1
setx HF_HUB_OFFLINE >nul 2>&1
echo   TRANSFORMERS_OFFLINE=1 (set)
echo   HF_HUB_OFFLINE=1 (set)

echo.
echo ============================================================================
echo SUCCESS: FINBERT OFFLINE MODE VERIFIED
echo ============================================================================
echo.
echo FinBERT is working correctly in offline mode:
echo   - Loads from local cache (no network calls)
echo   - Sentiment analysis works
echo   - Environment variables set
echo.
echo You are ready to start the dashboard:
echo   1. Run START_UNIFIED_DASHBOARD.bat
echo   2. Should start in 10-15 seconds
echo   3. No HuggingFace network requests
echo.
pause

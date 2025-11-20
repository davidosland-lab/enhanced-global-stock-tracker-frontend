@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo FINBERT SENTIMENT ANALYSIS TEST
echo ================================================================
echo.
echo This will test FinBERT sentiment analyzer and show which mode
echo it's using (FinBERT transformer model or keyword fallback).
echo.
echo ================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
echo.

echo [2/3] Checking transformers library (required for FinBERT)...
python -c "import transformers; print(f'✓ transformers version: {transformers.__version__}')" 2>nul
if errorlevel 1 (
    echo [WARNING] transformers library NOT installed
    echo.
    echo FinBERT will use FALLBACK MODE ^(keyword-based analysis^)
    echo.
    echo To enable full FinBERT transformer model:
    echo   pip install transformers torch
    echo.
) else (
    echo ✓ transformers library installed
    echo.
)
echo.

echo [3/3] Testing FinBERT analyzer...
echo.

python -c "
import sys
sys.path.insert(0, 'models')

print('Loading FinBERT analyzer...')
from finbert_sentiment import finbert_analyzer

print(f'✓ Analyzer loaded')
print(f'  - Model loaded: {finbert_analyzer.is_loaded}')
print(f'  - Using fallback: {finbert_analyzer.use_fallback}')
print(f'  - Model name: {finbert_analyzer.model_name}')
print()

# Test with sample financial news
test_texts = [
    'Company reports strong profit growth with record revenue',
    'Stock price crashes amid weak earnings report',
    'Company announces dividend payment'
]

print('Testing sentiment analysis:')
print('=' * 60)

for i, text in enumerate(test_texts, 1):
    print(f'{i}. Text: {text[:50]}...')
    result = finbert_analyzer.analyze_text(text)
    print(f'   Sentiment: {result[\"sentiment\"]}')
    print(f'   Confidence: {result[\"confidence\"]:.1f}%%')
    print(f'   Compound: {result[\"compound\"]:.3f}')
    print(f'   Method: {result[\"method\"]}')
    print()

print('=' * 60)
print()

if finbert_analyzer.is_loaded:
    print('✅ FinBERT TRANSFORMER MODEL is working!')
    print('   Using ProsusAI/finbert neural network model')
else:
    print('⚠ FinBERT FALLBACK MODE active')
    print('   Using keyword-based sentiment analysis')
    print()
    print('Fallback mode works but is less accurate than transformer model.')
    print('To enable transformer model, install: pip install transformers torch')
"

if errorlevel 1 (
    echo.
    echo [ERROR] FinBERT test failed
    echo Check that models/finbert_sentiment.py exists
) else (
    echo.
    echo [SUCCESS] FinBERT test completed
)

echo.
echo ================================================================
echo Press any key to close...
pause >nul

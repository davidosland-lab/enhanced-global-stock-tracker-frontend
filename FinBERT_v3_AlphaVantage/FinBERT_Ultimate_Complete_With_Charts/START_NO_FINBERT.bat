@echo off
echo ================================================================================
echo STARTING WITHOUT FINBERT (Uses fallback sentiment)
echo ================================================================================
echo.

REM Set environment to disable FinBERT
SET USE_FINBERT=0
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8
SET TRANSFORMERS_OFFLINE=1

echo Starting server without FinBERT...
echo This will use keyword-based sentiment analysis instead.
echo.

REM Create a temporary Python wrapper that disables FinBERT
echo import os > temp_start.py
echo os.environ['USE_FINBERT'] = '0' >> temp_start.py
echo FINBERT_AVAILABLE = False >> temp_start.py
echo import app_finbert_ultimate_original_with_key >> temp_start.py

python temp_start.py

del temp_start.py
pause
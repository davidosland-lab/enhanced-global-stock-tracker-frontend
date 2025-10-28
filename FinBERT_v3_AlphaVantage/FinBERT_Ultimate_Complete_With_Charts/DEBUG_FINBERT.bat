@echo off
echo ================================================================================
echo DEBUGGING FINBERT STARTUP
echo ================================================================================
echo.

SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8

echo Running with full error output...
echo.

python -u app_finbert_ultimate_original_with_key.py 2>&1

echo.
echo ================================================================================
echo If the server failed, the error is shown above.
echo ================================================================================
pause
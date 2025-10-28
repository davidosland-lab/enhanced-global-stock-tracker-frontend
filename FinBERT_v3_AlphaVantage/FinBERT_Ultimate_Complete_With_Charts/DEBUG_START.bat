@echo off
echo ================================================================================
echo DIAGNOSTIC START FOR FINBERT v3.0
echo ================================================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking required packages...
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
python -c "import pandas; print(f'pandas: {pandas.__version__}')"
python -c "import yfinance; print(f'yfinance: {yfinance.__version__}')"
python -c "import flask; print(f'flask: {flask.__version__}')"
python -c "import sklearn; print(f'sklearn: {sklearn.__version__}')"

echo.
echo Checking for .env file issues...
if exist ".env" (
    echo Found .env file - removing it...
    del /f /q ".env"
)

echo.
echo Setting environment variables...
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8
SET PYTHONDONTWRITEBYTECODE=1

echo.
echo Testing Python import of the app...
python -c "import app_finbert_ultimate_av" 2>&1

echo.
echo Starting server with error output...
echo ================================================================================
python app_finbert_ultimate_av.py 2>&1

pause
@echo off
REM ===================================================================
REM FinBERT v4.4 - Installation Verification Script
REM ===================================================================
REM This script checks that all components are properly installed
REM ===================================================================

echo ========================================
echo   FinBERT v4.4 Installation Check
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    echo Please run INSTALL.bat first!
    pause
    exit /b 1
)

echo.
echo Checking Python packages...
echo.

python -c "import flask; print('[OK] Flask:', flask.__version__)" 2>nul || echo [ERROR] Flask not installed
python -c "import flask_cors; print('[OK] Flask-CORS: Installed')" 2>nul || echo [ERROR] Flask-CORS not installed
python -c "import yfinance; print('[OK] yfinance:', yfinance.__version__)" 2>nul || echo [ERROR] yfinance not installed
python -c "import pandas; print('[OK] pandas:', pandas.__version__)" 2>nul || echo [ERROR] pandas not installed
python -c "import numpy; print('[OK] numpy:', numpy.__version__)" 2>nul || echo [ERROR] numpy not installed
python -c "import ta; print('[OK] ta: Installed')" 2>nul || echo [ERROR] ta not installed
python -c "import requests; print('[OK] requests: Installed')" 2>nul || echo [ERROR] requests not installed

echo.
echo Checking optional packages...
echo.

python -c "import tensorflow; print('[OK] TensorFlow:', tensorflow.__version__)" 2>nul || echo [INFO] TensorFlow not installed (optional)
python -c "import transformers; print('[OK] Transformers: Installed')" 2>nul || echo [INFO] Transformers not installed (optional)
python -c "import torch; print('[OK] PyTorch: Installed')" 2>nul || echo [INFO] PyTorch not installed (optional)
python -c "import apscheduler; print('[OK] APScheduler: Installed')" 2>nul || echo [INFO] APScheduler not installed (optional)

echo.
echo Checking directories...
echo.

if exist data (echo [OK] data directory exists) else (echo [WARNING] data directory missing)
if exist models (echo [OK] models directory exists) else (echo [ERROR] models directory missing)
if exist templates (echo [OK] templates directory exists) else (echo [ERROR] templates directory missing)

echo.
echo Checking files...
echo.

if exist app_finbert_v4_dev.py (echo [OK] app_finbert_v4_dev.py found) else (echo [ERROR] app_finbert_v4_dev.py missing)
if exist config_dev.py (echo [OK] config_dev.py found) else (echo [ERROR] config_dev.py missing)
if exist requirements.txt (echo [OK] requirements.txt found) else (echo [ERROR] requirements.txt missing)

echo.
echo ========================================
echo   Verification Complete
echo ========================================
echo.
echo If all critical packages show [OK], you can run START_FINBERT.bat
echo If you see [ERROR] for Flask-CORS, run FIX_FLASK_CORS.bat
echo.
pause

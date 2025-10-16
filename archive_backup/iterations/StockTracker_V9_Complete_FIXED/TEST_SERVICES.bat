@echo off
echo ============================================================
echo Stock Tracker V9 - Service Test
echo ============================================================
echo.

REM Activate virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found
    echo Please run INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

echo Testing Python installation...
python --version
echo.

echo Testing required packages...
python -c "print('Testing imports...')" 2>nul
python -c "import fastapi; print(f'✓ FastAPI {fastapi.__version__}')" 2>nul || echo ✗ FastAPI not installed
python -c "import uvicorn; print('✓ Uvicorn installed')" 2>nul || echo ✗ Uvicorn not installed
python -c "import pandas; print(f'✓ Pandas {pandas.__version__}')" 2>nul || echo ✗ Pandas not installed
python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')" 2>nul || echo ✗ NumPy not installed
python -c "import yfinance; print('✓ yfinance installed')" 2>nul || echo ✗ yfinance not installed
python -c "import sklearn; print(f'✓ scikit-learn {sklearn.__version__}')" 2>nul || echo ✗ scikit-learn not installed
python -c "import joblib; print('✓ joblib installed')" 2>nul || echo ✗ joblib not installed
python -c "import aiohttp; print('✓ aiohttp installed')" 2>nul || echo ✗ aiohttp not installed
echo.

echo Optional packages:
python -c "import ta; print('✓ Technical Analysis (ta) installed')" 2>nul || echo ✗ TA not installed (optional)
python -c "import xgboost; print('✓ XGBoost installed')" 2>nul || echo ✗ XGBoost not installed (optional)
python -c "import transformers; print('✓ Transformers (FinBERT) installed')" 2>nul || echo ✗ FinBERT not installed (optional)
echo.

echo Testing service files...
if exist "main_backend.py" (echo ✓ main_backend.py found) else (echo ✗ main_backend.py missing)
if exist "enhanced_ml_backend.py" (echo ✓ enhanced_ml_backend.py found) else (echo ✗ enhanced_ml_backend.py missing)
if exist "finbert_backend.py" (echo ✓ finbert_backend.py found) else (echo ✗ finbert_backend.py missing)
if exist "backtesting_backend.py" (echo ✓ backtesting_backend.py found) else (echo ✗ backtesting_backend.py missing)
if exist "prediction_center.html" (echo ✓ prediction_center.html found) else (echo ✗ prediction_center.html missing)
echo.

echo Testing port availability...
netstat -an | findstr :8002 >nul 2>&1
if %errorlevel%==0 (echo ⚠ Port 8002 is in use) else (echo ✓ Port 8002 is available)
netstat -an | findstr :8003 >nul 2>&1
if %errorlevel%==0 (echo ⚠ Port 8003 is in use) else (echo ✓ Port 8003 is available)
netstat -an | findstr :8004 >nul 2>&1
if %errorlevel%==0 (echo ⚠ Port 8004 is in use) else (echo ✓ Port 8004 is available)
netstat -an | findstr :8005 >nul 2>&1
if %errorlevel%==0 (echo ⚠ Port 8005 is in use) else (echo ✓ Port 8005 is available)
echo.

echo ============================================================
echo Test Complete!
echo ============================================================
echo.
echo If all core packages show ✓, you can run START_WINDOWS.bat
echo Optional packages are not required for basic functionality
echo.
pause
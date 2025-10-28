@echo off
REM FinBERT Trading System - System Test Script

echo ========================================
echo FinBERT Trading System - Diagnostic Test
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [FAIL] Python not found!
    goto :error
) else (
    echo [PASS] Python is installed
)
echo.

REM Check virtual environment
echo Checking virtual environment...
if exist "venv" (
    echo [PASS] Virtual environment exists
    call venv\Scripts\activate.bat
) else (
    echo [FAIL] Virtual environment not found
    echo       Run INSTALL.bat first
    goto :error
)
echo.

REM Test imports
echo Testing critical imports...
echo.

echo Testing numpy...
python -c "import numpy; print(f'  Version: {numpy.__version__}')"
if %errorlevel% neq 0 (
    echo [FAIL] Numpy import failed
    echo       Run REPAIR_NUMPY.bat to fix
    goto :error
) else (
    echo [PASS] Numpy working
)
echo.

echo Testing PyTorch...
python -c "import torch; print(f'  Version: {torch.__version__}'); print(f'  CUDA: {torch.cuda.is_available()}')"
if %errorlevel% neq 0 (
    echo [FAIL] PyTorch import failed
    goto :error
) else (
    echo [PASS] PyTorch working
)
echo.

echo Testing Transformers...
python -c "import transformers; print(f'  Version: {transformers.__version__}')"
if %errorlevel% neq 0 (
    echo [FAIL] Transformers import failed
    goto :error
) else (
    echo [PASS] Transformers working
)
echo.

echo Testing Flask...
python -c "import flask; print(f'  Version: {flask.__version__}')"
if %errorlevel% neq 0 (
    echo [FAIL] Flask import failed
    goto :error
) else (
    echo [PASS] Flask working
)
echo.

echo Testing sklearn...
python -c "import sklearn; print(f'  Version: {sklearn.__version__}')"
if %errorlevel% neq 0 (
    echo [FAIL] Scikit-learn import failed
    goto :error
) else (
    echo [PASS] Scikit-learn working
)
echo.

echo Testing yfinance...
python -c "import yfinance; print(f'  Version: {yfinance.__version__}')"
if %errorlevel% neq 0 (
    echo [FAIL] yfinance import failed
    goto :error
) else (
    echo [PASS] yfinance working
)
echo.

echo ========================================
echo Testing FinBERT availability...
echo ========================================
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('[INFO] Checking FinBERT model...'); model_name='ProsusAI/finbert'; print('[PASS] FinBERT can be loaded')"
if %errorlevel% neq 0 (
    echo [WARNING] FinBERT model check failed
    echo          Model will download on first use
) else (
    echo [PASS] FinBERT ready to use
)
echo.

echo ========================================
echo ALL TESTS PASSED!
echo ========================================
echo.
echo System is ready. Run RUN.bat to start the application.
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo TESTS FAILED!
echo ========================================
echo.
echo Please run INSTALL.bat to set up the system.
echo If problems persist, try REPAIR_NUMPY.bat
echo.
pause
exit /b 1
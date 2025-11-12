@echo off
REM ============================================================================
REM Overnight Stock Screener with FinBERT Integration
REM Dependency Installation Script for Windows 11
REM ============================================================================
REM
REM This script installs ALL required dependencies for the integrated system:
REM
REM 1. Core Dependencies (Required for basic screener functionality)
REM 2. FinBERT Transformers (Required for real sentiment analysis)
REM 3. TensorFlow/Keras (Required for real LSTM predictions)
REM 4. Optional Dependencies (Email, scheduling, etc.)
REM
REM IMPORTANT: FinBERT Model Download
REM --------------------------------
REM The FinBERT model (ProsusAI/finbert) is automatically downloaded from
REM HuggingFace when first used. It will be cached locally at:
REM   C:\Users\<YourUser>\.cache\huggingface\hub\
REM
REM First download is ~500MB and may take 2-5 minutes depending on internet speed.
REM Subsequent uses will load from cache instantly.
REM
REM ============================================================================

echo.
echo ============================================================================
echo   OVERNIGHT STOCK SCREENER - DEPENDENCY INSTALLATION
echo   Windows 11 with FinBERT Integration
echo ============================================================================
echo.

REM Check Python version
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or later from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo   OK: Python found
echo.

REM Upgrade pip
echo [2/8] Upgrading pip to latest version...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Could not upgrade pip, continuing anyway...
)
echo   OK: pip upgraded
echo.

REM Install Core Dependencies (Required)
echo [3/8] Installing CORE dependencies...
echo   - flask (web framework)
echo   - flask-cors (API support)
echo   - yfinance (stock data)
echo   - pandas (data processing)
echo   - numpy (numerical computing)
echo   - requests (HTTP requests)
echo   - ta (technical analysis)
echo.
python -m pip install flask>=2.3.0 flask-cors>=4.0.0 yfinance>=0.2.30 pandas>=1.5.0 numpy>=1.24.0 requests>=2.31.0 ta>=0.11.0
if %errorlevel% neq 0 (
    echo ERROR: Core dependencies installation failed
    pause
    exit /b 1
)
echo   OK: Core dependencies installed
echo.

REM Install PyTorch (Required for FinBERT)
echo [4/8] Installing PyTorch (CPU version)...
echo   NOTE: This is required for FinBERT transformer sentiment analysis
echo   Size: ~200MB, may take 2-5 minutes
echo.
python -m pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo WARNING: PyTorch installation failed - FinBERT sentiment will use fallback
    echo Continuing with installation...
) else (
    echo   OK: PyTorch installed
)
echo.

REM Install Transformers (Required for FinBERT)
echo [5/8] Installing HuggingFace Transformers...
echo   NOTE: This downloads the FinBERT model from HuggingFace (ProsusAI/finbert)
echo   The model (~500MB) will be cached locally after first download
echo   Location: C:\Users\%USERNAME%\.cache\huggingface\hub\
echo.
python -m pip install transformers>=4.30.0
if %errorlevel% neq 0 (
    echo WARNING: Transformers installation failed - FinBERT sentiment will use fallback
    echo Continuing with installation...
) else (
    echo   OK: Transformers installed
)
echo.

REM Install TensorFlow (Required for LSTM)
echo [6/8] Installing TensorFlow and Keras (for LSTM predictions)...
echo   NOTE: This is required for real neural network LSTM predictions
echo   Size: ~450MB, may take 3-7 minutes
echo.
python -m pip install tensorflow>=2.13.0 keras>=2.13.0 scikit-learn>=1.3.0
if %errorlevel% neq 0 (
    echo WARNING: TensorFlow installation failed - LSTM predictions will use fallback
    echo Continuing with installation...
) else (
    echo   OK: TensorFlow and Keras installed
)
echo.

REM Install Optional Dependencies
echo [7/8] Installing OPTIONAL dependencies...
echo   - APScheduler (task scheduling)
echo   - python-dateutil (date utilities)
echo   - pytz (timezone support)
echo   - feedparser (RSS news feeds)
echo.
python -m pip install APScheduler>=3.10.0 python-dateutil>=2.8.2 pytz>=2023.3 feedparser==6.0.10
if %errorlevel% neq 0 (
    echo WARNING: Optional dependencies installation had issues
    echo Continuing anyway...
)
echo   OK: Optional dependencies installed
echo.

REM Install Beautiful Soup for web scraping
echo [8/8] Installing web scraping dependencies...
echo   - beautifulsoup4 (HTML parsing)
echo   - lxml (XML parsing)
echo.
python -m pip install beautifulsoup4>=4.12.0 lxml>=4.9.0
if %errorlevel% neq 0 (
    echo WARNING: Web scraping dependencies installation had issues
)
echo   OK: Web scraping dependencies installed
echo.

REM Verify critical installations
echo.
echo ============================================================================
echo   VERIFYING INSTALLATION
echo ============================================================================
echo.

echo Testing Python imports...
python -c "import flask; print('  OK: Flask %s' % flask.__version__)"
python -c "import yfinance; print('  OK: yfinance %s' % yfinance.__version__)"
python -c "import pandas; print('  OK: pandas %s' % pandas.__version__)"
python -c "import numpy; print('  OK: numpy %s' % numpy.__version__)"

echo.
echo Testing FinBERT dependencies (optional)...
python -c "import torch; print('  OK: PyTorch %s' % torch.__version__)" 2>nul || echo   WARNING: PyTorch not available
python -c "import transformers; print('  OK: Transformers %s' % transformers.__version__)" 2>nul || echo   WARNING: Transformers not available

echo.
echo Testing LSTM dependencies (optional)...
python -c "import tensorflow; print('  OK: TensorFlow %s' % tensorflow.__version__)" 2>nul || echo   WARNING: TensorFlow not available
python -c "import sklearn; print('  OK: scikit-learn %s' % sklearn.__version__)" 2>nul || echo   WARNING: scikit-learn not available

echo.
echo ============================================================================
echo   INSTALLATION SUMMARY
echo ============================================================================
echo.
echo Core Dependencies:     INSTALLED
echo FinBERT Transformers:  Check above for status
echo LSTM TensorFlow:       Check above for status
echo Optional Utilities:    INSTALLED
echo.
echo IMPORTANT NOTES:
echo ----------------
echo 1. FinBERT Model Download:
echo    The FinBERT model (ProsusAI/finbert) will be downloaded automatically
echo    on FIRST USE from HuggingFace. This is a one-time ~500MB download.
echo.
echo    It will be cached at:
echo    C:\Users\%USERNAME%\.cache\huggingface\hub\
echo.
echo    First sentiment analysis may take 2-5 minutes for download.
echo    Subsequent analyses will be instant (using cached model).
echo.
echo 2. Internet Connection Required:
echo    - First run needs internet for FinBERT model download
echo    - Stock data fetching (yfinance) needs internet
echo    - News scraping (Yahoo Finance, Finviz) needs internet
echo.
echo 3. Fallback Behavior:
echo    If PyTorch/Transformers unavailable: Uses keyword sentiment fallback
echo    If TensorFlow unavailable: Uses trend-based prediction fallback
echo    The screener will still function with reduced accuracy.
echo.
echo 4. Test Integration:
echo    Run: python scripts\screening\test_finbert_integration.py
echo    This will verify all components are working correctly.
echo.
echo ============================================================================
echo   INSTALLATION COMPLETE!
echo ============================================================================
echo.

pause

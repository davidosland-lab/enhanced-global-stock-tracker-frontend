@echo off
echo ================================================================
echo   FIX MISSING PACKAGES - Quick Repair
echo ================================================================
echo.
echo This script will install the missing packages:
echo   - TensorFlow (for LSTM models)
echo   - aiohttp (for news scraping)
echo   - beautifulsoup4 and lxml (for web scraping)
echo   - sentencepiece (for FinBERT tokenizer)
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ================================================================
echo Installing TensorFlow...
echo ================================================================
pip install tensorflow
if %errorlevel% neq 0 (
    echo WARNING: TensorFlow installation failed
    echo LSTM features will be limited
) else (
    echo ✓ TensorFlow installed successfully
)

echo.
echo ================================================================
echo Installing web scraping libraries...
echo ================================================================
pip install aiohttp beautifulsoup4 lxml
if %errorlevel% neq 0 (
    echo WARNING: Web scraping libraries installation failed
    echo News sentiment may be limited
) else (
    echo ✓ Web scraping libraries installed successfully
)

echo.
echo ================================================================
echo Installing sentencepiece (for FinBERT)...
echo ================================================================
pip install sentencepiece
if %errorlevel% neq 0 (
    echo WARNING: sentencepiece installation failed
) else (
    echo ✓ sentencepiece installed successfully
)

echo.
echo ================================================================
echo Installing APScheduler and pytz (for prediction caching)...
echo ================================================================
pip install APScheduler pytz
if %errorlevel% neq 0 (
    echo WARNING: APScheduler/pytz installation failed
    echo Prediction caching will not work
) else (
    echo ✓ APScheduler and pytz installed successfully
)

echo.
echo ================================================================
echo Verification:
echo ================================================================
python -c "import tensorflow; print('✓ TensorFlow:', tensorflow.__version__)" 2>nul || echo ✗ TensorFlow not installed
python -c "import aiohttp; print('✓ aiohttp:', aiohttp.__version__)" 2>nul || echo ✗ aiohttp not installed
python -c "import bs4; print('✓ BeautifulSoup4 installed')" 2>nul || echo ✗ BeautifulSoup4 not installed
python -c "import sentencepiece; print('✓ sentencepiece installed')" 2>nul || echo ✗ sentencepiece not installed
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✓ APScheduler installed')" 2>nul || echo ✗ APScheduler not installed
python -c "import pytz; print('✓ pytz installed')" 2>nul || echo ✗ pytz not installed

echo.
echo ================================================================
echo Done! Missing packages have been installed.
echo ================================================================
echo.
echo You can now start the application with START_FINBERT_V4.bat
echo.
pause

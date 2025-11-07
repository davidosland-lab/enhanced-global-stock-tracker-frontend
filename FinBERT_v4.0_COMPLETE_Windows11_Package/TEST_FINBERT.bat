@echo off
echo ================================================================
echo    FINBERT VERIFICATION TEST
echo ================================================================
echo.
echo This script will test if FinBERT is properly installed and working.
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo ================================================================
echo TEST 1: Checking Python Version
echo ================================================================
python --version
echo.

echo ================================================================
echo TEST 2: Checking Core Packages
echo ================================================================
echo Checking NumPy...
python -c "import numpy; print('✓ NumPy', numpy.__version__)"
if %errorlevel% neq 0 (
    echo ✗ NumPy not installed
    goto :END_TESTS
)

echo Checking Pandas...
python -c "import pandas; print('✓ Pandas', pandas.__version__)"
if %errorlevel% neq 0 (
    echo ✗ Pandas not installed
    goto :END_TESTS
)

echo Checking Flask...
python -c "import flask; print('✓ Flask', flask.__version__)"
if %errorlevel% neq 0 (
    echo ✗ Flask not installed
    goto :END_TESTS
)
echo.

echo ================================================================
echo TEST 3: Checking FinBERT Dependencies
echo ================================================================
echo Checking PyTorch...
python -c "import torch; print('✓ PyTorch', torch.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ✗ PyTorch NOT INSTALLED - FinBERT will not work!
    echo.
    echo SOLUTION: Run INSTALL.bat to install PyTorch
    echo PyTorch is ~2GB and may take 5-10 minutes to install.
    goto :END_TESTS
) else (
    echo ✓ PyTorch is installed
)

echo Checking Transformers...
python -c "import transformers; print('✓ Transformers', transformers.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Transformers NOT INSTALLED - FinBERT will not work!
    echo.
    echo SOLUTION: Run INSTALL.bat to install Transformers
    goto :END_TESTS
) else (
    echo ✓ Transformers is installed
)
echo.

echo ================================================================
echo TEST 4: Checking FinBERT Module Import
echo ================================================================
echo Testing finbert_sentiment module...
python -c "from models.finbert_sentiment import finbert_analyzer; print('✓ FinBERT module imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ FinBERT module import FAILED
    echo.
    echo This could indicate:
    echo - Missing models directory
    echo - Corrupted Python files
    echo - Import errors in the code
    goto :END_TESTS
)

echo Testing finbert_analyzer initialization...
python -c "from models.finbert_sentiment import finbert_analyzer; print('✓ FinBERT Analyzer Status:', 'Loaded' if finbert_analyzer.is_loaded else 'Available (model will download on first use)')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ FinBERT analyzer initialization FAILED
    goto :END_TESTS
)
echo.

echo ================================================================
echo TEST 5: Checking News Scraping Module
echo ================================================================
echo Testing news_sentiment_real module...
python -c "from models.news_sentiment_real import get_sentiment_sync; print('✓ News scraping module loaded')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ News scraping module import FAILED
    goto :END_TESTS
)
echo.

echo ================================================================
echo TEST 6: Testing FinBERT Sentiment Analysis
echo ================================================================
echo.
echo Testing simple sentiment analysis...
echo This will analyze a simple financial text.
echo If this is the first time, FinBERT model will download (~400MB).
echo This may take 2-5 minutes. Please wait...
echo.

python -c "from models.finbert_sentiment import finbert_analyzer; result = finbert_analyzer.analyze_text('The stock showed strong growth with excellent profit margins'); print('✓ Sentiment Analysis Test:'); print('  Text: Strong growth with excellent profit'); print('  Sentiment:', result['sentiment']); print('  Confidence:', result['confidence'], '%%'); print('  Method:', result['method']); print('  Scores:', result['scores'])" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Sentiment analysis test FAILED
    echo.
    echo This could indicate:
    echo - FinBERT model download failed (check internet)
    echo - Not enough disk space (~400MB needed)
    echo - Firewall blocking HuggingFace
    goto :END_TESTS
)
echo.

echo ================================================================
echo TEST 7: All Tests Passed!
echo ================================================================
echo.
echo ✓ FinBERT is properly installed and working!
echo.
echo You can now:
echo   1. Run START_FINBERT_V4.bat to start the application
echo   2. Open http://localhost:5000 in your browser
echo   3. Test sentiment analysis for stocks like AAPL, TSLA, NVDA
echo.
echo Note: First sentiment request will download the model if not cached.
echo      This takes 2-5 minutes but only happens once.
echo.
goto :END

:END_TESTS
echo.
echo ================================================================
echo TESTS FAILED - FinBERT is NOT properly configured
echo ================================================================
echo.
echo Please check the error messages above and:
echo   1. Read TROUBLESHOOTING_FINBERT.txt for solutions
echo   2. Run INSTALL.bat if packages are missing
echo   3. Ensure you have internet connection
echo   4. Ensure you have 4GB free disk space
echo.

:END
pause

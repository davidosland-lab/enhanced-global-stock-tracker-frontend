@echo off
REM ============================================================================
REM UK Pipeline - Install Missing Dependencies
REM Version: v1.3.15.34
REM ============================================================================

echo.
echo ============================================================================
echo  UK PIPELINE - DEPENDENCY INSTALLER v1.3.15.34
echo ============================================================================
echo.
echo This will install the missing packages for full FinBERT support:
echo   - transformers (Hugging Face transformers for FinBERT)
echo   - feedparser (RSS news feed parsing)
echo   - beautifulsoup4 (HTML parsing for web scraping)
echo   - scipy (Scientific computing)
echo   - pandas (Data analysis)
echo   - scikit-learn (Machine learning)
echo   - torch (PyTorch for FinBERT backend)
echo.
pause

echo.
echo [1/7] Installing transformers...
pip install transformers>=4.30.0
if errorlevel 1 (
    echo [ERROR] Failed to install transformers
    pause
    exit /b 1
)

echo.
echo [2/7] Installing feedparser...
pip install feedparser>=6.0.10
if errorlevel 1 (
    echo [ERROR] Failed to install feedparser
    pause
    exit /b 1
)

echo.
echo [3/7] Installing beautifulsoup4...
pip install beautifulsoup4>=4.12.0
if errorlevel 1 (
    echo [ERROR] Failed to install beautifulsoup4
    pause
    exit /b 1
)

echo.
echo [4/7] Installing scipy...
pip install scipy>=1.10.0
if errorlevel 1 (
    echo [ERROR] Failed to install scipy
    pause
    exit /b 1
)

echo.
echo [5/7] Installing pandas...
pip install pandas>=1.5.0
if errorlevel 1 (
    echo [ERROR] Failed to install pandas
    pause
    exit /b 1
)

echo.
echo [6/7] Installing scikit-learn...
pip install scikit-learn>=1.3.0
if errorlevel 1 (
    echo [ERROR] Failed to install scikit-learn
    pause
    exit /b 1
)

echo.
echo [7/7] Installing torch (PyTorch)...
pip install torch>=2.0.0
if errorlevel 1 (
    echo [ERROR] Failed to install torch
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  INSTALLATION COMPLETE!
echo ============================================================================
echo.
echo Verifying installation...
python -c "import transformers, feedparser, bs4, scipy, pandas, sklearn, torch; print('[OK] All dependencies installed successfully!')"
if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may not have installed correctly.
    echo Please check the errors above.
) else (
    echo.
    echo [SUCCESS] All packages verified!
    echo.
    echo You can now run the UK pipeline:
    echo   python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
)

echo.
pause

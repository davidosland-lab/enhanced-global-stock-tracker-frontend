@echo off
REM ===================================================================
REM  VERIFY BoE RSS FIX - Diagnostic & Installation Script
REM  Version: v1.3.15.43 Hotfix
REM  Purpose: Verify and fix Bank of England RSS scraper
REM ===================================================================

echo.
echo ============================================================
echo   Bank of England RSS Scraper - Verification Tool
echo   Version: v1.3.15.43
echo ============================================================
echo.

REM Change to installation directory
cd /d "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"

echo [Step 1/4] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)
echo   [OK] Python detected
echo.

echo [Step 2/4] Checking feedparser installation...
python -c "import feedparser; print(f'  [OK] feedparser {feedparser.__version__} installed')" 2>nul
if %errorlevel% neq 0 (
    echo   [MISSING] feedparser not installed
    echo.
    echo   Installing feedparser...
    pip install feedparser --quiet --disable-pip-version-check
    if %errorlevel% neq 0 (
        echo   ERROR: Failed to install feedparser
        pause
        exit /b 1
    )
    echo   [OK] feedparser installed successfully
) else (
    echo   feedparser is already installed
)
echo.

echo [Step 3/4] Verifying macro_news_monitor.py patch...
findstr /C:"_scrape_boe_news_rss()" models\screening\macro_news_monitor.py >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] RSS scraper not found in code
    echo   Please reapply COMPLETE_PATCH_v1.3.15.43.zip
    pause
    exit /b 1
)
echo   [OK] RSS scraper code detected
echo.

echo [Step 4/4] Testing BoE RSS feed access...
python -c "import feedparser; feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss'); print(f'  [OK] RSS feed accessible: {len(feed.entries)} articles found')" 2>nul
if %errorlevel% neq 0 (
    echo   [WARNING] Could not fetch RSS feed
    echo   Check internet connection or firewall settings
) else (
    echo   RSS feed working correctly
)
echo.

echo ============================================================
echo   Verification Complete
echo ============================================================
echo.
echo RESULTS:
echo   - Python: OK
echo   - feedparser: OK (or just installed)
echo   - Code patch: OK
echo   - RSS feed: Check above
echo.
echo NEXT STEPS:
echo   1. Run UK pipeline again:
echo      python run_uk_full_pipeline.py --full-scan --capital 100000
echo.
echo   2. Check logs for BoE articles:
echo      type logs\uk_pipeline.log ^| findstr "Bank of England"
echo      type logs\uk_pipeline.log ^| findstr "BoE:"
echo.
echo   Expected: 4-8 BoE articles in macro news section
echo.
pause

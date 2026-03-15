@echo off
REM ================================================================================
REM BOE NEWS DIAGNOSTIC SCRIPT v1.0
REM ================================================================================
REM
REM This script diagnoses why Bank of England news is not appearing
REM after applying patch v1.3.15.43
REM
REM ================================================================================

echo.
echo ================================================================================
echo  BANK OF ENGLAND NEWS DIAGNOSTIC TOOL
echo ================================================================================
echo.
echo This tool will check 7 critical points to diagnose why BoE news is not appearing
echo.
pause

REM ================================================================================
REM CHECK 1: VERIFY INSTALLATION DIRECTORY
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 1: VERIFY INSTALLATION DIRECTORY
echo ================================================================================
echo.

if not exist "run_uk_full_pipeline.py" (
    echo [ERROR] Not in installation directory
    echo Please run this from: C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\
    pause
    exit /b 1
)

echo [OK] Running from: %CD%
echo.

REM ================================================================================
REM CHECK 2: VERIFY PATCH WAS APPLIED
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 2: VERIFY PATCH FILES WERE COPIED
echo ================================================================================
echo.

echo Checking file modification dates...
echo.

dir /T:W models\screening\macro_news_monitor.py | findstr /C:"macro_news_monitor.py"
echo.

echo If the date above shows 2026-01-27 or today, the patch was applied.
echo If it shows an older date (Jan 15 or earlier), the patch did NOT copy the file.
echo.

REM ================================================================================
REM CHECK 3: VERIFY RSS SCRAPER EXISTS IN CODE
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 3: VERIFY RSS SCRAPER FUNCTION EXISTS
echo ================================================================================
echo.

findstr /C:"def _scrape_boe_news_rss" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo [OK] _scrape_boe_news_rss function found in code
) else (
    echo [ERROR] _scrape_boe_news_rss function NOT found
    echo This means the old file is still in use
    echo.
    echo FIX: Copy the patched file manually:
    echo   copy /Y COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py models\screening\
)
echo.

REM ================================================================================
REM CHECK 4: VERIFY CODE CALLS RSS SCRAPER
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 4: VERIFY CODE CALLS RSS SCRAPER (NOT OLD HTML SCRAPER)
echo ================================================================================
echo.

findstr /C:"boe_news = self._scrape_boe_news_rss()" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo [OK] Code calls RSS scraper: _scrape_boe_news_rss()
) else (
    echo [WARNING] Code may be calling old HTML scraper
    echo.
    echo Checking for old HTML scraper call...
    findstr /C:"boe_news = self._scrape_uk_boe_news()" models\screening\macro_news_monitor.py >nul
    if %errorlevel% equ 0 (
        echo [ERROR] Code still calls OLD HTML scraper: _scrape_uk_boe_news()
        echo This means the patch did NOT update the file
        echo.
        echo FIX: Copy the patched file manually:
        echo   copy /Y COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py models\screening\
    )
)
echo.

REM ================================================================================
REM CHECK 5: VERIFY FEEDPARSER IS INSTALLED
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 5: VERIFY FEEDPARSER PACKAGE IS INSTALLED
echo ================================================================================
echo.

pip show feedparser >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] feedparser is installed
    pip show feedparser | findstr "Version:"
) else (
    echo [ERROR] feedparser is NOT installed
    echo.
    echo FIX: Install feedparser:
    echo   pip install feedparser
    echo.
    echo Without feedparser, the code falls back to old HTML scraper which returns 0 articles
)
echo.

REM ================================================================================
REM CHECK 6: TEST BOE RSS FEED ACCESSIBILITY
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 6: TEST BOE RSS FEED ACCESSIBILITY
echo ================================================================================
echo.

echo Testing BoE RSS feed: https://www.bankofengland.co.uk/news.rss
echo.

python -c "import urllib.request; r = urllib.request.urlopen('https://www.bankofengland.co.uk/news.rss'); print('[OK] BoE RSS feed accessible'); print(f'Status: {r.status}'); print(f'Content length: {len(r.read())} bytes')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Cannot access BoE RSS feed
    echo This could be a network issue or firewall blocking
    echo.
    echo Please test manually in browser:
    echo   https://www.bankofengland.co.uk/news.rss
)
echo.

REM ================================================================================
REM CHECK 7: CLEAR PYTHON CACHE
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 7: CLEAR PYTHON CACHE
echo ================================================================================
echo.

echo Python may be using cached (old) .pyc files
echo.

if exist "models\screening\__pycache__" (
    echo Deleting __pycache__ directory...
    rmdir /S /Q "models\screening\__pycache__"
    echo [OK] Cache cleared
) else (
    echo [INFO] No __pycache__ directory found
)
echo.

REM ================================================================================
REM CHECK 8: TEST RSS SCRAPER DIRECTLY
REM ================================================================================

echo.
echo ================================================================================
echo CHECK 8: TEST RSS SCRAPER DIRECTLY (REQUIRES FEEDPARSER)
echo ================================================================================
echo.

echo Testing BoE RSS scraper directly...
echo.

python -c "try:\n    import feedparser\n    feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss')\n    print(f'[OK] RSS feed parsed')\n    print(f'Entries found: {len(feed.entries)}')\n    if feed.entries:\n        print(f'\\nFirst article:')\n        print(f'  Title: {feed.entries[0].title}')\n        print(f'  Link: {feed.entries[0].link}')\n        print(f'  Published: {feed.entries[0].published}')\nexcept ImportError:\n    print('[ERROR] feedparser not installed')\n    print('Install with: pip install feedparser')\nexcept Exception as e:\n    print(f'[ERROR] {e}')" 2>nul

echo.

REM ================================================================================
REM SUMMARY AND RECOMMENDATIONS
REM ================================================================================

echo.
echo ================================================================================
echo  DIAGNOSTIC SUMMARY
echo ================================================================================
echo.

echo Based on the checks above, here are the most likely issues:
echo.
echo [Issue 1] Patch file not copied (80%% likely):
echo   - FIX: copy /Y COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py models\screening\
echo.
echo [Issue 2] feedparser not installed (15%% likely):
echo   - FIX: pip install feedparser
echo.
echo [Issue 3] Python using cached .pyc files (5%% likely):
echo   - FIX: rmdir /S /Q models\screening\__pycache__
echo.
echo ================================================================================
echo  COMPLETE FIX (RUN ALL THREE COMMANDS)
echo ================================================================================
echo.
echo Run these commands in order:
echo.
echo 1. Copy patched file:
echo    copy /Y COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py models\screening\
echo.
echo 2. Install feedparser:
echo    pip install feedparser
echo.
echo 3. Clear Python cache:
echo    rmdir /S /Q models\screening\__pycache__
echo.
echo 4. Test UK pipeline:
echo    python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.
echo ================================================================================
echo  EXPECTED OUTPUT AFTER FIX
echo ================================================================================
echo.
echo In logs\uk_pipeline.log you should see:
echo   [OK] Bank of England News (RSS): 4-6 articles
echo   [OK] UK Macro News: 8-10 articles
echo   Articles Analyzed: 8-10
echo   Sentiment: BULLISH/BEARISH (not NEUTRAL)
echo.
echo ================================================================================

echo.
echo Diagnostic complete! Press any key to exit...
pause >nul

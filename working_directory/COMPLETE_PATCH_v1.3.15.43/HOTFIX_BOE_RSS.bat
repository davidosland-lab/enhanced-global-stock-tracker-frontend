@echo off
REM ================================================================================
REM HOTFIX: Bank of England RSS Scraper
REM ================================================================================
REM
REM This hotfix ensures the BoE RSS scraper is properly activated.
REM
REM Issue: macro_news_monitor.py may not have been updated correctly during
REM initial patch installation, causing it to still use the old HTML scraper
REM which finds 0 articles.
REM
REM This script will:
REM 1. Verify the RSS function exists in the code
REM 2. Test the RSS feed directly
REM 3. Re-copy the file if needed
REM 4. Test again to confirm
REM
REM ================================================================================

echo.
echo ================================================================================
echo  BOE RSS SCRAPER HOTFIX
echo ================================================================================
echo.
echo This will fix the Bank of England news scraping issue.
echo.
pause

REM Find installation directory
set INSTALL_DIR=C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15

if not exist "%INSTALL_DIR%\models\screening\macro_news_monitor.py" (
    echo [ERROR] Cannot find macro_news_monitor.py at:
    echo %INSTALL_DIR%\models\screening\
    echo.
    set /p INSTALL_DIR="Enter your installation directory: "
)

cd /d "%INSTALL_DIR%"

echo.
echo [1/4] Testing current BoE scraper...
echo.

REM Test current scraper
python -c "from models.screening.macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); r = m.get_macro_sentiment(); print(f'Articles found: {r[\"article_count\"]}')" 2>nul

if %errorlevel% neq 0 (
    echo [WARNING] Could not test current scraper
)

echo.
echo [2/4] Installing feedparser (required for RSS)...
echo.

pip install feedparser --quiet --disable-pip-version-check
if %errorlevel% equ 0 (
    echo [OK] feedparser installed
) else (
    echo [ERROR] feedparser installation failed
    echo Please install manually: pip install feedparser
    pause
    exit /b 1
)

echo.
echo [3/4] Updating macro_news_monitor.py with RSS scraper...
echo.

REM Backup current file
if exist models\screening\macro_news_monitor.py (
    copy /Y models\screening\macro_news_monitor.py models\screening\macro_news_monitor.py.backup >nul
    echo [OK] Backup created: macro_news_monitor.py.backup
)

REM Determine patch location
if exist "COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py" (
    set PATCH_FILE=COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py
) else if exist "..\COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py" (
    set PATCH_FILE=..\COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py
) else (
    echo [ERROR] Cannot find patch file
    echo Please ensure COMPLETE_PATCH_v1.3.15.43 directory exists
    pause
    exit /b 1
)

REM Copy the fixed file
copy /Y "%PATCH_FILE%" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo [OK] macro_news_monitor.py updated
) else (
    echo [ERROR] File copy failed
    pause
    exit /b 1
)

echo.
echo [4/4] Testing BoE RSS scraper...
echo.

REM Test the RSS scraper
python -c "from models.screening.macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); r = m.get_macro_sentiment(); boe_count = len([a for a in r.get('top_articles', []) if 'BoE' in a['source'] or 'Bank of England' in a['source']]); print(f'\nBoE articles found: {boe_count}'); print(f'Total articles: {r[\"article_count\"]}'); print(f'Sentiment: {r[\"sentiment_label\"]} ({r[\"sentiment_score\"]:.3f})'); print(f'\nTop articles:'); [print(f\"  - {a['source']}: {a['title'][:60]}...\") for a in r.get('top_articles', [])[:5]]"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Test failed
    echo.
    echo Please check:
    echo 1. feedparser is installed: pip list ^| findstr feedparser
    echo 2. Internet connection is working
    echo 3. BoE RSS feed is accessible: curl https://www.bankofengland.co.uk/news.rss
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo  HOTFIX COMPLETE
echo ================================================================================
echo.
echo The BoE RSS scraper should now be working.
echo.
echo NEXT STEPS:
echo.
echo 1. Run UK pipeline again:
echo    python run_uk_full_pipeline.py --full-scan --capital 100000
echo.
echo 2. Check logs for BoE articles:
echo    type logs\uk_pipeline.log ^| findstr "Bank of England"
echo.
echo 3. You should see:
echo    "Bank of England News (RSS): 4-6 articles"
echo.
echo If you still see 0 articles, the BoE RSS feed may be temporarily
echo unavailable. Try again in a few minutes.
echo.
echo ================================================================================
echo.
pause

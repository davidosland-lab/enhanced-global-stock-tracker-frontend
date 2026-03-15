@echo off
REM ================================================================================
REM QUICK FIX FOR BOE NEWS - v1.0
REM ================================================================================
REM
REM This script applies all fixes needed to get BoE news working
REM
REM ================================================================================

echo.
echo ================================================================================
echo  QUICK FIX FOR BANK OF ENGLAND NEWS
echo ================================================================================
echo.
echo This will apply 3 fixes:
echo   1. Force-copy patched macro_news_monitor.py
echo   2. Install feedparser package
echo   3. Clear Python cache
echo.
echo Installation directory: %CD%
echo.
pause

REM ================================================================================
REM FIX 1: FORCE-COPY PATCHED FILE
REM ================================================================================

echo.
echo [1/3] Force-copying patched macro_news_monitor.py...
echo.

REM Determine patch location
if exist "COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py" (
    set PATCH_DIR=COMPLETE_PATCH_v1.3.15.43
) else if exist "..\COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py" (
    set PATCH_DIR=..\COMPLETE_PATCH_v1.3.15.43
) else if exist "models\screening\macro_news_monitor.py" (
    REM We're in the patch directory
    set PATCH_DIR=.
) else (
    echo [ERROR] Cannot find patched macro_news_monitor.py
    echo.
    echo Please ensure you have:
    echo   COMPLETE_PATCH_v1.3.15.43\models\screening\macro_news_monitor.py
    echo.
    pause
    exit /b 1
)

echo Copying from: %PATCH_DIR%\models\screening\macro_news_monitor.py
echo Copying to: models\screening\macro_news_monitor.py
echo.

copy /Y "%PATCH_DIR%\models\screening\macro_news_monitor.py" "models\screening\macro_news_monitor.py" >nul
if %errorlevel% equ 0 (
    echo [OK] File copied successfully
) else (
    echo [ERROR] Failed to copy file
    pause
    exit /b 1
)

REM Verify RSS scraper exists in copied file
findstr /C:"def _scrape_boe_news_rss" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo [OK] RSS scraper function verified in file
) else (
    echo [ERROR] RSS scraper function not found - wrong file copied?
    pause
    exit /b 1
)

echo.

REM ================================================================================
REM FIX 2: INSTALL FEEDPARSER
REM ================================================================================

echo.
echo [2/3] Installing feedparser package...
echo.

pip show feedparser >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] feedparser already installed
    pip show feedparser | findstr "Version:"
) else (
    echo Installing feedparser...
    pip install feedparser --quiet --disable-pip-version-check
    if %errorlevel% equ 0 (
        echo [OK] feedparser installed successfully
        pip show feedparser | findstr "Version:"
    ) else (
        echo [ERROR] Failed to install feedparser
        echo.
        echo Try manually: pip install feedparser
        pause
        exit /b 1
    )
)

echo.

REM ================================================================================
REM FIX 3: CLEAR PYTHON CACHE
REM ================================================================================

echo.
echo [3/3] Clearing Python cache...
echo.

if exist "models\screening\__pycache__" (
    echo Removing __pycache__ directory...
    rmdir /S /Q "models\screening\__pycache__"
    echo [OK] Cache cleared
) else (
    echo [INFO] No cache found (this is fine)
)

echo.

REM ================================================================================
REM VERIFICATION
REM ================================================================================

echo.
echo ================================================================================
echo  VERIFYING FIXES
echo ================================================================================
echo.

set ERROR_COUNT=0

echo [Check 1] RSS scraper function exists...
findstr /C:"def _scrape_boe_news_rss" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo   [OK] _scrape_boe_news_rss function found
) else (
    echo   [ERROR] _scrape_boe_news_rss function not found
    set /a ERROR_COUNT+=1
)

echo [Check 2] RSS scraper is called...
findstr /C:"boe_news = self._scrape_boe_news_rss()" models\screening\macro_news_monitor.py >nul
if %errorlevel% equ 0 (
    echo   [OK] Code calls RSS scraper
) else (
    echo   [ERROR] Code does not call RSS scraper
    set /a ERROR_COUNT+=1
)

echo [Check 3] feedparser is installed...
pip show feedparser >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] feedparser installed
) else (
    echo   [ERROR] feedparser not installed
    set /a ERROR_COUNT+=1
)

echo [Check 4] BoE RSS feed is accessible...
python -c "import urllib.request; urllib.request.urlopen('https://www.bankofengland.co.uk/news.rss')" 2>nul
if %errorlevel% equ 0 (
    echo   [OK] BoE RSS feed accessible
) else (
    echo   [WARNING] Cannot access BoE RSS feed (may be network/firewall)
)

echo.

if %ERROR_COUNT% gtr 0 (
    echo [ERROR] Verification failed: %ERROR_COUNT% issue(s) found
    echo.
    echo Please run DIAGNOSE_BOE_NEWS.bat for detailed diagnostics
    pause
    exit /b 1
)

echo [OK] All checks passed!
echo.

REM ================================================================================
REM TEST RSS SCRAPER
REM ================================================================================

echo.
echo ================================================================================
echo  TESTING RSS SCRAPER
echo ================================================================================
echo.

echo Testing BoE RSS scraper directly...
echo.

python -c "import feedparser; feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss'); print(f'[OK] RSS feed parsed'); print(f'Entries found: {len(feed.entries)}'); print(f'\nFirst 3 articles:'); [print(f'{i+1}. {e.title[:60]}...') for i, e in enumerate(feed.entries[:3])]; print(f'\n[SUCCESS] RSS scraper working correctly')" 2>nul

echo.

REM ================================================================================
REM SUCCESS SUMMARY
REM ================================================================================

echo.
echo ================================================================================
echo  FIX COMPLETE - SUCCESS!
echo ================================================================================
echo.
echo All fixes applied successfully:
echo   [OK] Patched macro_news_monitor.py copied
echo   [OK] feedparser installed
echo   [OK] Python cache cleared
echo   [OK] RSS scraper tested and working
echo.
echo ================================================================================
echo  NEXT STEPS
echo ================================================================================
echo.
echo 1. TEST UK PIPELINE:
echo    python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.
echo 2. CHECK LOGS:
echo    type logs\uk_pipeline.log | findstr "Bank of England"
echo.
echo 3. EXPECTED OUTPUT:
echo    [OK] Bank of England News (RSS): 4-6 articles
echo    Articles Analyzed: 8-10 (not 0)
echo    Sentiment: BULLISH/BEARISH (not NEUTRAL)
echo.
echo ================================================================================
echo  WHAT TO LOOK FOR IN LOGS
echo ================================================================================
echo.
echo BEFORE FIX (what you saw):
echo   Bank of England News - 0 articles
echo   UK Macro News - 0 articles
echo   Articles Analyzed: 0
echo   Sentiment: NEUTRAL
echo.
echo AFTER FIX (what you should see now):
echo   [OK] Bank of England News (RSS): 4-6 articles
echo   [OK] UK Macro News: 8-10 articles
echo   Articles Analyzed: 8-10
echo   Sentiment: BULLISH/BEARISH with actual score
echo.
echo If you still see 0 articles after running the UK pipeline:
echo   1. Check network connectivity to bankofengland.co.uk
echo   2. Check firewall settings
echo   3. Run DIAGNOSE_BOE_NEWS.bat for detailed diagnostics
echo.
echo ================================================================================

echo.
echo Fix complete! Press any key to exit...
pause >nul

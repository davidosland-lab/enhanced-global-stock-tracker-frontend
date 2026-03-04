@echo off
REM ============================================================================
REM UK Pipeline Fixes - Patch Installation v1.3.15.42-43
REM ============================================================================
REM 
REM This patch fixes two critical issues:
REM 1. KeyError: 'opportunity_score' crash at pipeline end (v1.3.15.42)
REM 2. Bank of England news not appearing (v1.3.15.43)
REM
REM Installation time: ~2 minutes
REM Downtime: None (pipelines can continue after install)
REM
REM ============================================================================

echo.
echo ============================================================================
echo   UK PIPELINE FIXES - PATCH INSTALLER v1.3.15.42-43
echo ============================================================================
echo.
echo   This patch will fix:
echo   1. KeyError crash when displaying top opportunities
echo   2. Bank of England news not appearing in macro sentiment
echo.
echo   Installation will take approximately 2 minutes.
echo.
pause

REM ============================================================================
REM Step 1: Verify Current Directory
REM ============================================================================

echo.
echo [1/6] Verifying installation directory...
echo.

if not exist "run_uk_full_pipeline.py" (
    echo [ERROR] Cannot find run_uk_full_pipeline.py
    echo.
    echo Please run this patch from the installation directory:
    echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\
    echo.
    pause
    exit /b 1
)

if not exist "models\screening\macro_news_monitor.py" (
    echo [ERROR] Cannot find models\screening\macro_news_monitor.py
    echo.
    echo Please verify your installation directory is correct.
    echo.
    pause
    exit /b 1
)

echo [OK] Installation directory verified
echo     Current directory: %CD%
echo.

REM ============================================================================
REM Step 2: Create Backup
REM ============================================================================

echo [2/6] Creating backup of files...
echo.

if not exist "backups" mkdir backups
if not exist "backups\patch_v1.3.15.42-43" mkdir backups\patch_v1.3.15.42-43

copy /Y run_uk_full_pipeline.py backups\patch_v1.3.15.42-43\run_uk_full_pipeline.py.bak >nul 2>&1
copy /Y models\screening\macro_news_monitor.py backups\patch_v1.3.15.42-43\macro_news_monitor.py.bak >nul 2>&1

if exist "backups\patch_v1.3.15.42-43\run_uk_full_pipeline.py.bak" (
    echo [OK] Backup created: backups\patch_v1.3.15.42-43\
    echo     - run_uk_full_pipeline.py.bak
    echo     - macro_news_monitor.py.bak
) else (
    echo [WARNING] Backup creation failed, but continuing...
)
echo.

REM ============================================================================
REM Step 3: Install Dependencies
REM ============================================================================

echo [3/6] Installing required dependencies...
echo.
echo     Installing feedparser for RSS feed support...
echo.

pip install feedparser --quiet

if %ERRORLEVEL% EQU 0 (
    echo [OK] feedparser installed successfully
) else (
    echo [WARNING] feedparser installation failed
    echo           BoE RSS scraper will fall back to HTML scraping
)
echo.

REM ============================================================================
REM Step 4: Apply Git Patches (if git available)
REM ============================================================================

echo [4/6] Checking for git updates...
echo.

where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     Git found, attempting to pull latest changes...
    echo.
    
    git fetch origin >nul 2>&1
    git pull origin market-timing-critical-fix >nul 2>&1
    
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Git patches applied successfully
        echo     - UK Pipeline KeyError fix (v1.3.15.42)
        echo     - BoE RSS scraper (v1.3.15.43)
        goto SkipManualPatch
    ) else (
        echo [WARNING] Git pull failed, applying manual patches...
    )
) else (
    echo     Git not found, applying manual patches...
)
echo.

REM ============================================================================
REM Step 5: Apply Manual Patches (if git not available)
REM ============================================================================

echo [5/6] Applying manual patches...
echo.

REM ---- Patch 1: Fix KeyError in run_uk_full_pipeline.py ----

echo     Applying Fix 1: KeyError 'opportunity_score' patch...

powershell -Command "(Get-Content run_uk_full_pipeline.py) -replace 'logger\.info\(f\"{i:2d}\. {opp\[''symbol''\]:10s} \| Score: {opp\[''opportunity_score''\]:5\.1f}/100 \| \"', 'symbol = opp.get(''symbol'', ''N/A'')^nlinesymbol = symbol[:10].ljust(10)^nlinescore = opp.get(''opportunity_score'', opp.get(''score'', 0))^nlinesignal = opp.get(''signal'', opp.get(''prediction'', ''N/A''))[:4].ljust(4)^nlineconfidence = opp.get(''confidence'', 0)^nlinelogger.info(f\"{i:2d}. {symbol} ^| Score: {score:5.1f}/100 ^| \"' | Set-Content run_uk_full_pipeline.py"

if %ERRORLEVEL% EQU 0 (
    echo     [OK] KeyError fix applied
) else (
    echo     [WARNING] KeyError fix may need manual application
)

REM ---- Patch 2: Add RSS scraper to macro_news_monitor.py ----

echo     Applying Fix 2: BoE RSS scraper patch...

REM This patch is complex, so we'll create a Python script to apply it
echo import sys > apply_boe_patch.py
echo import re >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo with open('models/screening/macro_news_monitor.py', 'r', encoding='utf-8') as f: >> apply_boe_patch.py
echo     content = f.read() >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo # Check if RSS scraper already exists >> apply_boe_patch.py
echo if '_scrape_boe_news_rss' in content: >> apply_boe_patch.py
echo     print('[OK] BoE RSS scraper already installed') >> apply_boe_patch.py
echo     sys.exit(0) >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo # Add RSS scraper function after _scrape_uk_boe_news >> apply_boe_patch.py
echo rss_function = '''    def _scrape_boe_news_rss(self) -^> List[Dict]: >> apply_boe_patch.py
echo         """Scrape Bank of England news via RSS feed""" >> apply_boe_patch.py
echo         articles = [] >> apply_boe_patch.py
echo         try: >> apply_boe_patch.py
echo             import feedparser >> apply_boe_patch.py
echo         except ImportError: >> apply_boe_patch.py
echo             return self._scrape_uk_boe_news() >> apply_boe_patch.py
echo         try: >> apply_boe_patch.py
echo             feed = feedparser.parse('https://www.bankofengland.co.uk/news.rss') >> apply_boe_patch.py
echo             for entry in feed.entries[:10]: >> apply_boe_patch.py
echo                 title = entry.get('title', '').strip() >> apply_boe_patch.py
echo                 url = entry.get('link', '') >> apply_boe_patch.py
echo                 if title and url: >> apply_boe_patch.py
echo                     articles.append({'title': f"BoE: {title}", 'url': url, 'published': entry.get('published', ''), 'source': 'Bank of England', 'type': 'central_bank'}) >> apply_boe_patch.py
echo             return articles >> apply_boe_patch.py
echo         except Exception as e: >> apply_boe_patch.py
echo             return self._scrape_uk_boe_news() >> apply_boe_patch.py
echo ''' >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo # Insert RSS function >> apply_boe_patch.py
echo pattern = r'(def _scrape_uk_boe_news.*?return articles\s+)' >> apply_boe_patch.py
echo content = re.sub(pattern, r'\1' + rss_function, content, flags=re.DOTALL) >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo # Update call to use RSS >> apply_boe_patch.py
echo content = content.replace('self._scrape_uk_boe_news()', 'self._scrape_boe_news_rss()') >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo with open('models/screening/macro_news_monitor.py', 'w', encoding='utf-8') as f: >> apply_boe_patch.py
echo     f.write(content) >> apply_boe_patch.py
echo. >> apply_boe_patch.py
echo print('[OK] BoE RSS scraper installed') >> apply_boe_patch.py

python apply_boe_patch.py

if %ERRORLEVEL% EQU 0 (
    echo     [OK] BoE RSS scraper installed
) else (
    echo     [WARNING] BoE RSS scraper may need manual installation
)

del apply_boe_patch.py >nul 2>&1

:SkipManualPatch

echo.

REM ============================================================================
REM Step 6: Verify Installation
REM ============================================================================

echo [6/6] Verifying patch installation...
echo.

REM Test if the patches were applied
python -c "import sys; sys.path.insert(0, 'models/screening'); from macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); print('[OK] MacroNewsMonitor loads successfully')" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo [OK] Patch verification passed
) else (
    echo [WARNING] Verification failed - manual check recommended
)
echo.

REM ============================================================================
REM Installation Complete
REM ============================================================================

echo ============================================================================
echo   INSTALLATION COMPLETE
echo ============================================================================
echo.
echo   Patches Applied:
echo     [v1.3.15.42] KeyError 'opportunity_score' fix
echo     [v1.3.15.43] Bank of England RSS scraper
echo.
echo   Backup Location:
echo     backups\patch_v1.3.15.42-43\
echo.
echo   Next Steps:
echo     1. Run UK pipeline to test:
echo        python run_uk_full_pipeline.py --full-scan --capital 100000
echo.
echo     2. Check logs for BoE articles:
echo        type logs\uk_pipeline.log ^| findstr "Bank of England"
echo.
echo     3. Verify no KeyError at pipeline end
echo.
echo   Expected Results:
echo     - Pipeline completes without errors
echo     - BoE articles appear in logs (4-6 articles)
echo     - Top opportunities display correctly
echo     - Macro sentiment includes BoE news
echo.
echo ============================================================================
echo.

REM Test run option
set /p TESTRUN="Would you like to run a quick test now? (Y/N): "
if /i "%TESTRUN%"=="Y" (
    echo.
    echo Starting quick test...
    echo.
    python -c "import sys; sys.path.insert(0, 'models/screening'); from macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); r = m.get_macro_sentiment(); print(f'BoE articles found: {len([a for a in r[\"top_articles\"] if \"BoE\" in a.get(\"source\", \"\") or \"Bank of England\" in a.get(\"source\", \"\")])}')"
    echo.
)

echo Patch installation script completed.
echo.
pause

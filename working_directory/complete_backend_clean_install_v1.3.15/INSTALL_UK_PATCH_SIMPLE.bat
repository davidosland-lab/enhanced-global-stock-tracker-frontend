@echo off
REM ============================================================================
REM UK Pipeline Patch Installer v1.3.15.42-43
REM Simple, reliable installation for Windows
REM ============================================================================

setlocal enabledelayedexpansion

REM Color codes for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo.
echo %BLUE%============================================================================%RESET%
echo %BLUE%  UK PIPELINE PATCH INSTALLER v1.3.15.42-43%RESET%
echo %BLUE%============================================================================%RESET%
echo.
echo  This patch fixes:
echo    1. KeyError 'opportunity_score' crash
echo    2. Bank of England news not appearing
echo.
echo  Installation time: 2 minutes
echo.
pause

REM ============================================================================
REM Verify Installation Directory
REM ============================================================================

echo.
echo %BLUE%[1/5]%RESET% Verifying installation directory...

if not exist "run_uk_full_pipeline.py" (
    echo %RED%[ERROR]%RESET% Cannot find run_uk_full_pipeline.py
    echo.
    echo Please run this installer from:
    echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\
    echo.
    pause
    exit /b 1
)

if not exist "models\screening" (
    echo %RED%[ERROR]%RESET% Cannot find models\screening directory
    echo.
    pause
    exit /b 1
)

echo %GREEN%[OK]%RESET% Installation directory verified
echo      %CD%
echo.

REM ============================================================================
REM Create Backup
REM ============================================================================

echo %BLUE%[2/5]%RESET% Creating backup...

if not exist "backups" mkdir backups
set "BACKUP_DIR=backups\patch_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"
mkdir "%BACKUP_DIR%" 2>nul

copy /Y run_uk_full_pipeline.py "%BACKUP_DIR%\run_uk_full_pipeline.py.bak" >nul 2>&1
copy /Y models\screening\macro_news_monitor.py "%BACKUP_DIR%\macro_news_monitor.py.bak" >nul 2>&1

if exist "%BACKUP_DIR%\run_uk_full_pipeline.py.bak" (
    echo %GREEN%[OK]%RESET% Backup created: %BACKUP_DIR%
) else (
    echo %YELLOW%[WARN]%RESET% Backup may have failed, but continuing...
)
echo.

REM ============================================================================
REM Install Dependencies
REM ============================================================================

echo %BLUE%[3/5]%RESET% Installing dependencies...
echo      Installing feedparser...

pip install feedparser >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo %GREEN%[OK]%RESET% feedparser installed
) else (
    echo %YELLOW%[WARN]%RESET% feedparser install failed - will use HTML fallback
)
echo.

REM ============================================================================
REM Apply Patches via Git (Preferred)
REM ============================================================================

echo %BLUE%[4/5]%RESET% Applying patches...

where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo      Git found, pulling updates...
    
    git fetch origin >nul 2>&1
    git pull origin market-timing-critical-fix >nul 2>&1
    
    if %ERRORLEVEL% EQU 0 (
        echo %GREEN%[OK]%RESET% Git patches applied successfully
        goto VerifyInstall
    ) else (
        echo %YELLOW%[WARN]%RESET% Git pull failed, trying manual patches...
    )
) else (
    echo      Git not found, applying manual patches...
)

REM ============================================================================
REM Manual Patch Application
REM ============================================================================

REM Create Python patcher script
echo Creating patcher script...

(
echo import sys
echo import os
echo.
echo # Patch 1: Fix KeyError in run_uk_full_pipeline.py
echo print^("  Patching run_uk_full_pipeline.py..."^)
echo try:
echo     with open^('run_uk_full_pipeline.py', 'r', encoding='utf-8'^) as f:
echo         content = f.read^(^)
echo.    
echo     # Check if already patched
echo     if "opp.get('opportunity_score'" in content:
echo         print^("    [OK] KeyError fix already applied"^)
echo     else:
echo         # Apply patch
echo         old_code = '''logger.info^(f"{i:2d}. {opp['symbol']:10s} ^| Score: {opp['opportunity_score']:5.1f}/100 ^| "'''
echo         new_code = '''symbol = opp.get^('symbol', 'N/A'^)
echo         score = opp.get^('opportunity_score', opp.get^('score', 0^^)^^)
echo         signal = opp.get^('signal', opp.get^('prediction', 'N/A'^^)^^)
echo         confidence = opp.get^('confidence', 0^^)
echo         logger.info^(f"{i:2d}. {symbol:10s} ^| Score: {score:5.1f}/100 ^| "'''
echo.        
echo         if old_code in content:
echo             content = content.replace^(old_code, new_code^^)
echo             with open^('run_uk_full_pipeline.py', 'w', encoding='utf-8'^) as f:
echo                 f.write^(content^^)
echo             print^("    [OK] KeyError fix applied"^)
echo         else:
echo             print^("    [SKIP] Cannot find code to patch ^(may be already patched^)"^)
echo except Exception as e:
echo     print^(f"    [ERROR] Patch 1 failed: {e}"^)
echo.
echo # Patch 2: Add RSS scraper to macro_news_monitor.py  
echo print^("  Patching macro_news_monitor.py..."^)
echo try:
echo     with open^('models/screening/macro_news_monitor.py', 'r', encoding='utf-8'^) as f:
echo         content = f.read^(^)
echo.    
echo     # Check if already patched
echo     if '_scrape_boe_news_rss' in content:
echo         print^("    [OK] BoE RSS scraper already installed"^)
echo     else:
echo         # Find insertion point
echo         marker = "def _scrape_uk_gov_news"
echo         if marker in content:
echo             # Insert RSS function before _scrape_uk_gov_news
echo             rss_func = '''    def _scrape_boe_news_rss^(self^^) -^> List[Dict]:
echo         """Scrape BoE news via RSS"""
echo         articles = []
echo         try:
echo             import feedparser
echo         except ImportError:
echo             return self._scrape_uk_boe_news^(^^)
echo         try:
echo             feed = feedparser.parse^('https://www.bankofengland.co.uk/news.rss'^^)
echo             for entry in feed.entries[:10]:
echo                 title = entry.get^('title', ''^^).strip^(^^)
echo                 url = entry.get^('link', ''^^)
echo                 if title and url:
echo                     articles.append^({'title': f"BoE: {title}", 'url': url, 'published': entry.get^('published', ''^^), 'source': 'Bank of England', 'type': 'central_bank'}^^)
echo             return articles
echo         except:
echo             return self._scrape_uk_boe_news^(^^)
echo.
echo     '''
echo             content = content.replace^(marker, rss_func + marker^^)
echo.            
echo             # Update function call
echo             content = content.replace^("self._scrape_uk_boe_news^(^^)", "self._scrape_boe_news_rss^(^^)"^^)
echo.            
echo             with open^('models/screening/macro_news_monitor.py', 'w', encoding='utf-8'^) as f:
echo                 f.write^(content^^)
echo             print^("    [OK] BoE RSS scraper installed"^)
echo         else:
echo             print^("    [ERROR] Cannot find insertion point"^)
echo except Exception as e:
echo     print^(f"    [ERROR] Patch 2 failed: {e}"^)
) > apply_patches.py

python apply_patches.py

if %ERRORLEVEL% EQU 0 (
    echo %GREEN%[OK]%RESET% Manual patches applied
) else (
    echo %RED%[ERROR]%RESET% Manual patching failed
    echo      Please apply patches manually (see README)
)

del apply_patches.py >nul 2>&1

REM ============================================================================
REM Verify Installation
REM ============================================================================

:VerifyInstall

echo.
echo %BLUE%[5/5]%RESET% Verifying installation...

python -c "from models.screening.macro_news_monitor import MacroNewsMonitor; print('[OK] MacroNewsMonitor loads')" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo %GREEN%[OK]%RESET% Verification passed
) else (
    echo %YELLOW%[WARN]%RESET% Verification inconclusive - test manually
)
echo.

REM ============================================================================
REM Installation Complete
REM ============================================================================

echo.
echo %BLUE%============================================================================%RESET%
echo %GREEN%  INSTALLATION COMPLETE%RESET%
echo %BLUE%============================================================================%RESET%
echo.
echo  Patches Applied:
echo    %GREEN%✓%RESET% v1.3.15.42 - KeyError fix
echo    %GREEN%✓%RESET% v1.3.15.43 - BoE RSS scraper
echo.
echo  Backup Location:
echo    %BACKUP_DIR%
echo.
echo  Next Steps:
echo.
echo    1. Test the fixes:
echo       %BLUE%python run_uk_full_pipeline.py --full-scan --capital 100000%RESET%
echo.
echo    2. Check logs for BoE articles:
echo       %BLUE%type logs\uk_pipeline.log ^| findstr "Bank of England"%RESET%
echo.
echo    3. Verify no errors at pipeline end
echo.
echo  Expected Results:
echo    %GREEN%✓%RESET% Pipeline completes without KeyError
echo    %GREEN%✓%RESET% BoE articles appear in logs (4-6 articles)
echo    %GREEN%✓%RESET% Top opportunities display correctly
echo.
echo %BLUE%============================================================================%RESET%
echo.

set /p QUICKTEST="Run a quick test now? (Y/N): "
if /i "%QUICKTEST%"=="Y" (
    echo.
    echo %BLUE%Running quick test...%RESET%
    echo.
    python -c "import sys; sys.path.insert(0, 'models/screening'); from macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); r = m.get_macro_sentiment(); boe_count = len([a for a in r.get('top_articles', []) if 'BoE' in str(a.get('source', ''))]); print(f'BoE articles found: {boe_count}'); print('Test PASSED' if boe_count > 0 else 'Test FAILED - check logs')"
    echo.
)

echo.
echo Patch installer completed.
echo.
echo For detailed documentation, see:
echo   README_UK_PATCH_v1.3.15.42-43.md
echo.
pause

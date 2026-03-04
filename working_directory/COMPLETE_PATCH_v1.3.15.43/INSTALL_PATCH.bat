@echo off
REM ================================================================================
REM COMPLETE PATCH INSTALLER v1.3.15.43
REM ================================================================================
REM 
REM This patch includes ALL updates from v1.3.15.40 to v1.3.15.43:
REM   - v1.3.15.40: Global sentiment enhancement (US political coverage)
REM   - v1.3.15.41: ASX All Ordinaries chart fix
REM   - v1.3.15.42: UK pipeline KeyError fix
REM   - v1.3.15.43: Bank of England news RSS scraper
REM
REM Files modified:
REM   - run_uk_full_pipeline.py (KeyError fix)
REM   - unified_trading_dashboard.py (ASX chart fix)
REM   - models/screening/macro_news_monitor.py (Global + BoE RSS)
REM   - models/screening/uk_overnight_pipeline.py (UK macro integration)
REM   - models/screening/us_overnight_pipeline.py (US macro integration)
REM   - models/screening/overnight_pipeline.py (AU macro integration)
REM
REM ================================================================================

echo.
echo ================================================================================
echo  COMPLETE PATCH INSTALLER v1.3.15.43
echo ================================================================================
echo.
echo This patch combines 4 major updates:
echo   [1] Global Sentiment Enhancement (v1.3.15.40)
echo   [2] ASX Chart Fix (v1.3.15.41)
echo   [3] UK Pipeline KeyError Fix (v1.3.15.42)
echo   [4] Bank of England RSS Scraper (v1.3.15.43)
echo.
echo Files to be updated: 6 Python files
echo Installation time: ~30 seconds
echo Downtime required: Dashboard restart only (15 seconds)
echo.
pause

REM ================================================================================
REM STEP 1: DETECT INSTALLATION DIRECTORY
REM ================================================================================

echo.
echo [1/6] Detecting installation directory...
echo.

REM Check if we're in the right directory
if exist "run_uk_full_pipeline.py" (
    echo [OK] Running from installation directory
    set INSTALL_DIR=%CD%
    goto :install_files
)

REM Check parent directory
if exist "..\run_uk_full_pipeline.py" (
    echo [OK] Found installation in parent directory
    cd ..
    set INSTALL_DIR=%CD%
    goto :install_files
)

REM Check common installation path
if exist "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\run_uk_full_pipeline.py" (
    echo [OK] Found installation at default path
    cd /d "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
    set INSTALL_DIR=%CD%
    goto :install_files
)

echo [ERROR] Could not find installation directory
echo.
echo Please run this script from one of these locations:
echo   1. The installation directory itself
echo   2. The patch directory (one level inside installation)
echo.
echo Or manually specify the path:
set /p INSTALL_DIR="Enter full path to installation directory: "

if not exist "%INSTALL_DIR%\run_uk_full_pipeline.py" (
    echo [ERROR] Invalid path: %INSTALL_DIR%
    echo Cannot find run_uk_full_pipeline.py
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

:install_files

REM ================================================================================
REM STEP 2: BACKUP EXISTING FILES
REM ================================================================================

echo.
echo [2/6] Creating backup of existing files...
echo.

set BACKUP_DIR=backup_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul
mkdir "%BACKUP_DIR%\models" 2>nul
mkdir "%BACKUP_DIR%\models\screening" 2>nul

if exist "run_uk_full_pipeline.py" copy /Y "run_uk_full_pipeline.py" "%BACKUP_DIR%\" >nul
if exist "unified_trading_dashboard.py" copy /Y "unified_trading_dashboard.py" "%BACKUP_DIR%\" >nul
if exist "models\screening\macro_news_monitor.py" copy /Y "models\screening\macro_news_monitor.py" "%BACKUP_DIR%\models\screening\" >nul
if exist "models\screening\uk_overnight_pipeline.py" copy /Y "models\screening\uk_overnight_pipeline.py" "%BACKUP_DIR%\models\screening\" >nul
if exist "models\screening\us_overnight_pipeline.py" copy /Y "models\screening\us_overnight_pipeline.py" "%BACKUP_DIR%\models\screening\" >nul
if exist "models\screening\overnight_pipeline.py" copy /Y "models\screening\overnight_pipeline.py" "%BACKUP_DIR%\models\screening\" >nul

echo [OK] Backup created: %BACKUP_DIR%
echo.

REM ================================================================================
REM STEP 3: INSTALL PYTHON FILES
REM ================================================================================

echo.
echo [3/6] Installing updated Python files...
echo.

REM Determine patch location
if exist "COMPLETE_PATCH_v1.3.15.43\run_uk_full_pipeline.py" (
    set PATCH_DIR=COMPLETE_PATCH_v1.3.15.43
) else if exist "..\COMPLETE_PATCH_v1.3.15.43\run_uk_full_pipeline.py" (
    set PATCH_DIR=..\COMPLETE_PATCH_v1.3.15.43
) else if exist "run_uk_full_pipeline.py" (
    REM We're already in the patch directory
    set PATCH_DIR=.
) else (
    echo [ERROR] Cannot find patch files
    echo Please ensure COMPLETE_PATCH_v1.3.15.43 directory exists
    pause
    exit /b 1
)

echo Copying from: %PATCH_DIR%
echo.

REM Copy root-level Python files
if exist "%PATCH_DIR%\run_uk_full_pipeline.py" (
    copy /Y "%PATCH_DIR%\run_uk_full_pipeline.py" "%INSTALL_DIR%\" >nul
    echo   [OK] run_uk_full_pipeline.py (KeyError fix)
) else (
    echo   [SKIP] run_uk_full_pipeline.py (not found in patch)
)

if exist "%PATCH_DIR%\unified_trading_dashboard.py" (
    copy /Y "%PATCH_DIR%\unified_trading_dashboard.py" "%INSTALL_DIR%\" >nul
    echo   [OK] unified_trading_dashboard.py (ASX chart fix)
) else (
    echo   [SKIP] unified_trading_dashboard.py (not found in patch)
)

REM Copy screening modules
if exist "%PATCH_DIR%\models\screening\macro_news_monitor.py" (
    copy /Y "%PATCH_DIR%\models\screening\macro_news_monitor.py" "%INSTALL_DIR%\models\screening\" >nul
    echo   [OK] models/screening/macro_news_monitor.py (Global + BoE RSS)
) else (
    echo   [SKIP] macro_news_monitor.py (not found in patch)
)

if exist "%PATCH_DIR%\models\screening\uk_overnight_pipeline.py" (
    copy /Y "%PATCH_DIR%\models\screening\uk_overnight_pipeline.py" "%INSTALL_DIR%\models\screening\" >nul
    echo   [OK] models/screening/uk_overnight_pipeline.py (UK macro)
) else (
    echo   [SKIP] uk_overnight_pipeline.py (not found in patch)
)

if exist "%PATCH_DIR%\models\screening\us_overnight_pipeline.py" (
    copy /Y "%PATCH_DIR%\models\screening\us_overnight_pipeline.py" "%INSTALL_DIR%\models\screening\" >nul
    echo   [OK] models/screening/us_overnight_pipeline.py (US macro)
) else (
    echo   [SKIP] us_overnight_pipeline.py (not found in patch)
)

if exist "%PATCH_DIR%\models\screening\overnight_pipeline.py" (
    copy /Y "%PATCH_DIR%\models\screening\overnight_pipeline.py" "%INSTALL_DIR%\models\screening\" >nul
    echo   [OK] models/screening/overnight_pipeline.py (AU macro)
) else (
    echo   [SKIP] overnight_pipeline.py (not found in patch)
)

echo.
echo [OK] All Python files installed successfully
echo.

REM ================================================================================
REM STEP 4: INSTALL DEPENDENCIES
REM ================================================================================

echo.
echo [4/6] Installing required Python packages...
echo.

echo Installing feedparser (required for BoE RSS scraper)...
pip install feedparser --quiet --disable-pip-version-check
if %errorlevel% equ 0 (
    echo   [OK] feedparser installed
) else (
    echo   [WARNING] feedparser installation failed - BoE RSS may not work
    echo   [INFO] You can install manually: pip install feedparser
)

echo.

REM ================================================================================
REM STEP 5: VERIFY INSTALLATION
REM ================================================================================

echo.
echo [5/6] Verifying installation...
echo.

set ERROR_COUNT=0

if not exist "run_uk_full_pipeline.py" (
    echo   [ERROR] run_uk_full_pipeline.py missing
    set /a ERROR_COUNT+=1
)

if not exist "unified_trading_dashboard.py" (
    echo   [ERROR] unified_trading_dashboard.py missing
    set /a ERROR_COUNT+=1
)

if not exist "models\screening\macro_news_monitor.py" (
    echo   [ERROR] macro_news_monitor.py missing
    set /a ERROR_COUNT+=1
)

if not exist "models\screening\uk_overnight_pipeline.py" (
    echo   [ERROR] uk_overnight_pipeline.py missing
    set /a ERROR_COUNT+=1
)

if not exist "models\screening\us_overnight_pipeline.py" (
    echo   [ERROR] us_overnight_pipeline.py missing
    set /a ERROR_COUNT+=1
)

if not exist "models\screening\overnight_pipeline.py" (
    echo   [ERROR] overnight_pipeline.py missing
    set /a ERROR_COUNT+=1
)

if %ERROR_COUNT% gtr 0 (
    echo.
    echo [ERROR] Installation verification failed: %ERROR_COUNT% file(s) missing
    echo [INFO] Backup available at: %BACKUP_DIR%
    pause
    exit /b 1
)

echo [OK] All files verified
echo.

REM ================================================================================
REM STEP 6: FINAL INSTRUCTIONS
REM ================================================================================

echo.
echo [6/6] Installation complete!
echo.
echo ================================================================================
echo  PATCH INSTALLATION SUMMARY
echo ================================================================================
echo.
echo Status: SUCCESS
echo Version: v1.3.15.43
echo Files updated: 6 Python files
echo Backup location: %BACKUP_DIR%
echo.
echo ================================================================================
echo  WHAT'S BEEN FIXED
echo ================================================================================
echo.
echo [v1.3.15.40] Global Sentiment Enhancement
echo   - Expanded global news sources (Reuters, BBC, White House)
echo   - Increased macro weight from 20%% to 35%%
echo   - Enhanced US political coverage (tariffs, trade wars)
echo.
echo [v1.3.15.41] ASX All Ordinaries Chart Fix
echo   - Fixed midnight-spanning session handling
echo   - Corrected reference price calculation
echo   - Improved time filtering for 05:00-06:00 GMT
echo.
echo [v1.3.15.42] UK Pipeline KeyError Fix
echo   - Safe dictionary access with fallbacks
echo   - No more crashes on missing opportunity_score
echo   - Graceful handling of different data formats
echo.
echo [v1.3.15.43] Bank of England RSS Scraper
echo   - Added RSS feed scraper for BoE news
echo   - More reliable than HTML scraping
echo   - Captures MPC decisions, rate announcements, speeches
echo.
echo ================================================================================
echo  NEXT STEPS
echo ================================================================================
echo.
echo 1. RESTART DASHBOARD (if running):
echo    - Press Ctrl+C to stop current dashboard
echo    - Run: python unified_trading_dashboard.py
echo    - Dashboard will reload with ASX chart fix
echo.
echo 2. TEST UK PIPELINE:
echo    - Run: python run_uk_full_pipeline.py --full-scan --capital 100000
echo    - Should complete without KeyError
echo    - Should show BoE news articles in logs
echo.
echo 3. VERIFY BoE NEWS:
echo    - Check logs\uk_pipeline.log for:
echo      "Bank of England News (RSS): X articles"
echo    - Should see 4-6 BoE articles
echo.
echo 4. CHECK MACRO SENTIMENT:
echo    - UK pipeline logs should show:
echo      "Macro Impact: X points (35%% weight)"
echo    - Sentiment adjusted for global news
echo.
echo ================================================================================
echo  VERIFICATION COMMANDS
echo ================================================================================
echo.
echo Test BoE RSS scraper:
echo   python -c "from models.screening.macro_news_monitor import MacroNewsMonitor; m = MacroNewsMonitor('UK'); print(f'BoE articles: {len([a for a in m.get_macro_sentiment()[\"top_articles\"] if \"BoE\" in a[\"source\"]])}')"
echo.
echo Check dashboard ASX chart:
echo   Open http://localhost:8050 and check 24-Hour Market Performance
echo.
echo Run UK pipeline:
echo   python run_uk_full_pipeline.py --full-scan --capital 100000
echo.
echo ================================================================================
echo  ROLLBACK (if needed)
echo ================================================================================
echo.
echo If you experience issues, restore from backup:
echo   xcopy /Y /S "%BACKUP_DIR%\*.*" .
echo.
echo ================================================================================
echo  SUPPORT
echo ================================================================================
echo.
echo Documentation files included in patch:
echo   - GLOBAL_SENTIMENT_ENHANCEMENT_v1.3.15.40.md
echo   - ASX_CHART_FIX_v1.3.15.41.md
echo   - UK_PIPELINE_KEYERROR_FIX_v1.3.15.42.md
echo   - BOE_NEWS_NOT_APPEARING_FIX.md
echo.
echo For issues:
echo   1. Check logs\uk_pipeline.log for errors
echo   2. Verify feedparser installed: pip list ^| findstr feedparser
echo   3. Review documentation files for troubleshooting
echo.
echo ================================================================================

echo.
echo Installation complete! Press any key to exit...
pause >nul

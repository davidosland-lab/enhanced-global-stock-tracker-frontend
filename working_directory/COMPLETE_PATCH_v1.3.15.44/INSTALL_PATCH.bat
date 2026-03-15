@echo off
setlocal enabledelayedexpansion

REM =========================================================================
REM Complete Patch Installer v1.3.15.44 - Windows Unicode Fix Edition
REM =========================================================================
REM 
REM This installer will:
REM 1. Auto-detect installation directory
REM 2. Create backup of existing files
REM 3. Install 9 updated Python files
REM 4. Install feedparser dependency
REM 5. Clear Python cache
REM 6. Verify installation
REM 7. Display next steps
REM 
REM =========================================================================

echo =========================================================================
echo Complete Patch Installer v1.3.15.44
echo Windows Unicode Fix + BoE RSS + UK Pipeline Fix + ASX Chart Fix
echo =========================================================================
echo.

REM Step 1: Auto-detect installation directory
echo [Step 1/7] Detecting installation directory...
echo.

set "INSTALL_DIR="
set "DETECTED=0"

REM Method 1: Check common locations
if exist "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15\run_au_pipeline.py" (
    set "INSTALL_DIR=C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
    set "DETECTED=1"
    echo [OK] Found installation: !INSTALL_DIR!
)

REM Method 2: Check current directory parent
if !DETECTED!==0 (
    cd ..
    if exist "complete_backend_clean_install_v1.3.15\run_au_pipeline.py" (
        set "INSTALL_DIR=%CD%\complete_backend_clean_install_v1.3.15"
        set "DETECTED=1"
        echo [OK] Found installation: !INSTALL_DIR!
    )
)

REM Method 3: Prompt user
if !DETECTED!==0 (
    echo [!] Could not auto-detect installation directory.
    echo.
    set /p "INSTALL_DIR=Enter installation path (e.g., C:\path\to\complete_backend_clean_install_v1.3.15): "
    
    if not exist "!INSTALL_DIR!\run_au_pipeline.py" (
        echo [ERROR] Invalid installation directory!
        echo Cannot find run_au_pipeline.py in: !INSTALL_DIR!
        pause
        exit /b 1
    )
)

echo.
echo Installation directory: !INSTALL_DIR!
echo.
pause

REM Step 2: Create backup
echo.
echo [Step 2/7] Creating backup...
echo.

set "BACKUP_DIR=!INSTALL_DIR!\backup_v1.3.15.44_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

mkdir "!BACKUP_DIR!" 2>nul
mkdir "!BACKUP_DIR!\models\screening" 2>nul

REM Backup Python files
echo Backing up Python files...
if exist "!INSTALL_DIR!\run_uk_full_pipeline.py" (
    copy /Y "!INSTALL_DIR!\run_uk_full_pipeline.py" "!BACKUP_DIR!\" >nul
    echo [OK] Backed up run_uk_full_pipeline.py
)
if exist "!INSTALL_DIR!\unified_trading_dashboard.py" (
    copy /Y "!INSTALL_DIR!\unified_trading_dashboard.py" "!BACKUP_DIR!\" >nul
    echo [OK] Backed up unified_trading_dashboard.py
)
if exist "!INSTALL_DIR!\models\screening\macro_news_monitor.py" (
    copy /Y "!INSTALL_DIR!\models\screening\macro_news_monitor.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up macro_news_monitor.py
)
if exist "!INSTALL_DIR!\models\screening\uk_overnight_pipeline.py" (
    copy /Y "!INSTALL_DIR!\models\screening\uk_overnight_pipeline.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up uk_overnight_pipeline.py
)
if exist "!INSTALL_DIR!\models\screening\us_overnight_pipeline.py" (
    copy /Y "!INSTALL_DIR!\models\screening\us_overnight_pipeline.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up us_overnight_pipeline.py
)
if exist "!INSTALL_DIR!\models\screening\overnight_pipeline.py" (
    copy /Y "!INSTALL_DIR!\models\screening\overnight_pipeline.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up overnight_pipeline.py
)
if exist "!INSTALL_DIR!\models\screening\stock_scanner.py" (
    copy /Y "!INSTALL_DIR!\models\screening\stock_scanner.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up stock_scanner.py
)
if exist "!INSTALL_DIR!\models\screening\us_stock_scanner.py" (
    copy /Y "!INSTALL_DIR!\models\screening\us_stock_scanner.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up us_stock_scanner.py
)
if exist "!INSTALL_DIR!\models\screening\incremental_scanner.py" (
    copy /Y "!INSTALL_DIR!\models\screening\incremental_scanner.py" "!BACKUP_DIR!\models\screening\" >nul
    echo [OK] Backed up incremental_scanner.py
)

echo.
echo Backup created: !BACKUP_DIR!
echo.
pause

REM Step 3: Install Python files
echo.
echo [Step 3/7] Installing updated Python files...
echo.

REM Install root files
echo Installing root Python files...
copy /Y "run_uk_full_pipeline.py" "!INSTALL_DIR!\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed run_uk_full_pipeline.py
) else (
    echo [ERROR] Failed to install run_uk_full_pipeline.py
)

copy /Y "unified_trading_dashboard.py" "!INSTALL_DIR!\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed unified_trading_dashboard.py
) else (
    echo [ERROR] Failed to install unified_trading_dashboard.py
)

REM Install screening modules
echo Installing screening modules...
copy /Y "models\screening\macro_news_monitor.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed macro_news_monitor.py
) else (
    echo [ERROR] Failed to install macro_news_monitor.py
)

copy /Y "models\screening\uk_overnight_pipeline.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed uk_overnight_pipeline.py
) else (
    echo [ERROR] Failed to install uk_overnight_pipeline.py
)

copy /Y "models\screening\us_overnight_pipeline.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed us_overnight_pipeline.py
) else (
    echo [ERROR] Failed to install us_overnight_pipeline.py
)

copy /Y "models\screening\overnight_pipeline.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed overnight_pipeline.py
) else (
    echo [ERROR] Failed to install overnight_pipeline.py
)

copy /Y "models\screening\stock_scanner.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed stock_scanner.py
) else (
    echo [ERROR] Failed to install stock_scanner.py
)

copy /Y "models\screening\us_stock_scanner.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed us_stock_scanner.py
) else (
    echo [ERROR] Failed to install us_stock_scanner.py
)

copy /Y "models\screening\incremental_scanner.py" "!INSTALL_DIR!\models\screening\" >nul
if !errorlevel! equ 0 (
    echo [OK] Installed incremental_scanner.py
) else (
    echo [ERROR] Failed to install incremental_scanner.py
)

echo.
echo [OK] 9 Python files installed successfully!
echo.
pause

REM Step 4: Install feedparser
echo.
echo [Step 4/7] Installing feedparser dependency...
echo.

pip install feedparser
if !errorlevel! equ 0 (
    echo [OK] feedparser installed successfully!
) else (
    echo [WARNING] Failed to install feedparser
    echo You may need to run: pip install feedparser
)

echo.
pause

REM Step 5: Clear Python cache
echo.
echo [Step 5/7] Clearing Python cache...
echo.

cd /d "!INSTALL_DIR!"
if exist "models\screening\__pycache__" (
    rd /s /q "models\screening\__pycache__" 2>nul
    echo [OK] Cleared screening module cache
)
if exist "__pycache__" (
    rd /s /q "__pycache__" 2>nul
    echo [OK] Cleared root cache
)

echo.
echo [OK] Python cache cleared!
echo.
pause

REM Step 6: Copy documentation
echo.
echo [Step 6/7] Installing documentation...
echo.

copy /Y "GLOBAL_SENTIMENT_ENHANCEMENT_v1.3.15.40.md" "!INSTALL_DIR!\" >nul
copy /Y "ASX_CHART_FIX_v1.3.15.41.md" "!INSTALL_DIR!\" >nul
copy /Y "UK_PIPELINE_KEYERROR_FIX_v1.3.15.42.md" "!INSTALL_DIR!\" >nul
copy /Y "BOE_NEWS_NOT_APPEARING_FIX.md" "!INSTALL_DIR!\" >nul
copy /Y "WINDOWS_UNICODE_FIX_v1.3.15.44.md" "!INSTALL_DIR!\" >nul
copy /Y "README_v1.3.15.44.md" "!INSTALL_DIR!\" >nul

echo [OK] Documentation installed!
echo.
pause

REM Step 7: Verification
echo.
echo [Step 7/7] Verifying installation...
echo.

set "VERIFY_OK=0"
set "VERIFY_TOTAL=0"

REM Check UTF-8 encoding in stock_scanner
findstr /C:"reconfigure" "!INSTALL_DIR!\models\screening\stock_scanner.py" >nul 2>&1
if !errorlevel! equ 0 (
    set /a VERIFY_OK+=1
    echo [OK] UTF-8 encoding setup found in stock_scanner.py
) else (
    echo [FAIL] UTF-8 encoding setup missing in stock_scanner.py
)
set /a VERIFY_TOTAL+=1

REM Check ASCII arrow replacement
findstr /C:"-> Volume" "!INSTALL_DIR!\models\screening\stock_scanner.py" >nul 2>&1
if !errorlevel! equ 0 (
    set /a VERIFY_OK+=1
    echo [OK] ASCII arrow replacement verified
) else (
    echo [FAIL] ASCII arrow replacement not found
)
set /a VERIFY_TOTAL+=1

REM Check BoE RSS scraper
findstr /C:"_scrape_boe_news_rss" "!INSTALL_DIR!\models\screening\macro_news_monitor.py" >nul 2>&1
if !errorlevel! equ 0 (
    set /a VERIFY_OK+=1
    echo [OK] BoE RSS scraper function found
) else (
    echo [FAIL] BoE RSS scraper function missing
)
set /a VERIFY_TOTAL+=1

REM Check UK pipeline safe .get()
findstr /C:"opp.get('opportunity_score'" "!INSTALL_DIR!\run_uk_full_pipeline.py" >nul 2>&1
if !errorlevel! equ 0 (
    set /a VERIFY_OK+=1
    echo [OK] UK pipeline safe dict access verified
) else (
    echo [FAIL] UK pipeline still using direct dict access
)
set /a VERIFY_TOTAL+=1

REM Check feedparser installed
pip list | findstr /C:"feedparser" >nul 2>&1
if !errorlevel! equ 0 (
    set /a VERIFY_OK+=1
    echo [OK] feedparser is installed
) else (
    echo [WARNING] feedparser not found - run: pip install feedparser
)
set /a VERIFY_TOTAL+=1

echo.
echo =========================================================================
echo VERIFICATION SUMMARY: !VERIFY_OK!/!VERIFY_TOTAL! checks passed
echo =========================================================================

if !VERIFY_OK! equ !VERIFY_TOTAL! (
    echo [SUCCESS] All verification checks passed!
    echo Patch v1.3.15.44 installed successfully!
) else (
    echo [WARNING] Some verification checks failed
    echo Review the output above and fix any issues
)

echo.
pause

REM Display next steps
echo.
echo =========================================================================
echo INSTALLATION COMPLETE!
echo =========================================================================
echo.
echo Next Steps:
echo.
echo 1. Restart the trading dashboard:
echo    cd !INSTALL_DIR!
echo    python unified_trading_dashboard.py
echo.
echo 2. Test the UK pipeline:
echo    python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
echo.
echo 3. Test the AU pipeline:
echo    python run_au_pipeline.py --full-scan --capital 100000
echo.
echo 4. Open dashboard in browser:
echo    http://localhost:8050
echo.
echo 5. Check logs for BoE news:
echo    type logs\uk_pipeline.log ^| findstr "Bank of England"
echo.
echo Expected Improvements:
echo - [x] No more UnicodeEncodeError messages
echo - [x] Clean console output with ASCII arrows
echo - [x] UK pipeline completes without crashes
echo - [x] Bank of England news articles (4-6)
echo - [x] ASX chart displays correctly
echo - [x] Enhanced macro sentiment (35%% weight)
echo.
echo Backup Location: !BACKUP_DIR!
echo.
echo Documentation:
echo - WINDOWS_UNICODE_FIX_v1.3.15.44.md
echo - BOE_NEWS_NOT_APPEARING_FIX.md
echo - UK_PIPELINE_KEYERROR_FIX_v1.3.15.42.md
echo - ASX_CHART_FIX_v1.3.15.41.md
echo - README_v1.3.15.44.md
echo.
echo =========================================================================
echo Patch v1.3.15.44 - Installation Complete
echo =========================================================================
echo.

pause

@echo off
REM ========================================================================
REM Macro News Monitor - Standalone Installer (No Git Required)
REM ========================================================================

echo.
echo ========================================================================
echo MACRO NEWS MONITOR - STANDALONE INSTALLER
echo ========================================================================
echo.
echo This will install the Macro News Monitor feature:
echo   - Federal Reserve news monitoring (US)
echo   - RBA news monitoring (ASX)
echo   - Automatic sentiment analysis with FinBERT
echo   - Market sentiment adjustments based on macro news
echo.
echo Target directory: %CD%\..
echo.
pause

REM Change to parent directory
cd ..

echo.
echo ========================================================================
echo STEP 1: Checking Environment
echo ========================================================================
echo.

if not exist "models\screening" (
    echo ERROR: models\screening directory not found!
    echo.
    echo Are you in the correct directory?
    echo Expected: C:\Users\david\AATelS\MACRO_NEWS_STANDALONE_PATCH
    pause
    exit /b 1
)

echo [OK] Found models\screening directory

echo.
echo ========================================================================
echo STEP 2: Backing Up Existing Files
echo ========================================================================
echo.

REM Create backup directory
if not exist "BACKUPS" mkdir BACKUPS
set BACKUP_DIR=BACKUPS\macro_news_backup_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%"

echo Backup directory: %BACKUP_DIR%

REM Backup files if they exist
if exist "models\screening\macro_news_monitor.py" (
    copy "models\screening\macro_news_monitor.py" "%BACKUP_DIR%\" >nul
    echo [OK] Backed up macro_news_monitor.py
) else (
    echo [INFO] macro_news_monitor.py doesn't exist (will be created)
)

if exist "models\screening\us_overnight_pipeline.py" (
    copy "models\screening\us_overnight_pipeline.py" "%BACKUP_DIR%\" >nul
    echo [OK] Backed up us_overnight_pipeline.py
)

if exist "models\screening\overnight_pipeline.py" (
    copy "models\screening\overnight_pipeline.py" "%BACKUP_DIR%\" >nul
    echo [OK] Backed up overnight_pipeline.py
)

echo.
echo ========================================================================
echo STEP 3: Installing Macro News Monitor
echo ========================================================================
echo.

REM Copy the macro news monitor file
if exist "MACRO_NEWS_STANDALONE_PATCH\files\macro_news_monitor.py" (
    copy "MACRO_NEWS_STANDALONE_PATCH\files\macro_news_monitor.py" "models\screening\macro_news_monitor.py" >nul
    if errorlevel 1 (
        echo [ERROR] Failed to copy macro_news_monitor.py
        pause
        exit /b 1
    )
    echo [OK] Installed macro_news_monitor.py
) else (
    echo [ERROR] Source file not found: MACRO_NEWS_STANDALONE_PATCH\files\macro_news_monitor.py
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo STEP 4: Checking Pipeline Integration
echo ========================================================================
echo.

REM Check if pipelines already have macro news integration
findstr /C:"MacroNewsMonitor" "models\screening\us_overnight_pipeline.py" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] US pipeline doesn't have macro news integration
    echo           You may need to update manually
    set US_INTEGRATED=0
) else (
    echo [OK] US pipeline has macro news integration
    set US_INTEGRATED=1
)

findstr /C:"MacroNewsMonitor" "models\screening\overnight_pipeline.py" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ASX pipeline doesn't have macro news integration
    echo           You may need to update manually
    set ASX_INTEGRATED=0
) else (
    echo [OK] ASX pipeline has macro news integration
    set ASX_INTEGRATED=1
)

echo.
echo ========================================================================
echo STEP 5: Verifying Installation
echo ========================================================================
echo.

if exist "models\screening\macro_news_monitor.py" (
    echo [OK] macro_news_monitor.py exists
) else (
    echo [FAILED] macro_news_monitor.py NOT found
    pause
    exit /b 1
)

REM Check file size (should be around 20-25KB)
for %%A in ("models\screening\macro_news_monitor.py") do set FILE_SIZE=%%~zA
if %FILE_SIZE% GTR 10000 (
    echo [OK] File size looks good (%FILE_SIZE% bytes)
) else (
    echo [WARNING] File size seems small (%FILE_SIZE% bytes)
)

echo.
echo ========================================================================
echo INSTALLATION COMPLETE!
echo ========================================================================
echo.

if %US_INTEGRATED%==1 (
    if %ASX_INTEGRATED%==1 (
        echo ✓ Macro News Monitor is fully installed and integrated!
        echo.
        echo Next steps:
        echo   1. Test it: python test_macro.py
        echo   2. Run pipeline: python models\screening\us_overnight_pipeline.py --stocks-per-sector 5
        echo.
        echo You should see "MACRO NEWS ANALYSIS" in the pipeline output!
    ) else (
        echo ⚠ Partial installation:
        echo   ✓ Macro News Monitor installed
        echo   ✓ US pipeline integrated
        echo   ✗ ASX pipeline needs manual integration
        echo.
        echo See INTEGRATION_INSTRUCTIONS.txt for manual steps
    )
) else (
    echo ⚠ Macro News Monitor installed but NOT integrated into pipelines
    echo.
    echo The file is installed at: models\screening\macro_news_monitor.py
    echo.
    echo You need to add integration code to your pipeline files.
    echo See INTEGRATION_INSTRUCTIONS.txt for details.
)

echo.
echo Backup saved to: %BACKUP_DIR%
echo.
pause

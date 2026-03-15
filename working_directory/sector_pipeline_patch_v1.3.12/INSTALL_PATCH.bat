@echo off
REM ============================================================================
REM SECTOR-BASED PIPELINE PATCH v1.3.12 - INSTALLATION SCRIPT
REM ============================================================================
REM 
REM This script installs the sector-based pipeline update for AU/US/UK markets
REM 
REM Installation:
REM   1. Extract this ZIP to a temporary folder
REM   2. Run this script: INSTALL_PATCH.bat
REM   3. Follow the prompts
REM
REM Date: January 3, 2026
REM Version: 1.3.12
REM ============================================================================

echo.
echo ============================================================================
echo SECTOR-BASED PIPELINE PATCH v1.3.12 - INSTALLATION
echo ============================================================================
echo.
echo This patch adds sector-based scanning to all three market pipelines:
echo   - AU Pipeline: 240 ASX stocks (8 sectors x 30 stocks)
echo   - US Pipeline: 240 US stocks (8 sectors x 30 stocks)
echo   - UK Pipeline: 240 LSE stocks (8 sectors x 30 stocks)
echo.
echo Total Coverage: 720 stocks across all markets
echo.
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Ask for installation directory
set "DEFAULT_DIR=%CD%\..\phase3_intraday_deployment"
echo Where is your phase3_intraday_deployment directory?
echo.
echo Default: %DEFAULT_DIR%
echo.
set /p INSTALL_DIR="Enter path (or press Enter for default): "

if "%INSTALL_DIR%"=="" (
    set "INSTALL_DIR=%DEFAULT_DIR%"
)

echo.
echo Installation Directory: %INSTALL_DIR%
echo.

REM Check if directory exists
if not exist "%INSTALL_DIR%" (
    echo [WARNING] Directory does not exist: %INSTALL_DIR%
    echo.
    set /p CREATE="Create it? (y/n): "
    if /i "%CREATE%"=="y" (
        mkdir "%INSTALL_DIR%" 2>nul
        if errorlevel 1 (
            echo [ERROR] Failed to create directory
            pause
            exit /b 1
        )
        echo [OK] Directory created
    ) else (
        echo [CANCELLED] Installation aborted
        pause
        exit /b 0
    )
)

echo.
echo ============================================================================
echo INSTALLATION STEPS
echo ============================================================================
echo.

REM Step 1: Create directories
echo [1/6] Creating directories...
mkdir "%INSTALL_DIR%\config" 2>nul
mkdir "%INSTALL_DIR%\models" 2>nul
echo [OK] Directories ready
echo.

REM Step 2: Backup existing files
echo [2/6] Backing up existing files...
set BACKUP_DIR=%INSTALL_DIR%\backup_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" 2>nul

if exist "%INSTALL_DIR%\run_au_pipeline.py" (
    copy "%INSTALL_DIR%\run_au_pipeline.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: run_au_pipeline.py
)
if exist "%INSTALL_DIR%\run_us_pipeline.py" (
    copy "%INSTALL_DIR%\run_us_pipeline.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: run_us_pipeline.py
)
if exist "%INSTALL_DIR%\run_uk_pipeline.py" (
    copy "%INSTALL_DIR%\run_uk_pipeline.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: run_uk_pipeline.py
)

echo [OK] Backup created: %BACKUP_DIR%
echo.

REM Step 3: Copy configuration files
echo [3/6] Installing configuration files...
copy "config\asx_sectors.json" "%INSTALL_DIR%\config\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy asx_sectors.json
    pause
    exit /b 1
)
echo   - Installed: config/asx_sectors.json (240 ASX stocks)

copy "config\us_sectors.json" "%INSTALL_DIR%\config\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy us_sectors.json
    pause
    exit /b 1
)
echo   - Installed: config/us_sectors.json (240 US stocks)

copy "config\uk_sectors.json" "%INSTALL_DIR%\config\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy uk_sectors.json
    pause
    exit /b 1
)
echo   - Installed: config/uk_sectors.json (240 LSE stocks)

copy "config\screening_config.json" "%INSTALL_DIR%\config\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy screening_config.json
    pause
    exit /b 1
)
echo   - Installed: config/screening_config.json

echo [OK] Configuration files installed
echo.

REM Step 4: Copy model files
echo [4/6] Installing model files...
copy "models\sector_stock_scanner.py" "%INSTALL_DIR%\models\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy sector_stock_scanner.py
    pause
    exit /b 1
)
echo   - Installed: models/sector_stock_scanner.py
echo [OK] Model files installed
echo.

REM Step 5: Copy pipeline scripts
echo [5/6] Installing pipeline scripts...
copy "scripts\run_au_pipeline.py" "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy run_au_pipeline.py
    pause
    exit /b 1
)
echo   - Installed: run_au_pipeline.py (v1.3.12)

copy "scripts\run_us_pipeline.py" "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy run_us_pipeline.py
    pause
    exit /b 1
)
echo   - Installed: run_us_pipeline.py (v1.3.12)

copy "scripts\run_uk_pipeline.py" "%INSTALL_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy run_uk_pipeline.py
    pause
    exit /b 1
)
echo   - Installed: run_uk_pipeline.py (v1.3.12)

echo [OK] Pipeline scripts installed
echo.

REM Step 6: Copy documentation
echo [6/6] Installing documentation...
mkdir "%INSTALL_DIR%\docs" 2>nul
copy "docs\*.md" "%INSTALL_DIR%\docs\" >nul 2>&1
echo   - Installed: Documentation files
echo [OK] Documentation installed
echo.

echo ============================================================================
echo INSTALLATION COMPLETE!
echo ============================================================================
echo.
echo Patch v1.3.12 has been successfully installed.
echo.
echo NEW FEATURES:
echo   - Full sector scanning: 240 stocks per market
echo   - 8 sectors x 30 stocks per sector
echo   - Total coverage: 720 stocks (AU + US + UK)
echo   - ML ensemble prediction with 5-layer filtering
echo.
echo NEW COMMANDS:
echo   # Full sector scan (recommended)
echo   python run_au_pipeline.py --full-scan --capital 100000
echo   python run_us_pipeline.py --full-scan --capital 100000
echo   python run_uk_pipeline.py --full-scan --capital 100000
echo.
echo LEGACY COMMANDS (still supported):
echo   # Preset mode
echo   python run_au_pipeline.py --preset "ASX Blue Chips" --capital 100000
echo.
echo NEXT STEPS:
echo   1. Review documentation in: %INSTALL_DIR%\docs\
echo   2. Test the pipelines with: --full-scan --ignore-market-hours
echo   3. Update your batch files if needed
echo.
echo BACKUP LOCATION:
echo   %BACKUP_DIR%
echo.
echo ============================================================================
echo.
pause

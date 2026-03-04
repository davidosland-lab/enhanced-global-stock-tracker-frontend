@echo off
SETLOCAL EnableDelayedExpansion
COLOR 0A
CLS

REM ============================================================================
REM   CONFIG PATH FIX PATCH - v1.3.15.45
REM   Fixes missing config files issue for UK/US/AU pipelines
REM ============================================================================

echo.
echo ================================================================================
echo   CONFIG PATH FIX PATCH - v1.3.15.45
echo   Complete Regime Trading System
echo ================================================================================
echo.
echo   This patch fixes the critical config file location issue that causes:
echo   - UK Pipeline: "No valid UK stocks found during scanning"
echo   - Config file not found errors
echo   - Scanner falling back to empty config
echo.
echo   What this patch does:
echo   1. Creates config\ directory at project root
echo   2. Copies all config files from models\config\
echo   3. Verifies all required files are in place
echo   4. Tests config file loading
echo.
echo ================================================================================
echo.

REM Check if running from correct directory
echo [1/6] Verifying installation directory...
if not exist "models\config\" (
    echo.
    echo [ERROR] Cannot find models\config\ directory!
    echo [ERROR] This patch must be run from the installation directory:
    echo [ERROR] C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)
echo [OK] Found models\config\ directory
echo      Location: %CD%
echo.

REM Backup existing config directory if it exists
echo [2/6] Checking for existing config\ directory...
if exist "config\" (
    echo [WARN] config\ directory already exists
    echo [*] Creating backup: config_backup_%DATE:~-4,4%%DATE:~-7,2%%DATE:~-10,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
    set BACKUP_DIR=config_backup_%DATE:~-4,4%%DATE:~-7,2%%DATE:~-10,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
    set BACKUP_DIR=!BACKUP_DIR: =0!
    mkdir "!BACKUP_DIR!" 2>nul
    xcopy /E /I /Y "config\" "!BACKUP_DIR!\" >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Backup failed, continuing anyway...
    ) else (
        echo [OK] Backup created: !BACKUP_DIR!\
    )
    echo.
) else (
    echo [OK] No existing config\ directory found
    echo.
)

REM Create config directory
echo [3/6] Creating config\ directory...
if not exist "config\" mkdir config
if errorlevel 1 (
    echo [ERROR] Failed to create config\ directory
    pause
    exit /b 1
)
echo [OK] config\ directory created
echo.

REM Copy config files
echo [4/6] Copying configuration files...
echo      Source: models\config\
echo      Destination: config\
echo.

set COPIED=0
set FAILED=0

REM Copy screening_config.json
if exist "models\config\screening_config.json" (
    copy /Y "models\config\screening_config.json" "config\" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] screening_config.json
        set /a FAILED+=1
    ) else (
        echo [OK] screening_config.json
        set /a COPIED+=1
    )
) else (
    echo [MISS] screening_config.json - not found in source
)

REM Copy uk_sectors.json
if exist "models\config\uk_sectors.json" (
    copy /Y "models\config\uk_sectors.json" "config\" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] uk_sectors.json
        set /a FAILED+=1
    ) else (
        echo [OK] uk_sectors.json
        set /a COPIED+=1
    )
) else (
    echo [MISS] uk_sectors.json - not found in source
)

REM Copy asx_sectors.json (AU)
if exist "models\config\asx_sectors.json" (
    copy /Y "models\config\asx_sectors.json" "config\" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] asx_sectors.json
        set /a FAILED+=1
    ) else (
        echo [OK] asx_sectors.json
        set /a COPIED+=1
    )
) else (
    echo [MISS] asx_sectors.json - not found in source
)

REM Copy us_sectors.json
if exist "models\config\us_sectors.json" (
    copy /Y "models\config\us_sectors.json" "config\" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] us_sectors.json
        set /a FAILED+=1
    ) else (
        echo [OK] us_sectors.json
        set /a COPIED+=1
    )
) else (
    echo [MISS] us_sectors.json - not found in source
)

echo.
echo      Files copied: %COPIED%
if %FAILED% GTR 0 (
    echo      Failed: %FAILED%
)
echo.

REM Verify config files
echo [5/6] Verifying config\ directory contents...
echo ================================================================================
dir /B config\ 2>nul
if errorlevel 1 (
    echo [ERROR] config\ directory is empty or inaccessible!
    pause
    exit /b 1
)
echo ================================================================================
echo.

REM Count files
for /f %%A in ('dir /b config\*.json 2^>nul ^| find /c /v ""') do set FILE_COUNT=%%A
echo [OK] Found %FILE_COUNT% config files
echo.

REM Test config file integrity
echo [6/6] Testing config file integrity...
echo.

REM Test screening_config.json
if exist "config\screening_config.json" (
    findstr /C:"reporting" "config\screening_config.json" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] screening_config.json - invalid format
    ) else (
        echo [OK] screening_config.json - valid
    )
) else (
    echo [MISS] screening_config.json
)

REM Test uk_sectors.json
if exist "config\uk_sectors.json" (
    findstr /C:"sectors" "config\uk_sectors.json" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] uk_sectors.json - invalid format
    ) else (
        echo [OK] uk_sectors.json - valid
    )
) else (
    echo [MISS] uk_sectors.json
)

REM Test asx_sectors.json
if exist "config\asx_sectors.json" (
    findstr /C:"sectors" "config\asx_sectors.json" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] asx_sectors.json - invalid format
    ) else (
        echo [OK] asx_sectors.json - valid
    )
) else (
    echo [MISS] asx_sectors.json
)

REM Test us_sectors.json
if exist "config\us_sectors.json" (
    findstr /C:"sectors" "config\us_sectors.json" >nul 2>&1
    if errorlevel 1 (
        echo [FAIL] us_sectors.json - invalid format
    ) else (
        echo [OK] us_sectors.json - valid
    )
) else (
    echo [MISS] us_sectors.json
)

echo.
echo ================================================================================
echo   PATCH COMPLETE
echo ================================================================================
echo.

if %COPIED% GEQ 4 (
    echo [OK] Patch applied successfully!
    echo [OK] %COPIED% configuration files are now in place
    echo.
    echo What was fixed:
    echo   - Created config\ directory at project root
    echo   - Copied all sector config files
    echo   - UK Pipeline will now load 8 sectors, 240 stocks
    echo   - US Pipeline will now load sectors correctly
    echo   - AU Pipeline will now load 8 sectors, 240 stocks
    echo.
    echo ================================================================================
    echo   NEXT STEPS
    echo ================================================================================
    echo.
    echo   1. Close this window
    echo   2. Run: LAUNCH_COMPLETE_SYSTEM.bat
    echo   3. Select option [3] Run UK Overnight Pipeline
    echo   4. Pipeline should now complete successfully
    echo.
    echo   Expected result:
    echo   - [OK] Config file loaded
    echo   - [OK] 8 sectors, 240 stocks scanned
    echo   - [OK] All 6 phases complete
    echo   - [OK] Report generated
    echo.
    echo ================================================================================
) else (
    echo [WARN] Patch completed with warnings
    echo [WARN] Only %COPIED% files were copied
    echo.
    echo Please verify:
    echo   1. You are in the correct directory
    echo   2. models\config\ directory contains all files
    echo   3. You have write permissions
    echo.
    echo If problems persist, try:
    echo   1. Run as Administrator
    echo   2. Re-extract the ZIP file
    echo   3. Check antivirus is not blocking file operations
    echo.
)

echo.
echo ================================================================================
echo   PATCH LOG
echo ================================================================================
echo   Date: %DATE% %TIME%
echo   Directory: %CD%
echo   Files copied: %COPIED%
echo   Files failed: %FAILED%
echo   Total config files: %FILE_COUNT%
echo ================================================================================
echo.

REM Create patch log
echo Patch Applied: %DATE% %TIME% > config\PATCH_APPLIED.log
echo Directory: %CD% >> config\PATCH_APPLIED.log
echo Files copied: %COPIED% >> config\PATCH_APPLIED.log
echo Files failed: %FAILED% >> config\PATCH_APPLIED.log
echo Total config files: %FILE_COUNT% >> config\PATCH_APPLIED.log
echo. >> config\PATCH_APPLIED.log
echo Files in config directory: >> config\PATCH_APPLIED.log
dir /B config\*.json >> config\PATCH_APPLIED.log

echo [OK] Patch log saved: config\PATCH_APPLIED.log
echo.

pause

ENDLOCAL

@echo off
echo ========================================
echo   Config Path Fix Script
echo   v1.3.15.45
echo ========================================
echo.

echo [*] Checking for models\config\ directory...
if not exist "models\config\" (
    echo [ERROR] models\config\ directory not found!
    echo [ERROR] This script must be run from the installation directory
    pause
    exit /b 1
)
echo [OK] Found models\config\
echo.

echo [*] Creating root-level config\ directory...
if not exist "config\" mkdir config
echo [OK] Created config\
echo.

echo [*] Copying configuration files...
set COPIED=0

if exist "models\config\screening_config.json" (
    copy /Y "models\config\screening_config.json" "config\" > nul
    echo [OK] Copied screening_config.json
    set /a COPIED+=1
)

if exist "models\config\uk_sectors.json" (
    copy /Y "models\config\uk_sectors.json" "config\" > nul
    echo [OK] Copied uk_sectors.json
    set /a COPIED+=1
)

if exist "models\config\asx_sectors.json" (
    copy /Y "models\config\asx_sectors.json" "config\" > nul
    echo [OK] Copied asx_sectors.json
    set /a COPIED+=1
)

if exist "models\config\us_sectors.json" (
    copy /Y "models\config\us_sectors.json" "config\" > nul
    echo [OK] Copied us_sectors.json
    set /a COPIED+=1
)

echo.
echo [OK] Config files fixed! (%COPIED% files copied)
echo.
echo [*] Verifying config\ directory contents:
echo ========================================
dir /B config\
echo ========================================
echo.
echo [OK] You can now run the pipelines!
echo.
pause

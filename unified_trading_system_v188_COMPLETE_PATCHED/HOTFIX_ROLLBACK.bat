@echo off
REM ============================================================================
REM  HOTFIX v1.3.15.115 - Rollback Script
REM ============================================================================
REM
REM  Purpose: Restore report_generator.py to previous version
REM  Use this if hotfix causes issues or you want to revert
REM
REM ============================================================================

echo.
echo ============================================================================
echo  HOTFIX v1.3.15.115 - Rollback
echo ============================================================================
echo.
echo  This will restore report_generator.py to its previous version.
echo.
echo  WARNING: Reports will go back to the OLD location:
echo    pipelines\reports\morning_reports\
echo.
echo  Press Ctrl+C to cancel, or
pause

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Verify backup exists
if not exist "backups\report_generator.py.backup_*" (
    echo [ERROR] No backup file found in backups\ folder
    echo Cannot perform rollback without backup
    echo.
    echo Please restore manually or re-apply hotfix to create backup
    pause
    exit /b 1
)

echo.
echo [1/3] Creating safety backup of current version...
if not exist "backups" mkdir backups
copy "pipelines\models\screening\report_generator.py" "backups\report_generator.py.rollback_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
echo [OK] Current version backed up

echo.
echo [2/3] Restoring previous version from backup...

REM Find most recent backup
for /f "delims=" %%i in ('dir /b /o-d "backups\report_generator.py.backup_*"') do (
    set BACKUP_FILE=%%i
    goto :found_backup
)

:found_backup
echo Restoring from: %BACKUP_FILE%
copy "backups\%BACKUP_FILE%" "pipelines\models\screening\report_generator.py" >nul

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to restore backup
    pause
    exit /b 1
)

echo [OK] Previous version restored

echo.
echo [3/3] Verifying rollback...
findstr /C:"parent.parent.parent" "pipelines\models\screening\report_generator.py" >nul
findstr /C:"parent.parent.parent.parent" "pipelines\models\screening\report_generator.py" >nul

if %ERRORLEVEL% EQU 0 (
    echo [WARNING] File still contains hotfix - rollback may have failed
    echo Please verify manually
) else (
    echo [OK] Rollback successful - old version restored
)

echo.
echo ============================================================================
echo  ROLLBACK COMPLETE
echo ============================================================================
echo.
echo  Status: Previous version restored
echo  Reports will now save to: pipelines\reports\morning_reports\
echo.
echo  To re-apply hotfix later:
echo    Run APPLY_HOTFIX_v1.3.15.115.bat again
echo.
echo  Backups saved in backups\ folder:
dir /b backups\report_generator.py.*
echo.
echo ============================================================================
echo.
pause

@echo off
REM ============================================================================
REM ML Pipeline Integration - Backup Script
REM ============================================================================
REM This script backs up your existing files before applying the ML integration patch
REM 
REM Author: Enhanced Global Stock Tracker
REM Date: 2024-12-24
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo ML PIPELINE INTEGRATION - BACKUP SCRIPT
echo ============================================================================
echo.
echo This script will backup your existing files before applying the patch.
echo.
echo Target Directory: C:\Users\david\AATelS\finbert_v4.4.4\
echo.
pause

REM Set paths
set "BASE_DIR=C:\Users\david\AATelS\finbert_v4.4.4"
set "BACKUP_DIR=%BASE_DIR%\backups\ml_integration_backup_%DATE:~-4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

echo.
echo Creating backup directory...
echo %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul

REM Backup existing files
echo.
echo Backing up existing files...
echo.

REM Check and backup working_directory files
if exist "%BASE_DIR%\working_directory\manual_trading_phase3.py" (
    echo [BACKUP] manual_trading_phase3.py
    copy "%BASE_DIR%\working_directory\manual_trading_phase3.py" "%BACKUP_DIR%\" >nul 2>&1
) else (
    echo [SKIP] manual_trading_phase3.py - File not found
)

if exist "%BASE_DIR%\working_directory\phase3_signal_generator.py" (
    echo [BACKUP] phase3_signal_generator.py
    copy "%BASE_DIR%\working_directory\phase3_signal_generator.py" "%BACKUP_DIR%\" >nul 2>&1
) else (
    echo [SKIP] phase3_signal_generator.py - File not found
)

REM Check if ml_pipeline directory exists
if exist "%BASE_DIR%\working_directory\ml_pipeline" (
    echo [BACKUP] ml_pipeline directory
    xcopy "%BASE_DIR%\working_directory\ml_pipeline" "%BACKUP_DIR%\ml_pipeline\" /E /I /Y >nul 2>&1
) else (
    echo [SKIP] ml_pipeline directory - Not found (this is OK for first installation)
)

echo.
echo ============================================================================
echo BACKUP COMPLETE
echo ============================================================================
echo.
echo Backup Location: %BACKUP_DIR%
echo.
echo Files backed up:
dir "%BACKUP_DIR%" /B 2>nul
echo.
echo To restore from backup, copy files from the backup directory back to:
echo %BASE_DIR%\working_directory\
echo.
echo Press any key to continue with installation...
pause >nul

exit /b 0

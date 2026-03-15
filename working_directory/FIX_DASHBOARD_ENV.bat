@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM   DASHBOARD .ENV ENCODING FIX
REM   Fixes UnicodeDecodeError when starting dashboard
REM ============================================================================
REM
REM   This patch fixes:
REM   - UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
REM   - Adds load_dotenv=False parameter to dashboard.py
REM   - Prevents Flask from loading corrupt .env files
REM
REM   Version: 1.3.2 FINAL - WINDOWS COMPATIBLE
REM   Date: December 29, 2024
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   DASHBOARD .ENV ENCODING FIX
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   This patch fixes the UnicodeDecodeError when starting dashboard.py
echo.
echo   Error: 'utf-8' codec can't decode byte 0xff in position 0
echo   Fix: Adds load_dotenv=False to disable .env file loading
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Change to script directory
cd /d "%~dp0"

echo [Step 1/4] Checking current directory...
echo           Working directory: %CD%
echo.

REM ============================================================================
REM Check if dashboard.py exists
REM ============================================================================
echo [Step 2/4] Locating dashboard.py...

set "DASHBOARD_FILE=phase3_intraday_deployment\dashboard.py"

if not exist "%DASHBOARD_FILE%" (
    echo           [ERROR] File not found: %DASHBOARD_FILE%
    echo.
    echo           Please run this script from your Trading directory.
    echo           Expected location: C:\Users\david\Trading\
    echo.
    pause
    exit /b 1
)

echo           Found: %DASHBOARD_FILE%
echo.

REM ============================================================================
REM Check if fix is already applied
REM ============================================================================
echo [Step 3/4] Checking if fix is already applied...

findstr /C:"load_dotenv=False" "%DASHBOARD_FILE%" >nul 2>&1
if not errorlevel 1 (
    echo           [OK] Fix already applied!
    echo           The dashboard already has load_dotenv=False parameter.
    echo.
    echo           You can now run: python dashboard.py
    echo.
    pause
    exit /b 0
)

echo           Fix not yet applied. Proceeding...
echo.

REM ============================================================================
REM Apply the fix
REM ============================================================================
echo [Step 4/4] Applying fix...

REM Create backup
copy "%DASHBOARD_FILE%" "%DASHBOARD_FILE%.backup" >nul 2>&1
if exist "%DASHBOARD_FILE%.backup" (
    echo           Created backup: %DASHBOARD_FILE%.backup
) else (
    echo           [WARNING] Could not create backup file
)

REM Apply fix using PowerShell
echo           Modifying dashboard.py...

powershell -Command "$content = Get-Content '%DASHBOARD_FILE%' -Raw; if ($content -match 'app\.run\(\s*debug=False,\s*host=''0\.0\.0\.0'',\s*port=8050\s*\)') { $content = $content -replace '(app\.run\(\s*debug=False,\s*host=''0\.0\.0\.0'',\s*port=8050)\s*\)', '$1,`r`n        load_dotenv=False`r`n    )'; Set-Content '%DASHBOARD_FILE%' $content -NoNewline; Write-Host '           Successfully added load_dotenv=False parameter' } else { Write-Host '           [WARNING] Could not find expected app.run() pattern' }"

REM Verify fix was applied
findstr /C:"load_dotenv=False" "%DASHBOARD_FILE%" >nul 2>&1
if not errorlevel 1 (
    echo           [SUCCESS] Fix applied successfully!
) else (
    echo           [WARNING] Fix may not have been applied correctly.
    echo           Please check the file manually.
)

echo.

REM ============================================================================
REM Check for problematic .env files
REM ============================================================================
echo [Bonus] Checking for problematic .env files...
echo.

if exist ".env" (
    echo           Found .env in current directory
    echo           This may cause encoding issues.
    echo.
    set /p RENAME_ENV="           Do you want to rename it to .env.backup? (Y/N): "
    if /i "!RENAME_ENV!"=="Y" (
        ren .env .env.backup 2>nul
        if exist ".env.backup" (
            echo           Renamed .env to .env.backup
        ) else (
            echo           [WARNING] Could not rename .env file
        )
    )
    echo.
)

if exist "phase3_intraday_deployment\.env" (
    echo           Found .env in phase3_intraday_deployment\
    echo           This may cause encoding issues.
    echo.
    set /p RENAME_ENV2="           Do you want to rename it to .env.backup? (Y/N): "
    if /i "!RENAME_ENV2!"=="Y" (
        ren phase3_intraday_deployment\.env .env.backup 2>nul
        if exist "phase3_intraday_deployment\.env.backup" (
            echo           Renamed .env to .env.backup
        ) else (
            echo           [WARNING] Could not rename .env file
        )
    )
    echo.
)

REM ============================================================================
REM Summary
REM ============================================================================
echo ════════════════════════════════════════════════════════════════════════
echo   FIX COMPLETE
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   Status: ✅ Dashboard encoding fix applied successfully!
echo.
echo   Changes made:
echo   • Added load_dotenv=False parameter to app.run()
echo   • Created backup: %DASHBOARD_FILE%.backup
echo   • Dashboard will no longer try to load .env files
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM ============================================================================
REM Next steps
REM ============================================================================
echo NEXT STEPS:
echo.
echo 1. Test the dashboard:
echo    cd phase3_intraday_deployment
echo    python dashboard.py
echo.
echo    Expected output:
echo    INFO:__main__:Starting Paper Trading Dashboard...
echo    Dash is running on http://0.0.0.0:8050/
echo.
echo 2. Open your browser:
echo    http://localhost:8050
echo.
echo 3. Start paper trading (in a new terminal):
echo    cd phase3_intraday_deployment
echo    python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo If you encounter any issues, check the backup file:
echo %DASHBOARD_FILE%.backup
echo.
echo You can restore it by running:
echo copy "%DASHBOARD_FILE%.backup" "%DASHBOARD_FILE%"
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

echo Press any key to exit...
pause >nul

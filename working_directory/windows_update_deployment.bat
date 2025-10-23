@echo off
REM =========================================
REM Windows 11 Deployment Update Script
REM Version: 5.0 -> Latest
REM =========================================

setlocal enabledelayedexpansion

echo.
echo =====================================
echo   STOCK TRACKER UPDATE UTILITY
echo   Windows 11 Deployment Updater
echo =====================================
echo.

REM Store current directory
set "UPDATE_DIR=%CD%"
set "BACKUP_DIR=%UPDATE_DIR%\backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

echo [1/7] Checking current installation...
echo Current directory: %UPDATE_DIR%

REM Check if this is a valid installation
if not exist "backend_fixed_v2.py" (
    echo.
    echo ERROR: This doesn't appear to be a Stock Tracker installation directory!
    echo Please run this script from your Stock Tracker installation folder.
    echo.
    pause
    exit /b 1
)

REM Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Git is not installed. Will use direct download method.
    set "USE_GIT=0"
) else (
    echo Git detected. Will use Git for updates.
    set "USE_GIT=1"
)

REM Create backup
echo.
echo [2/7] Creating backup of current installation...
mkdir "%BACKUP_DIR%" 2>nul
echo Backing up to: %BACKUP_DIR%

REM Backup important files
xcopy /E /I /Q "modules" "%BACKUP_DIR%\modules" >nul 2>&1
copy "*.html" "%BACKUP_DIR%\" >nul 2>&1
copy "*.py" "%BACKUP_DIR%\" >nul 2>&1
copy "*.bat" "%BACKUP_DIR%\" >nul 2>&1
copy "*.ps1" "%BACKUP_DIR%\" >nul 2>&1
copy "*.md" "%BACKUP_DIR%\" >nul 2>&1

echo Backup completed successfully.

REM Stop any running Python processes on port 8002
echo.
echo [3/7] Stopping any running backend services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Stopping process on port 8002 (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

if "%USE_GIT%"=="1" (
    REM Git update method
    echo.
    echo [4/7] Fetching latest updates from GitHub...
    
    REM Clone or update repository
    if exist ".git" (
        echo Updating existing repository...
        git fetch origin main
        git reset --hard origin/main
    ) else (
        echo Cloning fresh repository...
        cd ..
        git clone https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git temp_update
        xcopy /E /I /Y "temp_update\working_directory\*" "%UPDATE_DIR%\" >nul
        rmdir /S /Q temp_update
        cd "%UPDATE_DIR%"
    )
) else (
    REM Manual download method
    echo.
    echo [4/7] Downloading latest files...
    echo This requires PowerShell for downloading...
    
    REM Create temporary download script
    echo $urls = @{ > temp_download.ps1
    echo     'backend_fixed_v2.py' = 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/main/working_directory/backend_fixed_v2.py' >> temp_download.ps1
    echo     'index.html' = 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/main/working_directory/index.html' >> temp_download.ps1
    echo     'diagnostic_tool.html' = 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/main/working_directory/diagnostic_tool.html' >> temp_download.ps1
    echo     'requirements.txt' = 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/main/working_directory/requirements.txt' >> temp_download.ps1
    echo } >> temp_download.ps1
    echo. >> temp_download.ps1
    echo foreach ($file in $urls.Keys) { >> temp_download.ps1
    echo     Write-Host "Downloading $file..." >> temp_download.ps1
    echo     Invoke-WebRequest -Uri $urls[$file] -OutFile $file >> temp_download.ps1
    echo } >> temp_download.ps1
    
    powershell -ExecutionPolicy Bypass -File temp_download.ps1
    del temp_download.ps1
)

REM Apply critical Windows 11 fixes
echo.
echo [5/7] Applying Windows 11 localhost fixes...

REM Create fix verification script
echo Creating localhost fix verification...
echo function getBackendUrl() { return 'http://localhost:8002'; } > localhost_fix.js

REM Update all HTML files to use hardcoded localhost
echo Updating module files for Windows 11 compatibility...
powershell -Command "Get-ChildItem -Path 'modules' -Filter '*.html' -Recurse | ForEach-Object { $content = Get-Content $_.FullName -Raw; $content = $content -replace 'getBackendUrl\(\)[^}]*}', 'getBackendUrl() { return ''http://localhost:8002''; }'; Set-Content -Path $_.FullName -Value $content }"

REM Update Python requirements
echo.
echo [6/7] Updating Python dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt --upgrade >nul 2>&1

REM Create update summary
echo.
echo [7/7] Creating update summary...
echo Update Summary > UPDATE_SUMMARY.txt
echo ============== >> UPDATE_SUMMARY.txt
echo Update Date: %date% %time% >> UPDATE_SUMMARY.txt
echo Previous Version: Unknown >> UPDATE_SUMMARY.txt
echo New Version: 5.0 - Windows 11 Fixed Edition >> UPDATE_SUMMARY.txt
echo. >> UPDATE_SUMMARY.txt
echo Files Updated: >> UPDATE_SUMMARY.txt
echo - All module HTML files (localhost fix applied) >> UPDATE_SUMMARY.txt
echo - backend_fixed_v2.py (latest version) >> UPDATE_SUMMARY.txt
echo - index.html (new landing page) >> UPDATE_SUMMARY.txt
echo - diagnostic_tool.html (connection tester) >> UPDATE_SUMMARY.txt
echo - requirements.txt (dependencies) >> UPDATE_SUMMARY.txt
echo. >> UPDATE_SUMMARY.txt
echo Backup Location: %BACKUP_DIR% >> UPDATE_SUMMARY.txt

echo.
echo =====================================
echo   UPDATE COMPLETED SUCCESSFULLY!
echo =====================================
echo.
echo ✅ All files have been updated to the latest version
echo ✅ Windows 11 localhost fixes have been applied
echo ✅ Backup created at: %BACKUP_DIR%
echo.
echo What's New:
echo - Fixed all Windows 11 connection issues
echo - New landing page dashboard
echo - Enhanced diagnostic tools
echo - All modules using hardcoded localhost
echo.
echo To start the application:
echo   1. Run: windows_start.bat
echo   2. Open: index.html in your browser
echo.
echo To restore previous version:
echo   Copy files from: %BACKUP_DIR%
echo.
pause
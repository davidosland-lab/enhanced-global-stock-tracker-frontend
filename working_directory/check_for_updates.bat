@echo off
REM =====================================
REM Stock Tracker Update Checker
REM =====================================

echo.
echo =====================================
echo   STOCK TRACKER UPDATE CHECKER
echo =====================================
echo.

REM Check current version
set "CURRENT_VERSION=Unknown"
if exist "VERSION.txt" (
    set /p CURRENT_VERSION=<VERSION.txt
)

echo Current Version: %CURRENT_VERSION%
echo.
echo Checking for updates...

REM Create temporary PowerShell script to check latest version
echo $url = "https://api.github.com/repos/davidosland-lab/enhanced-global-stock-tracker-frontend/releases/latest" > temp_check.ps1
echo try { >> temp_check.ps1
echo     $response = Invoke-WebRequest -Uri $url -UseBasicParsing >> temp_check.ps1
echo     $json = $response.Content ^| ConvertFrom-Json >> temp_check.ps1
echo     Write-Host "Latest Version: $($json.tag_name)" >> temp_check.ps1
echo     Write-Host "Release Date: $($json.published_at)" >> temp_check.ps1
echo     Write-Host "" >> temp_check.ps1
echo     if ($json.tag_name -eq "v5.0-windows-11-fix") { >> temp_check.ps1
echo         Write-Host "✅ You have the latest version!" -ForegroundColor Green >> temp_check.ps1
echo     } else { >> temp_check.ps1
echo         Write-Host "🔄 Update available: $($json.tag_name)" -ForegroundColor Yellow >> temp_check.ps1
echo         Write-Host "Run windows_update_deployment.bat to update" -ForegroundColor Yellow >> temp_check.ps1
echo     } >> temp_check.ps1
echo } catch { >> temp_check.ps1
echo     Write-Host "Unable to check for updates. Check your internet connection." -ForegroundColor Red >> temp_check.ps1
echo } >> temp_check.ps1

powershell -ExecutionPolicy Bypass -File temp_check.ps1
del temp_check.ps1

echo.
echo =====================================
echo.
echo Update Options:
echo   1. Run windows_update_deployment.bat for full update
echo   2. Download latest package from GitHub
echo   3. Visit: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
echo.
pause
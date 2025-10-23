# GSMT Indices Tracker Update Package Creator
# Creates a compact update package for distribution

$updateVersion = "2.0"
$packageName = "GSMT_IndicesTracker_Update_v$updateVersion"
$tempDir = "$env:TEMP\$packageName"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " GSMT Update Package Creator" -ForegroundColor Cyan
Write-Host " Creating Indices Tracker Update v$updateVersion" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create temporary directory
Write-Host "Creating temporary package directory..." -ForegroundColor Yellow
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null
New-Item -ItemType Directory -Path "$tempDir\frontend" | Out-Null

# Copy update files
Write-Host "Copying update files..." -ForegroundColor Yellow

# Copy the new tracker
Copy-Item "frontend\indices_tracker_percentage.html" "$tempDir\frontend\" -ErrorAction SilentlyContinue

# Copy update scripts
Copy-Item "UPDATE_INDICES_ENHANCED.cmd" "$tempDir\" -ErrorAction SilentlyContinue
Copy-Item "LAUNCH_INDICES_TRACKER.cmd" "$tempDir\" -ErrorAction SilentlyContinue
Copy-Item "UPDATE_README.md" "$tempDir\" -ErrorAction SilentlyContinue

# Create a simple installer batch file
$installerContent = @'
@echo off
cls
color 0A
title GSMT Indices Tracker Update v2.0 - Installer

echo ==========================================
echo  GSMT Indices Tracker Update v2.0
echo  Automatic Installer
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "frontend" (
    echo ERROR: This update must be run from the GSMT installation directory!
    echo.
    echo Please copy this update folder to your GSMT installation directory
    echo and run this installer again.
    echo.
    pause
    exit /b 1
)

echo Installing update files...
echo.

REM Copy the new tracker
copy /Y "frontend\indices_tracker_percentage.html" "..\frontend\" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to copy tracker file!
    pause
    exit /b 1
)

REM Copy launcher scripts  
copy /Y "*.cmd" "..\" >nul 2>&1
copy /Y "UPDATE_README.md" "..\" >nul 2>&1

echo.
echo ==========================================
echo  Update Successfully Installed!
echo ==========================================
echo.
echo New Features:
echo - Percentage changes on Y-axis
echo - Regional market selection
echo - Enhanced visual design
echo - Real-time statistics
echo.
echo To use the new tracker:
echo 1. Run LAUNCH_INDICES_TRACKER.cmd
echo    or
echo 2. Run RUN_GSMT.cmd and navigate to Global Indices
echo.
echo Press any key to exit...
pause >nul
'@

$installerContent | Out-File -FilePath "$tempDir\INSTALL_UPDATE.cmd" -Encoding ASCII

# Create version info file
$versionInfo = @"
GSMT Indices Tracker Update
Version: $updateVersion
Release Date: $(Get-Date -Format "yyyy-MM-dd")

Changes in this version:
- Y-axis displays percentage changes from previous close
- Regional market selection (Asia, Europe, Americas)  
- Enhanced market cards with live status indicators
- Real-time statistics panel
- Improved chart performance

Files included:
- frontend\indices_tracker_percentage.html
- UPDATE_INDICES_ENHANCED.cmd
- LAUNCH_INDICES_TRACKER.cmd
- UPDATE_README.md
- INSTALL_UPDATE.cmd
"@

$versionInfo | Out-File -FilePath "$tempDir\version.txt" -Encoding UTF8

# Create the ZIP package
Write-Host "Creating update package..." -ForegroundColor Yellow
$zipPath = "$PSScriptRoot\$packageName.zip"

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Add-Type -Assembly System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

# Clean up
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item $tempDir -Recurse -Force

# Calculate package size
$packageSize = (Get-Item $zipPath).Length / 1KB
$packageSizeStr = "{0:N2} KB" -f $packageSize

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " Update Package Created Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package: $packageName.zip" -ForegroundColor Cyan
Write-Host "Size: $packageSizeStr" -ForegroundColor Cyan
Write-Host "Location: $zipPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Distribution Instructions:" -ForegroundColor Yellow
Write-Host "1. Send $packageName.zip to users" -ForegroundColor White
Write-Host "2. Users extract to GSMT installation folder" -ForegroundColor White
Write-Host "3. Users run INSTALL_UPDATE.cmd" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
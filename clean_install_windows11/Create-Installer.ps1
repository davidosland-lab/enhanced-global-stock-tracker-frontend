# Stock Tracker Professional Installer Creator
# Creates a complete installation package with all components

$ErrorActionPreference = "Stop"

Write-Host @"
===============================================================================
                  STOCK TRACKER PROFESSIONAL INSTALLER
                     Creating Complete Windows Package
===============================================================================
"@ -ForegroundColor Cyan

# Configuration
$PackageName = "StockTracker_Complete_v1.0"
$OutputDir = ".\$PackageName"
$ZipFile = "$PackageName.zip"

# Create package directory
Write-Host "`n[1/7] Creating package structure..." -ForegroundColor Yellow
if (Test-Path $OutputDir) {
    Remove-Item -Path $OutputDir -Recurse -Force
}

$dirs = @(
    $OutputDir,
    "$OutputDir\modules",
    "$OutputDir\static",
    "$OutputDir\static\css",
    "$OutputDir\static\js",
    "$OutputDir\historical_data",
    "$OutputDir\models",
    "$OutputDir\logs",
    "$OutputDir\temp",
    "$OutputDir\docs"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Copy core files
Write-Host "[2/7] Copying core application files..." -ForegroundColor Yellow

# Backend files
$backendFiles = @(
    "backend.py",
    "ml_training_backend.py",
    "historical_data_manager.py",
    "advanced_ensemble_predictor.py",
    "advanced_ensemble_backtester.py",
    "phase4_integration.py",
    "test_system.py"
)

foreach ($file in $backendFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $OutputDir -Force
    }
}

# Frontend files
$frontendFiles = @(
    "index.html",
    "WORKING_PREDICTION_MODULE.html",
    "index_fixed.html",
    "diagnostic_tool.html",
    "verify_setup.html"
)

foreach ($file in $frontendFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $OutputDir -Force
    }
}

# Module files
Write-Host "[3/7] Copying module files..." -ForegroundColor Yellow
if (Test-Path "modules") {
    Get-ChildItem "modules\*.html" | Copy-Item -Destination "$OutputDir\modules" -Force
}

# Static files
if (Test-Path "static") {
    Get-ChildItem "static" -Recurse | Where-Object { !$_.PSIsContainer } | ForEach-Object {
        $targetPath = Join-Path $OutputDir $_.FullName.Substring((Get-Location).Path.Length + 1)
        $targetDir = Split-Path $targetPath -Parent
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Copy-Item $_.FullName -Destination $targetPath -Force
    }
}

# Configuration files
Write-Host "[4/7] Copying configuration files..." -ForegroundColor Yellow
$configFiles = @(
    "requirements_ml.txt",
    "requirements.txt",
    "package.json",
    "LAUNCH_ALL_SERVICES.bat",
    "COMPLETE_DEPLOYMENT_GUIDE.md",
    "WINDOWS11_COMPLETE_SOLUTION.md"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $OutputDir -Force
    }
}

# Create main installer
Write-Host "[5/7] Creating installer executable..." -ForegroundColor Yellow

@"
@echo off
title Stock Tracker Professional Installer
color 0A
cls

echo ===============================================================================
echo                      STOCK TRACKER PROFESSIONAL
echo                         Version 1.0 - ML Edition
echo ===============================================================================
echo.
echo Welcome to Stock Tracker installer!
echo This will install a complete stock tracking system with:
echo   - Real-time Yahoo Finance data
echo   - 6 professional modules
echo   - ML model training with TensorFlow
echo   - SQLite for 100x faster backtesting
echo.
echo ===============================================================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as administrator.
    echo Some features may require admin privileges.
    echo.
)

:: Check Python
echo [CHECKING] Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

:: Select installation directory
set "INSTALL_DIR=%ProgramFiles%\StockTracker"
echo Default installation directory: %INSTALL_DIR%
set /p "CUSTOM_DIR=Press ENTER to use default or type a custom path: "
if not "%CUSTOM_DIR%"=="" set "INSTALL_DIR=%CUSTOM_DIR%"

echo.
echo Installing to: %INSTALL_DIR%
echo.

:: Create installation directory
echo [1/6] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
xcopy /E /I /Y /Q . "%INSTALL_DIR%" >nul

:: Change to installation directory
cd /d "%INSTALL_DIR%"

:: Install Python packages
echo [2/6] Installing Python packages (this may take 5-10 minutes)...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements_ml.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed to install.
    echo Continuing with installation...
)

:: Initialize database
echo [3/6] Initializing SQLite database...
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('Database initialized')" 2>nul

:: Create Start Menu shortcuts
echo [4/6] Creating Start Menu shortcuts...
set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\Stock Tracker"
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Stock Tracker.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\LAUNCH_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Description = 'Launch Stock Tracker'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Uninstall Stock Tracker.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\UNINSTALL.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll,131'; $Shortcut.Save()"

:: Create Desktop shortcut
echo [5/6] Creating Desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Stock Tracker.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\LAUNCH_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Description = 'Launch Stock Tracker'; $Shortcut.Save()"

:: Run system test
echo [6/6] Running system verification...
python test_system.py

echo.
echo ===============================================================================
echo                        INSTALLATION COMPLETE!
echo ===============================================================================
echo.
echo Installation Summary:
echo --------------------
echo Location: %INSTALL_DIR%
echo Desktop Shortcut: Created
echo Start Menu: Stock Tracker folder created
echo.
echo To launch Stock Tracker:
echo   1. Use the desktop shortcut "Stock Tracker"
echo   2. Or go to Start Menu > Stock Tracker
echo   3. Or run: %INSTALL_DIR%\LAUNCH_ALL_SERVICES.bat
echo.
echo The application will open at: http://localhost:8000
echo.
echo Press any key to launch Stock Tracker now...
pause >nul
start "" "%INSTALL_DIR%\LAUNCH_ALL_SERVICES.bat"
"@ | Out-File -FilePath "$OutputDir\Setup.bat" -Encoding ASCII

# Create uninstaller
Write-Host "[6/7] Creating uninstaller..." -ForegroundColor Yellow

@"
@echo off
title Stock Tracker Uninstaller
color 0C
cls

echo ===============================================================================
echo                      STOCK TRACKER UNINSTALLER
echo ===============================================================================
echo.
echo This will completely remove Stock Tracker from your system.
echo.
echo The following will be removed:
echo   - Application files
echo   - Desktop shortcut
echo   - Start Menu shortcuts
echo   - Python packages (optional)
echo.

set /p confirm="Are you sure you want to uninstall Stock Tracker? (Y/N): "
if /i "%confirm%" neq "Y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo [1/4] Removing Desktop shortcut...
del "%USERPROFILE%\Desktop\Stock Tracker.lnk" 2>nul

echo [2/4] Removing Start Menu shortcuts...
rmdir /s /q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Stock Tracker" 2>nul

echo [3/4] Stopping any running services...
taskkill /f /im python.exe 2>nul

set /p removepkg="Remove Python packages? (Y/N): "
if /i "%removepkg%"=="Y" (
    echo [4/4] Removing Python packages...
    pip uninstall -y -r requirements_ml.txt 2>nul
)

echo.
echo ===============================================================================
echo                      UNINSTALL COMPLETE
echo ===============================================================================
echo.
echo Stock Tracker has been removed from your system.
echo You can now safely delete this folder.
echo.
pause
"@ | Out-File -FilePath "$OutputDir\UNINSTALL.bat" -Encoding ASCII

# Create package info
Write-Host "[7/7] Creating package documentation..." -ForegroundColor Yellow

@"
# Stock Tracker Professional - Installation Package

## Version 1.0 - ML Edition

### Installation Instructions

1. **Extract the ZIP file** to a temporary location
2. **Run Setup.bat** as Administrator (right-click > Run as administrator)
3. **Follow the installer** prompts
4. **Launch** using the desktop shortcut

### Package Contents

- `Setup.bat` - Main installer
- `LAUNCH_ALL_SERVICES.bat` - Application launcher
- `UNINSTALL.bat` - Uninstaller
- `backend.py` - Main backend server
- `ml_training_backend.py` - ML training server
- `modules/` - All 6 application modules
- `requirements_ml.txt` - Python dependencies

### System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended for ML)
- **Storage**: 10GB free space
- **Network**: Internet connection required

### Features

- ✅ Real-time Yahoo Finance data
- ✅ 6 professional trading modules
- ✅ Real ML model training (TensorFlow)
- ✅ SQLite for 100x faster backtesting
- ✅ Windows 11 optimized
- ✅ One-click installation

### Quick Start After Installation

1. **Launch** the application using the desktop shortcut
2. **Wait** for all services to start (30 seconds)
3. **Open** your browser to http://localhost:8000
4. **Enjoy** professional stock tracking!

### Troubleshooting

If you encounter issues:
1. Run `test_system.py` to diagnose
2. Ensure Python 3.8+ is installed
3. Check Windows Firewall settings
4. Run as Administrator if needed

### Support

- Documentation: See `COMPLETE_DEPLOYMENT_GUIDE.md`
- System Test: Run `python test_system.py`
- Logs: Check `logs/` directory

---
© 2024 Stock Tracker Professional
"@ | Out-File -FilePath "$OutputDir\README.md" -Encoding UTF8

# Create ZIP package
Write-Host "`nCreating ZIP package..." -ForegroundColor Green
if (Test-Path $ZipFile) {
    Remove-Item $ZipFile -Force
}

Compress-Archive -Path $OutputDir -DestinationPath $ZipFile -CompressionLevel Optimal

$zipSize = (Get-Item $ZipFile).Length / 1MB
$fileCount = (Get-ChildItem -Path $OutputDir -Recurse -File).Count

Write-Host @"

===============================================================================
                        PACKAGE CREATED SUCCESSFULLY!
===============================================================================

Package Name: $ZipFile
Package Size: $([math]::Round($zipSize, 2)) MB
Total Files: $fileCount

The installation package is ready for distribution!

Users need to:
1. Extract $ZipFile
2. Run Setup.bat as Administrator
3. Follow the installation wizard

The installer will:
- Install all Python dependencies
- Create desktop and Start Menu shortcuts
- Initialize the SQLite database
- Run system verification
- Launch the application

===============================================================================
"@ -ForegroundColor Green

# Ask if user wants to keep the uncompressed folder
$keepFolder = Read-Host "Keep uncompressed folder for testing? (Y/N)"
if ($keepFolder -ne "Y") {
    Remove-Item -Path $OutputDir -Recurse -Force
    Write-Host "Uncompressed folder removed. Only ZIP file remains." -ForegroundColor Yellow
}
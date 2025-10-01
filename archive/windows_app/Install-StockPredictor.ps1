# Stock Predictor Pro - PowerShell Installation Script
# Run with: powershell -ExecutionPolicy Bypass -File Install-StockPredictor.ps1

param(
    [string]$InstallPath = "$env:ProgramFiles\StockPredictorPro",
    [switch]$Silent = $false
)

# Set strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Info { Write-Host "$args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }

# Banner
Write-Host @"

███████╗████████╗ ██████╗  ██████╗██╗  ██╗    ██████╗ ██████╗ ███████╗██████╗ ██╗ ██████╗████████╗ ██████╗ ██████╗ 
██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝    ██╔══██╗██╔══██╗██╔════╝██╔══██╗██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
███████╗   ██║   ██║   ██║██║     █████╔╝     ██████╔╝██████╔╝█████╗  ██║  ██║██║██║        ██║   ██║   ██║██████╔╝
╚════██║   ██║   ██║   ██║██║     ██╔═██╗     ██╔═══╝ ██╔══██╗██╔══╝  ██║  ██║██║██║        ██║   ██║   ██║██╔══██╗
███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗    ██║     ██║  ██║███████╗██████╔╝██║╚██████╗   ██║   ╚██████╔╝██║  ██║
╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                                                                      
                            Professional AI-Powered Stock Prediction System v1.0.0
"@ -ForegroundColor Cyan

Write-Host ""

# Check for Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This installer requires Administrator privileges."
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    
    # Attempt to restart as admin
    $arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    if ($InstallPath -ne "$env:ProgramFiles\StockPredictorPro") {
        $arguments += " -InstallPath `"$InstallPath`""
    }
    if ($Silent) {
        $arguments += " -Silent"
    }
    
    Start-Process powershell -Verb RunAs -ArgumentList $arguments
    exit
}

# Check Windows version
$os = Get-WmiObject -Class Win32_OperatingSystem
$version = [version]$os.Version
if ($version.Major -lt 10) {
    Write-Error "Stock Predictor Pro requires Windows 10 or Windows 11"
    exit 1
}
Write-Success "Windows version check passed: $($os.Caption)"

# Check Python installation
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $pyVer = [version]$matches[1]
        if ($pyVer -ge [version]"3.9") {
            Write-Success "Python $($matches[1]) is installed"
        } else {
            throw "Python version $($matches[1]) is too old. Python 3.9+ required."
        }
    }
} catch {
    Write-Error "Python is not installed or not in PATH"
    
    if (!$Silent) {
        $response = Read-Host "Would you like to download Python now? (Y/N)"
        if ($response -eq 'Y') {
            Start-Process "https://www.python.org/downloads/"
            Write-Host "Please install Python 3.9+ and run this installer again." -ForegroundColor Yellow
        }
    }
    exit 1
}

# Create installation directory
Write-Info "Creating installation directory..."
try {
    if (Test-Path $InstallPath) {
        if (!$Silent) {
            $response = Read-Host "$InstallPath already exists. Overwrite? (Y/N)"
            if ($response -ne 'Y') {
                Write-Host "Installation cancelled."
                exit 0
            }
        }
        Remove-Item -Path $InstallPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Success "Created directory: $InstallPath"
} catch {
    Write-Error "Failed to create installation directory: $_"
    exit 1
}

# Copy application files
Write-Info "Copying application files..."
try {
    $sourceDir = Split-Path -Parent $PSCommandPath
    Copy-Item -Path "$sourceDir\*" -Destination $InstallPath -Recurse -Force
    Write-Success "Files copied successfully"
} catch {
    Write-Error "Failed to copy files: $_"
    exit 1
}

# Create user data directories
$userDataPath = "$env:APPDATA\StockPredictorPro"
Write-Info "Creating user data directories..."
try {
    @("models", "data", "logs", "config") | ForEach-Object {
        New-Item -ItemType Directory -Path "$userDataPath\$_" -Force | Out-Null
    }
    Write-Success "User data directories created"
} catch {
    Write-Warning "Failed to create some user directories: $_"
}

# Install Python dependencies
Write-Info "Installing Python dependencies (this may take several minutes)..."
Set-Location $InstallPath

try {
    # Create virtual environment
    Write-Info "Creating virtual environment..."
    & python -m venv venv 2>&1 | Out-Null
    Write-Success "Virtual environment created"
    
    # Activate virtual environment and install packages
    $activateScript = "$InstallPath\venv\Scripts\Activate.ps1"
    & $activateScript
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    & python -m pip install --upgrade pip --quiet 2>&1 | Out-Null
    
    # Install packages in groups to handle failures gracefully
    $packageGroups = @(
        @{Name="Core"; Packages=@("numpy", "pandas", "scikit-learn")},
        @{Name="GUI"; Packages=@("customtkinter", "pillow")},
        @{Name="ML Libraries"; Packages=@("xgboost", "lightgbm")},
        @{Name="Financial"; Packages=@("yfinance", "pandas-ta")},
        @{Name="Network"; Packages=@("requests", "aiohttp")}
    )
    
    foreach ($group in $packageGroups) {
        Write-Info "Installing $($group.Name) packages..."
        $packages = $group.Packages -join " "
        try {
            & pip install --no-cache-dir $packages --quiet 2>&1 | Out-Null
            Write-Success "$($group.Name) packages installed"
        } catch {
            Write-Warning "Some $($group.Name) packages failed to install"
        }
    }
    
    Write-Success "Package installation completed"
} catch {
    Write-Error "Failed to install dependencies: $_"
    Write-Warning "You may need to install dependencies manually"
}

# Create launch script
Write-Info "Creating launch script..."
$launchScript = @"
@echo off
cd /d "$InstallPath"
call venv\Scripts\activate.bat
start pythonw stock_predictor_pro.py
exit
"@
Set-Content -Path "$InstallPath\launch.bat" -Value $launchScript

# Create desktop shortcut
Write-Info "Creating desktop shortcut..."
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Stock Predictor Pro.lnk")
    $Shortcut.TargetPath = "$InstallPath\launch.bat"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.IconLocation = "$InstallPath\assets\icon.ico,0"
    $Shortcut.Description = "Stock Predictor Pro - AI Trading System"
    $Shortcut.Save()
    Write-Success "Desktop shortcut created"
} catch {
    Write-Warning "Failed to create desktop shortcut: $_"
}

# Create Start Menu shortcuts
Write-Info "Creating Start Menu shortcuts..."
$startMenuPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Stock Predictor Pro"
try {
    New-Item -ItemType Directory -Path $startMenuPath -Force | Out-Null
    
    # Application shortcut
    $Shortcut = $WshShell.CreateShortcut("$startMenuPath\Stock Predictor Pro.lnk")
    $Shortcut.TargetPath = "$InstallPath\launch.bat"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.IconLocation = "$InstallPath\assets\icon.ico,0"
    $Shortcut.Description = "Stock Predictor Pro - AI Trading System"
    $Shortcut.Save()
    
    # Readme shortcut
    $Shortcut = $WshShell.CreateShortcut("$startMenuPath\Documentation.lnk")
    $Shortcut.TargetPath = "$InstallPath\README.md"
    $Shortcut.Save()
    
    Write-Success "Start Menu shortcuts created"
} catch {
    Write-Warning "Failed to create Start Menu shortcuts: $_"
}

# Add to registry for uninstall
Write-Info "Adding to Windows registry..."
try {
    $registryPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro"
    New-Item -Path $registryPath -Force | Out-Null
    
    Set-ItemProperty -Path $registryPath -Name "DisplayName" -Value "Stock Predictor Pro"
    Set-ItemProperty -Path $registryPath -Name "UninstallString" -Value "$InstallPath\uninstall.bat"
    Set-ItemProperty -Path $registryPath -Name "DisplayIcon" -Value "$InstallPath\assets\icon.ico"
    Set-ItemProperty -Path $registryPath -Name "Publisher" -Value "Stock Predictor Team"
    Set-ItemProperty -Path $registryPath -Name "DisplayVersion" -Value "1.0.0"
    Set-ItemProperty -Path $registryPath -Name "InstallLocation" -Value $InstallPath
    Set-ItemProperty -Path $registryPath -Name "EstimatedSize" -Value 500000  # Size in KB
    
    Write-Success "Registry entries added"
} catch {
    Write-Warning "Failed to add registry entries: $_"
}

# Create uninstall script
$uninstallScript = @"
@echo off
echo Uninstalling Stock Predictor Pro...
rmdir /S /Q "$InstallPath"
del "$env:USERPROFILE\Desktop\Stock Predictor Pro.lnk" 2>nul
rmdir /S /Q "$startMenuPath" 2>nul
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /f 2>nul
echo.
echo Stock Predictor Pro has been uninstalled.
echo User data in %APPDATA%\StockPredictorPro has been preserved.
pause
"@
Set-Content -Path "$InstallPath\uninstall.bat" -Value $uninstallScript

# Installation complete
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Success "Installation Completed Successfully!"
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Info "Installation location: $InstallPath"
Write-Info "User data location: $userDataPath"
Write-Host ""
Write-Info "Shortcuts created:"
Write-Host "  • Desktop: Stock Predictor Pro.lnk"
Write-Host "  • Start Menu: Stock Predictor Pro folder"
Write-Host ""

if (!$Silent) {
    $response = Read-Host "Would you like to launch Stock Predictor Pro now? (Y/N)"
    if ($response -eq 'Y') {
        Write-Info "Launching Stock Predictor Pro..."
        Start-Process "$InstallPath\launch.bat"
    }
}

Write-Host ""
Write-Success "Thank you for installing Stock Predictor Pro!"
Write-Host ""

# Keep window open if not silent
if (!$Silent) {
    Write-Host "Press any key to exit..." -NoNewline
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
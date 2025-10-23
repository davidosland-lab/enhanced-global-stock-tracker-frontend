# ML Core Enhanced Production System
# Windows 11 PowerShell Installation Script
# Run with: powershell -ExecutionPolicy Bypass -File install_windows.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ML CORE ENHANCED PRODUCTION SYSTEM" -ForegroundColor Yellow
Write-Host "Windows 11 Installation (PowerShell)" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher from python.org" -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Check Python version
$versionString = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
$version = [double]$versionString
if ($version -lt 3.9) {
    Write-Host "WARNING: Python version $version detected. Version 3.9+ recommended" -ForegroundColor Yellow
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Virtual environment created!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green

Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet
Write-Host "Pip upgraded!" -ForegroundColor Green

Write-Host ""

# Install required packages
Write-Host "Installing required packages..." -ForegroundColor Green
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

# Core requirements
$packages = @(
    "scikit-learn>=1.3.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "tensorflow>=2.13.0",
    "fastapi>=0.103.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "yfinance>=0.2.28",
    "python-multipart>=0.0.6",
    "aiofiles>=23.0.0",
    "python-dateutil>=2.8.2"
)

$failed = @()

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    $output = pip install $package --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Warning: Failed to install $package" -ForegroundColor Yellow
        $failed += $package
    } else {
        Write-Host "  ✓ Installed successfully" -ForegroundColor Green
    }
}

Write-Host ""

# Try optional packages
Write-Host "Installing optional packages..." -ForegroundColor Green

# XGBoost
Write-Host "Installing XGBoost..." -ForegroundColor Gray
$output = pip install xgboost --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Info: XGBoost not installed, will use GradientBoosting as fallback" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ XGBoost installed" -ForegroundColor Green
}

Write-Host ""

# Create necessary directories
Write-Host "Creating data directories..." -ForegroundColor Green
$directories = @("data", "models", "logs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}
Write-Host "Directories ready!" -ForegroundColor Green

Write-Host ""

# Create PowerShell run script
Write-Host "Creating PowerShell run script..." -ForegroundColor Green
@"
# ML Core Enhanced Production System - Run Script
Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'ML CORE ENHANCED PRODUCTION SYSTEM' -ForegroundColor Yellow
Write-Host 'Starting service...' -ForegroundColor Yellow
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# Activate virtual environment
& '.\venv\Scripts\Activate.ps1'

# Start the ML Core system
Write-Host 'Starting ML Core on http://localhost:8000' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop the server' -ForegroundColor Yellow
Write-Host ''

python ml_core_enhanced_production.py

Write-Host ''
Write-Host 'Server stopped' -ForegroundColor Yellow
Write-Host 'Press any key to exit...'
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@ | Out-File -FilePath "run_ml_core.ps1" -Encoding UTF8

Write-Host "PowerShell run script created!" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Yellow
Write-Host "  1. Run: .\run_ml_core.ps1" -ForegroundColor White
Write-Host "     OR" -ForegroundColor Gray
Write-Host "  2. Run: run_ml_core.bat" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

if ($failed.Count -gt 0) {
    Write-Host "Note: Some packages failed to install:" -ForegroundColor Yellow
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Gray
    }
    Write-Host "The system may still work with reduced functionality" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
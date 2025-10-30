# Stock Analysis System - PowerShell Runner
# Run this with: powershell -ExecutionPolicy Bypass -File run_powershell.ps1

Clear-Host
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   STOCK ANALYSIS SYSTEM - POWERSHELL LAUNCHER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "Working Directory: $scriptDir"
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install from https://www.python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check virtual environment
$venvPath = Join-Path $scriptDir "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

if (Test-Path $venvPython) {
    Write-Host "[OK] Virtual environment found" -ForegroundColor Green
    $usePython = $venvPython
    $usePip = $venvPip
} else {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    if (Test-Path $venvPython) {
        Write-Host "[OK] Virtual environment created" -ForegroundColor Green
        $usePython = $venvPython
        $usePip = $venvPip
    } else {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        $usePython = "python"
        $usePip = "pip"
    }
}

Write-Host ""
Write-Host "Installing/Updating packages..." -ForegroundColor Yellow

# Install packages
$packages = @(
    "flask==3.0.0",
    "flask-cors==4.0.0",
    "yfinance==0.2.33",
    "pandas==2.1.4",
    "numpy==1.26.2",
    "plotly==5.18.0",
    "requests==2.31.0",
    "scikit-learn==1.3.2"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -NoNewline
    & $usePip install $package --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [WARNING]" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   STARTING SERVER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server URL: http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set environment variables
$env:FLASK_SKIP_DOTENV = "1"
$env:PYTHONUNBUFFERED = "1"

# Open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:8000"

# Run the server
& $usePython app.py

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
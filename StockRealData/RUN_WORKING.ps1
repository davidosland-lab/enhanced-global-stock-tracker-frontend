# Stock Analysis - Working Version Runner
# To run: Right-click and select "Run with PowerShell"

Clear-Host
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   STOCK ANALYSIS - WORKING VERSION" -ForegroundColor Cyan  
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "Working Directory: $scriptDir" -ForegroundColor Yellow
Write-Host ""

# Check if app_WORKING.py exists
if (-not (Test-Path "app_WORKING.py")) {
    Write-Host "[ERROR] app_WORKING.py not found!" -ForegroundColor Red
    Write-Host "Please ensure all files are extracted." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not installed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Checking packages..." -ForegroundColor Yellow

# Check and install packages
$packages = @(
    @{name="flask"; module="flask"},
    @{name="yfinance"; module="yfinance"},
    @{name="plotly"; module="plotly"},
    @{name="pandas"; module="pandas"},
    @{name="scikit-learn"; module="sklearn"},
    @{name="requests"; module="requests"}
)

foreach ($pkg in $packages) {
    Write-Host "Checking $($pkg.name)..." -NoNewline
    $result = python -c "import $($pkg.module)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [Installing]" -ForegroundColor Yellow
        pip install $($pkg.name) --quiet
    } else {
        Write-Host " [OK]" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   STARTING SERVER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server URL: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set environment variables
$env:FLASK_SKIP_DOTENV = "1"
$env:PYTHONUNBUFFERED = "1"

# Run the application
try {
    python app_WORKING.py
} catch {
    Write-Host ""
    Write-Host "[ERROR] Application failed: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
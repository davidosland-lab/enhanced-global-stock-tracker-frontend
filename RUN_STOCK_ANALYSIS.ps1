# PowerShell Script for Stock Analysis System
# Windows 11 Compatible

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "     UNIFIED STOCK ANALYSIS SYSTEM" -ForegroundColor Green
Write-Host "     PowerShell Launcher for Windows 11" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:FLASK_SKIP_DOTENV = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONUNBUFFERED = "1"

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Host ""
Write-Host "Installing/Updating required packages..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Gray
Write-Host ""

# Install packages
$packages = @(
    "flask",
    "flask-cors",
    "yfinance",
    "pandas",
    "numpy",
    "scikit-learn",
    "plotly",
    "requests",
    "ta"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    pip install --quiet --upgrade $package
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Starting Stock Analysis System..." -ForegroundColor Green
Write-Host "Server URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Features:" -ForegroundColor Cyan
Write-Host "✓ Real-time Yahoo Finance data" -ForegroundColor Green
Write-Host "✓ Alpha Vantage fallback (API integrated)" -ForegroundColor Green
Write-Host "✓ Machine Learning predictions" -ForegroundColor Green
Write-Host "✓ Technical indicators & charts" -ForegroundColor Green
Write-Host "✓ Australian stocks (.AX) support" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Run the application
try {
    python stock_analysis_unified_fixed.py
} catch {
    Write-Host ""
    Write-Host "[X] ERROR: Application failed to start" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Application has stopped." -ForegroundColor Yellow
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
# Stock Tracker Windows 11 PowerShell Startup Script
# Run this script with: powershell -ExecutionPolicy Bypass -File windows_start.ps1

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  STOCK TRACKER - WINDOWS 11 EDITION" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "[✓] Working directory: $scriptPath" -ForegroundColor Green

# Install requirements
Write-Host "[→] Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -q -r requirements.txt 2>$null
    Write-Host "[✓] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "[!] Warning: Some dependencies may have failed" -ForegroundColor Yellow
}

# Check for existing process on port 8002
Write-Host "[→] Checking port 8002..." -ForegroundColor Yellow
$processOnPort = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue
if ($processOnPort) {
    $pid = $processOnPort.OwningProcess
    Write-Host "[!] Found existing process on port 8002 (PID: $pid)" -ForegroundColor Yellow
    try {
        Stop-Process -Id $pid -Force
        Write-Host "[✓] Stopped existing process" -ForegroundColor Green
    } catch {
        Write-Host "[!] Could not stop process" -ForegroundColor Yellow
    }
}

# Create URLs for easy access
$baseUrl = "file:///$($scriptPath -replace '\\', '/')"
$urls = @{
    "Technical Analysis" = "$baseUrl/modules/technical_analysis_enhanced.html"
    "Prediction Centre" = "$baseUrl/modules/predictions/prediction_centre_advanced.html"
    "Desktop Version" = "$baseUrl/modules/technical_analysis_desktop.html"
    "Diagnostic Tool" = "$baseUrl/diagnostic_tool.html"
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  STARTING BACKEND API SERVER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend URL: " -NoNewline
Write-Host "http://localhost:8002" -ForegroundColor Green
Write-Host ""
Write-Host "Once started, open these URLs in your browser:" -ForegroundColor Yellow
Write-Host ""

foreach ($key in $urls.Keys) {
    Write-Host "  $key`:" -ForegroundColor Cyan
    Write-Host "  $($urls[$key])" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Start the backend
try {
    python backend_fixed_v2.py
} catch {
    Write-Host ""
    Write-Host "[✗] Backend failed to start" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
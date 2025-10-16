# StockTracker V10 - PowerShell Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "StockTracker V10 - PowerShell Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing Python processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Seconds 2

# Set environment variables for SSL
$env:SSL_CERT_FILE = ""
$env:SSL_CERT_DIR = ""
$env:REQUESTS_CA_BUNDLE = ""
$env:CURL_CA_BUNDLE = ""

# Get current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if venv exists
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "Virtual environment not found. Please run INSTALL.bat first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Function to start service
function Start-Service {
    param(
        [string]$Name,
        [string]$Script,
        [int]$Port
    )
    
    Write-Host "Starting $Name on port $Port..." -ForegroundColor Green
    
    $process = Start-Process -FilePath "venv\Scripts\python.exe" `
                            -ArgumentList $Script `
                            -WorkingDirectory $scriptPath `
                            -WindowStyle Minimized `
                            -PassThru
    
    Start-Sleep -Seconds 3
    
    # Check if port is listening
    $listening = netstat -an | Select-String ":$Port.*LISTENING"
    if ($listening) {
        Write-Host "✓ $Name started successfully on port $Port" -ForegroundColor Green
    } else {
        Write-Host "⚠ $Name may not have started correctly on port $Port" -ForegroundColor Yellow
    }
    
    return $process
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start all services
$services = @()
$services += Start-Service -Name "Main Backend" -Script "main_backend.py" -Port 8000
$services += Start-Service -Name "ML Backend" -Script "ml_backend.py" -Port 8002
$services += Start-Service -Name "FinBERT Backend" -Script "finbert_backend.py" -Port 8003
$services += Start-Service -Name "Historical Backend" -Script "historical_backend.py" -Port 8004
$services += Start-Service -Name "Backtesting Backend" -Script "backtesting_backend.py" -Port 8005

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Check all ports
$ports = @(8000, 8002, 8003, 8004, 8005)
$allRunning = $true

foreach ($port in $ports) {
    $listening = netstat -an | Select-String ":$port.*LISTENING"
    if ($listening) {
        Write-Host "✓ Port $port is active" -ForegroundColor Green
    } else {
        Write-Host "✗ Port $port is not listening" -ForegroundColor Red
        $allRunning = $false
    }
}

Write-Host ""
if ($allRunning) {
    Write-Host "All services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opening dashboard at http://localhost:8000" -ForegroundColor Cyan
    Start-Process "http://localhost:8000"
} else {
    Write-Host "Some services may not have started correctly." -ForegroundColor Yellow
    Write-Host "Check individual service windows for error messages." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 60
        
        # Periodic health check
        $stillRunning = $true
        foreach ($service in $services) {
            if ($service.HasExited) {
                $stillRunning = $false
                Write-Host "Warning: A service has stopped" -ForegroundColor Red
                break
            }
        }
        
        if (-not $stillRunning) {
            Write-Host "Restarting services..." -ForegroundColor Yellow
            break
        }
    }
} finally {
    # Clean up on exit
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    foreach ($service in $services) {
        if (-not $service.HasExited) {
            $service.Kill()
        }
    }
}
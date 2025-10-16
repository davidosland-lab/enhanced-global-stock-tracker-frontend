# Stock Tracker V5 PowerShell Launcher
# Run with: PowerShell -ExecutionPolicy Bypass -File Start-StockTracker.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stock Tracker V5 - Service Launcher" -ForegroundColor Yellow
Write-Host "With ML Backtesting & FinBERT Sentiment" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create logs directory
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "Created logs directory" -ForegroundColor Green
}

# Function to start service
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$LogFile,
        [int]$Port
    )
    
    Write-Host "Starting $Name on port $Port..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { $Command 2>&1 | Tee-Object -FilePath logs\$LogFile }" -WorkingDirectory $PWD
    Start-Sleep -Seconds 2
    
    # Check if port is listening
    $listening = netstat -an | Select-String ":$Port.*LISTENING"
    if ($listening) {
        Write-Host "✓ $Name started successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ $Name may not have started properly" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start services
Start-Service -Name "Main Backend API" -Command "python backend.py" -LogFile "backend.log" -Port 8002
Start-Service -Name "ML Backend" -Command "python ml_backend_enhanced.py" -LogFile "ml_backend.log" -Port 8003
Start-Service -Name "Integration Bridge" -Command "python integration_bridge.py" -LogFile "integration.log" -Port 8004
Start-Service -Name "Web Server" -Command "python -m http.server 8080" -LogFile "webserver.log" -Port 8080

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running on:" -ForegroundColor White
Write-Host "  • Web Interface:  " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8080" -ForegroundColor Cyan
Write-Host "  • Main API:       " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8002" -ForegroundColor Cyan
Write-Host "  • ML Backend:     " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8003" -ForegroundColor Cyan
Write-Host "  • Integration:    " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8004" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features available:" -ForegroundColor White
Write-Host "  ✓ Real-time Stock Tracking" -ForegroundColor Green
Write-Host "  ✓ ML Training & Prediction" -ForegroundColor Green
Write-Host "  ✓ Backtesting with `$100,000 capital" -ForegroundColor Green
Write-Host "  ✓ FinBERT Sentiment Analysis" -ForegroundColor Green
Write-Host "  ✓ 5 Trading Strategies" -ForegroundColor Green
Write-Host "  ✓ SQLite Historical Data Cache" -ForegroundColor Green
Write-Host ""

# Open browser
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping all services..." -ForegroundColor Red
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force
    Write-Host "All services stopped." -ForegroundColor Green
}
# Stock Tracker Pro - Windows 11 PowerShell Launcher
# Version 7.0 with Real ML Integration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stock Tracker Pro - Windows 11 Edition" -ForegroundColor Yellow
Write-Host "Version 7.0 with Real ML Integration" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/4] Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/4] Installing/Updating dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet --disable-pip-version-check

Write-Host ""
Write-Host "[3/4] Starting backend servers..." -ForegroundColor Green

# Kill any existing processes on ports 8002 and 8004
Write-Host "Cleaning up any existing processes..." -ForegroundColor Yellow
$processes8002 = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
$processes8004 = Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

foreach ($pid in $processes8002) {
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}
foreach ($pid in $processes8004) {
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Starting Main Backend Server (port 8002)..." -ForegroundColor Cyan
$backend1 = Start-Process python -ArgumentList "backend.py" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "Starting ML Backend Server (port 8004)..." -ForegroundColor Cyan
$backend2 = Start-Process python -ArgumentList "backend_ml_enhanced.py" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[4/4] Launching application..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Application is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Main Dashboard: " -NoNewline
Write-Host "http://localhost:8002" -ForegroundColor Yellow
Write-Host "Diagnostic Tool: " -NoNewline
Write-Host "http://localhost:8002/diagnostic_tool.html" -ForegroundColor Yellow
Write-Host "Verify Setup: " -NoNewline
Write-Host "http://localhost:8002/verify_setup.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening in your default browser..." -ForegroundColor Green
Start-Process "http://localhost:8002"

Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 60
        
        # Check if processes are still running
        if (-not $backend1.HasExited -and -not $backend2.HasExited) {
            # Both servers running
        } else {
            Write-Host "WARNING: One or more servers have stopped!" -ForegroundColor Red
            Write-Host "Restarting servers..." -ForegroundColor Yellow
            
            if ($backend1.HasExited) {
                $backend1 = Start-Process python -ArgumentList "backend.py" -PassThru -WindowStyle Hidden
            }
            if ($backend2.HasExited) {
                $backend2 = Start-Process python -ArgumentList "backend_ml_enhanced.py" -PassThru -WindowStyle Hidden
            }
        }
    }
} finally {
    # Clean up on exit
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $backend1.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $backend2.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}
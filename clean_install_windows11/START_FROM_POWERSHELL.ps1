# Quick Start Script for PowerShell
# Run this directly in PowerShell

Write-Host "Starting Stock Tracker..." -ForegroundColor Green

# Kill existing Python processes
Get-Process python*, pythonw* -ErrorAction SilentlyContinue | Stop-Process -Force

# Create directories if needed
@("historical_data", "logs", "uploads") | ForEach-Object {
    if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ | Out-Null }
}

# Install packages
Write-Host "Installing packages..." -ForegroundColor Yellow
pip install --quiet yfinance fastapi uvicorn pandas numpy "urllib3<2" 2>$null

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/c python -m http.server 8000" -WindowStyle Minimized
Start-Sleep -Seconds 2
Start-Process cmd -ArgumentList "/c python backend.py" -WindowStyle Minimized
Start-Sleep -Seconds 2

# Open browser
Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8000"

Write-Host "`nStock Tracker is starting!" -ForegroundColor Cyan
Write-Host "If page doesn't load, wait 10 seconds and refresh." -ForegroundColor Yellow
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host
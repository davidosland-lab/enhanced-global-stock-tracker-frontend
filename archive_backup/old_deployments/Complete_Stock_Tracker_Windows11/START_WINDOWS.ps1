# Complete Stock Tracker - Windows 11 Startup Script
# Run with: powershell -ExecutionPolicy Bypass -File START_WINDOWS.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Complete Stock Tracker - Windows 11" -ForegroundColor Yellow
Write-Host "  Starting on http://localhost:8002" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/5] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/5] Installing/Updating dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet --disable-pip-version-check 2>$null

# Check Historical Data Manager
Write-Host ""
Write-Host "[3/5] Checking Historical Data Manager..." -ForegroundColor Cyan
python -c "from historical_data_manager import HistoricalDataManager; print('✓ Historical Data Manager: Ready')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Note: Historical Data Manager will initialize on first run" -ForegroundColor Yellow
}

# Optional: Download initial data
Write-Host ""
Write-Host "[4/5] Would you like to download initial market data? (y/n)" -ForegroundColor Yellow
$downloadData = Read-Host
if ($downloadData -eq 'y' -or $downloadData -eq 'Y') {
    Write-Host "Downloading CBA.AX and major indices..." -ForegroundColor Cyan
    python -c @"
import asyncio
from historical_data_manager import HistoricalDataManager

async def download():
    manager = HistoricalDataManager()
    await manager.download_historical_data(
        symbols=['CBA.AX', '^AORD', '^GSPC', '^FTSE'],
        period='3mo',
        intervals=['1h', '1d']
    )
    print('✓ Initial data downloaded successfully!')

asyncio.run(download())
"@ 2>$null
}

# Open browser
Write-Host ""
Write-Host "[5/5] Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8002"

# Start server
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Server starting on http://localhost:8002" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Run the backend
python backend.py

# Keep window open if script fails
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Server stopped. Check errors above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
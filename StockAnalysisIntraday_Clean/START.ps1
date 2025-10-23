# Stock Analysis with Intraday Support - PowerShell Launcher

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     STOCK ANALYSIS WITH INTRADAY SUPPORT" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Set environment variables
$env:FLASK_SKIP_DOTENV = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

Write-Host ""
Write-Host "Starting server at http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Features:" -ForegroundColor Cyan
Write-Host "  • Intraday: 1m, 2m, 5m, 15m, 30m, 1h, 90m" -ForegroundColor White
Write-Host "  • Candlestick charts with real-time data" -ForegroundColor White
Write-Host "  • Technical indicators & ML predictions" -ForegroundColor White
Write-Host "  • Auto-refresh & Export to CSV" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Run the application
python app.py

# Keep window open on error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Application stopped. Check error messages above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
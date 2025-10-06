Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Windows 11 Stock Tracker - Starting..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Green
Write-Host "  - Real-time stock data from Yahoo Finance"
Write-Host "  - SQLite local storage (100x faster backtesting)"
Write-Host "  - CBA Enhanced tracker with Documents/Media"
Write-Host "  - Phase 4 predictor with GNN models"
Write-Host "  - Document analyzer with FinBERT"
Write-Host ""
Write-Host "Starting backend server on http://localhost:8002" -ForegroundColor Yellow
Write-Host ""
python backend.py
Read-Host "Press Enter to exit"

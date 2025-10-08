# PowerShell Script to Force Fix Backend
Write-Host "========================================" -ForegroundColor Green
Write-Host "  FORCE FIX BACKEND - PowerShell Method" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Kill all Python processes on port 8002
Write-Host "Killing backend processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | ForEach-Object {
    $processId = $_.OwningProcess
    if ($processId -gt 0) {
        Write-Host "  Killing process $processId"
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

# Also kill by name
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*backend.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# Check if backend.py has the endpoints
Write-Host ""
Write-Host "Checking backend.py for endpoints..." -ForegroundColor Yellow
$content = Get-Content "backend.py" -Raw

$hasHealth = $content -match "@app\.get\(`"/api/health`"\)"
$hasMarketSummary = $content -match "@app\.get\(`"/api/market-summary`"\)"

Write-Host "  /api/health found: $hasHealth"
Write-Host "  /api/market-summary found: $hasMarketSummary"

if (-not $hasHealth -or -not $hasMarketSummary) {
    Write-Host ""
    Write-Host "ENDPOINTS MISSING! Adding them now..." -ForegroundColor Red
    
    # Use the complete backend file
    if (Test-Path "backend_COMPLETE_WITH_ALL_ENDPOINTS.py") {
        Copy-Item "backend_COMPLETE_WITH_ALL_ENDPOINTS.py" "backend.py" -Force
        Write-Host "✓ Replaced backend.py with complete version" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Cannot find backend_COMPLETE_WITH_ALL_ENDPOINTS.py" -ForegroundColor Red
        Write-Host "Please run DIRECT_FIX_BACKEND.py manually" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Starting fixed backend..." -ForegroundColor Yellow
Start-Process python -ArgumentList "backend.py" -WindowStyle Minimized

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Testing endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/api/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ /api/health is working!" -ForegroundColor Green
        Write-Host $response.Content
    }
} catch {
    Write-Host "✗ /api/health failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "         FIX COMPLETE!" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Please refresh http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend Status should show Connected" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
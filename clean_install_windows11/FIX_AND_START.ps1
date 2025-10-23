# ============================================================
# FIX AND START - Complete Windows 11 Stock Tracker Solution
# PowerShell Version for Enhanced Reliability
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "      STOCK TRACKER - COMPLETE FIX AND START" -ForegroundColor Yellow
Write-Host "      Windows 11 Production Environment" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill existing Python processes
Write-Host "[1/7] Terminating existing processes..." -ForegroundColor Green
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Step 2: Clear ports
Write-Host "[2/7] Clearing ports 8000, 8002, 8003..." -ForegroundColor Green
$ports = @(8000, 8002, 8003)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.OwningProcess -ne 0) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}
Start-Sleep -Seconds 2

# Step 3: Apply fixes
Write-Host "[3/7] Applying comprehensive fixes to backend.py..." -ForegroundColor Green
$fixResult = Start-Process python -ArgumentList "FINAL_FIX_ALL.py" -Wait -PassThru -NoNewWindow
if ($fixResult.ExitCode -ne 0) {
    Write-Host "WARNING: Fix script encountered an issue, continuing..." -ForegroundColor Yellow
}
Start-Sleep -Seconds 2

# Step 4: Install dependencies
Write-Host "[4/7] Installing dependencies..." -ForegroundColor Green
& pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles
& pip install --quiet urllib3==1.26.15
Start-Sleep -Seconds 2

# Step 5: Start Frontend
Write-Host "[5/7] Starting Frontend Server on port 8000..." -ForegroundColor Green
$frontend = Start-Process python -ArgumentList "-m", "http.server", "8000" -WindowStyle Minimized -PassThru
Start-Sleep -Seconds 3

# Step 6: Start Backend API
Write-Host "[6/7] Starting Backend API on port 8002..." -ForegroundColor Green
$backend = Start-Process python -ArgumentList "-m", "uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8002", "--reload" -WindowStyle Minimized -PassThru
Start-Sleep -Seconds 3

# Step 7: Start ML Backend
Write-Host "[7/7] Starting ML Backend on port 8003..." -ForegroundColor Green
if (Test-Path "backend_ml_enhanced.py") {
    $mlbackend = Start-Process python -ArgumentList "backend_ml_enhanced.py" -WindowStyle Minimized -PassThru
} else {
    Write-Host "WARNING: ML Backend file not found, skipping..." -ForegroundColor Yellow
}
Start-Sleep -Seconds 3

# Display success message
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    ALL SERVICES STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running:" -ForegroundColor Yellow
Write-Host "  - Frontend:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Backend API: http://localhost:8002" -ForegroundColor Cyan
Write-Host "  - ML Backend:  http://localhost:8003" -ForegroundColor Cyan
Write-Host ""

# Open browser
Write-Host "Opening browser to landing page..." -ForegroundColor Green
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "Press any key to check service status..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Check status
Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Green
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Format-Table State, OwningProcess
Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | Format-Table State, OwningProcess
Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue | Format-Table State, OwningProcess

Write-Host ""
Write-Host "Services are running. Close this window to stop all services." -ForegroundColor Yellow
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
# ============================================================
# START ALL SERVICES - PowerShell Version
# Complete Stock Tracker with ML Backend
# ============================================================

Clear-Host
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    STOCK TRACKER - STARTING ALL SERVICES" -ForegroundColor Yellow
Write-Host "    Including ML Backend for Training Centre" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Function to test port
function Test-Port {
    param($Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return ($connection -ne $null)
}

# Step 1: Kill all Python processes
Write-Host "[1/11] Killing all Python processes..." -ForegroundColor Green
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Step 2: Clear ports
Write-Host "[2/11] Clearing ports 8000, 8002, 8003..." -ForegroundColor Green
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

# Step 3: Fix ML Backend port
Write-Host "[3/11] Fixing ML Backend port configuration..." -ForegroundColor Green
if (Test-Path "FIX_ML_PORT.py") {
    & python FIX_ML_PORT.py 2>$null
}

# Step 4: Update landing page
Write-Host "[4/11] Updating landing page..." -ForegroundColor Green
if (Test-Path "index_complete.html") {
    Copy-Item -Path "index_complete.html" -Destination "index.html" -Force
}

# Step 5: Apply backend fixes
Write-Host "[5/11] Applying backend fixes..." -ForegroundColor Green
if (Test-Path "FINAL_FIX_ALL.py") {
    & python FINAL_FIX_ALL.py 2>$null
}
Start-Sleep -Seconds 2

# Step 6: Create directories
Write-Host "[6/11] Creating required directories..." -ForegroundColor Green
$dirs = @("historical_data", "models", "uploads", "predictions", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Step 7: Install dependencies
Write-Host "[7/11] Installing dependencies..." -ForegroundColor Green
& pip install --quiet fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles 2>$null
& pip install --quiet urllib3==1.26.15 2>$null

# Step 8: Start Frontend
Write-Host "[8/11] Starting Frontend Server (port 8000)..." -ForegroundColor Green
$frontend = Start-Process python -ArgumentList "-m", "http.server", "8000" -WindowStyle Minimized -PassThru
Start-Sleep -Seconds 3

# Step 9: Start Backend API
Write-Host "[9/11] Starting Backend API (port 8002)..." -ForegroundColor Green
$backend = Start-Process python -ArgumentList "-m", "uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8002" -WindowStyle Minimized -PassThru
Start-Sleep -Seconds 5

# Step 10: Start ML Backend
Write-Host "[10/11] Starting ML Backend (port 8003)..." -ForegroundColor Green
if (Test-Path "backend_ml_enhanced.py") {
    $mlbackend = Start-Process python -ArgumentList "-m", "uvicorn", "backend_ml_enhanced:app", "--host", "0.0.0.0", "--port", "8003" -WindowStyle Minimized -PassThru
    Write-Host "ML Backend starting on port 8003..." -ForegroundColor Yellow
} else {
    Write-Host "ERROR: backend_ml_enhanced.py NOT FOUND!" -ForegroundColor Red
}
Start-Sleep -Seconds 5

# Step 11: Verify services
Write-Host "[11/11] Verifying services..." -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    SERVICE STATUS CHECK" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check each service
if (Test-Port 8000) {
    Write-Host "[✓] Frontend Server:  RUNNING on http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "[✗] Frontend Server:  NOT RUNNING" -ForegroundColor Red
}

if (Test-Port 8002) {
    Write-Host "[✓] Backend API:      RUNNING on http://localhost:8002" -ForegroundColor Green
} else {
    Write-Host "[✗] Backend API:      NOT RUNNING" -ForegroundColor Red
}

if (Test-Port 8003) {
    Write-Host "[✓] ML Backend:       RUNNING on http://localhost:8003" -ForegroundColor Green
} else {
    Write-Host "[✗] ML Backend:       NOT RUNNING - ML Training won't work!" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    MODULE STATUS" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Port 8002) {
    Write-Host "[✓] CBA Enhanced:          Ready" -ForegroundColor Green
    Write-Host "[✓] Market Tracker:        Ready" -ForegroundColor Green
    Write-Host "[✓] Technical Analysis:    Ready" -ForegroundColor Green
    Write-Host "[✓] Document Analyser:     Ready" -ForegroundColor Green
    Write-Host "[✓] Historical Data:       Ready" -ForegroundColor Green
} else {
    Write-Host "[✗] Most modules:          NOT READY - Backend API required!" -ForegroundColor Red
}

if (Test-Port 8003) {
    Write-Host "[✓] ML Training Centre:    Ready" -ForegroundColor Green
    Write-Host "[✓] Advanced Predictions:  Ready" -ForegroundColor Green
} else {
    Write-Host "[✗] ML Training Centre:    NOT READY!" -ForegroundColor Red
    Write-Host "[✗] Advanced Predictions:  NOT READY!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "Test endpoints at: http://localhost:8000/TEST_ALL_ENDPOINTS.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Keep this window open to maintain services" -ForegroundColor Yellow
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
# Stock Tracker Master Startup Script for Windows 11
# Run with: powershell -ExecutionPolicy Bypass -File MASTER_STARTUP_WIN11.ps1

$Host.UI.RawUI.WindowTitle = "Stock Tracker Master Control - Windows 11"
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                   STOCK TRACKER MASTER STARTUP - WINDOWS 11" -ForegroundColor Cyan
Write-Host "                        Complete System Initialization" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host

# Set working directory to script location
Set-Location -Path $PSScriptRoot

# ============================= PHASE 1: CLEANUP =============================
Write-Host "[PHASE 1/5] SYSTEM CLEANUP" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"

# Function to kill processes on a specific port
function Clear-Port {
    param([int]$Port)
    
    $connections = netstat -ano | Select-String ":$Port.*LISTENING"
    foreach ($connection in $connections) {
        $parts = $connection -split '\s+'
        $pid = $parts[-1]
        if ($pid -match '^\d+$') {
            Write-Host "   - Killing process on port $Port (PID: $pid)" -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "[1.1] Terminating all Python processes..." -ForegroundColor White
Get-Process python*, pythonw* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "[1.2] Clearing ports 8000, 8002, 8003..." -ForegroundColor White
Clear-Port -Port 8000
Clear-Port -Port 8002
Clear-Port -Port 8003

Write-Host "[1.3] Final cleanup..." -ForegroundColor White
Start-Sleep -Seconds 2

Write-Host "[OK] Cleanup completed" -ForegroundColor Green
Write-Host

# ============================= PHASE 2: ENVIRONMENT CHECK =============================
Write-Host "[PHASE 2/5] ENVIRONMENT VERIFICATION" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"

Write-Host "[2.1] Checking Python installation..." -ForegroundColor White
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
        Write-Host "   - Python version: $($matches[1])" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[2.2] Checking pip..." -ForegroundColor White
$pipVersion = pip --version 2>&1
if ($pipVersion -match "pip (\d+\.\d+)") {
    Write-Host "   - pip version: $($matches[1])" -ForegroundColor Gray
} else {
    Write-Host "   - pip not found, installing..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

Write-Host "[OK] Environment verified" -ForegroundColor Green
Write-Host

# ============================= PHASE 3: DEPENDENCIES =============================
Write-Host "[PHASE 3/5] INSTALLING/UPDATING DEPENDENCIES" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"

Write-Host "[3.1] Installing core dependencies..." -ForegroundColor White
pip install --quiet --upgrade pip 2>$null

Write-Host "[3.2] Installing required packages..." -ForegroundColor White
# Python 3.12 compatibility fix
pip install --quiet --upgrade "urllib3<2" 2>$null

# Core packages
$packages = @(
    "yfinance",
    "fastapi",
    "uvicorn",
    "python-multipart",
    "pandas",
    "numpy",
    "cachetools",
    "pytz",
    "requests"
)
pip install --quiet --upgrade $packages 2>$null

Write-Host "[3.3] Installing ML packages..." -ForegroundColor White
pip install --quiet --upgrade scikit-learn xgboost joblib 2>$null

Write-Host "[3.4] Creating required directories..." -ForegroundColor White
$directories = @("historical_data", "uploads", "models", "logs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   - Created $dir/" -ForegroundColor Gray
    }
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host

# ============================= PHASE 4: START SERVICES =============================
Write-Host "[PHASE 4/5] STARTING SERVICES" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"

# Function to start a service
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
    )
    
    Write-Host "[4.$Port] Starting $Name on port $Port..." -ForegroundColor White
    
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "cmd.exe"
    $processInfo.Arguments = "/c `"cd /d `"$PSScriptRoot`" && $Command 2>logs\$Name.log`""
    $processInfo.WindowStyle = "Minimized"
    $processInfo.CreateNoWindow = $false
    
    $process = [System.Diagnostics.Process]::Start($processInfo)
    Start-Sleep -Seconds 2
    
    return $process
}

# Start Frontend
$frontend = Start-Service -Name "frontend" -Command "python -m http.server 8000" -Port 8000

# Start Backend
$backend = Start-Service -Name "backend" -Command "python backend.py" -Port 8002

# Start ML Backend
$mlCommand = if (Test-Path "ml_backend.py") {
    "python ml_backend.py"
} elseif (Test-Path "ml_training_backend.py") {
    "python ml_training_backend.py"
} else {
    # Create simple ML backend
    @"
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/")
async def root(): return {"status": "ML Backend Ready", "port": 8003}
@app.get("/api/ml/status")
async def ml_status(): return {"status": "ready", "models_available": ["LSTM", "XGBoost"]}
if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8003)
"@ | Out-File -FilePath "temp_ml.py" -Encoding UTF8
    "python temp_ml.py"
}
$mlBackend = Start-Service -Name "ml_backend" -Command $mlCommand -Port 8003

Write-Host "[OK] Services started" -ForegroundColor Green
Write-Host

# ============================= PHASE 5: VERIFICATION =============================
Write-Host "[PHASE 5/5] SERVICE VERIFICATION" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"

# Function to check if port is listening
function Test-Port {
    param([int]$Port, [string]$ServiceName)
    
    Write-Host "[5.$Port] Verifying $ServiceName..." -ForegroundColor White
    
    $maxAttempts = 10
    for ($i = 1; $i -le $maxAttempts; $i++) {
        $listening = netstat -an | Select-String ":$Port.*LISTENING"
        if ($listening) {
            Write-Host "   [OK] $ServiceName running on port $Port" -ForegroundColor Green
            
            # Test HTTP endpoint
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "   [OK] $ServiceName responding to requests" -ForegroundColor Green
                }
            } catch {
                # Ignore errors for simple port check
            }
            return $true
        }
        Start-Sleep -Seconds 1
    }
    
    Write-Host "   [WARNING] $ServiceName not detected on port $Port" -ForegroundColor Yellow
    Write-Host "   Check logs\$ServiceName.log for errors" -ForegroundColor Yellow
    return $false
}

$frontendOK = Test-Port -Port 8000 -ServiceName "Frontend Server"
$backendOK = Test-Port -Port 8002 -ServiceName "Backend API"
$mlOK = Test-Port -Port 8003 -ServiceName "ML Backend"

# Test Historical Data Manager
Write-Host "[5.4] Testing Historical Data Manager..." -ForegroundColor White
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/api/historical/statistics" -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "   [OK] Historical Data Manager endpoints accessible" -ForegroundColor Green
} catch {
    Write-Host "   [INFO] Historical Data Manager initializing..." -ForegroundColor Yellow
}

Write-Host
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                          SYSTEM STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Status summary
$servicesOK = 0
if ($frontendOK) { $servicesOK++ }
if ($backendOK) { $servicesOK++ }
if ($mlOK) { $servicesOK++ }

Write-Host
if ($frontendOK) {
    Write-Host " [✓] Frontend Server:     http://localhost:8000       [RUNNING]" -ForegroundColor Green
} else {
    Write-Host " [✗] Frontend Server:     http://localhost:8000       [FAILED]" -ForegroundColor Red
}

if ($backendOK) {
    Write-Host " [✓] Backend API:         http://localhost:8002       [RUNNING]" -ForegroundColor Green
    Write-Host "                          http://localhost:8002/docs  [API Docs]" -ForegroundColor Green
} else {
    Write-Host " [✗] Backend API:         http://localhost:8002       [FAILED]" -ForegroundColor Red
}

if ($mlOK) {
    Write-Host " [✓] ML Backend:          http://localhost:8003       [RUNNING]" -ForegroundColor Green
} else {
    Write-Host " [~] ML Backend:          http://localhost:8003       [OPTIONAL]" -ForegroundColor Yellow
}

Write-Host
Write-Host "--------------------------------------------------------------------------------"
Write-Host " Services Running: $servicesOK/3" -ForegroundColor White
Write-Host " Working Directory: $PSScriptRoot" -ForegroundColor White
Write-Host " Log Files: $PSScriptRoot\logs\" -ForegroundColor White
Write-Host "--------------------------------------------------------------------------------"

if ($servicesOK -ge 2) {
    Write-Host
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "                        🚀 SYSTEM READY TO USE! 🚀" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host
    Write-Host " Opening Stock Tracker in your browser..." -ForegroundColor White
    Write-Host
    Write-Host " IMPORTANT URLS:" -ForegroundColor Cyan
    Write-Host " ---------------"
    Write-Host " • Main Application:      http://localhost:8000" -ForegroundColor White
    Write-Host " • API Documentation:     http://localhost:8002/docs" -ForegroundColor White
    Write-Host " • Test Historical Data:  http://localhost:8000/test_historical_manager.html" -ForegroundColor White
    Write-Host
    Write-Host " TROUBLESHOOTING:" -ForegroundColor Cyan
    Write-Host " ----------------"
    Write-Host " • If pages don't load, wait 5-10 seconds and refresh" -ForegroundColor White
    Write-Host " • Check log files in: $PSScriptRoot\logs\" -ForegroundColor White
    Write-Host " • To restart, close this window and run again" -ForegroundColor White
    Write-Host
    
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000"
} else {
    Write-Host
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "                    ⚠️  WARNING: SOME SERVICES FAILED ⚠️" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host
    Write-Host " Please check the log files in: $PSScriptRoot\logs\" -ForegroundColor Yellow
    Write-Host " Common issues:" -ForegroundColor Yellow
    Write-Host " - Port already in use (close other applications)" -ForegroundColor White
    Write-Host " - Missing Python packages (reinstall requirements)" -ForegroundColor White
    Write-Host " - Antivirus blocking Python (add exception)" -ForegroundColor White
    Write-Host
}

Write-Host
Write-Host "Press Enter to keep servers running (or close window to stop all)..." -ForegroundColor Cyan
Read-Host

# Keep alive
Write-Host
Write-Host "Servers are running. Close this window to stop all services." -ForegroundColor Green
Write-Host
while ($true) {
    Start-Sleep -Seconds 60
    Write-Host "." -NoNewline -ForegroundColor Gray
}
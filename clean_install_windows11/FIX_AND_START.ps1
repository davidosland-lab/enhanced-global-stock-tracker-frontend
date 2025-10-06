# Ultimate Stock Tracker Fix for Windows 11
# PowerShell Script with Better Error Handling

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "        ULTIMATE STOCK TRACKER - WINDOWS 11 FIX" -ForegroundColor Cyan
Write-Host "        PowerShell Edition with Error Handling" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to kill process on port
function Kill-ProcessOnPort {
    param($port)
    $process = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
        Write-Host "Killed process on port $port" -ForegroundColor Yellow
    }
}

# Phase 1: Clean up
Write-Host "[PHASE 1] Cleaning up existing processes..." -ForegroundColor Green
Kill-ProcessOnPort -port 8000
Kill-ProcessOnPort -port 8002
Kill-ProcessOnPort -port 8003
Start-Sleep -Seconds 2

# Phase 2: Check Python
Write-Host ""
Write-Host "[PHASE 2] Checking Python installation..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}
Write-Host "Found: $pythonVersion" -ForegroundColor Cyan

# Phase 3: Fix Python Environment
Write-Host ""
Write-Host "[PHASE 3] Fixing Python environment..." -ForegroundColor Green

# Fix setuptools first
Write-Host "Updating pip and setuptools..." -ForegroundColor Yellow
python -m pip install --upgrade pip 2>$null
python -m pip install --upgrade setuptools wheel 2>$null

# Phase 4: Install Dependencies
Write-Host ""
Write-Host "[PHASE 4] Installing required packages..." -ForegroundColor Green

$packages = @(
    "fastapi",
    "uvicorn",
    "yfinance",
    "pandas",
    "numpy",
    "python-multipart",
    "aiofiles",
    "cachetools"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -NoNewline
    $output = python -m pip install $package 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " Warning" -ForegroundColor Yellow
    }
}

# Phase 5: Check for backend file
Write-Host ""
Write-Host "[PHASE 5] Checking application files..." -ForegroundColor Green

$backendFile = ""
if (Test-Path "backend_ultimate_fixed.py") {
    $backendFile = "backend_ultimate_fixed.py"
    Write-Host "Found: backend_ultimate_fixed.py" -ForegroundColor Cyan
} elseif (Test-Path "backend.py") {
    $backendFile = "backend.py"
    Write-Host "Found: backend.py" -ForegroundColor Cyan
} else {
    Write-Host "No backend found, creating minimal version..." -ForegroundColor Yellow
    
    # Create minimal backend
    @'
import yfinance as yf
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/status")
async def status():
    return {"status": "online", "timestamp": datetime.now().isoformat()}

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            raise HTTPException(404, f"No data for {symbol}")
        latest = hist.iloc[-1]
        return {
            "symbol": symbol,
            "price": float(latest['Close']),
            "volume": int(latest['Volume']),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/historical/{symbol}")
async def get_historical(symbol: str, period: str = "1mo"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        return {"symbol": symbol, "data": data}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/technical/{symbol}")
async def get_technical(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")
        close = hist['Close']
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        return {
            "symbol": symbol,
            "indicators": {
                "sma_20": float(sma_20.iloc[-1]) if len(sma_20) > 0 else None,
                "sma_50": float(sma_50.iloc[-1]) if len(sma_50) > 0 else None,
                "current_price": float(close.iloc[-1])
            },
            "signals": {
                "trend": "bullish" if sma_20.iloc[-1] > sma_50.iloc[-1] else "bearish"
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/documents/upload")
async def upload_doc(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "size": len(contents),
        "size_mb": round(len(contents) / 1024 / 1024, 2),
        "status": "uploaded"
    }

@app.get("/api/indices")
async def get_indices():
    return {"indices": [], "count": 0}

@app.post("/api/predict")
async def predict(data: dict):
    return {"predictions": [], "method": "statistical"}

@app.post("/api/historical/batch-download")
async def batch_download(data: dict):
    return {"success": 0, "failed": 0, "results": []}

@app.get("/")
async def root():
    return {"status": "online", "port": 8002, "message": "Stock Tracker API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
'@ | Set-Content -Path "backend_minimal.py"
    
    $backendFile = "backend_minimal.py"
}

# Create uploads directory
if (!(Test-Path "uploads")) {
    New-Item -ItemType Directory -Name "uploads" | Out-Null
}

# Phase 6: Start Services
Write-Host ""
Write-Host "[PHASE 6] Starting services..." -ForegroundColor Green

# Start Backend
Write-Host "Starting Backend API on port 8002..."
Start-Process -FilePath "python" -ArgumentList $backendFile -WindowStyle Minimized

# Wait for backend to start
Start-Sleep -Seconds 5

# Test backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/api/status" -UseBasicParsing -TimeoutSec 2
    Write-Host "Backend API: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "Backend API: May have issues, trying alternative start..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8002" -WindowStyle Minimized
}

# Start Frontend
Write-Host "Starting Frontend Server on port 8000..."
if (Test-Path "frontend_server.py") {
    Start-Process -FilePath "python" -ArgumentList "frontend_server.py" -WindowStyle Minimized
} else {
    Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "8000" -WindowStyle Minimized
}

Start-Sleep -Seconds 3

# Phase 7: Launch Browser
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "        STOCK TRACKER IS READY!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
Write-Host "Backend API:  http://localhost:8002" -ForegroundColor Cyan
Write-Host "Frontend UI:  http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "Press any key to stop all services and exit..." -ForegroundColor Yellow
Read-Host

# Cleanup
Write-Host "Shutting down services..." -ForegroundColor Yellow
Kill-ProcessOnPort -port 8000
Kill-ProcessOnPort -port 8002
Kill-ProcessOnPort -port 8003

Write-Host "All services stopped!" -ForegroundColor Green
Start-Sleep -Seconds 2
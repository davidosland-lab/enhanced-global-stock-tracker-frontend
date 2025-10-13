#!/usr/bin/env python3
"""
Stock Tracker - Simple Python Startup
No batch file complications
"""

import subprocess
import sys
import os
import time
import webbrowser
import platform
import signal

def create_minimal_ml_backend():
    """Create a minimal ML backend if the file is missing"""
    ml_code = '''# Minimal ML Backend
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrainRequest(BaseModel):
    symbol: str
    model_type: str = "ensemble"
    epochs: int = 50

class PredictionRequest(BaseModel):
    symbol: str
    days: int = 7

@app.get("/")
async def root():
    return {"service": "ML Backend (Minimal)", "status": "ready"}

@app.get("/api/ml/status")
async def status():
    return {
        "status": "ready",
        "service": "ml_backend",
        "port": 8003,
        "models": ["lstm", "gru", "transformer", "ensemble"],
        "mode": "minimal"
    }

@app.post("/api/ml/train")
async def train(request: TrainRequest):
    return {
        "status": "training",
        "symbol": request.symbol,
        "model_type": request.model_type,
        "message": "Model training simulated (minimal mode)"
    }

@app.post("/api/ml/predict")
async def predict(request: PredictionRequest):
    import random
    predictions = []
    base_price = 170.50 if "CBA" in request.symbol else 100.0
    
    for i in range(request.days):
        change = random.uniform(-2, 3)
        price = base_price + (change * (i + 1))
        predictions.append({
            "day": i + 1,
            "price": round(price, 2),
            "confidence": round(0.85 - (i * 0.02), 2)
        })
    
    return {
        "symbol": request.symbol,
        "predictions": predictions,
        "model": "minimal"
    }

@app.post("/api/ml/backtest")
async def backtest(request: dict):
    return {
        "symbol": request.get("symbol", ""),
        "total_return": 0.12,
        "sharpe_ratio": 1.5,
        "max_drawdown": -0.08,
        "win_rate": 0.58,
        "message": "Simulated backtest (minimal mode)"
    }

@app.get("/api/ml/backtest/history")
async def backtest_history():
    return {"results": [], "count": 0}

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
    
    with open('ml_backend_minimal.py', 'w') as f:
        f.write(ml_code)
    print("Created minimal ML backend: ml_backend_minimal.py")

def check_files():
    """Check if required files exist"""
    required_files = {
        'backend.py': 'Main backend service',
        'index.html': 'Frontend interface',
        'ml_backend.py': 'ML service (optional)'
    }
    
    print("\nChecking required files...")
    all_found = True
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"  ✓ {file} - {description}")
        else:
            if file == 'ml_backend.py':
                print(f"  ⚠ {file} - {description} - Will create minimal version")
                create_minimal_ml_backend()
            else:
                print(f"  ✗ {file} - {description} - MISSING!")
                all_found = False
    
    if not all_found:
        print("\nERROR: Required files are missing!")
        print("Make sure you're running this from the extracted folder")
        return False
    
    return True

def install_packages():
    """Install minimal required packages"""
    print("\nChecking/Installing packages...")
    
    packages = [
        'fastapi',
        'uvicorn', 
        'yfinance',
        'pandas',
        'numpy',
        'pytz',
        'python-multipart',
        'httpx'
    ]
    
    for package in packages:
        print(f"  Installing {package}...", end=' ')
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package, '--quiet'],
            capture_output=True
        )
        if result.returncode == 0:
            print("✓")
        else:
            print("(may already be installed)")

def start_service(name, command, port):
    """Start a service"""
    print(f"\nStarting {name} on port {port}...")
    
    # Check if port is already in use
    if platform.system() == 'Windows':
        check_port = subprocess.run(
            f'netstat -an | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        if 'LISTENING' in check_port.stdout:
            print(f"  Port {port} already in use, attempting to free it...")
            # Try to kill process on port
            for line in check_port.stdout.split('\n'):
                if 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        time.sleep(1)
                        break
    
    # Start the service
    if platform.system() == 'Windows':
        process = subprocess.Popen(
            command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    time.sleep(2)
    
    if process.poll() is None:
        print(f"  ✓ {name} started successfully")
    else:
        print(f"  ⚠ {name} may have failed to start")
    
    return process

def main():
    print("\n" + "="*70)
    print("    STOCK TRACKER - PYTHON STARTUP")
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print(f"\nERROR: Python 3.7+ required (you have {sys.version})")
        input("Press Enter to exit...")
        return
    
    print(f"\n✓ Python {sys.version.split()[0]} detected")
    
    # Check files
    if not check_files():
        input("\nPress Enter to exit...")
        return
    
    # Install packages
    install_packages()
    
    # Start services
    print("\n" + "-"*70)
    print("Starting services...")
    print("-"*70)
    
    processes = []
    
    # Start Backend
    backend_cmd = f"{sys.executable} backend.py 8002"
    processes.append(start_service("Backend API", backend_cmd, 8002))
    
    # Start ML Backend
    if os.path.exists('ml_backend.py'):
        ml_cmd = f"{sys.executable} ml_backend.py 8003"
    else:
        ml_cmd = f"{sys.executable} ml_backend_minimal.py 8003"
    processes.append(start_service("ML Service", ml_cmd, 8003))
    
    # Start Frontend
    frontend_cmd = f"{sys.executable} -m http.server 8000"
    processes.append(start_service("Frontend", frontend_cmd, 8000))
    
    print("\n" + "="*70)
    print("    STOCK TRACKER IS READY!")
    print("="*70)
    print("\nServices running at:")
    print("  • Web Interface: http://localhost:8000")
    print("  • Backend API:   http://localhost:8002/docs")
    print("  • ML Service:    http://localhost:8003/docs")
    
    print("\nOpening browser in 3 seconds...")
    time.sleep(3)
    webbrowser.open('http://localhost:8000')
    
    print("\n⚠ Keep this window open!")
    print("Press Ctrl+C to stop all services\n")
    
    # Keep running
    try:
        while True:
            time.sleep(5)
            # Check if processes are still running
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print(f"\n⚠ Service {i+1} stopped unexpectedly")
    
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        for process in processes:
            if process:
                try:
                    process.terminate()
                    time.sleep(0.5)
                except:
                    pass
        
        # Clean up temp files
        if os.path.exists('ml_backend_minimal.py'):
            os.remove('ml_backend_minimal.py')
        
        print("All services stopped. Goodbye!")

if __name__ == "__main__":
    main()
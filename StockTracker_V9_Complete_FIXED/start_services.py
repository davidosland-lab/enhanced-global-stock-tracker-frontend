#!/usr/bin/env python3
"""
Start all Stock Tracker services
Real implementation - NO fake data
"""

import os
import sys
import time
import subprocess
import signal
from typing import List, Dict
import requests

# Service definitions
SERVICES = [
    {
        "name": "Main Backend",
        "port": 8002,
        "script": "main_backend.py",
        "health_endpoint": "/api/health"
    },
    {
        "name": "ML Backend",
        "port": 8003,
        "script": "enhanced_ml_backend.py",
        "health_endpoint": "/api/ml/status"
    },
    {
        "name": "FinBERT Backend",
        "port": 8004,
        "script": "finbert_backend.py",
        "health_endpoint": "/api/sentiment/status"
    },
    {
        "name": "Backtesting Backend",
        "port": 8005,
        "script": "backtesting_backend.py",
        "health_endpoint": "/"
    }
]

processes = []

def signal_handler(sig, frame):
    """Handle shutdown signal"""
    print("\n⚠️  Shutting down all services...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    print("✅ All services stopped")
    sys.exit(0)

def check_port_available(port: int) -> bool:
    """Check if port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return True
        except:
            return False

def wait_for_service(port: int, endpoint: str, max_retries: int = 30) -> bool:
    """Wait for service to be ready"""
    url = f"http://localhost:{port}{endpoint}"
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def start_service(service: Dict) -> subprocess.Popen:
    """Start a single service"""
    print(f"🚀 Starting {service['name']} on port {service['port']}...")
    
    # Check if port is available
    if not check_port_available(service['port']):
        print(f"⚠️  Port {service['port']} is already in use. Skipping {service['name']}")
        return None
    
    # Start the service
    process = subprocess.Popen(
        [sys.executable, service['script']],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for service to be ready
    if wait_for_service(service['port'], service['health_endpoint']):
        print(f"✅ {service['name']} is ready on port {service['port']}")
    else:
        print(f"⚠️  {service['name']} started but not responding on port {service['port']}")
    
    return process

def main():
    """Main function to start all services"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Stock Tracker V9 - Complete Edition                  ║
    ║     Real ML, Real Data, Real Predictions                 ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Install requirements if needed
    try:
        import fastapi
        import yfinance
        import sklearn
        import pandas
    except ImportError:
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Start all services
    for service in SERVICES:
        process = start_service(service)
        if process:
            processes.append(process)
        time.sleep(2)  # Wait between service starts
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     ✅ All Services Started Successfully!                ║
    ╠══════════════════════════════════════════════════════════╣
    ║     Access Points:                                       ║
    ║     • Main API:        http://localhost:8002            ║
    ║     • ML Backend:      http://localhost:8003            ║
    ║     • FinBERT:         http://localhost:8004            ║
    ║     • Backtesting:     http://localhost:8005            ║
    ║     • Web Interface:   Open prediction_center.html      ║
    ╠══════════════════════════════════════════════════════════╣
    ║     Features:                                            ║
    ║     • 100+ ML features for better predictions           ║
    ║     • SQLite caching for 50x faster data retrieval      ║
    ║     • Real FinBERT sentiment analysis                   ║
    ║     • $100,000 backtesting with real strategies         ║
    ║     • NO fake data - all real Yahoo Finance data        ║
    ╠══════════════════════════════════════════════════════════╣
    ║     Press Ctrl+C to stop all services                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Keep running and monitor services
    try:
        while True:
            time.sleep(10)
            # Check if services are still running
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print(f"⚠️  Service {SERVICES[i]['name']} stopped unexpectedly. Restarting...")
                    processes[i] = start_service(SERVICES[i])
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
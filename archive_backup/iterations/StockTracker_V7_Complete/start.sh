#!/bin/bash
echo "=================================="
echo "Stock Tracker V7 - Complete System"
echo "100% Real Implementation"
echo "=================================="
echo

# Check Python
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create directories
mkdir -p logs saved_models data

echo "Starting services..."
echo

# Kill any existing services on our ports
echo "Cleaning up old services..."
pkill -f "port=8002" 2>/dev/null
pkill -f "port=8003" 2>/dev/null
pkill -f "port=8004" 2>/dev/null
pkill -f "8080" 2>/dev/null
sleep 2

# Start Main Backend (Port 8002)
echo "[1/4] Starting Main Backend on port 8002..."
python3 backend.py > logs/backend.log 2>&1 &
echo "PID: $!"
sleep 2

# Start ML Backend (Port 8003) - REAL ML
echo "[2/4] Starting ML Backend on port 8003 (REAL ML)..."
python3 ml_backend.py > logs/ml_backend.log 2>&1 &
echo "PID: $!"
sleep 2

# Start FinBERT Backend (Port 8004)
echo "[3/4] Starting FinBERT Backend on port 8004..."
python3 finbert_backend.py > logs/finbert.log 2>&1 &
echo "PID: $!"
sleep 2

# Start Web Server (Port 8080)
echo "[4/4] Starting Web Server on port 8080..."
python3 -m http.server 8080 > logs/web.log 2>&1 &
echo "PID: $!"
sleep 2

echo
echo "=================================="
echo "All services started!"
echo "=================================="
echo
echo "Access at: http://localhost:8080"
echo
echo "Services:"
echo "- Main API: http://localhost:8002"
echo "- ML Backend: http://localhost:8003 (Real ML)"
echo "- FinBERT: http://localhost:8004"
echo "- Web UI: http://localhost:8080"
echo
echo "Features:"
echo "✓ Real ML training (500 trees, takes 10-60s)"
echo "✓ Real predictions from trained models"
echo "✓ Real FinBERT sentiment (or keyword fallback)"
echo "✓ Global indices tracking"
echo "✓ Document analysis"
echo "✓ Backtesting with $100k"
echo
echo "Press Ctrl+C to stop all services"
echo

# Keep script running
trap 'echo "Stopping services..."; pkill -P $$; exit' INT
while true; do sleep 1; done
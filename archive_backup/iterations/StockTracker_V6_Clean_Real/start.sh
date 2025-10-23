#!/bin/bash
# Stock Tracker V6 - Clean Real ML Implementation
# Start all services

echo "=================================="
echo "Stock Tracker V6 - Clean Install"
echo "Real ML Implementation"
echo "=================================="
echo

# Check Python
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create directories
mkdir -p logs
mkdir -p saved_models
mkdir -p data

echo "Starting services..."
echo

# Start Main Backend (Port 8002)
echo "[1/3] Starting Main Backend on port 8002..."
python3 backend.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Main Backend PID: $BACKEND_PID"
sleep 2

# Start ML Backend (Port 8003)
echo "[2/3] Starting ML Backend on port 8003..."
python3 ml_backend.py > logs/ml_backend.log 2>&1 &
ML_PID=$!
echo "ML Backend PID: $ML_PID"
sleep 2

# Start Web Server (Port 8080)
echo "[3/3] Starting Web Server on port 8080..."
python3 -m http.server 8080 > logs/web.log 2>&1 &
WEB_PID=$!
echo "Web Server PID: $WEB_PID"
sleep 2

echo
echo "=================================="
echo "All services started!"
echo "=================================="
echo
echo "Access the application at:"
echo "http://localhost:8080"
echo
echo "Services:"
echo "- Main API: http://localhost:8002"
echo "- ML Backend: http://localhost:8003"
echo "- Web Interface: http://localhost:8080"
echo
echo "PIDs saved to pids.txt"
echo "$BACKEND_PID" > pids.txt
echo "$ML_PID" >> pids.txt
echo "$WEB_PID" >> pids.txt
echo
echo "To stop all services, run: ./stop.sh"
echo
echo "Logs available in:"
echo "- logs/backend.log"
echo "- logs/ml_backend.log"
echo "- logs/web.log"
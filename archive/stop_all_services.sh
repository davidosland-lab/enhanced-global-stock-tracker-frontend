#!/bin/bash

echo "🛑 Stopping GSMT Trading System..."
echo "=================================="

# Read PIDs if available
if [ -f /home/user/webapp/.backend.pid ]; then
    BACKEND_PID=$(cat /home/user/webapp/.backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
fi

if [ -f /home/user/webapp/.frontend.pid ]; then
    FRONTEND_PID=$(cat /home/user/webapp/.frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
fi

# Also kill by port in case PIDs are stale
echo "Cleaning up any remaining processes..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null

# Clean up PID files
rm -f /home/user/webapp/.backend.pid
rm -f /home/user/webapp/.frontend.pid

echo "✅ All services stopped"
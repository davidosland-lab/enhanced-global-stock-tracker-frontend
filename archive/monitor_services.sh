#!/bin/bash

# Service monitor and auto-restart script
# This ensures services are always running

while true; do
    # Check backend
    if ! curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "$(date): Backend is down, restarting..."
        cd /home/user/webapp/render_backend
        pkill -f "uvicorn.*8000"
        sleep 2
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /home/user/webapp/backend.log 2>&1 &
        echo "$(date): Backend restarted with PID $!"
    fi
    
    # Check frontend
    if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ | grep -q "200\|304"; then
        echo "$(date): Frontend is down, restarting..."
        pkill -f "http.server 3000"
        sleep 2
        cd /home/user/webapp/frontend
        nohup python3 -m http.server 3000 > /home/user/webapp/frontend.log 2>&1 &
        echo "$(date): Frontend restarted with PID $!"
    fi
    
    # Sleep for 30 seconds before next check
    sleep 30
done
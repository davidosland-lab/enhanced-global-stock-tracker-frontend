#!/bin/bash

echo "🚀 Starting GSMT Trading System..."
echo "=================================="

# Change to webapp directory
cd /home/user/webapp

# Kill any existing services on our ports
echo "📦 Cleaning up old processes..."
pkill -f "port 8000" 2>/dev/null
pkill -f "port 3000" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
pkill -f "uvicorn.*8000" 2>/dev/null
sleep 2

# Start backend API
echo "🔧 Starting Backend API on port 8000..."
cd /home/user/webapp/render_backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /home/user/webapp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Test backend
echo "🔍 Testing backend health..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "   ✅ Backend is healthy" || echo "   ❌ Backend health check failed"

# Start frontend server
echo "🌐 Starting Frontend on port 3000..."
cd /home/user/webapp/frontend
nohup python3 -m http.server 3000 > /home/user/webapp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
sleep 2

# Save PIDs for later shutdown
echo "$BACKEND_PID" > /home/user/webapp/.backend.pid
echo "$FRONTEND_PID" > /home/user/webapp/.frontend.pid

echo ""
echo "✅ All services started successfully!"
echo "=================================="
echo ""
echo "📊 Access Points:"
echo "   Main Hub:     http://localhost:3000/"
echo "   API Backend:  http://localhost:8000/"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "🌐 Public URLs (if in sandbox):"
echo "   Frontend:     https://3000-\${SANDBOX_ID}.e2b.dev/"
echo "   Backend:      https://8000-\${SANDBOX_ID}.e2b.dev/"
echo ""
echo "📝 Logs:"
echo "   Backend:      /home/user/webapp/backend.log"
echo "   Frontend:     /home/user/webapp/frontend.log"
echo ""
echo "🛑 To stop all services, run: ./stop_all_services.sh"
#!/bin/bash

# Enhanced Global Stock Market Tracker - Development Script
# This script helps run the frontend locally and connect to either local or remote backend

echo "🚀 Enhanced Global Stock Market Tracker - Development Environment"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Parse command line arguments
BACKEND_MODE="remote"
FRONTEND_PORT=3000
BACKEND_PORT=8000

while [[ $# -gt 0 ]]; do
    case $1 in
        --local-backend)
            BACKEND_MODE="local"
            shift
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./dev.sh [options]"
            echo ""
            echo "Options:"
            echo "  --local-backend     Run with local backend (requires backend code)"
            echo "  --frontend-port     Set frontend port (default: 3000)"
            echo "  --backend-port      Set backend port (default: 8000)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if frontend port is available
if check_port $FRONTEND_PORT; then
    echo -e "${RED}Port $FRONTEND_PORT is already in use!${NC}"
    echo "Please stop the existing service or use --frontend-port to specify a different port."
    exit 1
fi

# Start backend if local mode
if [ "$BACKEND_MODE" = "local" ]; then
    if [ ! -d "backend" ]; then
        echo -e "${YELLOW}Warning: backend directory not found!${NC}"
        echo "To use local backend, you need to clone the backend repository."
        echo "Falling back to remote backend..."
        BACKEND_MODE="remote"
    else
        echo -e "${GREEN}Starting local backend on port $BACKEND_PORT...${NC}"
        cd backend
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        
        # Check if requirements are installed
        if ! python -c "import fastapi" 2>/dev/null; then
            echo "Installing backend dependencies..."
            pip install -r requirements.txt
        fi
        
        # Start backend
        uvicorn main:app --reload --port $BACKEND_PORT --host 0.0.0.0 &
        BACKEND_PID=$!
        cd ..
        
        echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
        echo "Backend URL: http://localhost:$BACKEND_PORT"
        echo "API Docs: http://localhost:$BACKEND_PORT/docs"
        echo ""
        
        # Wait for backend to be ready
        echo "Waiting for backend to be ready..."
        for i in {1..10}; do
            if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null; then
                echo -e "${GREEN}Backend is ready!${NC}"
                break
            fi
            sleep 1
        done
    fi
fi

# Display backend mode
if [ "$BACKEND_MODE" = "remote" ]; then
    echo -e "${YELLOW}Using remote backend at: https://web-production-68eaf.up.railway.app${NC}"
    echo ""
fi

# Start frontend
echo -e "${GREEN}Starting frontend on port $FRONTEND_PORT...${NC}"
cd frontend

# Use Python's built-in HTTP server
python3 -m http.server $FRONTEND_PORT &
FRONTEND_PID=$!

echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
echo ""
echo "================================================================"
echo -e "${GREEN}Development environment is ready!${NC}"
echo ""
echo "🌐 Frontend URL: http://localhost:$FRONTEND_PORT"
if [ "$BACKEND_MODE" = "local" ]; then
    echo "🔧 Backend URL: http://localhost:$BACKEND_PORT"
    echo "📚 API Docs: http://localhost:$BACKEND_PORT/docs"
else
    echo "🔧 Backend URL: https://web-production-68eaf.up.railway.app (Remote)"
fi
echo ""
echo "Press Ctrl+C to stop all services"
echo "================================================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Wait for processes
wait
#!/bin/bash
# Stock Tracker ML Services Startup Script
# Version 6.0 - ML Integration Enhanced

echo "========================================"
echo "Stock Tracker ML Services Startup Script"
echo "Version 6.0 - ML Integration Enhanced"
echo "========================================"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to script directory
cd "$(dirname "$0")"

echo -e "${YELLOW}Starting services in correct order...${NC}"
echo

# Function to check if port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Kill existing services if running
echo -e "${YELLOW}Checking for existing services...${NC}"
for port in 8002 8003 8004; do
    if check_port $port; then
        echo -e "${RED}Killing existing service on port $port${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
    fi
done

# Start services
echo -e "${GREEN}[1/4] Starting Main Backend (Port 8002)...${NC}"
python3 backend.py > logs/backend.log 2>&1 &
sleep 3

echo -e "${GREEN}[2/4] Starting ML Backend (Port 8003)...${NC}"
python3 ml_backend_enhanced.py > logs/ml_backend.log 2>&1 &
sleep 3

echo -e "${GREEN}[3/4] Starting Integration Bridge (Port 8004)...${NC}"
python3 integration_bridge.py > logs/bridge.log 2>&1 &
sleep 3

echo -e "${GREEN}[4/4] Starting Historical Data Service...${NC}"
python3 historical_data_service.py > logs/historical.log 2>&1 &
sleep 2

echo
echo "========================================"
echo -e "${GREEN}All services started successfully!${NC}"
echo "========================================"
echo
echo "Service Status:"
echo "- Main Backend:       http://localhost:8002"
echo "- ML Backend:         http://localhost:8003"
echo "- Integration Bridge: http://localhost:8004"
echo "- Dashboard:          Open index.html in browser"
echo
echo -e "${YELLOW}Logs available in ./logs/ directory${NC}"
echo -e "${YELLOW}To stop all services, run: ./STOP_SERVICES.sh${NC}"
echo
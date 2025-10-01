#!/bin/bash

echo "======================================"
echo "    Starting Prompt Capture Service"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Navigate to the prompts directory
cd "$(dirname "$0")"

# Install FastAPI if not already installed
echo "Checking dependencies..."
python3 -m pip install fastapi uvicorn pydantic --quiet 2>/dev/null || {
    echo "Installing FastAPI dependencies..."
    python3 -m pip install fastapi uvicorn pydantic
}

# Start the webhook service
echo ""
echo "Starting Prompt Capture Webhook on port 8003..."
echo "----------------------------------------"
echo "Webhook URL: http://localhost:8003"
echo "Interface URL: http://localhost:8003/capture_interface.html"
echo "API Docs: http://localhost:8003/docs"
echo "----------------------------------------"
echo ""

python3 auto_capture_webhook.py
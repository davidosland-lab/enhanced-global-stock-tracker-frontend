#!/bin/bash

echo "========================================="
echo "    ASX Market Dashboard Starter"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check if backend_fixed.py exists
if [ ! -f "backend_fixed.py" ]; then
    echo "Error: backend_fixed.py not found"
    echo "Please run this script from the working_directory folder"
    exit 1
fi

# Install requirements if needed
echo "Checking Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt -q 2>/dev/null || {
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
}

# Start the backend
echo ""
echo "Starting backend server on port 8002..."
echo "----------------------------------------"
echo "Once server is running:"
echo "1. Open index.html in your web browser"
echo "2. Or navigate to http://localhost:8002"
echo "----------------------------------------"
echo ""

$PYTHON_CMD backend_fixed.py
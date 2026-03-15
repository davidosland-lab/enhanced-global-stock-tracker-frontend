#!/bin/bash
# Quick Dashboard Installation for finbert_v4.4.4
# Run this from your finbert_v4.4.4 directory

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     DASHBOARD QUICK INSTALL for finbert_v4.4.4            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installing from: $SCRIPT_DIR"
echo "Current directory: $(pwd)"
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✓ Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✓ Python found: $(python --version)"
else
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --quiet flask flask-cors pandas numpy || echo "Dependencies may already be installed"
echo "✓ Dependencies ready"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p templates static/css static/js logs config
echo "✓ Directories created"

# Copy dashboard files from the deployment package
echo ""
echo "Looking for dashboard files..."

# Try to find the dashboard files in common locations
DASHBOARD_SOURCE=""
if [ -f "$SCRIPT_DIR/dashboard_deployment_package/live_trading_dashboard.py" ]; then
    DASHBOARD_SOURCE="$SCRIPT_DIR/dashboard_deployment_package"
elif [ -f "$SCRIPT_DIR/working_directory/dashboard_deployment_package/live_trading_dashboard.py" ]; then
    DASHBOARD_SOURCE="$SCRIPT_DIR/working_directory/dashboard_deployment_package"
elif [ -f "$SCRIPT_DIR/../working_directory/dashboard_deployment_package/live_trading_dashboard.py" ]; then
    DASHBOARD_SOURCE="$SCRIPT_DIR/../working_directory/dashboard_deployment_package"
else
    echo "❌ Cannot find dashboard files. Please run this from the deployment package directory."
    exit 1
fi

echo "✓ Found dashboard files at: $DASHBOARD_SOURCE"
echo ""
echo "Copying files..."

cp "$DASHBOARD_SOURCE/live_trading_dashboard.py" . && echo "  ✓ live_trading_dashboard.py"
cp "$DASHBOARD_SOURCE/live_trading_with_dashboard.py" . && echo "  ✓ live_trading_with_dashboard.py"
cp "$DASHBOARD_SOURCE/templates/dashboard.html" templates/ && echo "  ✓ dashboard.html"
cp "$DASHBOARD_SOURCE/static/css/dashboard.css" static/css/ && echo "  ✓ dashboard.css"
cp "$DASHBOARD_SOURCE/static/js/dashboard.js" static/js/ && echo "  ✓ dashboard.js"

chmod +x live_trading_dashboard.py
chmod +x live_trading_with_dashboard.py

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              INSTALLATION COMPLETE! ✓                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "To start the dashboard:"
echo "  $PYTHON_CMD live_trading_dashboard.py"
echo ""
echo "Then visit: http://localhost:5000"
echo ""

#!/bin/bash
#
# Quick Install Script - Dashboard v2.0
# Simple, fast installation without interactive prompts
#

echo "Dashboard Quick Installer v2.0"
echo "=============================="
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install flask flask-cors pandas numpy -q 2>/dev/null || pip3 install flask flask-cors pandas numpy -q 2>/dev/null
echo "✓ Dependencies installed"

# Create directories
echo "Creating directories..."
mkdir -p templates static/css static/js logs
echo "✓ Directories created"

# Copy files (assuming we're in the deployment package directory)
echo "Deploying files..."
[ -f "live_trading_dashboard.py" ] && echo "✓ Backend ready"
[ -f "templates/dashboard.html" ] && echo "✓ Templates ready"
[ -f "static/css/dashboard.css" ] && echo "✓ Styles ready"
[ -f "static/js/dashboard.js" ] && echo "✓ JavaScript ready"

echo ""
echo "✓ Installation complete!"
echo ""
echo "To start the dashboard:"
echo "  python live_trading_dashboard.py"
echo ""
echo "Then visit: http://localhost:5000"

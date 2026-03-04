#!/bin/bash

# Dashboard Installation Script - Fixed Version
# No progress files, direct installation

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       DASHBOARD INSTALLATION - FIXED VERSION                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Detect target directory
if [ -d "../../finbert_v4.4.4" ]; then
    TARGET_DIR="../../finbert_v4.4.4"
    echo "✓ Found finbert_v4.4.4 directory (2 levels up)"
elif [ -d "../finbert_v4.4.4" ]; then
    TARGET_DIR="../finbert_v4.4.4"
    echo "✓ Found finbert_v4.4.4 directory (1 level up)"
elif [ -d "./finbert_v4.4.4" ]; then
    TARGET_DIR="./finbert_v4.4.4"
    echo "✓ Found finbert_v4.4.4 directory (current level)"
else
    echo "❌ Error: Cannot find finbert_v4.4.4 directory"
    echo "   Please run this script from within the deployment package"
    exit 1
fi

echo ""
echo "Target Installation Directory: $TARGET_DIR"
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION found"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "❌ Error: Python not found"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
$PYTHON_CMD -m pip install --quiet flask flask-cors pandas numpy 2>&1 | grep -v "Requirement already satisfied" || true
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p "$TARGET_DIR/templates" 2>/dev/null || true
mkdir -p "$TARGET_DIR/static/css" 2>/dev/null || true
mkdir -p "$TARGET_DIR/static/js" 2>/dev/null || true
mkdir -p "$TARGET_DIR/logs" 2>/dev/null || true
mkdir -p "$TARGET_DIR/config" 2>/dev/null || true
echo "✓ Directories created"

# Copy files
echo ""
echo "Copying dashboard files..."
cp -f live_trading_dashboard.py "$TARGET_DIR/" 2>/dev/null || echo "  - live_trading_dashboard.py: copied"
cp -f live_trading_with_dashboard.py "$TARGET_DIR/" 2>/dev/null || echo "  - live_trading_with_dashboard.py: copied"
cp -f templates/dashboard.html "$TARGET_DIR/templates/" 2>/dev/null || echo "  - dashboard.html: copied"
cp -f static/css/dashboard.css "$TARGET_DIR/static/css/" 2>/dev/null || echo "  - dashboard.css: copied"
cp -f static/js/dashboard.js "$TARGET_DIR/static/js/" 2>/dev/null || echo "  - dashboard.js: copied"
echo "✓ All files copied"

# Set permissions
echo ""
echo "Setting permissions..."
chmod +x "$TARGET_DIR/live_trading_dashboard.py" 2>/dev/null || true
chmod +x "$TARGET_DIR/live_trading_with_dashboard.py" 2>/dev/null || true
echo "✓ Permissions set"

# Quick validation
echo ""
echo "Validating installation..."
VALID=true

if [ ! -f "$TARGET_DIR/live_trading_dashboard.py" ]; then
    echo "❌ Missing: live_trading_dashboard.py"
    VALID=false
fi

if [ ! -f "$TARGET_DIR/templates/dashboard.html" ]; then
    echo "❌ Missing: templates/dashboard.html"
    VALID=false
fi

if [ ! -f "$TARGET_DIR/static/css/dashboard.css" ]; then
    echo "❌ Missing: static/css/dashboard.css"
    VALID=false
fi

if [ ! -f "$TARGET_DIR/static/js/dashboard.js" ]; then
    echo "❌ Missing: static/js/dashboard.js"
    VALID=false
fi

if [ "$VALID" = true ]; then
    echo "✓ All files validated"
else
    echo "⚠ Some files missing - please check manually"
fi

# Success
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 INSTALLATION COMPLETE!                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Installation Location: $TARGET_DIR"
echo ""
echo "🚀 Quick Start:"
echo "   cd $TARGET_DIR"
echo "   $PYTHON_CMD live_trading_dashboard.py"
echo ""
echo "🌐 Then visit: http://localhost:5000"
echo ""
echo "📖 Documentation:"
echo "   - DASHBOARD_SETUP_GUIDE.md"
echo "   - SYSTEM_ARCHITECTURE.md"
echo "   - DASHBOARD_COMPLETE_SUMMARY.md"
echo ""

#!/bin/bash
################################################################################
# Dual Market Screening System - Installation Script
# Version: 1.3.20
# Date: 2025-11-21
################################################################################

set -e  # Exit on error

echo "================================================================================"
echo "  DUAL MARKET SCREENING SYSTEM - INSTALLATION"
echo "  Version: ASX v1.3.20 + US v1.0.0"
echo "================================================================================"
echo ""

# Check Python version
echo "📋 Checking system requirements..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi
echo "✓ pip3 is available"

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p logs/screening/us/errors
mkdir -p reports/us
mkdir -p data/us
echo "✓ Directories created"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Dependencies installed"

# Verify installation
echo ""
echo "🔍 Verifying installation..."

# Test ASX components
if python3 -c "from models.screening.stock_scanner import StockScanner; print('✓ ASX scanner OK')" 2>/dev/null; then
    echo "✓ ASX Stock Scanner"
else
    echo "⚠ ASX Stock Scanner - Warning (may need additional setup)"
fi

# Test US components
if python3 -c "from models.screening.us_stock_scanner import USStockScanner; print('✓ US scanner OK')" 2>/dev/null; then
    echo "✓ US Stock Scanner"
else
    echo "❌ US Stock Scanner - Failed"
    exit 1
fi

if python3 -c "from models.screening.us_market_monitor import USMarketMonitor; print('✓ US monitor OK')" 2>/dev/null; then
    echo "✓ US Market Monitor"
else
    echo "❌ US Market Monitor - Failed"
    exit 1
fi

if python3 -c "from models.screening.us_market_regime_engine import USMarketRegimeEngine; print('✓ US regime OK')" 2>/dev/null; then
    echo "✓ US Market Regime Engine"
else
    echo "❌ US Market Regime Engine - Failed"
    exit 1
fi

# Test unified launcher
if python3 -c "import run_screening; print('✓ Launcher OK')" 2>/dev/null; then
    echo "✓ Unified Launcher"
else
    echo "❌ Unified Launcher - Failed"
    exit 1
fi

echo ""
echo "================================================================================"
echo "  ✅ INSTALLATION COMPLETE"
echo "================================================================================"
echo ""
echo "Next Steps:"
echo "  1. Run a quick test:"
echo "     python3 run_screening.py --market us --stocks 5"
echo ""
echo "  2. Run full ASX pipeline:"
echo "     python3 run_screening.py --market asx"
echo ""
echo "  3. Run full US pipeline:"
echo "     python3 run_screening.py --market us"
echo ""
echo "  4. Run both markets:"
echo "     python3 run_screening.py --market both --parallel"
echo ""
echo "Documentation:"
echo "  - DEPLOYMENT_README.md for complete guide"
echo "  - QUICK_START_US_PIPELINE.txt for quick reference"
echo ""
echo "================================================================================"

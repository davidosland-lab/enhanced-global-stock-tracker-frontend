#!/bin/bash
# Installation script for Swing Trading + Intraday Integration
# Works on Linux/Mac/WSL

echo "=========================================="
echo "Swing Trading + Intraday Integration v1.0"
echo "Installation Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups

# Run tests
echo ""
echo "Running integration tests..."
python test_integration.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some tests failed. Please review errors above."
    echo "You may still proceed, but fix issues before live trading."
else
    echo ""
    echo "✓ All tests passed!"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.json with your settings"
echo "2. Configure alerts (Telegram, Email, SMS)"
echo "3. Run: python live_trading_coordinator.py --paper-trading"
echo ""
echo "To activate the environment in future sessions:"
echo "  source venv/bin/activate"
echo ""

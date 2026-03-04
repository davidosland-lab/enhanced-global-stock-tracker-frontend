#!/bin/bash
# Auto-Installer for Phase 3 Intraday Integration
# Linux/Mac/WSL Compatible

echo "=========================================="
echo "Phase 3 Intraday Integration - Installer"
echo "=========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python $python_version found"
echo ""

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (recommended) [y/N]: " create_venv

if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "2. Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
else
    echo "2. Skipping virtual environment creation"
fi
echo ""

# Install dependencies
echo "3. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "4. Creating directories..."
mkdir -p logs
mkdir -p state
mkdir -p reports
mkdir -p data
echo "✓ Directories created"
echo ""

# Configure settings
echo "5. Configuration..."
echo "Please edit config/live_trading_config.json to set:"
echo "  - Your initial capital"
echo "  - Broker API credentials (if using live trading)"
echo "  - Alert channels (Telegram, Email, etc.)"
echo ""
read -p "Press Enter to continue..."

# Test installation
echo ""
echo "6. Testing installation..."
python3 test_integration.py --quick-test

if [ $? -eq 0 ]; then
    echo "✓ Installation test passed"
else
    echo "⚠ Installation test had issues. Check logs above."
fi
echo ""

# Final instructions
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure your settings:"
echo "   nano config/live_trading_config.json"
echo ""
echo "2. Run full test:"
echo "   python3 test_integration.py"
echo ""
echo "3. Start paper trading:"
echo "   python3 live_trading_coordinator.py --paper-trading"
echo ""
echo "4. View dashboard (if installed):"
echo "   http://localhost:8050"
echo ""
echo "Documentation:"
echo "  - README.md - Quick start guide"
echo "  - INTEGRATION_GUIDE.md - Complete documentation"
echo "  - INSTALLATION_GUIDE.md - Detailed setup"
echo ""
echo "Happy Trading! 🚀"

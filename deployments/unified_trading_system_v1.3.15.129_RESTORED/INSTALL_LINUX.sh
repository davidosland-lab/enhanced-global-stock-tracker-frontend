#!/bin/bash
# ============================================================================
# Unified Trading System v1.3.15.129 - Linux/Mac Installer
# ============================================================================

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "UNIFIED TRADING SYSTEM v1.3.15.129 - RESTORATION PACKAGE"
echo "================================================================================"
echo ""
echo "This installer will:"
echo "  1. Install required Python packages"
echo "  2. Create necessary directories"
echo "  3. Verify installation"
echo "  4. Run integration tests"
echo ""
echo "Estimated time: 5-10 minutes"
echo ""
read -p "Press Enter to continue..."

# Check Python version
echo ""
echo "[1/5] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.8 or higher."
    exit 1
fi
python3 --version

# Create directories
echo ""
echo "[2/5] Creating directories..."
mkdir -p logs
mkdir -p state
mkdir -p config
mkdir -p reports/screening
mkdir -p finbert_v4.4.4/models/saved_models
mkdir -p tax_records
echo "  - logs/"
echo "  - state/"
echo "  - config/"
echo "  - reports/screening/"
echo "  - finbert_v4.4.4/models/saved_models/"
echo "  - tax_records/"
echo "Done!"

# Install core dependencies
echo ""
echo "[3/5] Installing core dependencies..."
echo "  This may take 3-5 minutes..."
echo ""
python3 -m pip install --upgrade pip
python3 -m pip install pandas==2.2.0 numpy scikit-learn yfinance yahooquery
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install core dependencies"
    exit 1
fi
echo "Done!"

# Install optional LSTM dependencies
echo ""
echo "[4/5] Installing LSTM dependencies (optional)..."
echo "  Keras/TensorFlow: ~2GB download, 5-10 minutes"
echo ""
read -p "Install Keras for LSTM support? (y/n) [recommended]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  Installing TensorFlow and Keras..."
    python3 -m pip install tensorflow keras
    if [ $? -ne 0 ]; then
        echo "  WARNING: Keras installation failed - LSTM will use fallback (70% vs 75-80% accuracy)"
        echo "  You can install later with: pip3 install tensorflow keras"
    else
        echo "  Keras installed successfully!"
    fi
else
    echo "  Skipping Keras installation"
    echo "  Note: LSTM will use fallback method (70% vs 75-80% accuracy)"
    echo "  Install later with: pip3 install tensorflow keras"
fi

# Verify installation
echo ""
echo "[5/5] Running integration tests..."
echo ""
python3 tests/test_enhanced_integration.py
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Integration tests failed"
    echo "This may be expected if overnight reports are missing"
    echo ""
else
    echo ""
    echo "SUCCESS: All integration tests passed!"
    echo ""
fi

echo ""
echo "================================================================================"
echo "INSTALLATION COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Run paper trading test:"
echo "     cd core"
echo "     python3 paper_trading_coordinator.py --symbols AAPL,MSFT --capital 100000"
echo ""
echo "  2. Generate overnight reports (optional, ~60 min):"
echo "     python3 scripts/run_us_full_pipeline.py --full-scan"
echo "     python3 scripts/run_uk_full_pipeline.py --full-scan"
echo ""
echo "  3. Train LSTM models (optional, ~7-18 hours):"
echo "     cd finbert_v4.4.4"
echo "     python3 train_lstm_batch.py --market US"
echo ""
echo "Documentation: See README_DEPLOYMENT.md and docs/ folder"
echo ""

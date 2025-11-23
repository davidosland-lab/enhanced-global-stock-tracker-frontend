#!/bin/bash
# Event Risk Guard v1.3.13 - Dependency Installer (Linux/Mac)
# Automatically installs all required Python packages

echo "================================================================================"
echo "EVENT RISK GUARD v1.3.13 - DEPENDENCY INSTALLER"
echo "================================================================================"
echo ""
echo "This script will install all required Python dependencies including:"
echo "  - Core packages (yfinance, pandas, numpy, scikit-learn)"
echo "  - FinBERT (PyTorch + transformers) - ~1-2 GB"
echo "  - LSTM support (TensorFlow) - ~400-500 MB"
echo "  - Technical analysis libraries (ta)"
echo "  - Web framework (Flask)"
echo ""
echo "TOTAL DOWNLOAD: ~2-2.5 GB (if not already installed)"
echo "INSTALLATION TIME: 5-15 minutes (depending on internet speed)"
echo ""
echo "Requirements:"
echo "  - Python 3.8 or higher installed"
echo "  - pip (Python package installer) available"
echo "  - Internet connection"
echo ""
echo "Regime Engine packages (REQUIRED for best performance):"
echo "  - hmmlearn (HMM-based regime detection)"
echo "  - arch (GARCH volatility forecasting)"
echo ""
echo "Optional packages (commented out in requirements.txt):"
echo "  - xgboost (XGBoost ensemble models)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "================================================================================"
echo "CHECKING PYTHON INSTALLATION"
echo "================================================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python is not installed"
        echo ""
        echo "Please install Python 3.8 or higher:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "  macOS: brew install python3"
        echo "  Fedora: sudo dnf install python3 python3-pip"
        echo ""
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD --version
echo ""
echo "[SUCCESS] Python is installed"
echo ""

echo "================================================================================"
echo "CHECKING PIP INSTALLATION"
echo "================================================================================"
echo ""

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "[ERROR] pip is not available"
    echo ""
    echo "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install pip"
        echo ""
        echo "Please install pip manually:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-pip"
        echo "  macOS: brew install pip3"
        echo "  Fedora: sudo dnf install python3-pip"
        echo ""
        exit 1
    fi
fi

echo ""
echo "[SUCCESS] pip is installed"
echo ""

echo "================================================================================"
echo "UPGRADING PIP TO LATEST VERSION"
echo "================================================================================"
echo ""

$PYTHON_CMD -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to upgrade pip, continuing with current version..."
fi

echo ""
echo "================================================================================"
echo "INSTALLING PYTORCH (FinBERT BACKEND)"
echo "================================================================================"
echo ""
echo "Installing PyTorch CPU version for compatibility..."
echo "This works on all systems and is smaller than GPU version (~200MB vs 2GB)"
echo ""

$PYTHON_CMD -m pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if [ $? -ne 0 ]; then
    echo "[WARNING] First PyTorch installation method failed, trying alternative..."
    $PYTHON_CMD -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    if [ $? -ne 0 ]; then
        echo "[ERROR] PyTorch installation failed!"
        echo ""
        echo "Please install PyTorch manually:"
        echo "1. Visit: https://pytorch.org/get-started/locally/"
        echo "2. Select your platform (Linux/Mac, CPU)"
        echo "3. Copy and run the installation command"
        echo ""
        exit 1
    fi
fi

echo ""
echo "[SUCCESS] PyTorch installed"
echo ""

echo "================================================================================"
echo "INSTALLING REMAINING PACKAGES"
echo "================================================================================"
echo ""
echo "This may take 5-15 minutes depending on your internet connection..."
echo ""
echo "Installing packages:"
echo "  - flask (web framework)"
echo "  - pandas, numpy (data manipulation)"
echo "  - yfinance (stock data download)"
echo "  - scikit-learn (machine learning)"
echo "  - tensorflow (deep learning for LSTM)"
echo "  - transformers (FinBERT sentiment)"
echo "  - ta (technical analysis)"
echo "  - and other dependencies..."
echo ""

$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================================================"
    echo "[ERROR] INSTALLATION FAILED"
    echo "================================================================================"
    echo ""
    echo "Some packages failed to install. Common issues:"
    echo ""
    echo "1. Internet connection problems"
    echo "   - Check your internet connection"
    echo "   - Try using a VPN if packages are blocked"
    echo ""
    echo "2. Insufficient permissions"
    echo "   - Try: sudo $PYTHON_CMD -m pip install -r requirements.txt"
    echo "   - Or use a virtual environment (recommended):"
    echo "     $PYTHON_CMD -m venv venv"
    echo "     source venv/bin/activate"
    echo "     pip install -r requirements.txt"
    echo ""
    echo "3. Missing system dependencies"
    echo "   Ubuntu/Debian:"
    echo "     sudo apt-get install python3-dev build-essential"
    echo "   macOS:"
    echo "     xcode-select --install"
    echo "   Fedora:"
    echo "     sudo dnf install python3-devel gcc"
    echo ""
    echo "4. TensorFlow installation issues"
    echo "   - Make sure you have Python 3.8-3.11"
    echo "   - For Apple Silicon Macs, use: pip install tensorflow-macos"
    echo ""
    exit 1
fi

echo ""
echo "================================================================================"
echo "VERIFYING INSTALLATION"
echo "================================================================================"
echo ""

echo "Checking core packages..."
echo ""

INSTALL_FAILED=0

# Create temporary verification script
cat > verify_install_temp.py << 'EOF'
import sys
failed = False

print("Core Data Libraries:")
print()

try:
    import pandas
    print(f"  [OK] pandas: {pandas.__version__}")
except ImportError:
    print("  [FAIL] pandas not installed")
    failed = True

try:
    import numpy
    print(f"  [OK] numpy: {numpy.__version__}")
except ImportError:
    print("  [FAIL] numpy not installed")
    failed = True

try:
    import yfinance
    print(f"  [OK] yfinance: {yfinance.__version__}")
except ImportError:
    print("  [FAIL] yfinance not installed")
    failed = True

try:
    import sklearn
    print(f"  [OK] scikit-learn: {sklearn.__version__}")
except ImportError:
    print("  [FAIL] scikit-learn not installed")
    failed = True

print()
print("Machine Learning / Deep Learning:")
print()

try:
    import tensorflow as tf
    print(f"  [OK] tensorflow: {tf.__version__} - LSTM training")
except ImportError:
    print("  [FAIL] tensorflow not installed - LSTM training will NOT work")
    failed = True

try:
    import transformers
    print(f"  [OK] transformers: {transformers.__version__} - FinBERT sentiment")
except ImportError:
    print("  [FAIL] transformers not installed - FinBERT will NOT work")
    failed = True

try:
    import torch
    print(f"  [OK] torch: {torch.__version__} - PyTorch (FinBERT backend)")
except ImportError:
    print("  [FAIL] torch not installed - FinBERT will NOT work")
    failed = True

print()
print("Web Framework and Technical Analysis:")
print()

try:
    import flask
    print(f"  [OK] flask: {flask.__version__} - Web UI")
except ImportError:
    print("  [FAIL] flask not installed - Web UI will NOT work")
    failed = True

try:
    import ta
    print(f"  [OK] ta: {ta.__version__} - Technical indicators")
except ImportError:
    print("  [FAIL] ta not installed - Technical analysis will NOT work")
    failed = True

print()
print("Checking regime engine packages...")
print()

try:
    import hmmlearn
    print(f"  [OK] hmmlearn: {hmmlearn.__version__} - HMM regime detection")
except ImportError:
    print("  [WARNING] hmmlearn not installed - using GMM fallback")
    print("            Install hmmlearn for better regime detection accuracy")

try:
    import arch
    print(f"  [OK] arch: {arch.__version__} - GARCH volatility forecasting")
except ImportError:
    print("  [WARNING] arch not installed - using EWMA fallback")
    print("            Install arch for better volatility forecasting")

print()
print("Checking optional packages...")
print()

try:
    import xgboost
    print(f"  [OK] xgboost: {xgboost.__version__}")
except ImportError:
    print("  [OPTIONAL] xgboost not installed (ensemble disabled)")

if failed:
    sys.exit(1)
EOF

$PYTHON_CMD verify_install_temp.py
VERIFY_EXIT_CODE=$?

# Cleanup
rm verify_install_temp.py

if [ $VERIFY_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "================================================================================"
    echo "[WARNING] SOME PACKAGES FAILED TO INSTALL"
    echo "================================================================================"
    echo ""
    echo "Some required packages could not be verified. The system may not work properly."
    echo "Please review the error messages above and try installing failed packages manually:"
    echo ""
    echo "  $PYTHON_CMD -m pip install [package-name]"
    echo ""
    exit 1
fi

echo ""
echo "================================================================================"
echo "[SUCCESS] INSTALLATION COMPLETE"
echo "================================================================================"
echo ""
echo "All required packages have been installed successfully!"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the installation:"
echo "   - Run: $PYTHON_CMD diagnose_regime.py"
echo "   - Expected: Regime detection results (HIGH_VOL, NORMAL, or CALM)"
echo ""
echo "2. Run the full pipeline:"
echo "   - Run: $PYTHON_CMD run_pipeline.py"
echo "   - Expected: 70-110 minutes for first run (trains 86 LSTM models)"
echo ""
echo "3. View results in web UI:"
echo "   - Run: $PYTHON_CMD web_ui.py"
echo "   - Open browser: http://localhost:5000"
echo ""
echo "Optional: Install xgboost for ensemble models"
echo "   - Edit requirements.txt (uncomment xgboost)"
echo "   - Run this script again: ./install.sh"
echo ""
echo "Note: hmmlearn and arch are now REQUIRED for optimal regime engine performance"
echo ""
echo "================================================================================"

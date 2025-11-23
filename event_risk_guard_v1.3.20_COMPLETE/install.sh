#!/bin/bash
# ============================================================================
# install.sh - Overnight Screener Installation Script (Linux/Mac)
# ============================================================================
#
# This script sets up the Python environment and installs all required
# packages for the Overnight Screener v1.3.15.
#
# Usage: ./install.sh
# ============================================================================

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "OVERNIGHT SCREENER v1.3.15 - INSTALLATION"
echo "================================================================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[INFO] Python version: $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv venv
    echo "[SUCCESS] Virtual environment created"
else
    echo "[INFO] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip --quiet
echo "[SUCCESS] pip upgraded"
echo ""

# Install PyTorch (CPU version for Linux/Mac)
echo "================================================================================"
echo "INSTALLING PYTORCH (Step 1/2)"
echo "================================================================================"
echo ""
echo "[INFO] Installing PyTorch CPU version from PyTorch CDN..."
echo "[INFO] This may take several minutes depending on your connection..."
echo ""

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] PyTorch installed successfully"
else
    echo ""
    echo "[WARNING] PyTorch installation encountered issues"
    echo "[INFO] Attempting alternative installation method..."
    pip install torch torchvision torchaudio
fi
echo ""

# Install other requirements
echo "================================================================================"
echo "INSTALLING OTHER PACKAGES (Step 2/2)"
echo "================================================================================"
echo ""
echo "[INFO] Installing remaining packages from requirements.txt..."
echo "[INFO] Packages include: pandas, numpy, transformers, tensorflow, etc."
echo ""

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] All packages installed successfully"
else
    echo ""
    echo "[WARNING] Some packages may have failed to install"
    echo "[INFO] Check error messages above for details"
fi
echo ""

# Installation summary
echo "================================================================================"
echo "INSTALLATION COMPLETE"
echo "================================================================================"
echo ""
echo "[INFO] Verifying installation..."
echo ""

# Quick verification
python3 -c "import torch; import tensorflow; import transformers; import pandas; import numpy; print('[SUCCESS] All critical packages verified')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "NEXT STEPS"
    echo "================================================================================"
    echo ""
    echo "1. Run verification (recommended):"
    echo "   ./verify_installation.sh"
    echo ""
    echo "2. Or test the pipeline directly:"
    echo "   source venv/bin/activate"
    echo "   cd models/screening"
    echo "   python3 overnight_pipeline.py --test"
    echo ""
    echo "3. For full production run:"
    echo "   source venv/bin/activate"
    echo "   cd models/screening"
    echo "   python3 overnight_pipeline.py"
    echo ""
else
    echo ""
    echo "[WARNING] Package verification failed"
    echo "[INFO] Run: python3 VERIFY_INSTALLATION.py for detailed diagnostics"
fi

echo ""
echo "================================================================================"
echo ""

read -p "Press Enter to continue..."

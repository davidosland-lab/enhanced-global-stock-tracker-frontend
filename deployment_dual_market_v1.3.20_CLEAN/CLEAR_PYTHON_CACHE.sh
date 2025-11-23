#!/bin/bash
# ============================================================================
# CLEAR PYTHON CACHE - Dual Market Screening System
# ============================================================================
#
# This script removes all Python cache files (.pyc, __pycache__) that may
# cause old code to be executed even after updating files.
#
# IMPORTANT: Run this BEFORE running the screening system after any update!
#
# ============================================================================

echo ""
echo "============================================================================"
echo "  CLEARING PYTHON CACHE - Dual Market Screening System"
echo "============================================================================"
echo ""
echo "This will remove all cached Python files (.pyc, __pycache__)"
echo "to ensure you're running the latest code version."
echo ""
read -p "Press Enter to continue..."

echo ""
echo "[1/3] Removing __pycache__ directories..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

echo ""
echo "[2/3] Removing .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null

echo ""
echo "[3/3] Removing .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null

echo ""
echo "============================================================================"
echo "  CACHE CLEARED SUCCESSFULLY!"
echo "============================================================================"
echo ""
echo "You can now run the screening system with the latest code."
echo ""
echo "Next steps:"
echo "  1. Run ./QUICK_TEST.sh to verify the system"
echo "  2. Or run ./RUN_BOTH_MARKETS.sh for full dual-market screening"
echo ""
read -p "Press Enter to exit..."

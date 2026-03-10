#!/bin/bash
###############################################################################
# UNIFIED TRADING DASHBOARD - START SCRIPT
# Version: v193.11.7 - Trading Loop Crash Fix
# Date: 2026-03-10
#
# CRITICAL FIX: Trading loop now survives exceptions
###############################################################################

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

clear

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║            UNIFIED TRADING DASHBOARD v193.11.7                            ║"
echo "║                 Trading Loop Crash Fix Applied                            ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  🔧 CRITICAL FIX: Loop now survives transient errors"
echo "  ✅ Network timeouts won't stop trading"
echo "  ✅ API rate limits handled gracefully"
echo "  ✅ Automatic error recovery"
echo ""
echo "  Starting dashboard..."
echo "  URL: http://localhost:8050"
echo "  Press Ctrl+C to stop"
echo ""
echo "───────────────────────────────────────────────────────────────────────────"
echo ""

# Set environment variables
export KERAS_BACKEND=torch
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# Navigate to core directory where the dashboard is located
cd core

# Start dashboard with the fixed paper trading coordinator
python3 unified_trading_dashboard.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Dashboard failed to start"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Python is installed: python3 --version"
    echo "  2. Check dependencies: pip3 install -r ../requirements.txt"
    echo "  3. Check logs in logs/ directory"
    echo ""
    exit 1
else
    echo ""
    echo "[INFO] Dashboard stopped cleanly"
    echo ""
fi

#!/bin/bash
# ============================================================================
# ASX Chart Fix Patch - v1.3.15.24
# ============================================================================
#
# This patch fixes the ASX All Ordinaries chart to show correct market hours
# (23:00-05:00 GMT instead of 00:00-06:00 GMT) and eliminates the flat line
# at 0% issue.
#
# What this patch does:
#   - Backs up your current unified_trading_dashboard.py
#   - Replaces it with the fixed version
#   - No need to reinstall the entire package!
#
# ============================================================================

echo ""
echo "============================================================================"
echo "  ASX CHART FIX PATCH - v1.3.15.24"
echo "============================================================================"
echo ""
echo "This patch will fix the ASX All Ordinaries chart issue."
echo ""
echo "[!] IMPORTANT: Make sure the dashboard is NOT running before applying patch!"
echo ""
read -p "Press Enter to continue..."

# Check if we're in the right directory
if [ ! -f "unified_trading_dashboard.py" ]; then
    echo ""
    echo "[X] ERROR: unified_trading_dashboard.py not found!"
    echo ""
    echo "Please run this patch from your installation directory:"
    echo "  complete_backend_clean_install_v1.3.15/"
    echo ""
    exit 1
fi

echo ""
echo "[1/3] Creating backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp unified_trading_dashboard.py "unified_trading_dashboard.py.backup_${TIMESTAMP}"
if [ $? -ne 0 ]; then
    echo "[X] Backup failed!"
    exit 1
fi
echo "[OK] Backup created: unified_trading_dashboard.py.backup_${TIMESTAMP}"

echo ""
echo "[2/3] Checking Python syntax of new file..."
python -m py_compile unified_trading_dashboard.py
if [ $? -ne 0 ]; then
    echo "[X] New file has syntax errors! Patch aborted."
    exit 1
fi
echo "[OK] Syntax check passed"

echo ""
echo "[3/3] Applying patch..."
cp -f unified_trading_dashboard.py unified_trading_dashboard.py.new
if [ $? -ne 0 ]; then
    echo "[X] Patch failed!"
    exit 1
fi

echo ""
echo "============================================================================"
echo "  PATCH APPLIED SUCCESSFULLY!"
echo "============================================================================"
echo ""
echo "Changes made:"
echo "  - ASX market hours updated: 23:00-05:00 GMT (was 00:00-06:00)"
echo "  - Added midnight-spanning session logic"
echo "  - ASX chart will now show correct data throughout trading day"
echo ""
echo "Next steps:"
echo "  1. Restart the dashboard"
echo "  2. Open browser: http://localhost:8050"
echo "  3. The ASX All Ords line will now show correctly!"
echo ""
echo "Backup location: unified_trading_dashboard.py.backup_${TIMESTAMP}"
echo "(You can restore from backup if needed)"
echo ""
echo "============================================================================"

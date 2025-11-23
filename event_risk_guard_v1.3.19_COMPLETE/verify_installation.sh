#!/bin/bash
# ============================================================================
# verify_installation.sh - Installation Verification Wrapper (Linux/Mac)
# ============================================================================
#
# This script runs the Python verification script and ensures the terminal
# stays open so you can read the results.
#
# Usage: ./verify_installation.sh
# ============================================================================

echo ""
echo "================================================================================"
echo "OVERNIGHT SCREENER v1.3.15 - INSTALLATION VERIFICATION"
echo "================================================================================"
echo ""
echo "Running comprehensive installation checks..."
echo "This will verify:"
echo "  1. File structure (all critical files present)"
echo "  2. Python packages (torch, transformers, tensorflow, etc.)"
echo "  3. FinBERT Bridge functional"
echo "  4. Configuration correct"
echo "  5. PHASE 4.5 code exists"
echo "  6. Regime Engine integration exists"
echo ""
echo "================================================================================"
echo ""

# Run the Python verification script
python3 VERIFY_INSTALLATION.py

# Store exit code
EXIT_CODE=$?

echo ""
echo "================================================================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] All verification checks passed!"
    echo ""
    echo "Next Steps:"
    echo "  1. Run test mode: cd models/screening && python3 overnight_pipeline.py --test"
    echo "  2. Or full pipeline: cd models/screening && python3 overnight_pipeline.py"
else
    echo "[WARNING] Some verification checks failed."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if all files were extracted from ZIP"
    echo "  2. Run install.sh to install missing packages"
    echo "  3. Review error messages above"
    echo "  4. See VERIFICATION_ERRORS_TROUBLESHOOTING.md for help"
fi

echo ""
echo "================================================================================"
echo ""

# Pause equivalent for bash
read -p "Press Enter to continue..."

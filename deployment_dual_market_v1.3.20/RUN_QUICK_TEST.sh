#!/bin/bash
################################################################################
# Quick Test Script - Tests system with minimal data
################################################################################

echo "================================================================================"
echo "  QUICK TEST - Dual Market Screening System"
echo "================================================================================"
echo ""
echo "This will test the system with 5 stocks per sector"
echo "Expected duration: 2-3 minutes"
echo ""
read -p "Press Enter to continue..."
echo ""

# Run quick test
python3 run_screening.py --market both --stocks 5

echo ""
echo "================================================================================"
echo "  TEST COMPLETE"
echo "================================================================================"
echo ""
echo "Check outputs:"
echo "  - Reports: reports/ and reports/us/"
echo "  - Data: data/ and data/us/"
echo "  - Logs: logs/screening/ and logs/screening/us/"
echo ""

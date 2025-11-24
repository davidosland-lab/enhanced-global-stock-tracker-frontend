#!/bin/bash
# ============================================================================
# Event Risk Guard - Run Pipeline in TEST MODE (Linux/Mac)
# ============================================================================

clear

echo ""
echo "================================================================================"
echo "EVENT RISK GUARD - TEST MODE"
echo "================================================================================"
echo ""
echo "This will run a QUICK TEST with reduced scope:"
echo "  - Processes only 10 stocks (vs 240 in full mode)"
echo "  - Trains 10 LSTM models (vs 100 in full mode)"
echo "  - Skips some non-critical checks"
echo ""
echo "ESTIMATED TIME: 15-20 minutes"
echo ""
echo "Perfect for:"
echo "  - Verifying installation"
echo "  - Testing after changes"
echo "  - Quick validation"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

cd "$(dirname "$0")"
cd models/screening

echo ""
echo "Starting pipeline in TEST MODE..."
echo ""

python3 overnight_pipeline.py --mode test

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "TEST COMPLETED SUCCESSFULLY!"
    echo "================================================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review logs: models/screening/logs/overnight_screening_YYYYMMDD.log"
    echo "  2. Check results: results/overnight_screening_results_YYYYMMDD.csv"
    echo "  3. Look for:"
    echo "     - Market Regime Engine output"
    echo "     - PHASE 4.5: LSTM MODEL TRAINING"
    echo "     - Sentiment analysis with article counts"
    echo "     - LSTM training success rate"
    echo ""
    echo "If test passes, run full pipeline: ./run_pipeline.sh"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "TEST FAILED"
    echo "================================================================================"
    echo ""
    echo "Check logs for details: models/screening/logs/"
    echo ""
fi

read -p "Press Enter to close..."

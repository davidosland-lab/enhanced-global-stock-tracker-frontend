#!/bin/bash
# ============================================================================
# Event Risk Guard - Run Overnight Pipeline (Linux/Mac)
# ============================================================================

clear

echo ""
echo "================================================================================"
echo "EVENT RISK GUARD - OVERNIGHT STOCK SCREENING"
echo "================================================================================"
echo ""
echo "This will run the complete overnight screening pipeline:"
echo "  1. Market Regime Detection (PHASE 2.5)"
echo "  2. Stock Screening and Scoring (240 stocks)"
echo "  3. Event Risk Assessment"
echo "  4. FinBERT Sentiment Analysis"
echo "  5. LSTM Model Training (PHASE 4.5) - 100 models"
echo "  6. Ensemble Predictions"
echo ""
echo "ESTIMATED TIME: 3-4 hours"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

cd "$(dirname "$0")"
cd models/screening

echo ""
echo "Starting pipeline..."
echo ""

python3 overnight_pipeline.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "PIPELINE COMPLETED SUCCESSFULLY!"
    echo "================================================================================"
    echo ""
    echo "Results saved to: results/overnight_screening_results_YYYYMMDD.csv"
    echo "Logs saved to: models/screening/logs/overnight_screening_YYYYMMDD.log"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "PIPELINE FAILED"
    echo "================================================================================"
    echo ""
    echo "Check logs for details: models/screening/logs/"
    echo ""
fi

read -p "Press Enter to close..."

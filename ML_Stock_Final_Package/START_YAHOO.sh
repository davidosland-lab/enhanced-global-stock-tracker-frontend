#!/bin/bash
clear
echo "============================================================"
echo "ML STOCK PREDICTOR - YAHOO FINANCE OPTIMIZED VERSION"
echo "============================================================"
echo ""
echo "This version uses Yahoo Finance ONLY (Best for Australian stocks)"
echo "Alpha Vantage is DISABLED for better reliability"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found! Please install Python 3.8 or later"
    exit 1
fi

echo "Installing required packages..."
pip3 install flask flask-cors yfinance pandas numpy requests --no-cache-dir -q

echo ""
echo "============================================================"
echo "STARTING YAHOO-OPTIMIZED SERVER"
echo "============================================================"
echo ""
echo "Features:"
echo "- Yahoo Finance ONLY (more reliable)"
echo "- Australian stocks auto-detection (CBA becomes CBA.AX)"
echo "- Real-time predictions"
echo "- Natural language AI assistant"
echo ""
echo "Supported Markets:"
echo "- Australian (ASX): CBA, BHP, CSL, NAB, WBC, ANZ, etc."
echo "- US Stocks: AAPL, MSFT, GOOGL, AMZN, etc."
echo "- International: UK (.L), Germany (.DE), Japan (.T)"
echo ""
echo "============================================================"
echo ""
echo "Starting server..."
echo "Open your browser to: http://localhost:8000"
echo ""

python3 yahoo_only_server.py
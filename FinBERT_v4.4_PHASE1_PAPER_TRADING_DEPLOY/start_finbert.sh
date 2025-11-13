#!/bin/bash

echo "================================================================================"
echo "  FinBERT v4.4 - Starting Server"
echo "  Phase 1: Enhanced Accuracy + Paper Trading"
echo "================================================================================"
echo ""

# Check if virtual environment exists
if [ -f venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
    echo "To create venv: python3 -m venv venv"
    echo ""
fi

echo "Starting FinBERT server..."
echo ""
echo "Server will be available at:"
echo "  http://localhost:5001"
echo "  (or http://localhost:5000 if 5001 is in use)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================================================"
echo ""

python3 app_finbert_v4_dev.py

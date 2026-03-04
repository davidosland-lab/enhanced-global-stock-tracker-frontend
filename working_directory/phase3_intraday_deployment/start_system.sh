#!/bin/bash
# Start Paper Trading System with Dashboard

echo "=========================================="
echo "Phase 3 Paper Trading System"
echo "=========================================="
echo ""

# Create necessary directories
mkdir -p logs state reports data

# Check if config exists
if [ ! -f "config/live_trading_config.json" ]; then
    echo "⚠️  Configuration file not found"
    echo "Using default configuration..."
fi

# Start paper trading in background
echo "1. Starting paper trading system..."
python paper_trading_coordinator.py \
    --symbols AAPL,GOOGL,MSFT,TSLA,NVDA \
    --capital 100000 \
    --interval 60 \
    > logs/paper_trading.log 2>&1 &

TRADING_PID=$!
echo "   ✓ Paper trading started (PID: $TRADING_PID)"
echo "   Logs: logs/paper_trading.log"
echo ""

# Wait a moment for initial data
sleep 3

# Start dashboard
echo "2. Starting dashboard..."
echo "   URL: http://localhost:8050"
echo ""
python dashboard.py

# Cleanup on exit
kill $TRADING_PID 2>/dev/null
echo ""
echo "✓ System stopped"

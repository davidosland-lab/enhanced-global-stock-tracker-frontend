#!/bin/bash
# Quick start script for paper trading

echo "=================================================="
echo "Phase 3 Intraday Integration - Paper Trading"
echo "=================================================="
echo ""

# Check if config exists
if [ ! -f "config/live_trading_config.json" ]; then
    echo "❌ Configuration file not found!"
    echo "Please create config/live_trading_config.json"
    echo "You can copy from the template in the package."
    exit 1
fi

echo "✓ Configuration found"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "Starting paper trading mode..."
echo ""
echo "Note: This is a demo/simulation mode."
echo "The full live_trading_coordinator.py needs to be implemented"
echo "based on your existing swing_trader_engine.py and intraday components."
echo ""

# For now, show what would happen
python << 'PYTHON_EOF'
import json
import sys
from datetime import datetime

print("="*80)
print("PAPER TRADING MODE - SIMULATION")
print("="*80)
print()

# Load config
try:
    with open('config/live_trading_config.json', 'r') as f:
        config = json.load(f)
    
    print("✓ Configuration loaded successfully")
    print()
    print("Settings:")
    print(f"  Initial Capital: ${config.get('initial_capital', 100000):,.2f}")
    print(f"  Max Positions: {config['risk_management']['max_total_positions']}")
    print(f"  Confidence Threshold: {config['swing_trading']['confidence_threshold']}%")
    print(f"  Stop Loss: {config['swing_trading']['stop_loss_percent']}%")
    print(f"  Intraday Entry Enhancement: {config['cross_timeframe']['use_intraday_for_entries']}")
    print(f"  Intraday Exit Enhancement: {config['cross_timeframe']['use_intraday_for_exits']}")
    print()
    
    # Check alerts
    telegram_enabled = config.get('alerts', {}).get('telegram', {}).get('enabled', False)
    email_enabled = config.get('alerts', {}).get('email', {}).get('enabled', False)
    
    print("Alerts:")
    print(f"  Telegram: {'✓ Enabled' if telegram_enabled else '○ Disabled'}")
    print(f"  Email: {'✓ Enabled' if email_enabled else '○ Disabled'}")
    print()
    
    print("="*80)
    print("NEXT STEPS TO IMPLEMENT FULL SYSTEM:")
    print("="*80)
    print()
    print("1. Locate your swing_trader_engine.py file")
    print("   (from finbert_v4.4.4/models/backtesting/)")
    print()
    print("2. Locate your intraday monitoring components:")
    print("   - models/screening/spi_monitor.py")
    print("   - models/screening/us_market_monitor.py")
    print("   - models/screening/macro_news_monitor.py")
    print("   - models/scheduling/intraday_rescan_manager.py")
    print()
    print("3. Create live_trading_coordinator.py that integrates:")
    print("   - Swing trading engine (your existing Phase 1-3 code)")
    print("   - Intraday monitoring components")
    print("   - Cross-timeframe decision logic")
    print("   - Broker API integration")
    print()
    print("4. Use the integration design from LIVE_TRADING_WITH_INTRADAY_INTEGRATION.md")
    print()
    print("="*80)
    print()
    
    print(f"Simulation timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

PYTHON_EOF

echo ""
echo "=================================================="
echo "To implement the full system, see:"
echo "  - README.md"
echo "  - PHASE3_INTRADAY_DEPLOYMENT_COMPLETE.md"
echo "=================================================="

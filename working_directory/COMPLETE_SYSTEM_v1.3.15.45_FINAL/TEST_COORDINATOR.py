"""
EMERGENCY DIAGNOSTIC: Test Paper Trading Coordinator
This script tests if the PaperTradingCoordinator can be initialized
"""

import sys
from pathlib import Path

print("="*60)
print("EMERGENCY DIAGNOSTIC: Paper Trading Initialization Test")
print("="*60)
print()

# Test 1: Check imports
print("[TEST 1] Checking imports...")
try:
    from paper_trading_coordinator import PaperTradingCoordinator
    print("✅ PaperTradingCoordinator imported successfully")
except ImportError as e:
    print(f"❌ FAILED to import PaperTradingCoordinator")
    print(f"   Error: {e}")
    sys.exit(1)

# Test 2: Check if SwingSignalGenerator is available
print("\n[TEST 2] Checking ML components...")
try:
    from ml_pipeline.swing_signal_generator import SwingSignalGenerator
    print("✅ SwingSignalGenerator available")
    ml_available = True
except ImportError as e:
    print(f"⚠️  SwingSignalGenerator NOT available")
    print(f"   Error: {e}")
    print("   Will fall back to simplified signals")
    ml_available = False

# Test 3: Check config file
print("\n[TEST 3] Checking configuration...")
config_path = Path('config/screening_config.json')
if config_path.exists():
    print(f"✅ Config file exists: {config_path}")
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Config file is valid JSON")
        
        # Check for required keys
        if 'swing_trading' in config:
            print(f"✅ swing_trading section found")
            threshold = config['swing_trading'].get('confidence_threshold', 'NOT SET')
            print(f"   Confidence threshold: {threshold}")
        else:
            print(f"⚠️  No swing_trading section in config")
            
    except Exception as e:
        print(f"❌ Config file is invalid")
        print(f"   Error: {e}")
else:
    print(f"⚠️  Config file not found: {config_path}")
    print("   Will use default configuration")

# Test 4: Initialize coordinator
print("\n[TEST 4] Attempting to initialize PaperTradingCoordinator...")
print("   Symbols: AAPL, MSFT")
print("   Capital: $100,000")
print(f"   Use ML: {ml_available}")
print()

try:
    coordinator = PaperTradingCoordinator(
        symbols=['AAPL', 'MSFT'],
        initial_capital=100000.0,
        use_real_swing_signals=ml_available  # Use ML if available
    )
    print("✅ PaperTradingCoordinator initialized successfully!")
    print()
    print("Coordinator Details:")
    print(f"  - Symbols: {coordinator.symbols}")
    print(f"  - Capital: ${coordinator.current_capital:,.2f}")
    print(f"  - ML Signals: {coordinator.use_real_swing_signals}")
    print(f"  - Max Positions: {coordinator.config['risk_management']['max_total_positions']}")
    print()
    
    # Test 5: Try to run one cycle
    print("\n[TEST 5] Attempting to run one trading cycle...")
    try:
        coordinator.run_single_cycle()
        print("✅ Single cycle completed successfully!")
        print()
        
        # Check if state was saved
        state_file = Path('state/paper_trading_state.json')
        if state_file.exists():
            print("✅ State file created successfully")
            import json
            with open(state_file, 'r') as f:
                state = json.load(f)
            print(f"   Timestamp: {state.get('timestamp', 'N/A')}")
            print(f"   Symbols: {state.get('symbols', [])}")
            print(f"   Positions: {state.get('positions', {}).get('count', 0)}")
        else:
            print("⚠️  State file not created")
            
    except Exception as e:
        print(f"❌ FAILED to run trading cycle")
        print(f"   Error: {e}")
        import traceback
        print("\n   Full traceback:")
        traceback.print_exc()
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FAILED to initialize PaperTradingCoordinator")
    print(f"   Error: {e}")
    print()
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)

print()
print("="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print()
print("RESULT: Paper Trading Coordinator is WORKING")
print()
print("If you see this message, the coordinator can initialize and run.")
print("The issue is likely in the dashboard's threading/callback setup.")
print()
print("RECOMMENDATION:")
print("1. The coordinator itself works fine")
print("2. Problem is in unified_trading_dashboard.py")
print("3. Likely issue: callback not triggering or thread not starting")
print("4. Try restarting dashboard with CTRL+C and run again")
print()

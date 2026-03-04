"""
Integration Test Script
=======================

Tests the Phase 1-3 swing trading with intraday monitoring integration.

This script validates:
- Configuration loading
- Portfolio initialization
- Position management
- Risk calculations
- Alert system (if configured)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

def test_configuration():
    """Test configuration loading"""
    print("\n" + "="*80)
    print("TEST 1: Configuration Loading")
    print("="*80)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✓ Configuration loaded successfully")
        
        # Validate required sections
        required_sections = ['swing_trading', 'intraday_monitoring', 'risk_management', 'cross_timeframe']
        for section in required_sections:
            if section in config:
                print(f"  ✓ Section '{section}' found")
            else:
                print(f"  ✗ Section '{section}' MISSING")
                return False
        
        # Display key settings
        print("\nKey Settings:")
        print(f"  Confidence Threshold: {config['swing_trading']['confidence_threshold']}%")
        print(f"  Max Position Size: {config['swing_trading']['max_position_size']*100}%")
        print(f"  Stop Loss: {config['swing_trading']['stop_loss_percent']}%")
        print(f"  Max Positions: {config['risk_management']['max_total_positions']}")
        print(f"  Intraday Scanning: Every {config['intraday_monitoring']['scan_interval_minutes']} minutes")
        
        return True
    
    except FileNotFoundError:
        print("✗ config.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config.json: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return False


def test_coordinator_initialization():
    """Test LiveTradingCoordinator initialization"""
    print("\n" + "="*80)
    print("TEST 2: Live Trading Coordinator Initialization")
    print("="*80)
    
    try:
        from live_trading_coordinator import LiveTradingCoordinator
        
        coordinator = LiveTradingCoordinator(
            market="US",
            initial_capital=100000.0,
            config_file="config.json",
            paper_trading=True
        )
        
        print("✓ Coordinator initialized successfully")
        print(f"  Market: {coordinator.market}")
        print(f"  Initial Capital: ${coordinator.initial_capital:,.2f}")
        print(f"  Paper Trading: {coordinator.paper_trading}")
        
        # Test portfolio status
        status = coordinator.get_portfolio_status()
        print("\nInitial Portfolio Status:")
        print(f"  Cash: ${status['capital']['current_cash']:,.2f}")
        print(f"  Total Value: ${status['capital']['total_value']:,.2f}")
        print(f"  Open Positions: {status['positions']['count']}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import LiveTradingCoordinator: {e}")
        return False
    except Exception as e:
        print(f"✗ Error initializing coordinator: {e}")
        return False


def test_position_management():
    """Test position management features"""
    print("\n" + "="*80)
    print("TEST 3: Position Management")
    print("="*80)
    
    try:
        from live_trading_coordinator import LiveTradingCoordinator, LivePosition, PositionType
        from datetime import datetime
        
        coordinator = LiveTradingCoordinator(
            market="US",
            initial_capital=100000.0,
            paper_trading=True
        )
        
        # Create a test position
        test_position = LivePosition(
            symbol="AAPL",
            position_type=PositionType.SWING,
            entry_date=datetime.now(),
            entry_price=175.00,
            shares=140,
            stop_loss=169.75,
            trailing_stop=169.75,
            profit_target=189.00,
            target_exit_date=datetime.now() + timedelta(days=7),
            current_price=175.00,
            unrealized_pnl=0.0,
            unrealized_pnl_pct=0.0,
            entry_signal_strength=65.5,
            regime="MILD_UPTREND",
            notes="Test position"
        )
        
        coordinator.positions["AAPL"] = test_position
        print("✓ Test position created: AAPL")
        print(f"  Entry: ${test_position.entry_price:.2f}")
        print(f"  Shares: {test_position.shares}")
        print(f"  Stop Loss: ${test_position.stop_loss:.2f}")
        print(f"  Profit Target: ${test_position.profit_target:.2f}")
        
        # Update position with price change
        coordinator.update_positions({"AAPL": 180.00})
        
        updated_position = coordinator.positions["AAPL"]
        print("\n✓ Position updated with new price: $180.00")
        print(f"  Unrealized P&L: ${updated_position.unrealized_pnl:,.2f}")
        print(f"  Unrealized P&L %: {updated_position.unrealized_pnl_pct:+.2f}%")
        
        # Get portfolio status
        status = coordinator.get_portfolio_status()
        print("\nPortfolio Status:")
        print(f"  Open Positions: {status['positions']['count']}")
        print(f"  Invested Capital: ${status['capital']['invested']:,.2f}")
        print(f"  Total Unrealized P&L: ${status['positions']['total_unrealized_pnl']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in position management test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_calculations():
    """Test risk management calculations"""
    print("\n" + "="*80)
    print("TEST 4: Risk Management")
    print("="*80)
    
    try:
        from live_trading_coordinator import LiveTradingCoordinator
        
        coordinator = LiveTradingCoordinator(
            market="US",
            initial_capital=100000.0,
            config_file="config.json",
            paper_trading=True
        )
        
        # Test risk parameters
        config = coordinator.config
        
        print("Risk Parameters:")
        print(f"  ✓ Max Total Positions: {config['risk_management']['max_total_positions']}")
        print(f"  ✓ Max Portfolio Heat: {config['risk_management']['max_portfolio_heat']*100}%")
        print(f"  ✓ Max Single Trade Risk: {config['risk_management']['max_single_trade_risk']*100}%")
        
        # Calculate position sizing example
        initial_capital = coordinator.initial_capital
        max_position_size = config['swing_trading']['max_position_size']
        max_position_value = initial_capital * max_position_size
        
        print(f"\nPosition Sizing (25% max):")
        print(f"  Max Position Value: ${max_position_value:,.2f}")
        print(f"  Example: AAPL @ $175 = {int(max_position_value / 175)} shares")
        
        # Test boosted position sizing
        boost_threshold = config['cross_timeframe']['sentiment_boost_threshold']
        max_boosted_size = config['cross_timeframe']['max_boosted_position_size']
        max_boosted_value = initial_capital * max_boosted_size
        
        print(f"\nBoosted Position Sizing (30% max when sentiment >{boost_threshold}):")
        print(f"  Max Boosted Value: ${max_boosted_value:,.2f}")
        print(f"  Example: AAPL @ $175 = {int(max_boosted_value / 175)} shares")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in risk calculations test: {e}")
        return False


def test_state_persistence():
    """Test state save/load functionality"""
    print("\n" + "="*80)
    print("TEST 5: State Persistence")
    print("="*80)
    
    try:
        from live_trading_coordinator import LiveTradingCoordinator
        import os
        
        coordinator = LiveTradingCoordinator(
            market="US",
            initial_capital=100000.0,
            paper_trading=True
        )
        
        # Save state
        test_state_file = "test_state.json"
        coordinator.save_state(test_state_file)
        
        if os.path.exists(test_state_file):
            print(f"✓ State saved successfully to {test_state_file}")
            
            # Load and validate
            with open(test_state_file, 'r') as f:
                state = json.load(f)
            
            print("✓ State loaded and validated")
            print(f"  Timestamp: {state['timestamp']}")
            print(f"  Market: {state['market']}")
            print(f"  Capital: ${state['capital']:,.2f}")
            
            # Clean up
            os.remove(test_state_file)
            print("✓ Test state file cleaned up")
            
            return True
        else:
            print("✗ State file not created")
            return False
        
    except Exception as e:
        print(f"✗ Error in state persistence test: {e}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("SWING TRADING + INTRADAY INTEGRATION TEST SUITE")
    print("Phase 1-3 Complete")
    print("="*80)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("Coordinator Initialization", test_coordinator_initialization),
        ("Position Management", test_position_management),
        ("Risk Calculations", test_risk_calculations),
        ("State Persistence", test_state_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed")
    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is ready for paper trading!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Please review errors above")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

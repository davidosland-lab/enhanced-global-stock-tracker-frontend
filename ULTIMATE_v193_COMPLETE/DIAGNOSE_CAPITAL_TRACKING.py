"""
Capital Tracking Diagnostic Tool
=================================
Checks why state file is not being saved and capital is not updating correctly.
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

import json
from datetime import datetime

def main():
    print("="*80)
    print("CAPITAL TRACKING DIAGNOSTIC")
    print("="*80)
    
    # Check 1: State directory
    print("\n[CHECK 1] State Directory")
    state_dir = Path('state')
    print(f"  Exists: {state_dir.exists()}")
    print(f"  Writable: {state_dir.exists() and state_dir.is_dir()}")
    
    if state_dir.exists():
        files = list(state_dir.glob('*'))
        print(f"  Files: {len(files)}")
        for f in files:
            print(f"    - {f.name} ({f.stat().st_size} bytes)")
    
    # Check 2: State file
    print("\n[CHECK 2] State File")
    state_file = Path('state/paper_trading_state.json')
    print(f"  Path: {state_file}")
    print(f"  Exists: {state_file.exists()}")
    
    if state_file.exists():
        size = state_file.stat().st_size
        print(f"  Size: {size} bytes")
        
        if size > 0:
            try:
                with open(state_file) as f:
                    state = json.load(f)
                
                print(f"  Valid JSON: Yes")
                print(f"\n  Capital Info:")
                print(f"    Total: ${state.get('capital', {}).get('total', 0):,.2f}")
                print(f"    Cash: ${state.get('capital', {}).get('cash', 0):,.2f}")
                print(f"    Invested: ${state.get('capital', {}).get('invested', 0):,.2f}")
                
                print(f"\n  Positions:")
                positions = state.get('positions', {}).get('open', [])
                print(f"    Count: {len(positions)}")
                for pos in positions:
                    symbol = pos.get('symbol', '?')
                    shares = pos.get('shares', 0)
                    entry = pos.get('entry_price', 0)
                    current = pos.get('current_price', 0)
                    print(f"    - {symbol}: {shares} shares @ ${entry:.2f} (current: ${current:.2f})")
                
            except json.JSONDecodeError as e:
                print(f"  Valid JSON: No - {e}")
        else:
            print(f"  Status: EMPTY FILE")
    else:
        print(f"  Status: DOES NOT EXIST")
    
    # Check 3: Try to import PaperTradingCoordinator
    print("\n[CHECK 3] PaperTradingCoordinator Module")
    try:
        from paper_trading_coordinator import PaperTradingCoordinator
        print("  Import: SUCCESS")
        
        # Check if it has save_state method
        has_save = hasattr(PaperTradingCoordinator, 'save_state')
        print(f"  Has save_state(): {has_save}")
        
        has_get_status = hasattr(PaperTradingCoordinator, 'get_status_dict')
        print(f"  Has get_status_dict(): {has_get_status}")
        
    except ImportError as e:
        print(f"  Import: FAILED - {e}")
    
    # Check 4: Log files
    print("\n[CHECK 4] Log Files")
    logs_dir = Path('logs')
    if logs_dir.exists():
        log_files = sorted(logs_dir.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
        print(f"  Found: {len(log_files)} log files")
        
        for log_file in log_files[:5]:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            size = log_file.stat().st_size
            print(f"    - {log_file.name}: {size} bytes (modified: {mtime})")
            
            # Check for recent activity
            if size > 0:
                with open(log_file) as f:
                    lines = f.readlines()
                    
                # Look for trading cycle messages
                cycle_lines = [l for l in lines if 'CYCLE' in l or 'trading cycle' in l.lower()]
                save_lines = [l for l in lines if 'State saved' in l or 'save_state' in l.lower()]
                error_lines = [l for l in lines if 'ERROR' in l or 'Error' in l]
                
                if cycle_lines:
                    print(f"      Trading cycles: {len(cycle_lines)} messages")
                    if cycle_lines:
                        print(f"      Last: {cycle_lines[-1].strip()[:100]}")
                
                if save_lines:
                    print(f"      State saves: {len(save_lines)} messages")
                    if save_lines:
                        print(f"      Last: {save_lines[-1].strip()[:100]}")
                
                if error_lines and len(error_lines) > 0:
                    print(f"      Errors: {len(error_lines)} messages")
                    for err in error_lines[-3:]:
                        print(f"      - {err.strip()[:120]}")
    else:
        print("  Logs directory does not exist")
    
    # Check 5: Test save_state functionality
    print("\n[CHECK 5] Test Save State Function")
    try:
        from paper_trading_coordinator import PaperTradingCoordinator
        
        # Create minimal test instance
        test_sys = PaperTradingCoordinator(
            symbols=['TEST'],
            initial_capital=100000,
            use_real_swing_signals=False
        )
        
        print("  Test instance created: SUCCESS")
        
        # Try to save state
        test_path = 'state/diagnostic_test.json'
        test_sys.save_state(test_path)
        
        if Path(test_path).exists():
            size = Path(test_path).stat().st_size
            print(f"  Test save: SUCCESS ({size} bytes)")
            
            # Read it back
            with open(test_path) as f:
                test_state = json.load(f)
            
            print(f"  Test state capital: ${test_state['capital']['total']:,.2f}")
            
            # Clean up
            Path(test_path).unlink()
            print(f"  Cleanup: SUCCESS")
        else:
            print(f"  Test save: FAILED - file not created")
            
    except Exception as e:
        print(f"  Test save: FAILED - {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    print("  1. Check if trading loop is actually running (look for [CYCLE] messages)")
    print("  2. Verify save_state() is being called after trades")
    print("  3. Check file permissions on state/ directory")
    print("  4. Review logs for any save_state errors")
    print()

if __name__ == '__main__':
    main()

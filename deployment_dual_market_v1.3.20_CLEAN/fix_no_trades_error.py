#!/usr/bin/env python3
"""
Quick fix for 'No trades executed' error
Patches swing_trader_engine.py to return valid results instead of error
"""

import os
import sys
import shutil
from datetime import datetime

def apply_fix(file_path):
    """Apply the no-trades fix"""
    
    print(f"[INFO] Reading {os.path.basename(file_path)}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'message\': \'No trades executed - strategy did not find' in content:
        print("[OK] File already patched!")
        return True
    
    # Create backup
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"[INFO] Creating backup: {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    # Apply fix
    old_code = '''        if not self.closed_trades:
            return {
                'error': 'No trades executed',
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date
            }'''
    
    new_code = '''        if not self.closed_trades:
            # Return valid results with 0 trades instead of error
            return {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': self.initial_capital,
                'final_value': self.capital,
                'total_return': 0.0,
                'total_return_pct': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'avg_hold_time': 0.0,
                'trades': [],
                'equity_curve': [],
                'message': 'No trades executed - strategy did not find any opportunities that met the criteria'
            }'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("[OK] Fix applied successfully")
    else:
        print("[ERROR] Could not find code to replace")
        print("[INFO] File may already be fixed or different than expected")
        return False
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] File updated successfully")
    return True


def main():
    """Main function"""
    print()
    print("=" * 60)
    print("  Fix 'No Trades Executed' Error")
    print("=" * 60)
    print()
    
    # Get path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter path to FinBERT directory: ").strip().strip('"').strip("'")
    
    # Auto-detect finbert_v4.4.4 subdirectory
    target_file = None
    
    for possible_path in [
        os.path.join(base_path, 'finbert_v4.4.4', 'models', 'backtesting', 'swing_trader_engine.py'),
        os.path.join(base_path, 'models', 'backtesting', 'swing_trader_engine.py')
    ]:
        if os.path.exists(possible_path):
            target_file = possible_path
            break
    
    if not target_file:
        print(f"[ERROR] Cannot find swing_trader_engine.py in {base_path}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"[INFO] Target file: {target_file}")
    print()
    
    # Apply fix
    if apply_fix(target_file):
        print()
        print("=" * 60)
        print("  Fix Applied Successfully!")
        print("=" * 60)
        print()
        print("NEXT STEPS:")
        print("1. Restart the FinBERT server")
        print("2. Test the Swing Trading backtest")
        print("3. 'No trades executed' will now show as warning, not error")
        print()
    else:
        print()
        print("=" * 60)
        print("  Fix Failed")
        print("=" * 60)
        print()
    
    input("Press Enter to exit...")


if __name__ == '__main__':
    main()

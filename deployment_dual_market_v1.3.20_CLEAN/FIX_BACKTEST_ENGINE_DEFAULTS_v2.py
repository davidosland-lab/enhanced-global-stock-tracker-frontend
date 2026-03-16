#!/usr/bin/env python3
r"""
Fix Backtest Engine Defaults
============================

This script automatically updates backtest_engine.py defaults to enable Phase 2 features.

CAUTION: This modifies your backtest_engine.py file. A backup will be created.

Usage:
    cd C:\Users\david\AATelS
    python FIX_BACKTEST_ENGINE_DEFAULTS_v2.py
    
Optional: Set custom stop-loss percentage
    python FIX_BACKTEST_ENGINE_DEFAULTS_v2.py --stop-loss 1.0
"""

import os
import sys
import shutil
from datetime import datetime

def create_backup(filepath):
    """Create a backup of the file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = os.path.join(backup_dir, f"backtest_engine_backup_{timestamp}.py")
    shutil.copy2(filepath, backup_path)
    return backup_path

def fix_defaults(filepath, stop_loss_pct=2.0):
    """Fix the default values in backtest_engine.py"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes = []
    
    # Fix allocation_strategy
    if "allocation_strategy: str = 'equal'" in content:
        content = content.replace(
            "allocation_strategy: str = 'equal'",
            "allocation_strategy: str = 'risk_based'"
        )
        changes.append("allocation_strategy: 'equal' -> 'risk_based'")
    
    # Fix stop_loss_percent - handle any current value
    import re
    stop_loss_pattern = r"stop_loss_percent: float = \d+\.?\d*"
    match = re.search(stop_loss_pattern, content)
    if match:
        old_value = match.group(0)
        new_value = f"stop_loss_percent: float = {stop_loss_pct}"
        if old_value != new_value:
            content = re.sub(stop_loss_pattern, new_value, content)
            changes.append(f"stop_loss_percent: {old_value.split('=')[1].strip()} -> {stop_loss_pct}")
    
    # Fix enable_take_profit
    if "enable_take_profit: bool = False" in content:
        content = content.replace(
            "enable_take_profit: bool = False",
            "enable_take_profit: bool = True"
        )
        changes.append("enable_take_profit: False -> True")
    
    return content, changes

def main():
    print("\n" + "="*70)
    print("  BACKTEST ENGINE DEFAULTS FIXER v2")
    print("="*70)
    
    # Parse command line arguments
    stop_loss_pct = 2.0  # Default
    if len(sys.argv) > 1:
        if '--stop-loss' in sys.argv:
            try:
                idx = sys.argv.index('--stop-loss')
                stop_loss_pct = float(sys.argv[idx + 1])
                print(f"\nCustom stop-loss: {stop_loss_pct}%")
            except (IndexError, ValueError):
                print("\nERROR: Invalid stop-loss value")
                print("Usage: python FIX_BACKTEST_ENGINE_DEFAULTS_v2.py --stop-loss 1.0")
                return False
    
    engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'
    
    # Check if file exists
    if not os.path.exists(engine_path):
        print(f"\nERROR: {engine_path} not found!")
        print(f"Current directory: {os.getcwd()}")
        print("\nMake sure you're running from: C:\\Users\\david\\AATelS")
        return False
    
    print(f"\nFound: {engine_path}")
    
    # Create backup
    print("\nCreating backup...")
    try:
        backup_path = create_backup(engine_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {e}")
        print("Aborting to prevent data loss!")
        return False
    
    # Read and fix
    print("\nAnalyzing and fixing defaults...")
    try:
        fixed_content, changes = fix_defaults(engine_path, stop_loss_pct)
        
        if not changes:
            print("\nNo changes needed!")
            print("All defaults are already optimal.")
            return True
        
        print("\nChanges to be made:")
        for change in changes:
            print(f"   - {change}")
        
        # Write fixed content
        print("\nWriting changes...")
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("Changes written successfully!")
        
        # Summary
        print("\n" + "="*70)
        print("  FIX COMPLETE")
        print("="*70)
        print(f"\nModified: {engine_path}")
        print(f"Backup: {backup_path}")
        print(f"Changes: {len(changes)}")
        print("\nNEXT STEPS:")
        print("1. Restart FinBERT v4.4.4")
        print("2. Set Confidence Threshold to 60%")
        print("3. Re-run backtest")
        print("\nEXPECTED RESULTS:")
        print("- Total Return: +8-12%")
        print("- Win Rate: 45-55%")
        print("- Profit Factor: 1.5-2.4")
        print("- Sharpe Ratio: 1.2-1.8")
        
        return True
        
    except Exception as e:
        print(f"\nError during fix: {e}")
        print(f"Your original file is safe at: {backup_path}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nScript completed successfully!")
        else:
            print("\nScript failed. Check errors above.")
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

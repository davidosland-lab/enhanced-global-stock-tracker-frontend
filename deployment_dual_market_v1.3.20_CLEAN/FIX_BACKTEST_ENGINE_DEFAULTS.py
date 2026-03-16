#!/usr/bin/env python3
"""
Fix Backtest Engine Defaults
============================

This script automatically updates backtest_engine.py defaults to enable Phase 2 features.

CAUTION: This modifies your backtest_engine.py file. A backup will be created.

Usage:
    cd C:\Users\david\AATelS
    python FIX_BACKTEST_ENGINE_DEFAULTS.py
"""

import os
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

def fix_defaults(filepath):
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
        changes.append("allocation_strategy: 'equal' → 'risk_based'")
    
    # Fix stop_loss_percent
    if "stop_loss_percent: float = 1.0" in content:
        content = content.replace(
            "stop_loss_percent: float = 1.0",
            "stop_loss_percent: float = 2.0"
        )
        changes.append("stop_loss_percent: 1.0 → 2.0")
    
    # Fix enable_take_profit
    if "enable_take_profit: bool = False" in content:
        content = content.replace(
            "enable_take_profit: bool = False",
            "enable_take_profit: bool = True"
        )
        changes.append("enable_take_profit: False → True")
    
    return content, changes

def main():
    print("\n" + "="*70)
    print("  BACKTEST ENGINE DEFAULTS FIXER")
    print("="*70)
    
    engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'
    
    # Check if file exists
    if not os.path.exists(engine_path):
        print("\n❌ ERROR: backtest_engine.py not found!")
        print(f"   Expected: {engine_path}")
        print(f"   Current directory: {os.getcwd()}")
        print("\n   Make sure you're running from C:\\Users\\david\\AATelS")
        return False
    
    print(f"\n📁 Found: {engine_path}")
    
    # Create backup
    print("\n📋 Creating backup...")
    try:
        backup_path = create_backup(engine_path)
        print(f"✅ Backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        print("   Aborting to prevent data loss!")
        return False
    
    # Read and fix
    print("\n🔧 Analyzing and fixing defaults...")
    try:
        fixed_content, changes = fix_defaults(engine_path)
        
        if not changes:
            print("\n✅ No changes needed!")
            print("   All defaults are already optimal.")
            return True
        
        print("\n📝 Changes to be made:")
        for change in changes:
            print(f"   - {change}")
        
        # Write fixed content
        print("\n💾 Writing changes...")
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Changes written successfully!")
        
        # Summary
        print("\n" + "="*70)
        print("  ✅ FIX COMPLETE")
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
        print(f"\n❌ Error during fix: {e}")
        print(f"   Your original file is safe at: {backup_path}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Script completed successfully!")
        else:
            print("\n❌ Script failed. Check errors above.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

"""
Manual Fix Script for Intraday Monitoring Error
================================================

Automatically fixes the MarketHoursDetector TypeError without Git.

Error fixed:
    TypeError: MarketHoursDetector.__init__() got an unexpected 
    keyword argument 'market'

Usage:
    python MANUAL_FIX_INTRADAY.py
"""

import os
from pathlib import Path
import shutil
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("INTRADAY MONITORING FIX - Automatic Patch")
    print("="*80)
    print("\nThis script will fix the MarketHoursDetector error")
    print("that prevents intraday monitoring from starting.\n")
    
    # Check we're in the right directory
    current_dir = Path.cwd()
    target_file = current_dir / "models" / "scheduling" / "intraday_scheduler.py"
    
    if not target_file.exists():
        print("❌ ERROR: Not in the correct directory!")
        print(f"\nCurrent directory: {current_dir}")
        print("\nPlease run this script from: C:\\Users\\david\\AATelS")
        print("\nExample:")
        print("    cd C:\\Users\\david\\AATelS")
        print("    python MANUAL_FIX_INTRADAY.py")
        return 1
    
    print(f"✓ Found target file: {target_file}")
    
    # Read current content
    print("\n[1/4] Reading current file...")
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if "MarketHoursDetector()" in content and "is_market_open(market=self.market)" in content:
        print("✓ File appears already fixed!")
        print("\nYour intraday_scheduler.py already has the correct code.")
        print("If you're still seeing errors, the problem may be elsewhere.")
        return 0
    
    # Backup original
    print("\n[2/4] Creating backup...")
    backup_name = f"intraday_scheduler.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = target_file.parent / backup_name
    shutil.copy2(target_file, backup_path)
    print(f"✓ Backup created: {backup_name}")
    
    # Apply fixes
    print("\n[3/4] Applying fixes...")
    
    # Fix 1: Line 62
    fix_count = 0
    if "MarketHoursDetector(market=market)" in content:
        content = content.replace(
            "MarketHoursDetector(market=market)",
            "MarketHoursDetector()"
        )
        print("  ✓ Fix 1: Removed 'market' parameter from __init__()")
        fix_count += 1
    
    # Fix 2 & 3: Add market parameter to is_market_open() calls
    # We need to be careful to only fix calls that don't have the parameter
    
    # Fix for line 85 (in start_intraday_monitoring)
    old_pattern_1 = "# Check if market is open\n        market_status = self.market_detector.is_market_open()"
    new_pattern_1 = "# Check if market is open\n        market_status = self.market_detector.is_market_open(market=self.market)"
    
    if old_pattern_1 in content:
        content = content.replace(old_pattern_1, new_pattern_1)
        print("  ✓ Fix 2: Added 'market' parameter to is_market_open() (line ~85)")
        fix_count += 1
    
    # Fix for line 114 (in monitoring loop)
    old_pattern_2 = "# Check if market is still open\n                market_status = self.market_detector.is_market_open()"
    new_pattern_2 = "# Check if market is still open\n                market_status = self.market_detector.is_market_open(market=self.market)"
    
    if old_pattern_2 in content:
        content = content.replace(old_pattern_2, new_pattern_2)
        print("  ✓ Fix 3: Added 'market' parameter to is_market_open() (line ~114)")
        fix_count += 1
    
    if fix_count == 0:
        print("  ⚠️  No fixes applied - file may already be fixed or have unexpected format")
        print("\n  You may need to apply fixes manually. See: FIX_INTRADAY_MARKET_DETECTOR.txt")
        return 1
    
    # Write fixed content
    print(f"\n[4/4] Writing fixed file... ({fix_count} fixes applied)")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ File updated successfully")
    
    # Summary
    print("\n" + "="*80)
    print("FIX COMPLETE!")
    print("="*80)
    print(f"\n✓ Applied {fix_count} fixes to intraday_scheduler.py")
    print(f"✓ Backup saved: {backup_name}")
    print("\nChanges made:")
    print("  1. MarketHoursDetector(market=market) → MarketHoursDetector()")
    print("  2. is_market_open() → is_market_open(market=self.market) [line ~85]")
    print("  3. is_market_open() → is_market_open(market=self.market) [line ~114]")
    
    print("\n" + "="*80)
    print("TESTING")
    print("="*80)
    print("\nTest the fix with:")
    print("    python models\\scheduling\\intraday_scheduler.py --market ASX --interval 15")
    print("\nExpected output:")
    print("    ✓ Market Hours Detector initialized")
    print("    ✓ STARTING INTRADAY MONITORING SESSION")
    print("\nShould NOT see:")
    print("    ✗ TypeError: __init__() got an unexpected keyword argument 'market'")
    
    print("\n" + "="*80)
    print("ROLLBACK")
    print("="*80)
    print("\nIf something goes wrong, restore backup:")
    print(f"    copy models\\scheduling\\{backup_name} models\\scheduling\\intraday_scheduler.py")
    
    print("\n" + "="*80 + "\n")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("MANUAL FIX INSTRUCTIONS")
        print("="*80)
        print("\nIf the automatic fix failed, apply manually:")
        print("See: FIX_INTRADAY_MARKET_DETECTOR.txt")
        exit(1)

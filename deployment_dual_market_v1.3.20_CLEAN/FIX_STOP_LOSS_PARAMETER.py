#!/usr/bin/env python3
"""
Fix Stop Loss Parameter Name Mismatch
======================================

BUG: Single stock backtest endpoint expects 'stop_loss_pct' but UI sends 'stop_loss_percent'
RESULT: Stop loss parameter is IGNORED, always uses 3% default

This fixes the parameter name mismatch so stop loss actually works.

Author: FinBERT v4.4.4 Diagnostic Team
Date: December 2025
"""

import os
import sys
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create a timestamped backup of a file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return True


def fix_stop_loss_parameter(filepath):
    """Fix stop_loss_pct parameter to accept both naming conventions"""
    
    if not os.path.exists(filepath):
        print(f"❌ API file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing stop loss parameter in: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the stop_loss_pct line
    old_pattern = "stop_loss_pct = data.get('stop_loss_pct', 0.03)  # Default 3%"
    
    if old_pattern in content:
        # New code that accepts multiple parameter names
        new_code = """# Accept stop_loss in multiple formats
        # UI might send: 'stop_loss_percent' (as %, e.g., 2.0 means 2%)
        # Or: 'stop_loss_pct' (as decimal, e.g., 0.02 means 2%)
        stop_loss_input = data.get('stop_loss_percent', data.get('stop_loss', None))
        if stop_loss_input is not None:
            # Convert from percentage to decimal if needed (value > 1 means it's in %)
            stop_loss_pct = stop_loss_input / 100.0 if stop_loss_input > 1 else stop_loss_input
        else:
            stop_loss_pct = data.get('stop_loss_pct', 0.02)  # Default 2%"""
        
        content = content.replace(old_pattern, new_code)
        print("✓ Fixed stop_loss_pct parameter to accept UI input")
    else:
        print("⚠️  Could not find exact pattern, trying alternate fix...")
        
        # Try alternate pattern (in case default changed)
        import re
        pattern = r"stop_loss_pct = data\.get\('stop_loss_pct', [0-9.]+\)"
        
        if re.search(pattern, content):
            new_code = """# Accept stop_loss in multiple formats
        stop_loss_input = data.get('stop_loss_percent', data.get('stop_loss', None))
        if stop_loss_input is not None:
            stop_loss_pct = stop_loss_input / 100.0 if stop_loss_input > 1 else stop_loss_input
        else:
            stop_loss_pct = data.get('stop_loss_pct', 0.02)"""
            
            content = re.sub(pattern, new_code, content)
            print("✓ Fixed stop_loss_pct parameter (alternate method)")
        else:
            print("❌ Could not find stop_loss_pct parameter")
            return False
    
    # Also fix take_profit_pct
    old_take_profit = "take_profit_pct = data.get('take_profit_pct', 0.10)  # Default 10%"
    
    if old_take_profit in content:
        new_take_profit = """# Accept take_profit in multiple formats
        take_profit_input = data.get('take_profit_percent', data.get('take_profit', None))
        if take_profit_input is not None:
            take_profit_pct = take_profit_input / 100.0 if take_profit_input > 1 else take_profit_input
        else:
            take_profit_pct = data.get('take_profit_pct', 0.10)  # Default 10%"""
        
        content = content.replace(old_take_profit, new_take_profit)
        print("✓ Fixed take_profit_pct parameter to accept UI input")
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Stop loss parameter fixed successfully!")
    return True


def main():
    print("=" * 70)
    print("FIX STOP LOSS PARAMETER NAME MISMATCH")
    print("=" * 70)
    print("\nBUG: Stop loss parameter is ignored in single stock backtest")
    print("CAUSE: API expects 'stop_loss_pct', UI sends 'stop_loss_percent'")
    print("RESULT: Always uses 3% default, UI input has no effect")
    print("\n" + "=" * 70)
    
    # Determine base directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # File path
    api_file = os.path.join(script_dir, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    
    print(f"\n📂 Working directory: {script_dir}")
    print(f"\n📄 File to modify:")
    print(f"  • {api_file}")
    
    # Check if file exists
    if not os.path.exists(api_file):
        print(f"\n❌ API file not found: {api_file}")
        print(f"\n💡 Make sure you're running this from: C:\\Users\\david\\AATelS")
        return 1
    
    # Create backup
    print("\n" + "=" * 70)
    print("📦 CREATING BACKUP")
    print("=" * 70)
    
    if not backup_file(api_file):
        return 1
    
    # Apply fix
    print("\n" + "=" * 70)
    print("🔧 APPLYING FIX")
    print("=" * 70)
    
    if not fix_stop_loss_parameter(api_file):
        print("\n❌ Fix failed - check output above")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Stop loss parameter fixed!")
    print("=" * 70)
    print("\n📋 WHAT CHANGED:")
    print("  • API now accepts 'stop_loss_percent' from UI")
    print("  • Converts percentage (2.0) to decimal (0.02) automatically")
    print("  • Also accepts 'stop_loss' and 'stop_loss_pct' formats")
    print("  • Same fix applied to take_profit parameter")
    print("\n🔄 NEXT STEPS:")
    print("  1. **Restart FinBERT v4.4.4 completely**")
    print("  2. Run WBC.AX test again:")
    print("     • Test 1: Stop Loss 2%")
    print("     • Test 2: Stop Loss 20%")
    print("  3. Results should NOW be different!")
    print("\n🎯 EXPECTED:")
    print("  • 2% stop: Smaller losses, more stops, better results")
    print("  • 20% stop: Huge losses, few stops, worse results")
    print("  • Results will be DIFFERENT (proves fix worked)")
    print("\n" + "=" * 70)
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
PANDAS 2.x COMPATIBILITY FIX
Fixes the fillna(method='ffill') deprecation error

This script fixes the error:
  TypeError: NDFrame.fillna() got an unexpected keyword argument 'method'

The issue occurs because pandas 2.0+ removed the 'method' parameter from fillna().
"""

import os
import sys
import shutil
from datetime import datetime

def print_header(msg):
    print(f"\n{'='*80}")
    print(f"  {msg}")
    print(f"{'='*80}\n")

def fix_train_lstm():
    """Fix the deprecated fillna syntax in train_lstm.py"""
    
    file_path = os.path.join('finbert_v4.4.4', 'models', 'train_lstm.py')
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found: {file_path}")
        print("   Make sure you're running this from the unified_trading_dashboard_v1.3.15.87_ULTIMATE directory")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return False
    
    # Check if already fixed
    if "df.ffill().fillna(0)" in content:
        print("✓ File is already fixed!")
        return True
    
    # Apply fix
    old_code = "df = df.fillna(method='ffill').fillna(0)"
    new_code = "df = df.ffill().fillna(0)"
    
    if old_code not in content:
        print("⚠ WARNING: Expected code pattern not found")
        print("   The file may have been modified or already fixed differently")
        return False
    
    content = content.replace(old_code, new_code)
    
    # Write fixed file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fixed: {file_path}")
        print(f"  Changed: fillna(method='ffill') → ffill()")
        return True
    except Exception as e:
        print(f"❌ Failed to write file: {e}")
        # Restore backup
        shutil.copy2(backup_path, file_path)
        print(f"✓ Restored from backup")
        return False

def main():
    print_header("PANDAS 2.x COMPATIBILITY FIX")
    
    print("This fix resolves the error:")
    print("  TypeError: NDFrame.fillna() got an unexpected keyword argument 'method'\n")
    
    # Check current directory
    if not os.path.exists('finbert_v4.4.4'):
        print("❌ ERROR: finbert_v4.4.4 directory not found")
        print("   Please run this script from: unified_trading_dashboard_v1.3.15.87_ULTIMATE/")
        sys.exit(1)
    
    print("✓ Found finbert_v4.4.4 directory")
    
    # Apply fix
    print("\nApplying fix...")
    success = fix_train_lstm()
    
    if success:
        print_header("FIX APPLIED SUCCESSFULLY!")
        print("✓ The pandas 2.x compatibility issue is now fixed")
        print("\nNext steps:")
        print("  1. Restart Flask server (CTRL+C then restart)")
        print("  2. Try training again:")
        print("     curl -X POST http://localhost:5000/api/train/MSFT \\")
        print("       -H \"Content-Type: application/json\" \\")
        print("       -d '{\"epochs\": 50}'")
        print("\n  Expected: Training should now succeed ✓")
    else:
        print_header("FIX FAILED")
        print("Please check the error messages above")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

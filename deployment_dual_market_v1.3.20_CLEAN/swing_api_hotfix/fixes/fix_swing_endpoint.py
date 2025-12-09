#!/usr/bin/env python3
"""
Swing API Hotfix - Fix HistoricalDataLoader initialization
"""

import os
import sys
import shutil
from datetime import datetime

def apply_fix(app_file_path):
    """Apply the fix to app_finbert_v4_dev.py"""
    
    print("[INFO] Reading app_finbert_v4_dev.py...")
    
    with open(app_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'data_loader = HistoricalDataLoader(\n            symbol=symbol,' in content:
        print("[OK] File already patched!")
        return True
    
    # Create backup
    backup_path = f"{app_file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"[INFO] Creating backup: {backup_path}")
    shutil.copy2(app_file_path, backup_path)
    
    # Apply fix
    old_code = '''        # Phase 1: Load price data
        data_loader = HistoricalDataLoader()
        price_data = data_loader.load_price_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )'''
    
    new_code = '''        # Phase 1: Load price data
        data_loader = HistoricalDataLoader(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        price_data = data_loader.load_price_data(interval='1d')'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("[OK] Fix applied successfully")
    else:
        print("[WARN] Could not find exact code to replace")
        print("[INFO] Trying alternate pattern...")
        
        # Try alternate pattern
        old_code2 = "data_loader = HistoricalDataLoader()"
        new_code2 = '''data_loader = HistoricalDataLoader(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )'''
        
        if old_code2 in content:
            content = content.replace(old_code2, new_code2)
            print("[OK] Alternate fix applied")
        else:
            print("[ERROR] Could not apply fix - file may be different than expected")
            return False
    
    # Write updated content
    with open(app_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] File updated successfully")
    return True


def main():
    """Main function"""
    print()
    print("=" * 60)
    print("  Swing API Hotfix - Fix HistoricalDataLoader Error")
    print("=" * 60)
    print()
    print("ERROR FIXED:")
    print("  HistoricalDataLoader.__init__() missing 3 required")
    print("  positional arguments: 'symbol', 'start_date', 'end_date'")
    print()
    
    # Get path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter path to FinBERT directory: ").strip().strip('"').strip("'")
    
    # Auto-detect finbert_v4.4.4 subdirectory
    if os.path.exists(os.path.join(base_path, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')):
        app_file = os.path.join(base_path, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
        print(f"[INFO] Found in subdirectory: {base_path}\\finbert_v4.4.4")
    elif os.path.exists(os.path.join(base_path, 'app_finbert_v4_dev.py')):
        app_file = os.path.join(base_path, 'app_finbert_v4_dev.py')
        print(f"[INFO] Found in directory: {base_path}")
    else:
        print(f"[ERROR] Cannot find app_finbert_v4_dev.py in {base_path}")
        print()
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"[INFO] Target file: {app_file}")
    print()
    
    # Apply fix
    if apply_fix(app_file):
        print()
        print("=" * 60)
        print("  Fix Applied Successfully!")
        print("=" * 60)
        print()
        print("NEXT STEPS:")
        print("1. Restart the FinBERT server")
        print("2. Test the Swing Trading backtest again")
        print()
        print("The error should now be resolved!")
        print()
    else:
        print()
        print("=" * 60)
        print("  Fix Failed")
        print("=" * 60)
        print()
        print("Please check the error messages above.")
        print("You may need to apply the fix manually.")
        print()
    
    input("Press Enter to exit...")


if __name__ == '__main__':
    main()

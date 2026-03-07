"""
EMERGENCY HOTFIX - Fix Remaining Unicode in market_data_fetcher.py
==================================================================

Run this immediately if you're getting UnicodeEncodeError from line 70
of models/market_data_fetcher.py

This script will:
1. Check if the emoji is present on line 70
2. Replace it with [CACHE]
3. Verify the fix
"""

import os
import sys

def emergency_fix():
    file_path = "models/market_data_fetcher.py"
    
    if not os.path.exists(file_path):
        print("[ERROR] File not found. Are you in the ULTIMATE_v193_COMPLETE directory?")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check line 70 (index 69)
    if len(lines) < 70:
        print("[ERROR] File has fewer than 70 lines")
        sys.exit(1)
    
    original_line = lines[69]
    print(f"[CHECK] Line 70 current content:")
    print(f"  {original_line.strip()}")
    
    # Check if it needs fixing
    if '📦' in original_line:
        print("\n[!] FOUND UNICODE EMOJI - Fixing...")
        lines[69] = original_line.replace('📦', '[CACHE]')
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[OK] Fixed! New line 70:")
        print(f"  {lines[69].strip()}")
        print("\n[OK] File updated successfully")
        return True
    elif '[CACHE]' in original_line:
        print("\n[OK] Already fixed! No action needed.")
        return False
    else:
        print(f"\n[!] Unexpected content on line 70:")
        print(f"  Expected: logger.info('[CACHE] Using cached market data')")
        print(f"  Found: {original_line.strip()}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("EMERGENCY HOTFIX - market_data_fetcher.py Line 70")
    print("=" * 70)
    print()
    
    try:
        fixed = emergency_fix()
        
        if fixed:
            print()
            print("=" * 70)
            print("SUCCESS! Now run your pipeline again:")
            print("  python scripts\\run_us_full_pipeline.py --mode production")
            print("=" * 70)
        else:
            print()
            print("=" * 70)
            print("No changes made. Check if you need a full reinstall.")
            print("See: CLEAN_INSTALL_v193.11.5_INSTRUCTIONS.txt")
            print("=" * 70)
    except Exception as e:
        print(f"\n[ERROR] Failed to apply fix: {e}")
        print("You may need to edit the file manually:")
        print(f"  1. Open: models\\market_data_fetcher.py")
        print(f"  2. Go to line 70")
        print(f"  3. Replace 📦 with [CACHE]")
        print(f"  4. Save and retry")
        sys.exit(1)

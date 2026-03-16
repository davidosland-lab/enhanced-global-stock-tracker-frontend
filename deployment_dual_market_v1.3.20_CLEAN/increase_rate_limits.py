"""
Quick Fix: Increase Rate Limit Delays
Increases delays in all scanners to prevent Yahoo Finance rate limiting
"""

import re
from pathlib import Path

def update_rate_limit(file_path, new_delay=1.0):
    """Update rate limit delay in a scanner file"""
    
    if not Path(file_path).exists():
        print(f"⊘ {file_path} not found - skipping")
        return False
    
    print(f"\nUpdating {file_path}...")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = str(file_path) + '.before_rate_increase'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Backup created: {backup_path}")
    
    # Find and replace rate_limit_delay
    pattern = r'self\.rate_limit_delay = [0-9.]+  # .*'
    replacement = f'self.rate_limit_delay = {new_delay}  # Increased to avoid rate limiting'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print(f"  ✗ Could not find rate_limit_delay setting")
        return False
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ Updated rate_limit_delay: 0.5s → {new_delay}s")
    return True

def main():
    print("="*80)
    print("INCREASE RATE LIMIT DELAYS")
    print("="*80)
    print("\nThis will increase delays in all scanners to prevent rate limiting.")
    print("Current delay: 0.5s")
    print("New delay: 1.0s")
    print("\nThis will make pipelines ~50% slower but prevent 'Too Many Requests' errors.")
    print("\n" + "="*80)
    
    input("\nPress Enter to continue...")
    
    files = [
        'models/screening/stock_scanner.py',       # ASX scanner
        'models/screening/us_stock_scanner.py',    # US scanner  
    ]
    
    success_count = 0
    for file_path in files:
        if update_rate_limit(file_path, new_delay=1.0):
            success_count += 1
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Updated: {success_count}/{len(files)} files")
    
    if success_count > 0:
        print("\n✓ Rate limits increased!")
        print("\nNext steps:")
        print("  1. Re-run your pipeline")
        print("  2. Should see 'Rate limiting: 1.0s delay' in startup")
        print("  3. Pipeline will be slower but more reliable")
        print("\nIf you still get rate limited, increase to 1.5s or 2.0s")
    else:
        print("\n✗ No files were updated")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

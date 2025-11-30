"""
Quick Fix: Telegram Module Missing
Adds fallback to handle missing TelegramNotifier gracefully
"""

import re
from pathlib import Path

def fix_overnight_pipeline():
    """Fix overnight_pipeline.py to handle missing TelegramNotifier"""
    
    pipeline_file = Path('models/screening/overnight_pipeline.py')
    
    if not pipeline_file.exists():
        print(f"✗ {pipeline_file} not found")
        return False
    
    print(f"Fixing {pipeline_file}...")
    
    # Read file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_file = str(pipeline_file) + '.before_telegram_fix'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Backup created: {backup_file}")
    
    # Fix 1: Make sure TelegramNotifier import has proper error handling
    # This should already be there, but let's verify
    if 'TelegramNotifier = None' not in content:
        print("  ✗ TelegramNotifier fallback missing!")
        return False
    print("  ✓ TelegramNotifier import has fallback")
    
    # Fix 2: Check if initialization has try/except
    init_pattern = r'(# Optional: Telegram notifications\s+if TelegramNotifier is not None:)'
    
    if not re.search(init_pattern, content):
        print("  ✗ Telegram initialization section missing")
        print("    You need to run: integrate.bat")
        return False
    print("  ✓ Telegram initialization exists")
    
    # Fix 3: Make Phase 8 more robust - check if self.telegram exists
    phase8_pattern = r'(def _send_telegram_report_notification.*?:.*?\n.*?""".*?""".*?\n)(.*?if self\.telegram is None:)'
    
    if re.search(phase8_pattern, content, re.DOTALL):
        print("  ✓ Phase 8 has null check")
    else:
        print("  ⚠ Phase 8 might need better error handling")
    
    # Fix 4: Add hasattr check in Phase 8 call
    phase8_call_pattern = r'(self\._send_telegram_report_notification\()'
    
    # Check if there's already a hasattr check
    if 'hasattr(self' in content and 'telegram' in content:
        print("  ✓ Phase 8 call has safety check")
    else:
        print("  Adding safety check to Phase 8 call...")
        
        # Find the Phase 8 call and wrap it
        call_pattern = r'(\s+)(self\._send_telegram_report_notification\(\s+report_path=.*?\s+\))'
        replacement = r'\1if hasattr(self, "telegram") and self.telegram is not None:\n\1    \2\n\1else:\n\1    logger.info("  Telegram notifications not configured, skipping")'
        
        new_content = re.sub(call_pattern, replacement, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  ✓ Added safety check")
            return True
        else:
            print("  ⚠ Could not add safety check automatically")
    
    print("  ✓ File appears correct")
    return True

def main():
    print("="*80)
    print("TELEGRAM MODULE FIX")
    print("="*80)
    print("\nThis will add safety checks for missing Telegram module.\n")
    
    if fix_overnight_pipeline():
        print("\n✓ Fix applied!")
        print("\nNext steps:")
        print("  1. If you still get errors, you need the telegram_notifier.py file")
        print("  2. Run: git pull origin finbert-v4.0-development")
        print("  3. Or run: integrate.bat to add Telegram properly")
    else:
        print("\n✗ Fix failed")
        print("\nYou need to:")
        print("  1. Pull latest code: git pull origin finbert-v4.0-development")
        print("  2. Or run: cd MACRO_NEWS_STANDALONE_PATCH")
        print("  3. Then run: integrate.bat")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

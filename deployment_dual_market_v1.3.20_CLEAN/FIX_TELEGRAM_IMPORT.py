"""
Fix TelegramNotifier Import in Pipeline
========================================

This script fixes the 'TelegramNotifier not defined' error by ensuring
the variable is always defined, even if the import fails.
"""

from pathlib import Path
import shutil
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("FIX TELEGRAM IMPORT IN PIPELINE")
    print("="*80)
    
    # Target file
    pipeline_file = Path("models/screening/overnight_pipeline.py")
    
    if not pipeline_file.exists():
        print(f"\n❌ ERROR: File not found: {pipeline_file}")
        print("\nPlease run this from: C:\\Users\\david\\AATelS")
        input("\nPress Enter to exit...")
        return 1
    
    print(f"\n✓ Found: {pipeline_file}")
    
    # Backup
    print("\n[1/3] Creating backup...")
    backup_file = pipeline_file.parent / f"{pipeline_file.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(pipeline_file, backup_file)
    print(f"✓ Backup: {backup_file.name}")
    
    # Read content
    print("\n[2/3] Reading file...")
    content = pipeline_file.read_text(encoding='utf-8')
    
    # Find the import section
    old_import = '''# Telegram notification support
try:
    from ..notifications.telegram_notifier import TelegramNotifier
except ImportError:
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
    except ImportError:
        TelegramNotifier = None'''
    
    # New import with explicit initialization
    new_import = '''# Telegram notification support
TelegramNotifier = None  # Initialize to None first
try:
    from ..notifications.telegram_notifier import TelegramNotifier
except ImportError:
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
    except ImportError:
        TelegramNotifier = None  # Keep as None if import fails'''
    
    # Apply fix
    print("\n[3/3] Applying fix...")
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Import section updated")
    else:
        print("⚠️  Could not find exact import pattern")
        print("   Trying alternative fix...")
        
        # Alternative: Just add TelegramNotifier = None at the top of imports
        # Find the first "try:" after the docstring
        import_start = content.find('# Telegram notification support')
        if import_start > 0:
            # Insert initialization before the try block
            before = content[:import_start]
            after = content[import_start:]
            content = before + "TelegramNotifier = None  # Ensure it's always defined\n" + after
            print("✓ Added explicit initialization")
        else:
            print("✗ Could not apply fix automatically")
            input("\nPress Enter to exit...")
            return 1
    
    # Write fixed content
    pipeline_file.write_text(content, encoding='utf-8')
    print("✓ File updated")
    
    # Success
    print("\n" + "="*80)
    print("FIX APPLIED SUCCESSFULLY!")
    print("="*80)
    print("\nWhat was fixed:")
    print("  Added: TelegramNotifier = None")
    print("  This ensures the variable is always defined, even if import fails")
    print("\nYour pipeline should now work!")
    print("\nTest it:")
    print("  pipeline.bat")
    print("\n" + "="*80)
    
    input("\nPress Enter to exit...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        exit(1)

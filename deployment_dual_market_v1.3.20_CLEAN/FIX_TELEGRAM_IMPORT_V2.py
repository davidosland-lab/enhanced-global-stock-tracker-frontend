"""
Fix TelegramNotifier Import - Version 2
========================================

More aggressive fix that ensures TelegramNotifier is defined.
"""

from pathlib import Path
import shutil
from datetime import datetime
import re

def main():
    print("\n" + "="*80)
    print("FIX TELEGRAM IMPORT - VERSION 2")
    print("="*80)
    
    pipeline_file = Path("models/screening/overnight_pipeline.py")
    
    if not pipeline_file.exists():
        print(f"\n❌ File not found: {pipeline_file}")
        input("Press Enter...")
        return 1
    
    print(f"\n✓ Found: {pipeline_file}")
    
    # Backup
    print("\n[1/4] Creating backup...")
    backup = pipeline_file.parent / f"{pipeline_file.name}.backup_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(pipeline_file, backup)
    print(f"✓ Backup: {backup.name}")
    
    # Read content
    print("\n[2/4] Reading file...")
    content = pipeline_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Find the import section and check if TelegramNotifier = None exists
    print("\n[3/4] Analyzing imports...")
    telegram_import_line = -1
    telegram_init_exists = False
    
    for i, line in enumerate(lines):
        if 'TelegramNotifier = None' in line and not line.strip().startswith('#'):
            telegram_init_exists = True
            print(f"✓ Found initialization at line {i+1}")
        if '# Telegram notification support' in line:
            telegram_import_line = i
            print(f"✓ Found import section at line {i+1}")
    
    if telegram_init_exists:
        print("\n⚠️  TelegramNotifier = None already exists!")
        print("   The problem might be elsewhere.")
        print("\n   Let's check where TelegramNotifier is used...")
        
        for i, line in enumerate(lines):
            if 'if TelegramNotifier' in line or 'TelegramNotifier(' in line:
                print(f"   Line {i+1}: {line.strip()}")
        
        input("\nPress Enter to continue anyway...")
    
    # Apply fix - add initialization right after imports, before any usage
    print("\n[4/4] Applying fix...")
    
    # Strategy: Add TelegramNotifier = None at the TOP of the file, after imports
    # Find the end of all imports
    last_import_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            last_import_line = i
        elif line.strip().startswith('logger ='):
            last_import_line = i
            break
    
    # Check if we already added it
    if not telegram_init_exists:
        # Add right after the last import/logger definition
        insert_pos = last_import_line + 1
        
        # Add some blank lines and our initialization
        lines.insert(insert_pos, '')
        lines.insert(insert_pos + 1, '# Ensure TelegramNotifier is always defined (fix for import issues)')
        lines.insert(insert_pos + 2, 'TelegramNotifier = None')
        lines.insert(insert_pos + 3, '')
        
        print(f"✓ Added 'TelegramNotifier = None' at line {insert_pos + 3}")
    else:
        print("⚠️  Already exists, no changes made")
    
    # Also add it before the class definition as a safety
    class_def_line = -1
    for i, line in enumerate(lines):
        if 'class OvernightPipeline' in line or 'class Overnight' in line:
            class_def_line = i
            break
    
    if class_def_line > 0 and not telegram_init_exists:
        # Add before class
        lines.insert(class_def_line, '# Safety: Ensure TelegramNotifier exists')
        lines.insert(class_def_line + 1, 'if "TelegramNotifier" not in dir():')
        lines.insert(class_def_line + 2, '    TelegramNotifier = None')
        lines.insert(class_def_line + 3, '')
        print(f"✓ Added safety check before class at line {class_def_line + 1}")
    
    # Write back
    content = '\n'.join(lines)
    pipeline_file.write_text(content, encoding='utf-8')
    print("✓ File updated")
    
    # Verify
    print("\n[VERIFY] Checking if fix worked...")
    content = pipeline_file.read_text()
    if 'TelegramNotifier = None' in content:
        print("✓ TelegramNotifier = None is now in the file")
    else:
        print("✗ Something went wrong")
        input("\nPress Enter...")
        return 1
    
    print("\n" + "="*80)
    print("FIX APPLIED!")
    print("="*80)
    print("\nTest with:")
    print("  python DEBUG_PIPELINE_IMPORT.py")
    print("\nOr run pipeline:")
    print("  python models\\screening\\overnight_pipeline.py")
    print("\n" + "="*80)
    
    input("\nPress Enter...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter...")
        exit(1)

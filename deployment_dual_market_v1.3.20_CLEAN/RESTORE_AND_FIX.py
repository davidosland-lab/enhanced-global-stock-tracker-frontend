"""
Restore backup and apply correct fix
=====================================
"""

from pathlib import Path
import shutil
from datetime import datetime

print("\n" + "="*80)
print("RESTORE BACKUP AND APPLY CORRECT FIX")
print("="*80)

pipeline_file = Path("models/screening/overnight_pipeline.py")
pipeline_dir = pipeline_file.parent

# Find the most recent backup
backups = sorted(pipeline_dir.glob("overnight_pipeline.py.backup*"), reverse=True)

if not backups:
    print("\n❌ No backup files found!")
    print("Cannot restore. You'll need to manually fix the indentation.")
    input("\nPress Enter...")
    exit(1)

print(f"\nFound {len(backups)} backup(s)")
print(f"Most recent: {backups[0].name}")

# Restore the most recent backup
print("\n[1/3] Restoring backup...")
shutil.copy2(backups[0], pipeline_file)
print(f"✓ Restored from: {backups[0].name}")

# Now apply the fix CORRECTLY - only modify the import section
print("\n[2/3] Applying fix to import section...")

try:
    content = pipeline_file.read_text(encoding='utf-8')
except:
    content = pipeline_file.read_text(encoding='latin-1')

# Find the telegram import section and replace it
old_pattern = '''# Telegram notification support
try:
    from ..notifications.telegram_notifier import TelegramNotifier
except ImportError:
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
    except ImportError:
        TelegramNotifier = None'''

new_pattern = '''# Telegram notification support
TelegramNotifier = None  # Initialize first to prevent NameError
try:
    from ..notifications.telegram_notifier import TelegramNotifier
except ImportError:
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
    except ImportError:
        pass  # Already set to None above'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✓ Updated import section")
else:
    print("⚠️  Exact pattern not found")
    print("   Trying line-by-line approach...")
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Find the line with "# Telegram notification support"
        if '# Telegram notification support' in line:
            # Insert TelegramNotifier = None on the next line
            lines.insert(i + 1, 'TelegramNotifier = None  # Initialize first')
            print(f"✓ Inserted at line {i + 2}")
            break
    
    content = '\n'.join(lines)

# Write back
print("\n[3/3] Writing file...")
try:
    pipeline_file.write_text(content, encoding='utf-8')
except:
    pipeline_file.write_text(content, encoding='utf-8', errors='ignore')

print("✓ File written")

# Verify
print("\n[VERIFY] Testing import...")
try:
    # Quick syntax check
    import py_compile
    py_compile.compile(str(pipeline_file), doraise=True)
    print("✓ Python syntax is valid!")
except SyntaxError as e:
    print(f"✗ Syntax error: {e}")
    print("\nRestoring backup again...")
    shutil.copy2(backups[0], pipeline_file)
    print("✓ Restored backup")
    input("\nPress Enter...")
    exit(1)

print("\n" + "="*80)
print("FIX APPLIED SUCCESSFULLY!")
print("="*80)
print("\nThe fix:")
print("  Added 'TelegramNotifier = None' before the import try/except")
print("  This prevents NameError when import fails")
print("\nTest with:")
print("  python models\\screening\\overnight_pipeline.py")
print("\nOr:")
print("  python DEBUG_PIPELINE_IMPORT.py")
print("\n" + "="*80)

input("\nPress Enter...")

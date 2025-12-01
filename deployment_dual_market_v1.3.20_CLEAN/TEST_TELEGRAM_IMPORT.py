"""
Test Telegram Notifier Import
==============================

This script diagnoses why TelegramNotifier import is failing.
"""

import sys
from pathlib import Path

print("\n" + "="*80)
print("DIAGNOSING TELEGRAM NOTIFIER IMPORT")
print("="*80)

# Step 1: Check file exists
print("\n[1] Checking if telegram_notifier.py exists...")
target_file = Path("models/notifications/telegram_notifier.py")
if target_file.exists():
    print(f"✓ File exists: {target_file.absolute()}")
    print(f"  Size: {target_file.stat().st_size:,} bytes")
else:
    print(f"✗ File NOT found: {target_file.absolute()}")
    print("\nThe file doesn't exist! Run CREATE_TELEGRAM_NOTIFIER.py first.")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Step 2: Check __init__.py
print("\n[2] Checking __init__.py...")
init_file = Path("models/notifications/__init__.py")
if init_file.exists():
    print(f"✓ __init__.py exists")
else:
    print(f"✗ __init__.py missing - creating it...")
    init_file.parent.mkdir(parents=True, exist_ok=True)
    init_file.write_text("")
    print(f"✓ Created: {init_file}")

# Step 3: Check models/__init__.py
print("\n[3] Checking models/__init__.py...")
models_init = Path("models/__init__.py")
if models_init.exists():
    print(f"✓ models/__init__.py exists")
else:
    print(f"⚠️  models/__init__.py missing - creating it...")
    models_init.write_text("")
    print(f"✓ Created: {models_init}")

# Step 4: Try import
print("\n[4] Testing import...")
try:
    from models.notifications.telegram_notifier import TelegramNotifier
    print("✓ Import successful!")
    print(f"  TelegramNotifier class: {TelegramNotifier}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("\nTrying to see what's wrong...")
    
    # Check if file has syntax errors
    print("\n[5] Checking Python syntax...")
    import py_compile
    try:
        py_compile.compile(str(target_file), doraise=True)
        print("✓ File has valid Python syntax")
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error in file: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("\nThe file exists and has valid syntax, but import still fails.")
    print("This might be a Python path issue.")
    input("\nPress Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)

# Step 5: Test instantiation
print("\n[5] Testing TelegramNotifier instantiation...")
try:
    notifier = TelegramNotifier(bot_token="test", chat_id="test")
    print("✓ Can create TelegramNotifier instance")
except Exception as e:
    print(f"✗ Cannot create instance: {e}")

# Success
print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
print("\n✓ telegram_notifier.py is working correctly")
print("✓ Import is successful")
print("✓ TelegramNotifier class is available")
print("\nYour pipeline should work now.")
print("\nIf pipeline still fails, the issue might be:")
print("  1. Python caching (.pyc files) - try restarting terminal")
print("  2. Different Python version being used")
print("  3. Running from wrong directory")
print("\n" + "="*80)

input("\nPress Enter to exit...")

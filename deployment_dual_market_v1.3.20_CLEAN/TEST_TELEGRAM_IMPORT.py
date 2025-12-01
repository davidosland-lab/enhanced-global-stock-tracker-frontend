"""
Test Telegram Notifier Import
==============================

This script tests if telegram_notifier.py can be imported correctly.
"""

import sys
from pathlib import Path

print("\n" + "="*80)
print("TELEGRAM NOTIFIER IMPORT TEST")
print("="*80)

print(f"\nCurrent directory: {Path.cwd()}")
print(f"Python version: {sys.version}")

# Test 1: Check if file exists
print("\n[TEST 1] Checking if file exists...")
file_path = Path("models/notifications/telegram_notifier.py")
if file_path.exists():
    print(f"✓ File exists: {file_path}")
    print(f"  Size: {file_path.stat().st_size:,} bytes")
else:
    print(f"✗ File NOT found: {file_path}")
    print("\nExpected location:")
    print("  C:\\Users\\david\\AATelS\\models\\notifications\\telegram_notifier.py")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Test 2: Check __init__.py
print("\n[TEST 2] Checking __init__.py...")
init_path = Path("models/notifications/__init__.py")
if init_path.exists():
    print(f"✓ __init__.py exists")
else:
    print(f"⚠️  __init__.py missing - creating it...")
    init_path.write_text("")
    print(f"✓ Created: {init_path}")

# Test 3: Try importing
print("\n[TEST 3] Testing import...")
try:
    from models.notifications.telegram_notifier import TelegramNotifier
    print("✓ Import successful!")
    print(f"  TelegramNotifier class: {TelegramNotifier}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("\nTrying to read the file to check for syntax errors...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile it
        compile(content, str(file_path), 'exec')
        print("✓ File syntax is valid")
        print("\nBut import still failed. Possible reasons:")
        print("  1. Missing dependency (requests module)")
        print("  2. Python path issue")
        
    except SyntaxError as se:
        print(f"✗ Syntax error in file: {se}")
    
    input("\nPress Enter to exit...")
    sys.exit(1)

# Test 4: Try creating instance
print("\n[TEST 4] Testing class instantiation...")
try:
    notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
    print("✓ TelegramNotifier instance created")
    print(f"  Enabled: {notifier.enabled}")
except Exception as e:
    print(f"✗ Failed to create instance: {e}")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Test 5: Check requests module
print("\n[TEST 5] Checking dependencies...")
try:
    import requests
    print("✓ requests module available")
except ImportError:
    print("✗ requests module missing")
    print("\nInstall it with:")
    print("  pip install requests")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Success
print("\n" + "="*80)
print("ALL TESTS PASSED!")
print("="*80)
print("\n✓ telegram_notifier.py is working correctly")
print("✓ TelegramNotifier can be imported")
print("✓ All dependencies are available")
print("\nThe import should work in your pipeline.")
print("\nIf pipeline still fails, the issue might be:")
print("  1. Pipeline is running from a different directory")
print("  2. Python path is different when pipeline runs")
print("  3. Different Python environment/virtualenv")
print("\n" + "="*80)

input("\nPress Enter to exit...")

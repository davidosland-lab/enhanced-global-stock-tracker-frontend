"""
Test TelegramNotifier Installation
===================================

Quick test to verify telegram_notifier.py is installed correctly.
"""

import sys
from pathlib import Path

print("\n" + "="*80)
print("TESTING TELEGRAM NOTIFIER INSTALLATION")
print("="*80)

# Test 1: Import
print("\n[TEST 1] Importing TelegramNotifier...")
try:
    from models.notifications.telegram_notifier import TelegramNotifier
    print("✓ TelegramNotifier imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("\nPossible causes:")
    print("  1. File not in correct location")
    print("  2. Missing __init__.py files")
    print("  3. Python path issues")
    print("\nExpected location:")
    print("  C:\\Users\\david\\AATelS\\models\\notifications\\telegram_notifier.py")
    sys.exit(1)

# Test 2: Class instantiation
print("\n[TEST 2] Creating TelegramNotifier instance...")
try:
    # Create with dummy credentials (won't send anything)
    notifier = TelegramNotifier(
        bot_token="dummy_token",
        chat_id="dummy_chat_id"
    )
    print("✓ TelegramNotifier instance created")
except Exception as e:
    print(f"✗ Instantiation failed: {e}")
    sys.exit(1)

# Test 3: Check methods exist
print("\n[TEST 3] Checking required methods...")
required_methods = [
    'send_message',
    'send_document',
    'send_photo',
    'send_breakout_alert',
    'send_morning_report',
    'test_connection'
]

missing_methods = []
for method in required_methods:
    if hasattr(notifier, method):
        print(f"  ✓ {method}")
    else:
        print(f"  ✗ {method} MISSING")
        missing_methods.append(method)

if missing_methods:
    print(f"\n✗ Missing {len(missing_methods)} required methods")
    sys.exit(1)

# Test 4: Check configuration loading
print("\n[TEST 4] Checking configuration loading...")
config_path = Path("config/intraday_rescan_config.json")
if config_path.exists():
    import json
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        # Check for Telegram config
        telegram_config = None
        if 'notifications' in config and 'telegram' in config['notifications']:
            telegram_config = config['notifications']['telegram']
            print("  ✓ Found notifications.telegram section")
        elif 'alerts' in config and 'telegram' in config['alerts']:
            telegram_config = config['alerts']['telegram']
            print("  ✓ Found alerts.telegram section (legacy format)")
        
        if telegram_config:
            enabled = telegram_config.get('enabled', False)
            has_token = bool(telegram_config.get('bot_token'))
            has_chat = bool(telegram_config.get('chat_id'))
            
            print(f"    - Enabled: {enabled}")
            print(f"    - Bot token configured: {has_token}")
            print(f"    - Chat ID configured: {has_chat}")
            
            if not enabled:
                print("  ⚠ Telegram is disabled in config")
            elif not has_token or not has_chat:
                print("  ⚠ Telegram credentials incomplete")
            else:
                print("  ✓ Telegram fully configured")
        else:
            print("  ⚠ No Telegram configuration found")
            print("    (This is OK if you haven't set up Telegram yet)")
    
    except Exception as e:
        print(f"  ✗ Failed to load config: {e}")
else:
    print("  ⚠ Config file not found (this is normal if not set up yet)")

# Test 5: Check file location
print("\n[TEST 5] Verifying file location...")
expected_file = Path("models/notifications/telegram_notifier.py")
if expected_file.exists():
    file_size = expected_file.stat().st_size
    print(f"  ✓ File found: {expected_file}")
    print(f"    Size: {file_size:,} bytes")
    
    if file_size < 1000:
        print("  ⚠ File appears too small (possible incomplete installation)")
    else:
        print("  ✓ File size looks good")
else:
    print(f"  ✗ File not found: {expected_file}")
    sys.exit(1)

# Summary
print("\n" + "="*80)
print("INSTALLATION TEST COMPLETE")
print("="*80)
print("\n✓ TelegramNotifier is installed correctly")
print("✓ All required methods are available")
print("✓ Ready to use in overnight pipeline")
print("\nNext steps:")
print("  1. Configure Telegram credentials (if not done yet)")
print("  2. Run: pipeline.bat")
print("  3. Check Phase 8 for Telegram notifications")
print("\n" + "="*80 + "\n")

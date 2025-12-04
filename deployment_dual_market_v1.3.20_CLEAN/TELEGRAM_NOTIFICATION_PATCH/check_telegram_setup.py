#!/usr/bin/env python3
"""
Telegram Setup Diagnostic Tool
Checks if Telegram notifications are properly configured for morning reports
"""

import json
from pathlib import Path
import sys

def check_telegram_setup():
    """Check Telegram configuration and provide actionable feedback"""
    
    print("="*80)
    print("TELEGRAM MORNING REPORT - SETUP CHECKER")
    print("="*80)
    print()
    
    # Check 1: Config file exists
    config_path = Path('config/intraday_rescan_config.json')
    if not config_path.exists():
        print("❌ FAIL: Config file not found!")
        print(f"   Expected: {config_path.absolute()}")
        print()
        print("ACTION: Ensure you're running from the project root directory")
        return False
    
    print(f"✅ Config file found: {config_path}")
    
    # Check 2: Load config
    try:
        with open(config_path) as f:
            config = json.load(f)
        print("✅ Config file loaded successfully")
    except Exception as e:
        print(f"❌ FAIL: Could not load config: {e}")
        return False
    
    # Check 3: notifications section exists
    if 'notifications' not in config:
        print("❌ FAIL: 'notifications' section missing in config")
        print()
        print("ACTION: Add this to your config file:")
        print("""
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN_HERE",
      "chat_id": "YOUR_CHAT_ID_HERE"
    }
  }
""")
        return False
    
    print("✅ 'notifications' section found")
    
    # Check 4: notifications.telegram exists
    if 'telegram' not in config['notifications']:
        print("❌ FAIL: 'notifications.telegram' section missing")
        print()
        print("ACTION: Add 'telegram' to notifications section")
        return False
    
    print("✅ 'notifications.telegram' section found")
    
    telegram_cfg = config['notifications']['telegram']
    
    # Check 5: enabled flag
    enabled = telegram_cfg.get('enabled', False)
    if not enabled:
        print("⚠️  WARNING: Telegram notifications are DISABLED")
        print("   Current: enabled = false")
        print()
        print("ACTION: Set 'enabled': true in notifications.telegram")
    else:
        print("✅ Telegram notifications are ENABLED")
    
    # Check 6: bot_token
    bot_token = telegram_cfg.get('bot_token', '')
    if not bot_token:
        print("❌ FAIL: bot_token is empty!")
        print()
        print("ACTION: Get bot token from @BotFather on Telegram:")
        print("   1. Open Telegram, search for @BotFather")
        print("   2. Send /newbot and follow instructions")
        print("   3. Copy the bot token (looks like: 123456789:ABCdef...)")
        print("   4. Paste it into config: \"bot_token\": \"YOUR_TOKEN\"")
        return False
    
    print(f"✅ bot_token found: {bot_token[:20]}...{bot_token[-5:]}")
    
    # Check 7: chat_id
    chat_id = telegram_cfg.get('chat_id', '')
    if not chat_id:
        print("❌ FAIL: chat_id is empty!")
        print()
        print("ACTION: Get your chat ID:")
        print("   1. Start a chat with your bot on Telegram")
        print("   2. Send any message to the bot")
        print(f"   3. Visit: https://api.telegram.org/bot{bot_token}/getUpdates")
        print("   4. Find 'chat':{'id': YOUR_CHAT_ID}")
        print("   5. Paste it into config: \"chat_id\": \"YOUR_CHAT_ID\"")
        return False
    
    print(f"✅ chat_id found: {chat_id}")
    
    # Check 8: Test connection
    print()
    print("Testing Telegram connection...")
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
        
        telegram = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        result = telegram.send_message("✅ Test message from AATelS Setup Checker!")
        
        if result:
            print("✅ SUCCESS: Test message sent!")
            print("   Check your Telegram to confirm you received it.")
        else:
            print("❌ FAIL: Message send returned False")
            print("   Check your bot token and chat ID")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Connection test failed: {e}")
        print()
        print("Common issues:")
        print("   - Wrong bot token")
        print("   - Wrong chat ID")
        print("   - Bot not started (send /start to your bot)")
        print("   - Network/firewall blocking Telegram API")
        return False
    
    # All checks passed!
    print()
    print("="*80)
    print("✅ ALL CHECKS PASSED!")
    print("="*80)
    print()
    print("Your Telegram morning reports are ready! 🎉")
    print()
    print("Next steps:")
    print("1. Run test script: python test_morning_report_telegram.py")
    print("2. Run small pipeline: python models/screening/us_overnight_pipeline.py --stocks-per-sector 5")
    print("3. Check Telegram for morning report notification!")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = check_telegram_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print()
        print("="*80)
        print("UNEXPECTED ERROR")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

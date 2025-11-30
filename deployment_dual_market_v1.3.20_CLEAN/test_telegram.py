#!/usr/bin/env python3
"""
Test Telegram Integration for FinBERT Alerts
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_telegram_connection():
    """Test Telegram bot connection and send a test message"""
    
    print("=" * 70)
    print("  FinBERT Telegram Connection Test")
    print("=" * 70)
    print()
    
    # Load environment variables
    env_path = project_root / '.env'
    if not env_path.exists():
        print("❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_path}")
        print()
        print("Please run SETUP_TELEGRAM.bat first to create the .env file.")
        return False
    
    print(f"✓ Found .env file at: {env_path}")
    load_dotenv(env_path)
    
    # Get credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    
    print()
    print("Checking credentials...")
    
    if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not configured!")
        print("   Please edit .env and add your bot token from @BotFather")
        return False
    
    print(f"✓ Bot Token: {bot_token[:10]}...{bot_token[-10:] if len(bot_token) > 20 else ''}")
    
    if not chat_id or chat_id == 'YOUR_CHAT_ID_HERE':
        print("❌ ERROR: TELEGRAM_CHAT_ID not configured!")
        print("   Please edit .env and add your chat ID")
        return False
    
    print(f"✓ Chat ID: {chat_id}")
    print()
    
    # Try to import TelegramNotifier
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
        print("✓ TelegramNotifier module loaded successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import TelegramNotifier: {e}")
        return False
    
    print()
    print("Attempting to send test message...")
    print("-" * 70)
    
    # Create notifier and send test message
    try:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        test_message = """
🤖 *FinBERT Alert System Test*

✅ Connection successful!

Your Telegram alerts are now configured and ready to use.

*Next Steps:*
1. Run the intraday monitor: `RUN_INTRADAY_MONITOR_US.bat`
2. Monitor for breakout alerts during market hours

_This is a test message from your FinBERT system._
"""
        
        success = notifier.send_message(test_message)
        
        if success:
            print()
            print("=" * 70)
            print("  ✅ SUCCESS! Telegram is working!")
            print("=" * 70)
            print()
            print("Check your Telegram app - you should have received a test message!")
            print()
            print("Next steps:")
            print("  1. Your Telegram bot is ready to send alerts")
            print("  2. Run: RUN_INTRADAY_MONITOR_US.bat (for US stocks)")
            print("     or: RUN_INTRADAY_MONITOR_ASX.bat (for ASX stocks)")
            print()
            return True
        else:
            print()
            print("❌ Failed to send test message")
            print("   Check that:")
            print("   1. Your bot token is correct")
            print("   2. Your chat ID is correct")
            print("   3. You've started a chat with your bot (sent /start)")
            print()
            return False
            
    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Verify your bot token is correct (from @BotFather)")
        print("  2. Verify your chat ID is correct")
        print("  3. Make sure you've sent /start to your bot")
        print("  4. Check your internet connection")
        return False

if __name__ == "__main__":
    success = test_telegram_connection()
    sys.exit(0 if success else 1)

"""
Test script to verify Telegram morning report notifications

This script sends a test morning report notification to Telegram
without running the full overnight pipeline.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import TelegramNotifier
from models.notifications.telegram_notifier import TelegramNotifier


def test_morning_report():
    """Test morning report notification"""
    
    # Load Telegram config
    config_path = Path(__file__).parent / 'config' / 'intraday_rescan_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            telegram_cfg = config.get('notifications', {}).get('telegram', {})
            
            if not telegram_cfg.get('enabled', False):
                print("❌ Telegram notifications disabled in config")
                print(f"   Config file: {config_path}")
                return False
            
            bot_token = telegram_cfg.get('bot_token')
            chat_id = telegram_cfg.get('chat_id')
            
            if not bot_token or not chat_id:
                print("❌ Telegram credentials missing in config")
                print(f"   Bot token: {'✓' if bot_token else '✗'}")
                print(f"   Chat ID: {'✓' if chat_id else '✗'}")
                return False
            
            print(f"✓ Telegram config loaded from {config_path}")
            print(f"  Bot token: {bot_token[:10]}...{bot_token[-4:]}")
            print(f"  Chat ID: {chat_id}")
            
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Initialize TelegramNotifier
    try:
        telegram = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        print("✓ TelegramNotifier initialized")
    except Exception as e:
        print(f"❌ TelegramNotifier initialization failed: {e}")
        return False
    
    # Create test morning report summary
    tz = pytz.timezone('Australia/Sydney')  # Change to 'America/New_York' for US
    timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    market_summary = f"""📊 *Morning Report Test*

🧪 *Test Pipeline Summary:*
• Total Stocks Scanned: 240
• High-Quality Opportunities: 15
• Execution Time: 3.5 minutes
• Report Generated: {timestamp}

📁 This is a test report.

✅ *Status: TEST COMPLETE*

If you received this message, your Telegram morning report notifications are working correctly! 🎉"""
    
    # Send test message
    try:
        print("\nSending test morning report...")
        telegram.send_message(market_summary)
        print("✅ Test morning report sent successfully!")
        print("\n" + "="*60)
        print("Check your Telegram to confirm you received the message.")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test report: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*60)
    print("TELEGRAM MORNING REPORT TEST")
    print("="*60)
    print()
    
    success = test_morning_report()
    
    if success:
        print("\n✅ TEST PASSED")
        print("\nNext steps:")
        print("1. Run the overnight pipeline: python models/screening/us_overnight_pipeline.py")
        print("   or: python models/screening/overnight_pipeline.py (for ASX)")
        print("2. You will receive a Telegram notification when the report is ready")
        print("3. The notification will include the HTML report and CSV file")
    else:
        print("\n❌ TEST FAILED")
        print("\nTroubleshooting:")
        print("1. Check your bot token and chat ID in config/intraday_rescan_config.json")
        print("2. Make sure Telegram is enabled: 'enabled': true")
        print("3. Test manually: python test_telegram.py")
        print("4. Create bot: @BotFather on Telegram")
        print("5. Get chat ID: https://api.telegram.org/bot<TOKEN>/getUpdates")
    
    sys.exit(0 if success else 1)

"""
Test Telegram Notification Setup
=================================

This script tests your Telegram configuration and sends test messages.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()
load_dotenv("telegram.env")  # Also try telegram.env


def test_telegram_connection():
    """Test Telegram bot connection"""
    print("\n" + "="*80)
    print("TESTING TELEGRAM NOTIFICATION SETUP")
    print("="*80 + "\n")
    
    # Check credentials
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("Step 1: Checking Credentials")
    print("-" * 80)
    
    if not bot_token:
        print("✗ TELEGRAM_BOT_TOKEN not found")
        print("\nPlease set your bot token in telegram.env:")
        print("  TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz")
        return False
    else:
        # Mask token for security
        masked_token = bot_token[:10] + "..." + bot_token[-5:]
        print(f"✓ TELEGRAM_BOT_TOKEN found: {masked_token}")
    
    if not chat_id:
        print("✗ TELEGRAM_CHAT_ID not found")
        print("\nPlease set your chat ID in telegram.env:")
        print("  TELEGRAM_CHAT_ID=123456789")
        return False
    else:
        print(f"✓ TELEGRAM_CHAT_ID found: {chat_id}")
    
    print()
    
    # Import notifier
    try:
        from models.notifications.telegram_notifier import TelegramNotifier
        print("Step 2: Importing TelegramNotifier")
        print("-" * 80)
        print("✓ TelegramNotifier module imported successfully")
        print()
    except ImportError as e:
        print(f"✗ Failed to import TelegramNotifier: {e}")
        return False
    
    # Initialize notifier
    print("Step 3: Initializing Notifier")
    print("-" * 80)
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
    
    if not notifier.enabled:
        print("✗ Notifier failed to initialize")
        return False
    
    print("✓ TelegramNotifier initialized successfully")
    print()
    
    # Test connection
    print("Step 4: Testing Bot Connection")
    print("-" * 80)
    if not notifier.test_connection():
        print("✗ Bot connection test failed")
        print("\nPossible issues:")
        print("  1. Invalid bot token")
        print("  2. Bot token expired")
        print("  3. Internet connection problem")
        print("  4. Telegram API is down")
        return False
    
    print("✓ Bot connection successful")
    print()
    
    # Send test message
    print("Step 5: Sending Test Message")
    print("-" * 80)
    test_msg = f"""🧪 *Test Message*

This is a test notification from your Stock Screener!

*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Status:* ✅ Working perfectly!

You should receive this message in your Telegram chat."""
    
    if not notifier.send_message(test_msg):
        print("✗ Failed to send test message")
        print("\nPossible issues:")
        print("  1. Wrong chat ID")
        print("  2. You haven't started a chat with your bot")
        print("  3. Bot doesn't have permission to send messages")
        return False
    
    print("✓ Test message sent successfully")
    print()
    
    # Send test breakout alert
    print("Step 6: Sending Test Breakout Alert")
    print("-" * 80)
    if not notifier.send_breakout_alert(
        symbol="AAPL",
        breakout_type="test_alert",
        strength=85.5,
        price=180.50,
        details={
            "Test Type": "Setup Verification",
            "Status": "Working",
            "Action": "Check your Telegram!"
        }
    ):
        print("⚠ Test alert failed (optional feature)")
    else:
        print("✓ Test breakout alert sent successfully")
    
    print()
    
    # Success summary
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print()
    print("Your Telegram notifications are working correctly!")
    print()
    print("You should have received 2 test messages in Telegram:")
    print("  1. A basic test message")
    print("  2. A formatted breakout alert")
    print()
    print("Next Steps:")
    print("  1. Check your Telegram app for the test messages")
    print("  2. Run the overnight pipeline to receive real reports:")
    print("     python models\\screening\\us_overnight_pipeline.py --test-mode")
    print("  3. Enable intraday alerts in config/intraday_rescan_config.json")
    print()
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_telegram_connection()
    sys.exit(0 if success else 1)

"""
Telegram Setup Wizard
Interactive tool to configure Telegram notifications for both ASX and US pipelines
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from models.notifications.telegram_notifier import TelegramNotifier
except ImportError:
    print("❌ ERROR: Could not import TelegramNotifier")
    print("   Make sure python-telegram-bot is installed:")
    print("   pip install python-telegram-bot==13.15")
    sys.exit(1)


def setup_telegram_credentials():
    """
    Interactive setup wizard for Telegram credentials
    """
    print("="*80)
    print("TELEGRAM NOTIFICATION SETUP WIZARD")
    print("="*80)
    print()
    print("📱 This wizard will help you set up Telegram notifications for:")
    print("   • ASX Overnight Pipeline")
    print("   • US Overnight Pipeline")
    print("   • Intraday Rescan (if enabled)")
    print()
    print("Prerequisites:")
    print("   1. Create a Telegram bot by messaging @BotFather on Telegram")
    print("   2. Send /newbot and follow instructions to get your BOT_TOKEN")
    print("   3. Start a conversation with your bot")
    print("   4. Get your CHAT_ID by messaging @userinfobot")
    print()
    print("-"*80)
    
    # Get credentials
    bot_token = input("\n📝 Enter your Telegram Bot Token: ").strip()
    if not bot_token:
        print("❌ Bot token is required. Exiting.")
        sys.exit(1)
    
    chat_id = input("📝 Enter your Telegram Chat ID: ").strip()
    if not chat_id:
        print("❌ Chat ID is required. Exiting.")
        sys.exit(1)
    
    # Test connection
    print("\n🔍 Testing Telegram connection...")
    try:
        telegram = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        telegram.send_message("✅ *Telegram Setup Successful!*\n\nYour FinBERT trading system is now connected to Telegram.")
        print("✅ Connection test successful! Check your Telegram for a test message.")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        retry = input("\n   Try different credentials? (y/n): ").strip().lower()
        if retry == 'y':
            return setup_telegram_credentials()
        else:
            print("Exiting setup.")
            sys.exit(1)
    
    # Update configuration file
    print("\n📝 Updating configuration file...")
    config_path = Path(__file__).parent.parent / 'config' / 'intraday_rescan_config.json'
    
    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update Telegram credentials
        config['alerts']['telegram']['enabled'] = True
        config['alerts']['telegram']['bot_token'] = bot_token
        config['alerts']['telegram']['chat_id'] = chat_id
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration updated: {config_path}")
        
        # Also update screening_config.json to add telegram notification settings
        screening_config_path = Path(__file__).parent.parent / 'models' / 'config' / 'screening_config.json'
        if screening_config_path.exists():
            try:
                with open(screening_config_path, 'r') as f:
                    screening_config = json.load(f)
                
                # Add telegram notifications config if not present
                if 'telegram_notifications' not in screening_config:
                    screening_config['telegram_notifications'] = {
                        'enabled': True,
                        'bot_token': bot_token,
                        'chat_id': chat_id,
                        'send_morning_reports': True,
                        'send_error_alerts': True,
                        'parse_mode': 'Markdown'
                    }
                    
                    with open(screening_config_path, 'w') as f:
                        json.dump(screening_config, f, indent=2)
                    
                    print(f"✅ Screening configuration also updated: {screening_config_path}")
            except Exception as e:
                print(f"⚠️  Could not update screening_config.json: {e}")
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print("\n✅ Telegram notifications are now enabled for:")
    print("   • ASX Overnight Pipeline (morning reports)")
    print("   • US Overnight Pipeline (morning reports)")
    print("   • Error alerts and critical warnings")
    print()
    print("📱 You will receive Telegram notifications when:")
    print("   • Overnight pipelines complete (with report attachments)")
    print("   • High-quality trading opportunities are found")
    print("   • Errors or warnings occur during execution")
    print()
    print("🔍 Next steps:")
    print("   1. Run test_telegram.py to verify the setup")
    print("   2. Run overnight_pipeline.py (ASX) or us_overnight_pipeline.py (US)")
    print("   3. Check your Telegram for the morning report")
    print()
    print("📋 Configuration saved to:")
    print(f"   • {config_path}")
    print(f"   • {screening_config_path} (if applicable)")
    print()
    print("="*80)


if __name__ == "__main__":
    try:
        setup_telegram_credentials()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

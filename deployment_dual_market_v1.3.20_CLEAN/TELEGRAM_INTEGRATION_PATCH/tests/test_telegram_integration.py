"""
Test Telegram Integration
Comprehensive test suite for Telegram notifications in both pipelines
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from models.notifications.telegram_notifier import TelegramNotifier
    telegram_available = True
except ImportError:
    print("❌ TelegramNotifier not available")
    telegram_available = False


def load_telegram_config():
    """Load Telegram configuration from intraday_rescan_config.json"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'intraday_rescan_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        telegram_cfg = config.get('alerts', {}).get('telegram', {})
        
        if not telegram_cfg.get('enabled', False):
            print("❌ Telegram notifications are disabled in config")
            return None
        
        bot_token = telegram_cfg.get('bot_token')
        chat_id = telegram_cfg.get('chat_id')
        
        if not bot_token or not chat_id:
            print("❌ Bot token or chat ID not configured")
            print(f"   Config path: {config_path}")
            print("   Run setup_telegram.py to configure credentials")
            return None
        
        return {
            'bot_token': bot_token,
            'chat_id': chat_id,
            'parse_mode': telegram_cfg.get('parse_mode', 'Markdown')
        }
    
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None


def test_basic_message():
    """Test 1: Send a basic text message"""
    print("\n" + "="*80)
    print("TEST 1: Basic Text Message")
    print("="*80)
    
    if not telegram_available:
        print("❌ FAILED: TelegramNotifier module not available")
        return False
    
    config = load_telegram_config()
    if not config:
        print("❌ FAILED: Telegram not configured")
        return False
    
    try:
        telegram = TelegramNotifier(
            bot_token=config['bot_token'],
            chat_id=config['chat_id']
        )
        
        message = f"""🧪 *Test Message*

This is a test message from the Telegram integration test suite.

*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Test:* Basic text message
*Status:* ✅ PASSED"""
        
        telegram.send_message(message)
        print("✅ PASSED: Basic message sent successfully")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_asx_morning_report_notification():
    """Test 2: Simulate ASX morning report notification"""
    print("\n" + "="*80)
    print("TEST 2: ASX Morning Report Notification")
    print("="*80)
    
    if not telegram_available:
        print("❌ FAILED: TelegramNotifier module not available")
        return False
    
    config = load_telegram_config()
    if not config:
        print("❌ FAILED: Telegram not configured")
        return False
    
    try:
        telegram = TelegramNotifier(
            bot_token=config['bot_token'],
            chat_id=config['chat_id']
        )
        
        # Simulate ASX morning report
        market_summary = f"""🇦🇺 *ASX Market Morning Report*

📊 *Pipeline Summary:*
• Total Stocks Scanned: 240
• High-Quality Opportunities (≥70%): 12
• Execution Time: 8.5 minutes
• Report Generated: {datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z')}

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ *Pipeline Status: COMPLETE*

🧪 *This is a TEST notification*"""
        
        telegram.send_message(market_summary)
        print("✅ PASSED: ASX morning report notification sent")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_us_morning_report_notification():
    """Test 3: Simulate US morning report notification"""
    print("\n" + "="*80)
    print("TEST 3: US Morning Report Notification")
    print("="*80)
    
    if not telegram_available:
        print("❌ FAILED: TelegramNotifier module not available")
        return False
    
    config = load_telegram_config()
    if not config:
        print("❌ FAILED: Telegram not configured")
        return False
    
    try:
        telegram = TelegramNotifier(
            bot_token=config['bot_token'],
            chat_id=config['chat_id']
        )
        
        # Simulate US morning report
        market_summary = f"""🇺🇸 *US Market Morning Report*

📊 *Pipeline Summary:*
• Total Stocks Scanned: 240
• High-Quality Opportunities (≥70%): 15
• Execution Time: 10.2 minutes
• Report Generated: {datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d %H:%M:%S %Z')}

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ *Pipeline Status: COMPLETE*

🧪 *This is a TEST notification*"""
        
        telegram.send_message(market_summary)
        print("✅ PASSED: US morning report notification sent")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_error_alert():
    """Test 4: Send an error alert"""
    print("\n" + "="*80)
    print("TEST 4: Error Alert Notification")
    print("="*80)
    
    if not telegram_available:
        print("❌ FAILED: TelegramNotifier module not available")
        return False
    
    config = load_telegram_config()
    if not config:
        print("❌ FAILED: Telegram not configured")
        return False
    
    try:
        telegram = TelegramNotifier(
            bot_token=config['bot_token'],
            chat_id=config['chat_id']
        )
        
        error_message = f"""🚨 *Pipeline Error Alert*

*Pipeline:* US Overnight Pipeline
*Phase:* Stock Scanning
*Error:* Connection timeout to yfinance API

*Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Action Required:* Check network connection and retry

🧪 *This is a TEST error notification*"""
        
        telegram.send_message(error_message)
        print("✅ PASSED: Error alert sent successfully")
        return True
    
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Run all Telegram integration tests"""
    print("\n" + "="*80)
    print("TELEGRAM INTEGRATION TEST SUITE")
    print("="*80)
    print("\nTesting Telegram notifications for ASX and US pipelines...")
    print("Check your Telegram app for test messages.\n")
    
    results = {}
    
    # Test 1: Basic message
    results['basic_message'] = test_basic_message()
    
    # Test 2: ASX morning report
    results['asx_report'] = test_asx_morning_report_notification()
    
    # Test 3: US morning report
    results['us_report'] = test_us_morning_report_notification()
    
    # Test 4: Error alert
    results['error_alert'] = test_error_alert()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✅ All tests passed! Telegram integration is working correctly.")
        print("   Both ASX and US pipelines will send notifications.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("   Run setup_telegram.py to reconfigure credentials.")
    
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Telegram Notification Diagnostic Tool
Helps identify why Telegram notifications weren't sent after pipeline run
"""

import json
from pathlib import Path

print("="*80)
print("TELEGRAM NOTIFICATION DIAGNOSTIC")
print("="*80)

# Check 1: Configuration file
config_path = Path("config/intraday_rescan_config.json")
print(f"\n1. Checking configuration file: {config_path}")

if not config_path.exists():
    print("   ❌ Configuration file NOT FOUND")
    print("   → This is a critical error!")
else:
    print("   ✓ Configuration file exists")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check notifications.telegram section
    print("\n2. Checking 'notifications.telegram' section:")
    
    if 'notifications' not in config:
        print("   ❌ 'notifications' key missing in config")
    elif 'telegram' not in config['notifications']:
        print("   ❌ 'telegram' key missing in notifications section")
    else:
        tg_config = config['notifications']['telegram']
        print(f"   ✓ Section exists")
        print(f"   - enabled: {tg_config.get('enabled', False)}")
        print(f"   - bot_token: {'SET' if tg_config.get('bot_token') else 'MISSING'}")
        print(f"   - chat_id: {'SET' if tg_config.get('chat_id') else 'MISSING'}")
        
        if not tg_config.get('enabled'):
            print("\n   ⚠️ ISSUE FOUND: enabled = false")
            print("   → Telegram notifications are disabled")
        
        if not tg_config.get('bot_token'):
            print("\n   ⚠️ ISSUE FOUND: bot_token is empty")
            print("   → Cannot send messages without bot token")
        
        if not tg_config.get('chat_id'):
            print("\n   ⚠️ ISSUE FOUND: chat_id is empty")
            print("   → Cannot send messages without chat ID")

    # Check alerts.telegram section (legacy)
    print("\n3. Checking 'alerts.telegram' section (legacy):")
    
    if 'alerts' in config and 'telegram' in config['alerts']:
        alert_tg = config['alerts']['telegram']
        print(f"   ✓ Section exists")
        print(f"   - enabled: {alert_tg.get('enabled', False)}")
        print(f"   - bot_token: {'SET' if alert_tg.get('bot_token') else 'MISSING'}")
        print(f"   - chat_id: {'SET' if alert_tg.get('chat_id') else 'MISSING'}")
        
        # Suggest migration
        if alert_tg.get('bot_token') and not config['notifications']['telegram'].get('bot_token'):
            print("\n   💡 SUGGESTION: Copy credentials from 'alerts.telegram' to 'notifications.telegram'")
    else:
        print("   ℹ️ No alerts.telegram section (this is OK)")

print("\n" + "="*80)
print("WHAT TO CHECK IN YOUR PIPELINE LOGS")
print("="*80)
print("""
Search your most recent pipeline log file for these patterns:

1. At startup (Phase 0):
   ✓ Look for: "Telegram notifications enabled"
   ✗ Look for: "Telegram notifications disabled"

2. After Phase 7 (Report Generation):
   ✓ Look for: "Sending Telegram morning report notification..."
   ✓ Look for: "✓ Telegram report sent"
   ✗ Look for: "✗ Telegram notification failed"
   ℹ️ Look for: "Telegram notifications disabled, skipping"

3. Check the log file location:
   - logs/overnight_pipeline_YYYY-MM-DD.log
   - Or look for console output if run interactively

If you see "Telegram notifications disabled, skipping", then:
→ The self.telegram object was None during initialization
→ Check why the TelegramNotifier wasn't created
""")

print("\n" + "="*80)
print("QUICK FIX INSTRUCTIONS")
print("="*80)
print("""
If notifications.telegram is empty but alerts.telegram has values:

1. Open: config/intraday_rescan_config.json

2. Find the 'notifications' section

3. Update it to match your alerts.telegram:
   
   "notifications": {
       "telegram": {
           "enabled": true,
           "bot_token": "YOUR_BOT_TOKEN_FROM_ALERTS_SECTION",
           "chat_id": "YOUR_CHAT_ID_FROM_ALERTS_SECTION"
       }
   }

4. Save and run: python check_telegram_setup.py

5. Test with: python models/screening/overnight_pipeline.py --stocks-per-sector 5
""")

print("\n" + "="*80)

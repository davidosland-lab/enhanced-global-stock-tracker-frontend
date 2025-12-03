================================================================================
TELEGRAM NOTIFICATION SETUP PATCH
================================================================================

Version: 1.0.0
Date: 2024-12-03
For: Overnight Stock Screener v1.3.14

================================================================================
WHAT THIS PATCH DOES
================================================================================

Enables Telegram notifications for your stock screening system:

✓ Real-time breakout alerts (text messages)
✓ Morning/overnight reports (HTML/PDF attachments)
✓ Pipeline status notifications
✓ Government announcement/news alerts
✓ Event risk detection alerts

ZERO COST - No SMS fees, no email limitations!

================================================================================
QUICK SETUP (5-10 MINUTES)
================================================================================

1. EXTRACT THIS PATCH
   
   Extract TELEGRAM_SETUP_PATCH.zip to:
   C:\Users\david\AATelS\
   
   After extraction, you should have:
   C:\Users\david\AATelS\TELEGRAM_SETUP_PATCH\

2. RUN THE SETUP SCRIPT
   
   Open Command Prompt and run:
   
   cd C:\Users\david\AATelS
   TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
   
   The script will guide you through:
   - Creating a Telegram bot (via @BotFather)
   - Getting your bot token and chat ID
   - Configuring credentials
   - Testing the connection

3. DONE!
   
   Once setup is complete, you'll receive:
   - Morning reports when the pipeline runs
   - Real-time alerts for breakout opportunities
   - Status notifications

================================================================================
MANUAL SETUP (IF AUTOMATED SCRIPT FAILS)
================================================================================

Step 1: Create Telegram Bot
----------------------------
1. Open Telegram on your phone or desktop
2. Search for: @BotFather
3. Send command: /newbot
4. Choose a name: "My Stock Screener Bot"
5. Choose a username: "mystock_screener_bot"
6. BotFather will give you a TOKEN like:
   123456789:ABCdefGhIjKlMnOpQrStUvWxYz

Step 2: Get Chat ID
--------------------
1. Search for your bot in Telegram
2. Start a chat and send any message
3. Open this URL in browser (replace YOUR_TOKEN):
   
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   
4. Find "chat":{"id": in the response
   Your CHAT_ID is the number after "id":

Step 3: Configure Credentials
------------------------------
1. Open or create: C:\Users\david\AATelS\telegram.env
2. Add these lines (with your actual values):
   
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
   TELEGRAM_CHAT_ID=123456789

Step 4: Update Config Files
----------------------------
1. Open: models\config\screening_config.json
2. Add the telegram_notifications section from:
   TELEGRAM_SETUP_PATCH\config\screening_config_telegram_patch.json
3. Update bot_token and chat_id with your credentials

4. Open: config\intraday_rescan_config.json
5. Find the "telegram" section under "alerts"
6. Set enabled: true
7. Add your bot_token and chat_id

Step 5: Test Setup
------------------
Run the test script:

cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py

You should receive test messages in Telegram.

================================================================================
WHAT YOU'LL RECEIVE
================================================================================

Morning Reports
---------------
When the overnight pipeline completes, you'll receive:
- Full HTML report as a document
- Summary of top opportunities
- Number of stocks scanned
- Execution time

Example:
  📊 US Morning Report
  2024-12-03 07:30
  
  Stocks Scanned: 240
  Top Picks: 10
  Scan Time: 45.2 min

Real-time Alerts
----------------
During intraday scanning, you'll get breakout alerts:

  🚀 BREAKOUT ALERT
  
  Symbol: AAPL
  Type: Price Breakout Up
  Strength: 85.3/100
  Price: $180.50
  Time: 14:35:20
  
  Details:
  • Change from prev: 3.20
  • Volume multiple: 2.10
  • Momentum 15m: 4.50

Pipeline Notifications
----------------------
- ✓ Pipeline started
- ✓ Pipeline completed successfully
- ✗ Pipeline errors
- 📈 High opportunity detected

================================================================================
CONFIGURATION OPTIONS
================================================================================

Edit: models\config\screening_config.json

telegram_notifications:
  enabled: true/false               - Enable/disable all Telegram
  
  morning_report:
    send_report: true/false         - Send morning report
    send_as_document: true/false    - Attach as file vs text
    include_summary: true/false     - Include summary stats
  
  alerts:
    enabled: true/false             - Enable breakout alerts
    min_alert_strength: 70.0        - Minimum strength to alert
    max_alerts_per_hour: 20         - Rate limit
    alert_types: [...]              - Types of alerts to send
    
    quiet_hours:
      enabled: true/false           - Enable quiet hours
      start: "23:00"                - No alerts after this time
      end: "07:00"                  - Resume alerts at this time
  
  notifications:
    pipeline_start: true/false      - Notify when pipeline starts
    pipeline_complete: true/false   - Notify when pipeline completes
    pipeline_errors: true/false     - Notify on errors
    high_opportunity_detected: true - Alert on high-score stocks

================================================================================
TESTING YOUR SETUP
================================================================================

Test 1: Test Script
-------------------
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py

Expected:
- ✓ Credentials found
- ✓ TelegramNotifier imported
- ✓ Bot connection successful
- ✓ Test messages sent
- Check Telegram for messages

Test 2: Manual Test
--------------------
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; n = TelegramNotifier(); n.send_message('Hello from Python!')"

Expected:
- Message appears in Telegram

Test 3: Pipeline Test
----------------------
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --test-mode

Expected:
- Pipeline runs with 5 test stocks
- Morning report sent to Telegram
- Check Telegram for report document

================================================================================
TROUBLESHOOTING
================================================================================

Issue: "Telegram not configured"
---------------------------------
Solution:
1. Check telegram.env exists in C:\Users\david\AATelS\
2. Verify it contains TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
3. Check there are no quotes around the values
4. Restart your Python script

Issue: "Bot connection failed"
-------------------------------
Solution:
1. Verify your bot token is correct
2. Check internet connection
3. Try the bot token in your browser:
   https://api.telegram.org/botYOUR_TOKEN/getMe
4. If it returns an error, the token is invalid

Issue: "Failed to send message"
--------------------------------
Solution:
1. Verify your chat ID is correct
2. Make sure you started a chat with your bot
3. Send any message to your bot in Telegram
4. Try getting updates to verify chat ID:
   https://api.telegram.org/botYOUR_TOKEN/getUpdates

Issue: "Wrong chat ID"
----------------------
Solution:
1. Open: https://api.telegram.org/botYOUR_TOKEN/getUpdates
2. Look for "chat":{"id":XXXXXXX
3. Your chat ID is the number after "id":
4. Common mistake: Using username instead of numeric ID

Issue: "Module not found"
-------------------------
Solution:
1. Verify you're running from C:\Users\david\AATelS\
2. Check models\notifications\telegram_notifier.py exists
3. Make sure Python can find the module:
   cd C:\Users\david\AATelS
   python -c "import models.notifications.telegram_notifier"

================================================================================
FILES IN THIS PATCH
================================================================================

TELEGRAM_SETUP_PATCH/
├── SETUP_TELEGRAM.bat                    - Automated setup script
├── README.txt                            - This file
├── update_config.py                      - Config updater script
├── config/
│   └── screening_config_telegram_patch.json  - Sample config
├── tests/
│   └── test_telegram.py                  - Test script
└── docs/
    └── TELEGRAM_INTEGRATION_GUIDE.md     - Detailed guide

================================================================================
SUPPORT & DOCUMENTATION
================================================================================

For detailed documentation, see:
- TELEGRAM_SETUP_PATCH\docs\TELEGRAM_INTEGRATION_GUIDE.md
- models\notifications\telegram_notifier.py (module docstring)

For issues:
- Check logs: logs/screening/
- Run test: TELEGRAM_SETUP_PATCH\tests\test_telegram.py
- Verify config: models\config\screening_config.json

================================================================================
SECURITY NOTES
================================================================================

⚠️ IMPORTANT:
- Never commit telegram.env to Git
- Keep your bot token private
- Don't share your chat ID
- Bot tokens in config files should use environment variables

Recommended:
- Use .env files for credentials
- Add telegram.env to .gitignore
- Rotate bot token if exposed

================================================================================
NEXT STEPS AFTER SETUP
================================================================================

1. ✓ Telegram setup complete

2. Run a test pipeline:
   cd C:\Users\david\AATelS
   python models\screening\us_overnight_pipeline.py --test-mode

3. Enable intraday alerts (optional):
   Edit: config\intraday_rescan_config.json
   Set: alerts.telegram.enabled = true

4. Customize notification settings:
   Edit: models\config\screening_config.json
   Configure quiet hours, alert thresholds, etc.

5. Schedule overnight pipeline:
   - Use Windows Task Scheduler
   - Or run manually each night

================================================================================

Ready to get started? Run:

cd C:\Users\david\AATelS
TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat

================================================================================

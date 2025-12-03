# 🧪 HOW TO TEST TELEGRAM SETUP

## Quick Test Checklist

After running `TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat`, verify everything works:

---

## ✅ Test 1: Verify Credentials (10 seconds)

### Check telegram.env exists and has credentials

```batch
cd C:\Users\david\AATelS
type telegram.env
```

**Expected Output**:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
TELEGRAM_CHAT_ID=123456789
```

**✓ PASS**: Both lines present with your actual values  
**✗ FAIL**: File missing or empty → Re-run setup

---

## ✅ Test 2: Verify Config Files Updated (20 seconds)

### Check screening_config.json has Telegram section

```batch
cd C:\Users\david\AATelS
findstr /C:"telegram_notifications" models\config\screening_config.json
```

**Expected Output**:
```
  "telegram_notifications": {
```

**✓ PASS**: Found "telegram_notifications"  
**✗ FAIL**: Not found → Manually add config section

---

## ✅ Test 3: Run Test Script (30 seconds)

### This is the main test - sends actual messages to Telegram

```batch
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

**Expected Output**:
```
================================================================================
TESTING TELEGRAM NOTIFICATION SETUP
================================================================================

Step 1: Checking Credentials
------------------------------------------------------------------------
✓ TELEGRAM_BOT_TOKEN found: 123456789:...xyz
✓ TELEGRAM_CHAT_ID found: 123456789

Step 2: Importing TelegramNotifier
------------------------------------------------------------------------
✓ TelegramNotifier module imported successfully

Step 3: Initializing Notifier
------------------------------------------------------------------------
✓ TelegramNotifier initialized successfully

Step 4: Testing Bot Connection
------------------------------------------------------------------------
✓ Bot connection successful

Step 5: Sending Test Message
------------------------------------------------------------------------
✓ Test message sent successfully

Step 6: Sending Test Breakout Alert
------------------------------------------------------------------------
✓ Test breakout alert sent successfully

================================================================================
✅ ALL TESTS PASSED!
================================================================================

Check your Telegram chat for the test messages!
```

**✓ PASS**: All 6 steps show ✓  
**✗ FAIL**: Any step shows ✗ → See troubleshooting below

**ALSO CHECK**: Your Telegram app should have 2 new messages!

---

## ✅ Test 4: Manual Message Test (10 seconds)

### Send a quick test message from Python

```batch
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; TelegramNotifier().send_message('✅ Manual test successful!')"
```

**Expected**: Message appears in Telegram immediately

**✓ PASS**: Message received in Telegram  
**✗ FAIL**: No message → Check credentials

---

## ✅ Test 5: Pipeline Test with Telegram (5-10 minutes)

### Run the full pipeline in test mode to verify reports are sent

```batch
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --test-mode --max-stocks 5
```

**Expected at the end**:
```
Sending morning report via Telegram...
✓ Telegram report sent successfully
```

**AND** in Telegram:
```
📊 US Morning Report
[Date/Time]

Stocks Scanned: 5
Top Picks: [X]
Scan Time: [X] min

[HTML report attached]
```

**✓ PASS**: Report received in Telegram  
**✗ FAIL**: No report → Check configuration

---

## 🔍 What to Check in Telegram App

After running tests, you should see:

### Message 1: Basic Test Message
```
🧪 Test Message

This is a test notification from your Stock Screener.

Time: [timestamp]
Status: ✅ Working perfectly!
```

### Message 2: Breakout Alert
```
🚀 BREAKOUT ALERT

Symbol: AAPL
Type: Test Alert
Strength: 85.5/100
Price: $180.50
Time: [timestamp]

Details:
• Test Type: Setup Verification
• Status: Working
• Action: Check your Telegram!
```

### Message 3: Manual Test (if you ran Test 4)
```
✅ Manual test successful!
```

### Message 4: Morning Report (if you ran Test 5)
```
📊 US Morning Report
[timestamp]

Stocks Scanned: 5
Top Picks: [number]
Scan Time: [X] min

[Document: us_morning_report_[date].html]
```

---

## ❌ Troubleshooting Failed Tests

### Test Failed: "TELEGRAM_BOT_TOKEN not found"

**Problem**: Credentials not set

**Fix**:
```batch
cd C:\Users\david\AATelS
# Create telegram.env manually
notepad telegram.env
```

Add these lines (with YOUR values):
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
TELEGRAM_CHAT_ID=123456789
```

Save and re-test.

---

### Test Failed: "Bot connection failed"

**Problem**: Invalid bot token

**Fix**:
1. Test your bot token in browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```
2. Should return JSON with bot info
3. If error, token is wrong - get new token from @BotFather
4. Update `telegram.env` with correct token

---

### Test Failed: "Failed to send message"

**Problem**: Wrong chat ID or haven't started chat with bot

**Fix**:
1. Open Telegram
2. Search for your bot (the username you created)
3. Start chat with bot
4. Send ANY message (e.g., "Hello")
5. Get your chat ID:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
6. Look for: `"chat":{"id":123456789`
7. Update `telegram.env` with correct chat ID
8. Re-test

---

### Test Failed: "Module not found: telegram_notifier"

**Problem**: Running from wrong directory

**Fix**:
```batch
cd C:\Users\david\AATelS
# Verify you're in the right place
dir models\notifications\telegram_notifier.py
# Should find the file

# If found, re-run test from this directory
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

---

### Test Failed: Python import error

**Problem**: Missing dependencies

**Fix**:
```batch
cd C:\Users\david\AATelS
pip install requests python-dotenv
# Re-test
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

---

## ✅ Success Indicators

### You know it's working when:

1. ✓ **test_telegram.py shows**: "✅ ALL TESTS PASSED!"
2. ✓ **Telegram app has**: 2 test messages
3. ✓ **Manual test**: Message arrives instantly
4. ✓ **Pipeline test**: Morning report received
5. ✓ **telegram.env**: Contains bot token and chat ID
6. ✓ **Config files**: Have telegram_notifications section

---

## 📊 Quick Status Check

Run this to see overall status:

```batch
cd C:\Users\david\AATelS
python -c "import os; from dotenv import load_dotenv; load_dotenv('telegram.env'); print('Bot Token:', 'FOUND' if os.getenv('TELEGRAM_BOT_TOKEN') else 'MISSING'); print('Chat ID:', 'FOUND' if os.getenv('TELEGRAM_CHAT_ID') else 'MISSING'); from models.notifications.telegram_notifier import TelegramNotifier; n=TelegramNotifier(); print('Telegram Enabled:', n.enabled); print('Connection Test:', 'PASS' if n.test_connection() else 'FAIL')"
```

**Expected Output**:
```
Bot Token: FOUND
Chat ID: FOUND
Telegram Enabled: True
Connection Test: PASS
```

---

## 🎯 Complete Test Sequence

Run all tests in order:

```batch
cd C:\Users\david\AATelS

REM Test 1: Check credentials
type telegram.env

REM Test 2: Check config
findstr /C:"telegram_notifications" models\config\screening_config.json

REM Test 3: Run test script (MAIN TEST)
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py

REM Test 4: Manual message
python -c "from models.notifications.telegram_notifier import TelegramNotifier; TelegramNotifier().send_message('All tests complete!')"

REM Test 5: Check Telegram app for 3 messages
```

**If all pass**: Telegram is ready! 🎉  
**If any fail**: See troubleshooting section above

---

## 📱 What Happens Next

Once tests pass:

### Automatic Notifications
- **Morning reports**: Sent after overnight pipeline completes
- **Breakout alerts**: Sent during intraday scanning
- **Pipeline status**: Start/complete/error notifications

### Manual Testing Anytime
```batch
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

### Run Pipeline to Get Real Report
```batch
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --test-mode
# Wait 10-15 minutes
# Check Telegram for morning report
```

---

## 🔧 Advanced: Test Individual Features

### Test Just Connection
```python
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; n=TelegramNotifier(); print('Connected!' if n.test_connection() else 'Failed')"
```

### Test Send Message
```python
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; TelegramNotifier().send_message('Test 123')"
```

### Test Send Document
```python
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; import pathlib; report=list(pathlib.Path('reports/morning_reports').glob('*.html'))[0]; TelegramNotifier().send_document(report)"
```

### Test Breakout Alert
```python
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; TelegramNotifier().send_breakout_alert('TEST', 'test_alert', 99.0, 100.0, {'Status': 'Testing'})"
```

---

## ✨ Summary

**Quick Test** (30 seconds):
```batch
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

**Expected**: "✅ ALL TESTS PASSED!" + 2 messages in Telegram

**Complete Test** (10 minutes):
```batch
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --test-mode
```

**Expected**: Morning report document in Telegram

---

**If you see test messages in Telegram, setup is complete!** 🎉📱

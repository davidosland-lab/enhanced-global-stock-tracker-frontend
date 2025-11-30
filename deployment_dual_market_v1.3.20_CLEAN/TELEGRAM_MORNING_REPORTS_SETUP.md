# Telegram Morning Report Notifications - Setup Guide

## ✅ Current Status

**Question**: "After I run the overnight pipeline is it supposed to send a message through telegram?"

**Answer**: **YES!** 🎉 The code is ready, but Telegram needs configuration.

---

## 🔍 **What I Found**

Your configuration file has:
```json
"alerts": {
  "telegram": {
    "enabled": true,
    "bot_token": "",    ❌ EMPTY
    "chat_id": ""       ❌ EMPTY
  }
}

"notifications": {
  "telegram": {}        ❌ EMPTY SECTION
}
```

**Problem**: The overnight pipelines look for `notifications.telegram`, but this section is empty.

---

## 📱 **What You Should Receive**

When properly configured, after each overnight pipeline run you'll get:

### **Telegram Message:**
```
🇺🇸 US Market Morning Report

📊 Pipeline Summary:
• Total Stocks Scanned: 240
• High-Quality Opportunities (≥70%): 18
• Execution Time: 12.3 minutes
• Report Generated: 2025-11-30 06:30:15 EST

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ Pipeline Status: COMPLETE
```

### **Attachments:**
- 📄 **HTML Report** (formatted report with charts)
- 📊 **CSV File** (data export for Excel)

---

## 🛠️ **How to Fix This**

### **Option A: Quick Copy (5 minutes)** ✅ RECOMMENDED

If you already have working Telegram credentials in `alerts.telegram`, just copy them:

#### **Step 1: Edit Config File**
```bash
cd C:\Users\david\AATelS
notepad config\intraday_rescan_config.json
```

#### **Step 2: Find the `notifications` Section**

Look for this:
```json
"notifications": {
  "telegram": {}
}
```

#### **Step 3: Copy Your Credentials**

Find your `bot_token` and `chat_id` from the `alerts` section and copy them to `notifications`:

**Change FROM:**
```json
"notifications": {
  "telegram": {}
}
```

**Change TO:**
```json
"notifications": {
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE"
  }
}
```

**IMPORTANT**: Copy the EXACT same `bot_token` and `chat_id` from your `alerts.telegram` section!

#### **Step 4: Save and Test**
```bash
python test_morning_report_telegram.py
```

You should receive a test message!

---

### **Option B: Fresh Setup (10 minutes)**

If you don't have Telegram credentials yet:

#### **Step 1: Create Telegram Bot**

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name: "AATelS Trading Bot"
4. Choose a username: "aatels_trading_bot" (must end with `_bot`)
5. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### **Step 2: Get Your Chat ID**

1. Start a chat with your new bot (click the link from BotFather)
2. Send any message to the bot (e.g., "Hello")
3. Visit this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":` in the response
5. **Copy your chat ID** (a number like `123456789` or `-123456789`)

#### **Step 3: Update Config File**

```bash
cd C:\Users\david\AATelS
notepad config\intraday_rescan_config.json
```

Update the `notifications` section:
```json
"notifications": {
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789"
  }
}
```

#### **Step 4: Test**
```bash
python test_morning_report_telegram.py
```

---

## 🧪 **Testing**

### **Test 1: Telegram Notifier**
```bash
cd C:\Users\david\AATelS

python -c "
from models.notifications.telegram_notifier import TelegramNotifier
import json

# Load config
with open('config/intraday_rescan_config.json') as f:
    config = json.load(f)

telegram_cfg = config['notifications']['telegram']
bot_token = telegram_cfg['bot_token']
chat_id = telegram_cfg['chat_id']

print(f'Bot Token: {bot_token[:20]}...')
print(f'Chat ID: {chat_id}')

# Initialize and test
telegram = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
result = telegram.send_message('✅ Test message from AATelS Pipeline!')
print(f'Result: {result}')
"
```

**Expected**: You receive a message in Telegram!

### **Test 2: Morning Report Test Script**
```bash
python test_morning_report_telegram.py
```

**Expected**: You receive a formatted morning report message!

### **Test 3: Full Pipeline**
```bash
# Run with small dataset first
python models/screening/us_overnight_pipeline.py --stocks-per-sector 5
```

**Expected**: Pipeline completes and you receive the morning report!

---

## 📋 **Checklist**

Before running the overnight pipeline:

- [ ] ✅ `notifications.telegram` section exists in config
- [ ] ✅ `enabled: true` is set
- [ ] ✅ `bot_token` is filled in (from BotFather)
- [ ] ✅ `chat_id` is filled in (from getUpdates)
- [ ] ✅ Test message received successfully
- [ ] ✅ Bot has been started with `/start` command

---

## 🔧 **Troubleshooting**

### **Problem: No message received**

**Check 1: Config loaded correctly**
```bash
python -c "
import json
config = json.load(open('config/intraday_rescan_config.json'))
print('Telegram enabled:', config['notifications']['telegram']['enabled'])
print('Bot token present:', bool(config['notifications']['telegram']['bot_token']))
print('Chat ID present:', bool(config['notifications']['telegram']['chat_id']))
"
```

**Check 2: Pipeline initialization**
Look for this log message when pipeline starts:
```
✓ Telegram notifications enabled
```

If you see:
```
Telegram notifications disabled (missing credentials)
```
→ Your bot_token or chat_id is missing/empty

**Check 3: Bot token valid**
Visit:
```
https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

Should return bot information (not error).

**Check 4: Started bot**
Make sure you've sent `/start` to your bot in Telegram!

---

## 📂 **Config File Location**

```
C:\Users\david\AATelS\config\intraday_rescan_config.json
```

**Full structure needed:**
```json
{
  "intraday_rescan": { ... },
  "incremental_scanning": { ... },
  "breakout_detection": { ... },
  "alerts": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    }
  },
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN",
      "chat_id": "YOUR_CHAT_ID"
    }
  },
  "tracking": { ... },
  "performance": { ... },
  "logging": { ... }
}
```

**Note**: Both `alerts.telegram` and `notifications.telegram` should have the same credentials.

---

## ✅ **Expected Pipeline Behavior**

### **With Telegram Configured:**
1. Pipeline runs (Phase 1-6)
2. Report generated
3. 📱 **Telegram notification sent** with summary + attachments
4. Log shows: `✓ Telegram report sent: ...`

### **Without Telegram Configured:**
1. Pipeline runs (Phase 1-6)
2. Report generated
3. Log shows: `Telegram notifications disabled, skipping`
4. ❌ No Telegram message

---

## 🎯 **Quick Fix Summary**

**If you have bot_token and chat_id already:**
1. Edit `config/intraday_rescan_config.json`
2. Find `"notifications": { "telegram": {} }`
3. Add your credentials:
   ```json
   "notifications": {
     "telegram": {
       "enabled": true,
       "bot_token": "PASTE_YOUR_TOKEN",
       "chat_id": "PASTE_YOUR_CHAT_ID"
     }
   }
   ```
4. Save and test: `python test_morning_report_telegram.py`
5. Run pipeline: `python models/screening/us_overnight_pipeline.py`

**Done!** 🎉

---

## 📱 **Example Notification**

When working, you'll receive messages like:

```
🇺🇸 US Market Morning Report

📊 Pipeline Summary:
• Total Stocks Scanned: 240
• High-Quality Opportunities (≥70%): 18
• Execution Time: 12.3 minutes
• Report Generated: 2025-11-30 06:30:15 EST

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ Pipeline Status: COMPLETE
```

Plus 2 file attachments:
- 📄 `us_morning_report_20251130_063015.html`
- 📊 `us_screening_results_20251130.csv`

---

## 🚀 **Next Steps**

1. **Configure Telegram** (5-10 minutes)
2. **Test with small pipeline** (`--stocks-per-sector 5`)
3. **Verify message received**
4. **Run full overnight pipeline**
5. **Enjoy automated morning reports!** 🎉

---

**Status**: Telegram integration is ✅ **READY** in code, just needs ⚙️ **CONFIGURATION**  
**Time to setup**: 5-10 minutes  
**Benefit**: Automatic morning reports with HTML + CSV attachments!

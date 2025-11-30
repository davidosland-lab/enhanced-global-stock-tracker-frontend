# 🔧 Fix Telegram Notifications on Local Machine

## ❌ Problem Identified

Your pipeline ran successfully, but **NO Telegram notification** was sent because:

1. ❌ The `notifications.telegram` section is **MISSING** from your config
2. ❌ The `alerts.telegram` section exists but has **empty credentials**

## 🎯 Root Cause

The overnight pipeline looks for Telegram configuration in **two places** (in order):

```python
# Location 1 (PREFERRED): notifications.telegram
config['notifications']['telegram']

# Location 2 (FALLBACK): alerts.telegram  
config['alerts']['telegram']
```

**Your config is missing BOTH of these!**

---

## ✅ Solution: Add Telegram Configuration

### Step 1: Locate Your Config File

On your local machine:
```
C:\Users\david\AATelS\config\intraday_rescan_config.json
```

### Step 2: Add the Missing Section

Open the file and add this **notifications** section (if it doesn't exist):

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN_HERE",
      "chat_id": "YOUR_CHAT_ID_HERE"
    }
  },
  
  "alerts": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN_HERE",
      "chat_id": "YOUR_CHAT_ID_HERE"
    }
  }
}
```

**Where to get these values:**
- `bot_token`: From when you created the bot with @BotFather (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
- `chat_id`: Your Telegram user ID (looks like `123456789` or `-1001234567890` for groups)

---

## 🔍 Finding Your Telegram Credentials

### If You Already Have a Bot:

1. Open Telegram and search for **@BotFather**
2. Send: `/mybots`
3. Select your bot
4. Click **API Token** to reveal your `bot_token`

### If You Need Your Chat ID:

1. Open Telegram and search for **@userinfobot**
2. Send: `/start`
3. The bot will reply with your `chat_id`

### If You Don't Have a Bot Yet:

See the full setup guide: `TELEGRAM_MORNING_REPORTS_SETUP.md`

---

## ✅ Verification Steps

After updating the config:

### 1. Test the Configuration

```bash
cd C:\Users\david\AATelS
python check_telegram_setup.py
```

**Expected output:**
```
✅ Configuration Check:
   ✓ bot_token is configured
   ✓ chat_id is configured
   ✓ Telegram notifier initialized successfully

✅ Connection Test:
   ✓ Successfully connected to Telegram API
   ✓ Bot info retrieved: YourBotName
```

### 2. Run a Quick Test Pipeline

```bash
python models/screening/overnight_pipeline.py --stocks-per-sector 5
```

**Look for these log messages:**

✅ **At startup:**
```
✓ Telegram notifications enabled
Bot: YourBotName
Chat ID: 123456789
```

✅ **After Phase 7:**
```
================================================================================
PHASE 8: TELEGRAM NOTIFICATIONS
================================================================================
Sending Telegram morning report notification...
✓ Telegram report sent: 2025-11-30_market_report.html
✓ CSV file sent: 2025-11-30_screening_results.csv
```

### 3. Check Your Telegram

You should receive:
- 📱 A message with the pipeline summary
- 📄 HTML report attachment
- 📊 CSV file attachment

---

## 🚨 Troubleshooting

### Issue: "bot_token is invalid"
- ✅ Check you copied the FULL token (no spaces)
- ✅ Token should look like: `1234567890:ABCdef...`
- ✅ Generate a new token from @BotFather if needed

### Issue: "chat_id is invalid"
- ✅ Check you copied the correct ID from @userinfobot
- ✅ Make sure it's a number (not text)
- ✅ Can be positive (`123456789`) or negative (`-1001234567890`)

### Issue: Still no notifications
1. Check the log file: `logs/overnight_pipeline_YYYY-MM-DD.log`
2. Search for "Telegram"
3. Look for error messages

### Issue: "Telegram notifications disabled, skipping"
- The config wasn't loaded correctly
- Run `check_telegram_setup.py` to diagnose
- Make sure you saved the JSON file properly

---

## 📝 Example Config

Here's a complete working example:

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "7891234567:AAF5Qdx8vDe_kWxYzAbCdEfGhIjKlMnOpQr",
      "chat_id": "987654321"
    }
  },
  
  "alerts": {
    "telegram": {
      "enabled": true,
      "bot_token": "7891234567:AAF5Qdx8vDe_kWxYzAbCdEfGhIjKlMnOpQr",
      "chat_id": "987654321",
      "alert_on_signal": true,
      "min_confidence": 70
    }
  },
  
  "lstm": {
    "enabled": true,
    "model_count": 100
  }
}
```

**Note:** Replace the bot_token and chat_id with YOUR actual values!

---

## ⏱️ When Will I Receive Notifications?

**Telegram notifications are sent at the END of the pipeline:**

1. ✅ After all stocks are scanned (Phase 2)
2. ✅ After predictions are generated (Phase 3)
3. ✅ After AI scoring is complete (Phase 5)
4. ✅ After LSTM training finishes (Phase 6)
5. ✅ After reports are generated (Phase 7)
6. **📱 THEN: Telegram notification sent (Phase 8)**

**Total pipeline time:** ~10-15 minutes

---

## 🎯 Quick Action Checklist

- [ ] Open `C:\Users\david\AATelS\config\intraday_rescan_config.json`
- [ ] Add or update `notifications.telegram` section
- [ ] Insert your `bot_token` (from @BotFather)
- [ ] Insert your `chat_id` (from @userinfobot)
- [ ] Set `enabled: true`
- [ ] Save the file
- [ ] Run `python check_telegram_setup.py`
- [ ] Verify ✓ marks appear
- [ ] Run test pipeline: `python models/screening/overnight_pipeline.py --stocks-per-sector 5`
- [ ] Check Telegram for notification (~5 min later)

---

## 📚 Additional Resources

- **Full Setup Guide:** `TELEGRAM_MORNING_REPORTS_SETUP.md`
- **Diagnostic Tool:** `check_telegram_setup.py`
- **Phase 2 Fix:** `PHASE_2_VALIDATION_FIX_COMPLETE.md`

---

## ❓ Need Help?

If you're still having issues:

1. Run: `python check_telegram_setup.py` and share the output
2. Check: `logs/overnight_pipeline_YYYY-MM-DD.log` and search for "Telegram"
3. Verify: The config file has proper JSON syntax (no trailing commas, matching brackets)

**The pipeline completed successfully - you just need to add the Telegram credentials to receive the notifications!**

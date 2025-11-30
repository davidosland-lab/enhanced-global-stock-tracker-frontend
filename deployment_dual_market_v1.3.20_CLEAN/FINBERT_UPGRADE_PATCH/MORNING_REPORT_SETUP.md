# Morning Report Telegram Notifications Setup

## Overview

The FinBERT overnight pipelines (US & ASX) now automatically send morning report notifications via Telegram when they complete. You'll receive:

- 📊 **Summary message** with key statistics
- 📄 **HTML report** with charts and analysis
- 📊 **CSV file** for Excel analysis

---

## Setup Steps

### 1. Create Telegram Bot (if not already done)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Provide a name (e.g., "FinBERT Reports")
4. Provide a username (e.g., "finbert_reports_bot")
5. **Save the bot token** (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Start a chat with your new bot (send `/start`)
2. Open this URL in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"from":{"id":987654321...}` in the JSON response
4. **Save the chat ID** (the number after `"id":`)

### 3. Configure FinBERT

Edit `config/intraday_rescan_config.json`:

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN_HERE",
      "chat_id": "YOUR_CHAT_ID_HERE",
      "parse_mode": "Markdown",
      "disable_notification": false
    }
  }
}
```

**Important:** Replace `YOUR_BOT_TOKEN_HERE` and `YOUR_CHAT_ID_HERE` with your actual values.

### 4. Test the Setup

Run the test script:

```bash
cd C:\Users\david\AATelS
python test_morning_report_telegram.py
```

You should receive a test message in Telegram. If you do, morning report notifications are ready!

---

## Running the Overnight Pipelines

### US Market Pipeline

```bash
cd C:\Users\david\AATelS
python models/screening/us_overnight_pipeline.py
```

**When to run:** After US market close (after 4:00 PM ET)

### ASX Market Pipeline

```bash
cd C:\Users\david\AATelS
python models/screening/overnight_pipeline.py
```

**When to run:** After ASX market close (after 4:00 PM AEST)

---

## What You'll Receive

### 1. Summary Message

Example:
```
🇺🇸 US Market Morning Report

📊 Pipeline Summary:
• Total Stocks Scanned: 240
• High-Quality Opportunities (≥70%): 18
• Execution Time: 12.3 minutes
• Report Generated: 2025-11-30 05:30:15 EST

📁 Report files generated:
• HTML Report (with charts)
• CSV Export (for Excel)
• Pipeline Results (JSON)

✅ Pipeline Status: COMPLETE
```

### 2. HTML Report

- Attached as a document
- Open in browser for full charts and analysis
- Includes candlestick charts, sentiment analysis, opportunity rankings

### 3. CSV File

- Attached as a separate document
- Open in Excel for sorting, filtering, custom analysis
- Contains all stock data and predictions

---

## Troubleshooting

### No Telegram Message Received

**Check 1: Config file**
```bash
# Open config file and verify:
notepad config\intraday_rescan_config.json

# Ensure:
# - "enabled": true
# - bot_token is filled in
# - chat_id is filled in
```

**Check 2: Test manually**
```bash
python test_telegram.py
```

**Check 3: Pipeline logs**
```bash
# Check for Telegram initialization in pipeline output
# Look for:
# ✓ Telegram notifications enabled
# ...
# PHASE 8: TELEGRAM NOTIFICATIONS
# ✓ Telegram report sent
```

### Telegram Module Not Found

If you see "Telegram notifications disabled (module not available)":

```bash
pip install requests
```

### Bot Token / Chat ID Issues

- **Invalid token:** Create a new bot with @BotFather
- **Wrong chat ID:** Make sure you messaged your bot first, then get updates
- **Quotes in config:** Use double quotes: `"bot_token": "1234..."`, not `'bot_token': '1234...'`

---

## Scheduled Automation

### Windows Task Scheduler (Recommended)

1. Open **Task Scheduler**
2. Create Task → **General Tab:**
   - Name: "FinBERT US Morning Report"
   - Run whether user is logged on or not
   
3. **Triggers Tab:**
   - New → Daily at 5:00 AM (after US market close)
   
4. **Actions Tab:**
   - Action: Start a program
   - Program: `python`
   - Arguments: `models/screening/us_overnight_pipeline.py`
   - Start in: `C:\Users\david\AATelS`

5. Repeat for ASX pipeline (schedule for 5:00 PM AEST)

### Batch Files (Simple)

**US Pipeline:**
```batch
@echo off
cd C:\Users\david\AATelS
python models/screening/us_overnight_pipeline.py
pause
```

**ASX Pipeline:**
```batch
@echo off
cd C:\Users\david\AATelS
python models/screening/overnight_pipeline.py
pause
```

---

## Configuration Options

In `config/intraday_rescan_config.json`:

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,              // Enable/disable Telegram notifications
      "bot_token": "YOUR_TOKEN",    // Your Telegram bot token
      "chat_id": "YOUR_CHAT_ID",    // Your Telegram chat ID
      "parse_mode": "Markdown",     // Message formatting (Markdown/HTML)
      "disable_notification": false // true = silent notifications
    }
  }
}
```

**Silent Notifications:**
Set `"disable_notification": true` to receive notifications without sound/vibration.

---

## Report File Locations

After each pipeline run, reports are saved locally:

**US Reports:**
```
reports/us/
  ├── us_morning_report_YYYYMMDD_HHMMSS.html
  ├── us_screening_YYYYMMDD_HHMMSS.csv
  └── pipeline_state/
      └── YYYY-MM-DD_us_pipeline_state.json
```

**ASX Reports:**
```
reports/asx/
  ├── morning_report_YYYYMMDD_HHMMSS.html
  ├── asx_screening_YYYYMMDD_HHMMSS.csv
  └── pipeline_state/
      └── YYYY-MM-DD_pipeline_state.json
```

---

## Integration Status

✅ **US Overnight Pipeline** - Telegram integrated
✅ **ASX Overnight Pipeline** - Telegram integrated
✅ **Intraday Alerts** - Already working (tested)
✅ **Morning Reports** - Ready for testing

---

## Support

If you encounter issues:

1. Run `python test_morning_report_telegram.py` to verify setup
2. Check pipeline logs for error messages
3. Verify config file syntax (valid JSON)
4. Test with `python test_telegram.py` for basic connectivity

---

## Next Steps

1. ✅ Test with `python test_morning_report_telegram.py`
2. ⏱️ Run a full pipeline (US or ASX) to receive actual morning report
3. 📱 Verify you receive the Telegram notification with attachments
4. ⚙️ Set up scheduled automation (Task Scheduler or cron)
5. 🎯 Customize notification settings if needed

**Your morning reports will now arrive automatically via Telegram!** 📊📱

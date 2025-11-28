# Telegram Integration Setup Guide

## 📱 Overview

Telegram integration provides:
- **Real-time breakout alerts** - Instant notifications when signals are detected
- **Morning/overnight reports** - Daily HTML report attachments
- **Summary notifications** - Quick text summaries of scan results
- **Zero cost** - Telegram bot API is completely free

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Your Telegram Bot

1. **Open Telegram** on your phone or desktop

2. **Search for BotFather** - Official bot for creating new bots

3. **Send `/newbot`** command

4. **Follow the prompts**:
   - Choose a name for your bot (e.g., "My Stock Screener")
   - Choose a username (must end in 'bot', e.g., "mystockscreener_bot")

5. **Save your bot token** - You'll receive something like:
   ```
   123456789:AA...your_bot_token_here
   ```
   ⚠️ Keep this token secret!

---

### Step 2: Get Your Chat ID

1. **Start a chat with your bot**:
   - Click the link provided by BotFather
   - Or search for your bot username
   - Send `/start` to your bot

2. **Get updates from Telegram API**:
   - Open this URL in your browser (replace `<YOUR_BOT_TOKEN>` with your actual token):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

3. **Find your chat ID**:
   - Look for: `"chat":{"id":123456789,...}`
   - The number `123456789` is your **chat ID**
   
   Example response:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "message_id": 1,
         "from": {...},
         "chat": {
           "id": 123456789,  <-- This is your CHAT ID
           "first_name": "Your Name",
           "type": "private"
         },
         "text": "/start"
       }
     }]
   }
   ```

---

### Step 3: Add Credentials to .env File

1. **Create .env file** in the project root (if it doesn't exist):
   ```bash
   # Copy from example
   cp .env.example .env
   ```

2. **Edit .env** and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:AA...your_actual_bot_token
   TELEGRAM_CHAT_ID=123456789
   ```

3. **Save the file**

---

### Step 4: Enable Telegram in Configuration

Edit `config/intraday_rescan_config.json`:

```json
{
  "alerts": {
    "telegram": {
      "enabled": true,
      "bot_token": "",
      "chat_id": "",
      "parse_mode": "Markdown",
      "disable_notification": false
    }
  }
}
```

**Note**: If `bot_token` and `chat_id` are empty in the config, the system will automatically use values from `.env`.

---

### Step 5: Test Your Setup

Run the test script:

```bash
python models/notifications/telegram_notifier.py
```

**Expected output**:
```
TESTING TELEGRAM NOTIFIER
===========================
--- Testing Connection ---
✓ Connection successful

--- Testing Text Message ---
✓ Text message sent

--- Testing Breakout Alert ---
✓ Breakout alert sent

TEST COMPLETE
Check your Telegram chat for the test messages!
```

**Check your Telegram** - You should receive 2 test messages!

---

## 📊 Usage Examples

### 1. Intraday Breakout Alerts

When you run intraday monitoring, Telegram alerts are sent automatically:

```bash
# Start US market monitoring
RUN_INTRADAY_MONITOR_US.bat
```

You'll receive alerts like:
```
🚀 BREAKOUT ALERT

Symbol: AAPL
Type: Price Breakout Up
Strength: 85.3/100
Price: $180.50
Time: 14:25:30

Details:
• change_from_prev: 3.20
• volume_multiple: 2.10
• momentum_15m: 4.50
```

---

### 2. Morning Report Attachments

Add to your overnight pipeline (Python):

```python
from models.notifications.report_sender import ReportSender

# At the end of your pipeline
sender = ReportSender()
sender.send_morning_report(
    report_path="reports/overnight_us_report.html",
    market="US",
    pipeline_results={
        'total_stocks': 240,
        'top_opportunities': 15,
        'execution_time_minutes': 45.2
    }
)
```

You'll receive:
- 📊 **Attachment**: HTML report file (tap to open in browser)
- 📝 **Caption**: Summary with key metrics

---

### 3. Quick Summary Notifications

Send text-only summaries:

```python
from models.notifications.report_sender import ReportSender

sender = ReportSender()
sender.send_summary_notification(
    market="US",
    summary={
        'stocks_scanned': 240,
        'top_opportunities': 15,
        'execution_time': 45.2,
        'sentiment_label': 'Bullish',
        'market_regime': 'Bull Market'
    }
)
```

---

## ⚙️ Configuration Options

### Telegram Settings in `config/intraday_rescan_config.json`

```json
{
  "alerts": {
    "alert_threshold": 70.0,  // Min strength to send alerts
    "max_alerts_per_hour": 20,  // Prevent alert spam
    
    "telegram": {
      "enabled": true,
      "bot_token": "",  // Leave empty to use .env
      "chat_id": "",  // Leave empty to use .env
      "parse_mode": "Markdown",  // or "HTML" or null
      "disable_notification": false  // true for silent notifications
    }
  }
}
```

---

## 🔒 Security Best Practices

### Protecting Your Bot Token

✅ **DO**:
- Keep `.env` file in `.gitignore` (already configured)
- Use environment variables for credentials
- Revoke token if accidentally exposed (via @BotFather)

❌ **DON'T**:
- Commit `.env` file to Git
- Share bot token publicly
- Hardcode credentials in source code

### Revoking a Compromised Token

If your token is exposed:
1. Open @BotFather in Telegram
2. Send `/mybots`
3. Select your bot
4. Click "API Token" → "Revoke current token"
5. Get new token and update `.env`

---

## 🛠️ Troubleshooting

### Issue: "Telegram not configured" Error

**Cause**: Missing or incorrect credentials

**Solution**:
1. Check `.env` file exists and has correct format:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:AA...
   TELEGRAM_CHAT_ID=123456789
   ```
2. Verify no extra spaces or quotes
3. Restart application to reload `.env`

---

### Issue: "Failed to send Telegram message"

**Cause**: Bot token invalid or chat ID wrong

**Solution**:
1. Test connection:
   ```python
   python -c "
   from models.notifications.telegram_notifier import TelegramNotifier
   notifier = TelegramNotifier()
   print(notifier.test_connection())
   "
   ```
2. Verify bot token hasn't been revoked
3. Confirm chat ID by getting updates again:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```

---

### Issue: Chat ID Not Found in getUpdates

**Cause**: No messages sent to bot yet

**Solution**:
1. Send `/start` to your bot in Telegram
2. Send any other message (e.g., "Hello")
3. Check getUpdates URL again
4. The most recent message will have your chat ID

---

### Issue: Bot Not Responding

**Cause**: Bot not started or token revoked

**Solution**:
1. Ensure you sent `/start` to the bot
2. Check if bot exists: Send `/mybots` to @BotFather
3. Verify token is active (test connection script)

---

## 📈 Advanced Features

### Group/Channel Notifications

To send alerts to a group or channel:

1. **Add bot to group/channel**
2. **Make bot an admin** (for channels)
3. **Get group/channel ID**:
   - Send a message in the group/channel
   - Visit getUpdates URL
   - Look for negative chat ID (e.g., `-1001234567890`)
4. **Update TELEGRAM_CHAT_ID** in `.env` with the negative ID

---

### Silent Notifications

For non-urgent alerts, use silent mode:

```json
{
  "telegram": {
    "disable_notification": true
  }
}
```

This sends messages without sound/vibration.

---

### HTML Formatting

Use HTML instead of Markdown:

```json
{
  "telegram": {
    "parse_mode": "HTML"
  }
}
```

Supported HTML tags:
- `<b>bold</b>`
- `<i>italic</i>`
- `<code>monospace</code>`
- `<a href="url">link</a>`

---

## 📱 Mobile Setup

### iOS

1. Install Telegram from App Store
2. Follow setup steps above
3. Enable notifications in iOS Settings → Telegram

### Android

1. Install Telegram from Play Store
2. Follow setup steps above
3. Enable notifications in Settings → Apps → Telegram

---

## 💡 Tips & Best Practices

### For Day Traders

✅ **Enable alerts**:
```json
{
  "alerts": {
    "alert_threshold": 75.0,  // Higher threshold = fewer alerts
    "telegram": {
      "enabled": true,
      "disable_notification": false  // Keep sound on
    }
  }
}
```

### For Swing Traders

✅ **Morning reports only**:
```json
{
  "alerts": {
    "telegram": {
      "enabled": true,
      "disable_notification": true  // Silent mode
    }
  }
}
```

### Alert Management

- **Start conservative**: Use higher `alert_threshold` (e.g., 75-80)
- **Adjust based on noise**: Lower if missing opportunities, raise if too many alerts
- **Use max_alerts_per_hour**: Prevents notification fatigue
- **Silent mode at night**: Set `disable_notification: true`

---

## 📚 API Documentation

### TelegramNotifier Methods

```python
from models.notifications.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

# Send text message
notifier.send_message("Hello from Stock Screener!")

# Send document (HTML, PDF, CSV, etc.)
notifier.send_document("reports/morning_report.html", caption="Morning Report")

# Send photo/image
notifier.send_photo("charts/spy_chart.png", caption="SPY Daily Chart")

# Send formatted breakout alert
notifier.send_breakout_alert(
    symbol="AAPL",
    breakout_type="price_breakout_up",
    strength=85.3,
    price=180.50,
    details={"momentum": 4.5}
)

# Test connection
if notifier.test_connection():
    print("Telegram configured correctly!")
```

---

### ReportSender Methods

```python
from models.notifications.report_sender import ReportSender

sender = ReportSender()

# Send morning report with HTML attachment
sender.send_morning_report(
    report_path="reports/us_report.html",
    market="US",
    pipeline_results=results
)

# Send text summary only
sender.send_summary_notification(
    market="US",
    summary={'stocks_scanned': 240, 'top_opportunities': 15}
)

# Send both US and ASX reports
sender.send_dual_market_summary(
    us_report_path="reports/us_report.html",
    asx_report_path="reports/asx_report.html",
    us_summary=us_results,
    asx_summary=asx_results
)
```

---

## 🆘 Support

### Getting Help

1. **Test scripts**: Run the test functions to diagnose issues
2. **Check logs**: Look for error messages in console output
3. **Verify credentials**: Double-check `.env` file
4. **Bot issues**: Use @BotFather to manage your bot

### Additional Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **BotFather Commands**: https://core.telegram.org/bots#botfather
- **Telegram Support**: https://telegram.org/support

---

## ✅ Checklist

Use this checklist to verify your setup:

- [ ] Created bot via @BotFather
- [ ] Saved bot token
- [ ] Sent /start to bot
- [ ] Retrieved chat ID from getUpdates
- [ ] Added credentials to .env file
- [ ] Enabled Telegram in config
- [ ] Ran test script successfully
- [ ] Received test messages in Telegram
- [ ] Configured alert thresholds
- [ ] (Optional) Added bot to group/channel

---

**Telegram integration is now complete! You'll receive real-time alerts and daily reports directly on your phone.** 📱🚀

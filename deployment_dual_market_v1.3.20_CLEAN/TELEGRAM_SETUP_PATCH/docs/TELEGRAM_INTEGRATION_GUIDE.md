# Telegram Integration Guide

## Overview

This guide explains how to integrate Telegram notifications into your Overnight Stock Screener system. Telegram provides:

- **Zero Cost**: Free notifications (no SMS/email fees)
- **Real-time**: Instant delivery to your phone
- **Rich Media**: Send reports, charts, and formatted alerts
- **Reliable**: 99.9% uptime, works worldwide
- **Secure**: End-to-end encrypted communication

## Features

### 1. Morning/Overnight Reports
- **What**: Complete HTML report sent as a document
- **When**: After overnight pipeline completes (typically 7:00 AM)
- **Contains**: Top opportunities, technical analysis, sentiment scores
- **Format**: HTML file you can open in browser

### 2. Real-time Breakout Alerts
- **What**: Instant notifications when high-probability opportunities detected
- **When**: During intraday scanning (market hours)
- **Contains**: Symbol, breakout type, strength, price, key metrics
- **Format**: Formatted text with emojis and markdown

### 3. Pipeline Status Notifications
- **What**: Updates on pipeline execution
- **When**: Pipeline start, completion, or errors
- **Contains**: Status, duration, stock count
- **Format**: Short status messages

### 4. News Sentiment Alerts
- **What**: Notifications for significant news sentiment changes
- **When**: Major news events detected
- **Contains**: Symbol, sentiment direction, confidence, key headlines
- **Format**: Formatted text with article links

## Setup Instructions

### Step 1: Create Your Telegram Bot

1. Open Telegram on your phone or desktop
2. Search for `@BotFather`
3. Start a conversation and send: `/newbot`
4. Follow the prompts:
   - **Name**: "My Stock Screener Bot" (can be anything)
   - **Username**: "mystock_screener_bot" (must end in 'bot')
5. BotFather will respond with your bot token:
   ```
   123456789:ABCdefGhIjKlMnOpQrStUvWxYz
   ```
   ⚠️ **Save this token** - you'll need it!

### Step 2: Get Your Chat ID

1. Search for your bot in Telegram (use the username you created)
2. Start a chat with your bot
3. Send any message (e.g., "Hello")
4. Open this URL in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
   Example:
   ```
   https://api.telegram.org/bot123456789:ABCdefGhIjKlMnOpQrStUvWxYz/getUpdates
   ```
5. Look for this in the response:
   ```json
   "chat":{"id":123456789,"first_name":"Your Name",...}
   ```
   The number after `"id":` is your **chat ID** (e.g., `123456789`)

### Step 3: Configure Credentials

**Option A: Use the automated script (recommended)**

```batch
cd C:\Users\david\AATelS
TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
```

The script will prompt for your bot token and chat ID, then configure everything automatically.

**Option B: Manual configuration**

1. Create or edit `telegram.env` in `C:\Users\david\AATelS\`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjKlMnOpQrStUvWxYz
   TELEGRAM_CHAT_ID=123456789
   ```

2. Update `models\config\screening_config.json`, add this section:
   ```json
   "telegram_notifications": {
     "enabled": true,
     "bot_token": "",
     "chat_id": "",
     "parse_mode": "Markdown",
     "morning_report": {
       "send_report": true,
       "send_as_document": true,
       "include_summary": true
     },
     "alerts": {
       "enabled": true,
       "min_alert_strength": 70.0,
       "max_alerts_per_hour": 20,
       "alert_types": ["breakout", "high_score", "news_sentiment"],
       "quiet_hours": {
         "enabled": false,
         "start": "23:00",
         "end": "07:00"
       }
     },
     "notifications": {
       "pipeline_start": true,
       "pipeline_complete": true,
       "pipeline_errors": true,
       "model_training_complete": false,
       "high_opportunity_detected": true
     }
   }
   ```
   
   **Note**: Leave `bot_token` and `chat_id` empty if using `telegram.env`

3. Update `config\intraday_rescan_config.json`:
   ```json
   "telegram": {
     "enabled": true,
     "bot_token": "",
     "chat_id": "",
     "parse_mode": "Markdown",
     "disable_notification": false
   }
   ```

### Step 4: Test Your Setup

```batch
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

You should receive test messages in Telegram confirming the setup works.

## Usage Examples

### Send Test Message

```python
from models.notifications.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()
notifier.send_message("🧪 Test notification!")
```

### Send Breakout Alert

```python
notifier.send_breakout_alert(
    symbol="AAPL",
    breakout_type="price_breakout_up",
    strength=85.3,
    price=180.50,
    details={
        "change_from_prev": 3.2,
        "volume_multiple": 2.1,
        "momentum_15m": 4.5
    }
)
```

### Send Morning Report

```python
notifier.send_morning_report(
    report_path="reports/morning_reports/us_morning_report_2024-12-03.html",
    market="US",
    summary={
        "stocks_scanned": 240,
        "top_opportunities": 10,
        "execution_time": 45.2
    }
)
```

### Send Document

```python
notifier.send_document(
    file_path="reports/analysis.pdf",
    caption="📊 Daily Analysis Report"
)
```

## Integration Points

### 1. Overnight Pipeline

The overnight pipeline automatically sends reports when enabled:

**File**: `models/screening/us_overnight_pipeline.py` (or ASX equivalent)

```python
# At the end of pipeline execution
if config.get("telegram_notifications", {}).get("enabled"):
    from models.notifications.telegram_notifier import TelegramNotifier
    
    notifier = TelegramNotifier()
    
    # Send completion notification
    notifier.send_message(
        f"✅ *Pipeline Complete*\n\n"
        f"Market: {market}\n"
        f"Stocks: {stocks_scanned}\n"
        f"Duration: {duration:.1f} min"
    )
    
    # Send report
    if report_path.exists():
        notifier.send_morning_report(
            report_path=report_path,
            market=market,
            summary={
                "stocks_scanned": stocks_scanned,
                "top_opportunities": len(top_picks),
                "execution_time": duration
            }
        )
```

### 2. Intraday Scanner

The intraday scanner sends real-time alerts:

**File**: `models/screening/intraday_scanner.py` (or similar)

```python
# When breakout detected
if opportunity_score >= alert_threshold:
    from models.notifications.telegram_notifier import TelegramNotifier
    
    notifier = TelegramNotifier()
    notifier.send_breakout_alert(
        symbol=symbol,
        breakout_type=breakout_type,
        strength=opportunity_score,
        price=current_price,
        details={
            "price_change": price_change,
            "volume_spike": volume_ratio,
            "momentum": momentum_score
        }
    )
```

### 3. News Sentiment Integration

Send alerts for significant news events:

```python
# When significant news sentiment detected
if abs(sentiment_score) > 0.6:
    from models.notifications.telegram_notifier import TelegramNotifier
    
    notifier = TelegramNotifier()
    
    sentiment_emoji = "📈" if sentiment_score > 0 else "📉"
    sentiment_label = "POSITIVE" if sentiment_score > 0 else "NEGATIVE"
    
    message = f"""{sentiment_emoji} *News Sentiment Alert*

*Symbol:* `{symbol}`
*Sentiment:* {sentiment_label} ({abs(sentiment_score)*100:.1f}% confidence)
*Articles:* {article_count}
*Source:* {', '.join(sources)}

*Key Headlines:*
{top_headlines}
"""
    
    notifier.send_message(message)
```

## Configuration Reference

### screening_config.json

```json
{
  "telegram_notifications": {
    // Master enable/disable
    "enabled": true,
    
    // Credentials (leave empty to use telegram.env)
    "bot_token": "",
    "chat_id": "",
    
    // Message formatting
    "parse_mode": "Markdown",  // or "HTML"
    
    // Morning report settings
    "morning_report": {
      "send_report": true,           // Send report after pipeline
      "send_as_document": true,       // Attach as file vs text
      "include_summary": true         // Include summary stats
    },
    
    // Alert settings
    "alerts": {
      "enabled": true,                // Enable real-time alerts
      "min_alert_strength": 70.0,     // Minimum score to alert
      "max_alerts_per_hour": 20,      // Rate limit
      "alert_types": [                // Types to alert on
        "breakout",
        "high_score",
        "news_sentiment"
      ],
      "quiet_hours": {
        "enabled": false,             // Enable quiet hours
        "start": "23:00",             // No alerts after
        "end": "07:00"                // Resume alerts at
      }
    },
    
    // Pipeline notifications
    "notifications": {
      "pipeline_start": true,         // Notify when starting
      "pipeline_complete": true,       // Notify when done
      "pipeline_errors": true,         // Notify on errors
      "model_training_complete": false, // Notify after training
      "high_opportunity_detected": true // Alert on high scores
    }
  }
}
```

### intraday_rescan_config.json

```json
{
  "alerts": {
    "telegram": {
      "enabled": true,                  // Enable Telegram alerts
      "bot_token": "",                  // Leave empty for env var
      "chat_id": "",                    // Leave empty for env var
      "parse_mode": "Markdown",
      "disable_notification": false     // Silent notifications
    }
  }
}
```

## Message Formatting

### Markdown Formatting

```python
message = """
*Bold text*
_Italic text_
`Code/monospace`
[Link text](https://example.com)
"""
notifier.send_message(message, parse_mode="Markdown")
```

### HTML Formatting

```python
message = """
<b>Bold text</b>
<i>Italic text</i>
<code>Code/monospace</code>
<a href="https://example.com">Link text</a>
"""
notifier.send_message(message, parse_mode="HTML")
```

### Emojis

Common emojis for trading alerts:

- 🚀 Strong bullish signal
- 📈 Bullish signal
- 📉 Bearish signal
- 📊 General market info
- ✅ Success/completion
- ✗ Error/failure
- ⚠️ Warning
- 💰 Profit opportunity
- 📰 News event

## Troubleshooting

### Issue: "Telegram not configured"

**Cause**: Bot token or chat ID not found

**Solution**:
1. Check `telegram.env` exists in `C:\Users\david\AATelS\`
2. Verify it contains both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
3. No quotes around values:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdef...  ✓ Correct
   TELEGRAM_BOT_TOKEN="123456789:ABCdef..." ✗ Wrong
   ```

### Issue: "Bot connection failed"

**Cause**: Invalid bot token or network issue

**Solution**:
1. Test your bot token in browser:
   ```
   https://api.telegram.org/botYOUR_TOKEN/getMe
   ```
   Should return bot info, not an error
2. Check internet connection
3. Verify token is correct (no extra spaces)

### Issue: "Failed to send message"

**Cause**: Wrong chat ID or bot not started

**Solution**:
1. Make sure you sent a message to your bot first
2. Verify chat ID is numeric (not username)
3. Get fresh chat ID:
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":123456789` in response

### Issue: "Module not found: telegram_notifier"

**Cause**: Wrong directory or path issue

**Solution**:
1. Verify you're in `C:\Users\david\AATelS\`
2. Check file exists: `models\notifications\telegram_notifier.py`
3. Test import:
   ```python
   cd C:\Users\david\AATelS
   python -c "import models.notifications.telegram_notifier"
   ```

### Issue: "Message too long"

**Cause**: Message exceeds 4096 characters

**Solution**:
- Telegram has a 4096 character limit for text messages
- The notifier auto-truncates, but you can split manually:
  ```python
  if len(message) > 4000:
      # Send as document instead
      with open("temp_message.txt", "w") as f:
          f.write(message)
      notifier.send_document("temp_message.txt")
  else:
      notifier.send_message(message)
  ```

## Security Best Practices

### 1. Protect Your Credentials

**DO**:
- Store credentials in `telegram.env` (git-ignored)
- Use environment variables
- Keep bot token private
- Rotate token if exposed

**DON'T**:
- Commit `telegram.env` to Git
- Share bot token publicly
- Hard-code credentials in Python files
- Use same bot for multiple systems

### 2. Rate Limiting

Telegram has rate limits:
- ~30 messages per second per bot
- ~20 messages per minute per chat

The notifier handles this automatically, but for high-volume:

```python
# Use batch sending
notifier.send_batch_alerts(
    alerts=alert_list,
    max_alerts=10  # Limit to 10 per batch
)
```

### 3. Error Handling

Always handle Telegram failures gracefully:

```python
try:
    success = notifier.send_message("Alert!")
    if not success:
        logger.warning("Telegram send failed, continuing anyway")
except Exception as e:
    logger.error(f"Telegram error: {e}")
    # Don't let Telegram failures stop your pipeline
```

## Advanced Features

### Quiet Hours

Prevent notifications during specific hours:

```json
"quiet_hours": {
  "enabled": true,
  "start": "23:00",
  "end": "07:00"
}
```

The notifier will automatically skip messages during these hours.

### Silent Notifications

Send messages without sound:

```python
notifier.send_message(
    "Background update",
    disable_notification=True  # No sound/vibration
)
```

### Custom Keyboards

Add interactive buttons (advanced):

```python
import requests

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "Choose an action:",
    "reply_markup": {
        "inline_keyboard": [[
            {"text": "View Report", "url": "https://example.com/report"},
            {"text": "Cancel", "callback_data": "cancel"}
        ]]
    }
}
requests.post(url, json=payload)
```

## Testing Checklist

- [ ] Bot created via @BotFather
- [ ] Bot token obtained
- [ ] Chat started with bot
- [ ] Chat ID obtained from getUpdates
- [ ] Credentials added to telegram.env
- [ ] Config files updated
- [ ] Test script passes: `python TELEGRAM_SETUP_PATCH\tests\test_telegram.py`
- [ ] Test message received in Telegram
- [ ] Test alert received in Telegram
- [ ] Pipeline test completes: `python models\screening\us_overnight_pipeline.py --test-mode`
- [ ] Morning report received in Telegram

## Next Steps

1. ✅ Complete setup using this guide
2. ✅ Test with `test_telegram.py`
3. ✅ Run pipeline test mode
4. Configure notification preferences in config files
5. Set up Windows Task Scheduler for overnight pipeline
6. Enable intraday alerts (optional)
7. Customize quiet hours and rate limits
8. Monitor logs for any issues

## Support

For issues or questions:
- Check logs: `logs/screening/`
- Review `telegram_notifier.py` docstrings
- Re-run test script with `-v` flag for verbose output
- Verify credentials are correct

## API Reference

See the `TelegramNotifier` class in `models/notifications/telegram_notifier.py` for complete API documentation.

Key methods:
- `send_message(text, parse_mode, disable_notification)`
- `send_document(file_path, caption, disable_notification)`
- `send_photo(photo_path, caption, disable_notification)`
- `send_breakout_alert(symbol, breakout_type, strength, price, details)`
- `send_morning_report(report_path, market, summary)`
- `send_batch_alerts(alerts, max_alerts)`
- `test_connection()`

---

**Ready to receive notifications?** Run the setup script:

```batch
cd C:\Users\david\AATelS
TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
```

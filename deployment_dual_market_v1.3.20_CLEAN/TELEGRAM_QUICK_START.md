# 🚀 TELEGRAM NOTIFICATIONS - QUICK START

## ⏱️ 5-Minute Setup

### Step 1: Download (30 seconds)
```
Download: TELEGRAM_SETUP_PATCH.zip (17 KB)
Location: deployment_dual_market_v1.3.20_CLEAN/TELEGRAM_SETUP_PATCH.zip
```

### Step 2: Extract (10 seconds)
```
Extract to: C:\Users\david\AATelS\
Result:     C:\Users\david\AATelS\TELEGRAM_SETUP_PATCH\
```

### Step 3: Run Setup (3-4 minutes)
```batch
cd C:\Users\david\AATelS
TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
```

**The script will guide you through**:
1. ✅ Creating Telegram bot (@BotFather)
2. ✅ Getting bot token
3. ✅ Getting chat ID
4. ✅ Configuring credentials
5. ✅ Testing connection

### Step 4: Done!
You'll receive test messages in Telegram confirming everything works.

---

## 📱 What You'll Receive

### 1. Morning Reports (7:00 AM)
```
📊 US Morning Report
2024-12-03 07:30

Stocks Scanned: 240
Top Picks: 10
Scan Time: 45.2 min

[Attached: us_morning_report.html]
```

### 2. Breakout Alerts (Real-time)
```
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
```

### 3. Pipeline Status
```
✅ Pipeline Complete
Duration: 45.2 min
Stocks: 240
Top Picks: 10
```

---

## 🎯 Quick Commands

### Test Your Setup
```batch
cd C:\Users\david\AATelS
python TELEGRAM_SETUP_PATCH\tests\test_telegram.py
```

### Send Test Message
```python
cd C:\Users\david\AATelS
python -c "from models.notifications.telegram_notifier import TelegramNotifier; TelegramNotifier().send_message('✅ Working!')"
```

### Run Test Pipeline
```batch
cd C:\Users\david\AATelS
python models\screening\us_overnight_pipeline.py --test-mode
```

---

## 📋 Creating Your Bot (2 minutes)

### In Telegram App:
1. Search: `@BotFather`
2. Send: `/newbot`
3. Name: `My Stock Screener Bot`
4. Username: `mystock_screener_bot`
5. **Copy the token** (looks like: `123456789:ABCdefGhIjKlMn...`)

### Get Chat ID:
1. Start chat with your bot
2. Send: `Hello`
3. Open in browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
4. Find: `"chat":{"id":123456789`
5. **Copy the number** after `"id":`

---

## ✅ Verification

After setup completes, verify:

**✓ Test messages received in Telegram**
- Basic test message
- Formatted breakout alert

**✓ Configuration files updated**
- `models/config/screening_config.json`
- `config/intraday_rescan_config.json`

**✓ Credentials saved**
- `telegram.env` created

---

## 🛟 Quick Troubleshooting

### "Telegram not configured"
- Check `telegram.env` exists
- Verify it has `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

### "Connection failed"
- Test token: `https://api.telegram.org/bot<TOKEN>/getMe`
- Check internet connection

### "Send failed"
- Send message to your bot first
- Verify chat ID is numeric

---

## 💰 Benefits

- ✅ **Zero Cost** - Free forever
- ✅ **Instant** - Real-time delivery
- ✅ **Reliable** - 99.9% uptime
- ✅ **Global** - Works anywhere
- ✅ **Rich** - HTML reports, formatted alerts
- ✅ **Simple** - 5-minute setup

---

## 📖 Full Documentation

- **Quick Start**: TELEGRAM_QUICK_START.md (this file)
- **Complete Guide**: TELEGRAM_SETUP_PATCH/README.txt
- **Detailed Docs**: TELEGRAM_SETUP_PATCH/docs/TELEGRAM_INTEGRATION_GUIDE.md
- **Summary**: TELEGRAM_SETUP_SUMMARY.md

---

## 🚀 Ready?

```batch
cd C:\Users\david\AATelS
TELEGRAM_SETUP_PATCH\SETUP_TELEGRAM.bat
```

**Your trading alerts, delivered instantly to your phone!** 📱✨

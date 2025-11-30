# 📱 TELEGRAM ALERTS SETUP - COMPLETE GUIDE

## Overview
This guide will help you set up Telegram notifications for FinBERT breakout alerts during intraday trading.

---

## 🤖 STEP 1: CREATE YOUR TELEGRAM BOT

### 1.1: Find BotFather
1. Open Telegram (mobile or desktop app)
2. Search for **@BotFather** (official Telegram bot)
3. Click on it and press **START**

### 1.2: Create Your Bot
Send these commands:
```
/newbot
```

BotFather will ask you:

**Question 1: "Alright, a new bot. How are we going to call it?"**
- Answer: Choose a display name (e.g., `FinBERT Alerts`)

**Question 2: "Now, let's choose a username for your bot..."**
- Answer: Must end in `bot` (e.g., `david_finbert_bot`)

### 1.3: Save Your Bot Token
BotFather will respond with something like:
```
Done! Congratulations on your new bot. You will find it at 
t.me/david_finbert_bot. You can now add a description, about 
section and profile picture for your bot, see /help for a list 
of commands.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
Keep your token secure and store it safely, it can be used by 
anyone to control your bot.
```

**📝 COPY THE TOKEN** (the long string with numbers and letters)

---

## 💬 STEP 2: GET YOUR CHAT ID

### 2.1: Start Chat with Your Bot
1. Click the link BotFather provides (e.g., `t.me/david_finbert_bot`)
2. Press **START** button
3. Send any message (e.g., type `Hello` and press enter)

### 2.2: Retrieve Your Chat ID

Open your web browser and go to this URL:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

**Replace `<YOUR_BOT_TOKEN>` with your actual bot token!**

**Example:**
```
https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890/getUpdates
```

You'll see JSON output like this:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,          ← THIS IS YOUR CHAT ID!
          "is_bot": false,
          "first_name": "David",
          "username": "david123"
        },
        "chat": {
          "id": 987654321,          ← ALSO HERE!
          "first_name": "David",
          "username": "david123",
          "type": "private"
        },
        "date": 1234567890,
        "text": "Hello"
      }
    }
  ]
}
```

**📝 COPY THE CHAT ID** (the number under `"from": { "id": ...`)

**If you see `"result": []` (empty):**
- You haven't sent a message to your bot yet
- Go back to Step 2.1 and send a message
- Then refresh the browser page

---

## 🔧 STEP 3: CONFIGURE FINBERT

### Method 1: Automated Setup (Easiest)

1. Navigate to your FinBERT directory:
   ```cmd
   cd C:\Users\david\AATelS
   ```

2. Run the setup wizard:
   ```cmd
   SETUP_TELEGRAM.bat
   ```

3. Follow the on-screen prompts
4. Enter your bot token when asked
5. Enter your chat ID when asked

### Method 2: Manual Setup

1. Navigate to your FinBERT directory:
   ```cmd
   cd C:\Users\david\AATelS
   ```

2. Open the `.env` file in a text editor (Notepad++)

3. Replace the placeholder values:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   TELEGRAM_CHAT_ID=987654321
   ```

4. Save the file

---

## ✅ STEP 4: TEST YOUR TELEGRAM CONNECTION

1. Run the test script:
   ```cmd
   cd C:\Users\david\AATelS
   python test_telegram.py
   ```

2. Expected output:
   ```
   ======================================================================
     FinBERT Telegram Connection Test
   ======================================================================

   ✓ Found .env file at: C:\Users\david\AATelS\.env
   ✓ Bot Token: 1234567890...1234567890
   ✓ Chat ID: 987654321
   ✓ TelegramNotifier module loaded successfully

   Attempting to send test message...
   ----------------------------------------------------------------------

   ======================================================================
     ✅ SUCCESS! Telegram is working!
   ======================================================================

   Check your Telegram app - you should have received a test message!
   ```

3. **Check your Telegram app** - you should receive a test message!

### Troubleshooting

**If test fails:**

❌ **Error: "Bot token not configured"**
- Your .env file doesn't have the correct token
- Make sure you copied the entire token from @BotFather
- No spaces or quotes needed in the .env file

❌ **Error: "Chat ID not configured"**
- Your .env file doesn't have the correct chat ID
- Make sure you got it from the /getUpdates URL
- Use just the numbers, no quotes

❌ **Error: "Failed to send message"**
- Check that you sent /start to your bot
- Verify your bot token is correct
- Verify your chat ID is correct
- Check your internet connection

---

## 🚀 STEP 5: RUN INTRADAY MONITORING

Once Telegram is working, you can start the intraday monitors:

### For US Market:
```cmd
cd C:\Users\david\AATelS
RUN_INTRADAY_MONITOR_US.bat
```

### For ASX Market:
```cmd
cd C:\Users\david\AATelS
RUN_INTRADAY_MONITOR_ASX.bat
```

---

## 📊 WHAT TO EXPECT

### During Market Hours:
The system will:
1. ✅ Detect market open automatically
2. ✅ Scan stocks every 15 minutes
3. ✅ Detect price breakouts and momentum changes
4. ✅ Send Telegram alerts for opportunities above 70% confidence

### Example Telegram Alert:
```
🚨 BREAKOUT ALERT

📈 AAPL - Apple Inc.
Price: $320.18 (+10.00%)
Signal: 89% confidence

⚡ Breakout Detected:
• Price surge: +3.5% in 15 min
• Volume spike: 2.5x average
• Momentum score: 85/100

🎯 Entry: $320.18
🛡️ Stop Loss: $312.00
🎁 Target: $335.00

⏰ 2025-11-30 10:45 AM EST
```

---

## ⚙️ CONFIGURATION OPTIONS

Edit `config/intraday_rescan_config.json` to customize:

### Alert Threshold
```json
"alerts": {
  "alert_threshold": 70.0,     // Only alert if confidence > 70%
  "max_alerts_per_hour": 20,   // Limit alerts per hour
}
```

### Scan Frequency
```json
"intraday_rescan": {
  "scan_interval_minutes": 15,  // Rescan every 15 minutes
}
```

### Breakout Sensitivity
```json
"breakout_detection": {
  "price_breakout_threshold": 2.0,      // 2% price move
  "volume_spike_multiplier": 2.0,       // 2x volume
  "momentum_threshold": 3.0,            // Momentum score
  "min_signal_strength": 60.0           // Minimum 60% confidence
}
```

### Disable Notifications Sound
```json
"telegram": {
  "enabled": true,
  "disable_notification": true,  // Silent notifications
}
```

---

## 🔐 SECURITY NOTES

1. **Keep your bot token secret!**
   - Don't share it with anyone
   - Don't commit .env to Git (it's in .gitignore)

2. **Chat ID is not sensitive**
   - It's just your Telegram user ID
   - But still, don't share unnecessarily

3. **Control your bot:**
   - Only you can send messages to yourself via your bot
   - Others can't use your bot unless they have your token

---

## 📚 ADDITIONAL RESOURCES

### Telegram Bot Commands (via @BotFather):
- `/mybots` - See all your bots
- `/deletebot` - Delete a bot
- `/setdescription` - Change bot description
- `/setabouttext` - Set about text

### FinBERT Documentation:
- `PHASE_3_QUICK_START_GUIDE.md` - Complete Phase 3 guide
- `TELEGRAM_SETUP_GUIDE.md` - Alternative setup guide
- `config/intraday_rescan_config.json` - Configuration file

---

## 🆘 NEED HELP?

**Common Issues:**

1. **"Empty result" when checking /getUpdates**
   - Send a message to your bot first
   - Refresh the browser

2. **Test script can't find .env file**
   - Make sure you're in the right directory
   - .env should be in `C:\Users\david\AATelS\`

3. **Telegram alerts not coming**
   - Check `config/intraday_rescan_config.json`
   - Make sure `"enabled": true` under telegram section
   - Check alert_threshold isn't too high

4. **Bot not responding**
   - Verify bot token is correct
   - Make sure you pressed START in bot chat
   - Check internet connection

---

## ✅ CHECKLIST

Before running intraday monitor, verify:

- [ ] Created Telegram bot via @BotFather
- [ ] Have bot token copied
- [ ] Started chat with bot (pressed START)
- [ ] Have chat ID from /getUpdates
- [ ] Updated .env file with credentials
- [ ] Ran test_telegram.py successfully
- [ ] Received test message in Telegram
- [ ] Reviewed config in intraday_rescan_config.json

---

**You're all set! Your Telegram alerts are ready to go!** 🎉

Run the intraday monitor during market hours and you'll receive real-time breakout alerts on your phone!

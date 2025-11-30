# Manual Installation Guide

## When to Use This Guide

Use manual installation if:
- Automatic patch fails
- You have custom modifications
- You want to understand each change
- Git conflicts occur

---

## Overview

This guide will manually install:
1. Morning Report Telegram Notifications
2. Macro News Monitoring (Fed/RBA)

**Estimated Time:** 15-20 minutes

---

## Prerequisites

- FinBERT overnight pipelines installed
- Python environment set up
- Text editor (Notepad++, VSCode, or similar)
- Telegram bot token and chat ID (if using Telegram)

---

## Part 1: Add New Files

### Step 1.1: Create Macro News Monitor

Create file: `models\screening\macro_news_monitor.py`

Copy the entire contents from:
```
FINBERT_UPGRADE_PATCH\files\macro_news_monitor.py
```

Or download from GitHub:
```
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/models/screening/macro_news_monitor.py
```

**Verify:** File should be ~620 lines, ~21 KB

### Step 1.2: Create Test Script

Create file: `test_morning_report_telegram.py`

Copy from the patch or create with this content:

```python
"""Test script to verify Telegram morning report notifications"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pytz

sys.path.insert(0, str(Path(__file__).parent))

from models.notifications.telegram_notifier import TelegramNotifier


def test_morning_report():
    """Test morning report notification"""
    
    config_path = Path(__file__).parent / 'config' / 'intraday_rescan_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            telegram_cfg = config.get('notifications', {}).get('telegram', {})
            
            if not telegram_cfg.get('enabled', False):
                print("❌ Telegram notifications disabled in config")
                return False
            
            bot_token = telegram_cfg.get('bot_token')
            chat_id = telegram_cfg.get('chat_id')
            
            if not bot_token or not chat_id:
                print("❌ Telegram credentials missing in config")
                return False
            
            print(f"✓ Telegram config loaded")
            
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    try:
        telegram = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        print("✓ TelegramNotifier initialized")
    except Exception as e:
        print(f"❌ TelegramNotifier initialization failed: {e}")
        return False
    
    tz = pytz.timezone('Australia/Sydney')
    timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    market_summary = f"""📊 *Morning Report Test*

🧪 *Test Pipeline Summary:*
• Total Stocks Scanned: 240
• High-Quality Opportunities: 15
• Execution Time: 3.5 minutes
• Report Generated: {timestamp}

📁 This is a test report.

✅ *Status: TEST COMPLETE*

If you received this message, your Telegram morning report notifications are working correctly! 🎉"""
    
    try:
        print("\nSending test morning report...")
        telegram.send_message(market_summary)
        print("✅ Test morning report sent successfully!")
        print("\nCheck your Telegram to confirm you received the message.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test report: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*60)
    print("TELEGRAM MORNING REPORT TEST")
    print("="*60)
    print()
    
    success = test_morning_report()
    
    if success:
        print("\n✅ TEST PASSED")
    else:
        print("\n❌ TEST FAILED")
    
    sys.exit(0 if success else 1)
```

**Verify:** File should be ~120 lines, ~4 KB

---

## Part 2: Modify US Overnight Pipeline

### Step 2.1: Add Import

Open: `models\screening\us_overnight_pipeline.py`

Find the line (around line 64):
```python
try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    EventRiskGuard = None
```

**Add after it:**
```python

# Macro news monitoring
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    MacroNewsMonitor = None
```

### Step 2.2: Initialize Macro Monitor

Find the section where `EmailNotifier` is initialized (around line 217):
```python
            # Optional: Email notifications
            if EmailNotifier is not None:
                self.notifier = EmailNotifier()
```

**Add before the Telegram section:**
```python
            
            # Optional: Macro News Monitor
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='US')
                logger.info("✓ Macro News Monitor enabled (Fed/economic data)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")
```

### Step 2.3: Enhance Sentiment Fetching

Find the method `_fetch_us_market_sentiment` (around line 496):

**Replace the return statement section** with:

```python
            logger.info(f"  Market Mood: {sentiment['vix']['market_mood']}")
            
            # Fetch macro news sentiment (Fed announcements, etc.)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    macro_news = self.macro_monitor.get_macro_sentiment()
                    
                    # Add macro news to sentiment
                    sentiment['macro_news'] = macro_news
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        # Macro news has 20% weight on overall sentiment
                        macro_adjustment = macro_news['sentiment_score'] * 10  # -10 to +10 scale
                        original_score = sentiment['overall']['score']
                        adjusted_score = original_score + macro_adjustment
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to 0-100
                        
                        logger.info(f"  Macro News Impact: {macro_adjustment:+.1f} points")
                        logger.info(f"  Adjusted Sentiment: {original_score:.1f} → {adjusted_score:.1f}")
                        
                        sentiment['overall']['score'] = adjusted_score
                        sentiment['overall']['macro_adjusted'] = True
                    
                except Exception as e:
                    logger.warning(f"Macro news fetch failed: {e}")
                    sentiment['macro_news'] = None
            else:
                sentiment['macro_news'] = None
            
            return sentiment
```

---

## Part 3: Modify ASX Overnight Pipeline

### Step 3.1: Add Import

Open: `models\screening\overnight_pipeline.py`

Find (around line 91):
```python
        EventRiskGuard = None
```

**Add after it:**
```python

# Macro news monitoring
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    MacroNewsMonitor = None
```

### Step 3.2: Initialize Macro Monitor

Find where Telegram is initialized (around line 230):

**Add before the Telegram section:**
```python
            
            # Optional: Macro News Monitor
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='ASX')
                logger.info("✓ Macro News Monitor enabled (RBA/economic data)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")
```

### Step 3.3: Enhance Sentiment Fetching

Find the method `_fetch_market_sentiment` (around line 539):

**Replace the return statement section** with:

```python
            logger.info(f"  Recommendation: {sentiment['recommendation']['stance']}")
            
            # Fetch macro news sentiment (RBA announcements, etc.)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    macro_news = self.macro_monitor.get_macro_sentiment()
                    
                    # Add macro news to sentiment
                    sentiment['macro_news'] = macro_news
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        # Macro news has 20% weight on overall sentiment
                        macro_adjustment = macro_news['sentiment_score'] * 10  # -10 to +10 scale
                        original_score = sentiment['sentiment_score']
                        adjusted_score = original_score + macro_adjustment
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to 0-100
                        
                        logger.info(f"  Macro News Impact: {macro_adjustment:+.1f} points")
                        logger.info(f"  Adjusted Sentiment: {original_score:.1f} → {adjusted_score:.1f}")
                        
                        sentiment['sentiment_score'] = adjusted_score
                        sentiment['macro_adjusted'] = True
                    
                except Exception as e:
                    logger.warning(f"Macro news fetch failed: {e}")
                    sentiment['macro_news'] = None
            else:
                sentiment['macro_news'] = None
            
            return sentiment
```

---

## Part 4: Configure Telegram

### Step 4.1: Update Config File

Open: `config\intraday_rescan_config.json`

Find or create the `notifications` section:

```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN_HERE",
      "chat_id": "YOUR_CHAT_ID_HERE",
      "parse_mode": "Markdown",
      "disable_notification": false
    },
    "email": {
      "enabled": false
    },
    "sms": {
      "enabled": false
    },
    "webhook": {
      "enabled": false
    }
  }
}
```

**Replace:**
- `YOUR_BOT_TOKEN_HERE` with your actual Telegram bot token
- `YOUR_CHAT_ID_HERE` with your actual Telegram chat ID

---

## Part 5: Test Installation

### Step 5.1: Test Macro News Monitor

```bash
cd C:\Users\david\AATelS
python models\screening\macro_news_monitor.py
```

**Expected Output:**
```
MACRO NEWS ANALYSIS - US MARKET
  Fetching Federal Reserve press releases...
  ✓ Federal Reserve Releases: X articles
✓ US Macro News: X articles, Sentiment: ...
```

### Step 5.2: Test Morning Reports

```bash
python test_morning_report_telegram.py
```

**Expected Output:**
```
✓ Telegram config loaded
✓ TelegramNotifier initialized
✅ Test morning report sent successfully!
```

**Check Telegram:** You should receive a test message

### Step 5.3: Test Full Pipeline

```bash
python models\screening\us_overnight_pipeline.py
```

**Look for:**
```
✓ Macro News Monitor enabled (Fed/economic data)
...
MACRO NEWS ANALYSIS - US MARKET
...
✓ US Macro News: X articles, Sentiment: ...
  Macro News Impact: ±X.X points
```

---

## Verification Checklist

- [ ] `macro_news_monitor.py` created (~620 lines)
- [ ] `test_morning_report_telegram.py` created (~120 lines)
- [ ] US pipeline imports MacroNewsMonitor
- [ ] US pipeline initializes macro_monitor
- [ ] US pipeline fetches macro sentiment
- [ ] ASX pipeline imports MacroNewsMonitor
- [ ] ASX pipeline initializes macro_monitor
- [ ] ASX pipeline fetches macro sentiment
- [ ] Telegram config has `notifications` section
- [ ] Bot token and chat ID configured
- [ ] Macro news test passes
- [ ] Morning report test passes
- [ ] Full pipeline runs successfully

---

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'macro_news_monitor'`

**Fix:** Verify file is in correct location:
```
models\screening\macro_news_monitor.py
```

### Telegram Not Working

**Error:** No test message received

**Fix:**
1. Check `config\intraday_rescan_config.json`
2. Verify `"enabled": true`
3. Check bot_token and chat_id are correct
4. Test with basic `test_telegram.py` first

### Macro News Not Fetching

**Error:** "Macro News Monitor disabled"

**Fix:** Check that `MacroNewsMonitor` import succeeded:
```python
print(MacroNewsMonitor)  # Should not be None
```

---

## Rollback

If you need to undo changes:

### Option 1: Git Reset
```bash
git reset --hard HEAD~X  # X = number of commits to undo
```

### Option 2: Manual Rollback
1. Delete `models\screening\macro_news_monitor.py`
2. Delete `test_morning_report_telegram.py`
3. Revert changes to `us_overnight_pipeline.py`
4. Revert changes to `overnight_pipeline.py`

---

## Support

**Documentation:**
- `MORNING_REPORT_SETUP.md` - Morning report details
- `MACRO_NEWS_INTEGRATION_COMPLETE.md` - Macro news details
- `NEWS_AND_EVENTS_STATUS.md` - Feature overview

**Need Help?**
Check the verification checklist above to ensure all steps completed successfully.

---

**Installation complete!** Run a pipeline to see the upgrades in action. 🚀

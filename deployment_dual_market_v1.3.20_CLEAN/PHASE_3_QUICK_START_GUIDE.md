# Phase 3 Auto-Rescan - Quick Start Guide

## 🚀 What is Phase 3?

Phase 3 adds **continuous intraday monitoring** for day traders, enabling real-time opportunity detection during market hours.

### Key Features

✅ **Auto-Rescan** - Automatically rescans every 15-30 minutes during market hours  
✅ **Incremental Scanning** - 80-90% API cost savings (only rescans changed stocks)  
✅ **Real-time Breakouts** - Detects price, volume, and momentum breakouts  
✅ **Multi-Channel Alerts** - Email, SMS (Twilio), and Webhook (Slack/Discord)  
✅ **Smart Detection** - Market hours aware, auto-start/stop  

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Run Your First Intraday Monitor

**For US Stocks:**
```bash
RUN_INTRADAY_MONITOR_US.bat
```

**For ASX Stocks:**
```bash
RUN_INTRADAY_MONITOR_ASX.bat
```

The monitor will:
- ✓ Auto-detect if market is open
- ✓ Scan stocks every 15-30 minutes
- ✓ Detect breakouts in real-time
- ✓ Display alerts in console

Press `Ctrl+C` to stop.

---

### Step 2: Configure Alerts (Optional)

Edit `config/intraday_rescan_config.json`:

```json
{
  "alerts": {
    "email": {
      "enabled": true,
      "to_addresses": ["your.email@example.com"],
      "smtp_server": "smtp.gmail.com",
      "smtp_username": "your.username@gmail.com",
      "smtp_password": "your_app_password"
    },
    "sms": {
      "enabled": true,
      "twilio_account_sid": "YOUR_SID",
      "twilio_auth_token": "YOUR_TOKEN",
      "twilio_from_number": "+1234567890",
      "to_numbers": ["+1234567890"]
    },
    "webhook": {
      "enabled": true,
      "type": "slack",
      "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
  }
}
```

---

### Step 3: Adjust Scan Settings (Optional)

Modify scan parameters in `config/intraday_rescan_config.json`:

```json
{
  "intraday_rescan": {
    "scan_interval_minutes": 15,
    "auto_start_on_market_open": true,
    "auto_stop_on_market_close": true
  },
  "incremental_scanning": {
    "price_change_threshold": 2.0,
    "volume_multiplier": 1.5,
    "min_rescan_interval": 15
  },
  "breakout_detection": {
    "price_breakout_threshold": 2.0,
    "volume_spike_multiplier": 2.0,
    "momentum_threshold": 3.0,
    "min_signal_strength": 60.0
  },
  "alerts": {
    "alert_threshold": 70.0
  }
}
```

**Key Settings:**
- `scan_interval_minutes`: Time between rescans (15-30 recommended)
- `price_change_threshold`: Min % price change to trigger rescan (default: 2%)
- `volume_multiplier`: Min volume multiple to trigger rescan (default: 1.5x)
- `min_signal_strength`: Min breakout strength to report (default: 60/100)
- `alert_threshold`: Min strength to send alerts (default: 70/100)

---

## 📊 Understanding Breakout Types

### Price Breakouts
- **Day High Break**: Stock hits new intraday high
- **Day Low Break**: Stock hits new intraday low
- **Price Breakout Up**: Significant upward move (≥2%)
- **Price Breakout Down**: Significant downward move (≥2%)

### Volume Breakouts
- **Volume Spike**: Unusual volume activity (≥2x average)

### Momentum Breakouts
- **Momentum Surge**: Strong directional momentum (≥3% in 15-60 min)
- **Momentum Reversal**: Divergence between short-term and long-term momentum

---

## 🛠️ Advanced Usage

### Running from Python

```python
from models.scheduling.intraday_scheduler import IntradayScheduler

# Create scheduler
scheduler = IntradayScheduler(
    market='US',
    scan_interval_minutes=15,
    config_file='config/intraday_rescan_config.json'
)

# Start monitoring (blocking)
scheduler.start()

# Or schedule background monitoring
scheduler.schedule_monitoring()
```

### Manual Rescan

```python
from models.scheduling.intraday_rescan_manager import IntradayRescanManager

# Initialize manager
manager = IntradayRescanManager(
    market='US',
    config_file='config/intraday_rescan_config.json'
)

# Prepare stock quotes (example)
stock_quotes = [
    {
        'symbol': 'AAPL',
        'price': 175.50,
        'volume': 50_000_000,
        'avg_volume': 60_000_000,
        # ... more fields
    },
    # ... more stocks
]

# Perform rescan
results = manager.perform_rescan(stock_quotes)

# Get session stats
stats = manager.get_session_stats()
print(f"Rescan count: {stats['rescan_count']}")
print(f"Tracked opportunities: {stats['tracked_opportunities']}")
```

---

## 📈 Performance & Costs

### API Cost Savings

**Without Incremental Scanning:**
- Full scan: 240 stocks × 5 API calls = 1,200 calls
- Every 15 min: 1,200 × 4 = 4,800 calls/hour
- Daily (6.5 hours): 31,200 calls
- **Cost: ~$3-5/day**

**With Incremental Scanning (80% savings):**
- Incremental: ~20% of stocks rescanned
- Every 15 min: 240 calls/scan × 4 = 960 calls/hour
- Daily (6.5 hours): 6,240 calls
- **Cost: $0.50-1.00/day** ✅

### Typical Performance

| Metric | Value |
|--------|-------|
| Full scan (240 stocks) | 8-12 minutes |
| Incremental scan (30-50 stocks) | 1-2 minutes |
| Breakout detection | <1 second |
| Alert dispatch | <2 seconds |
| Total rescan cycle | 1-3 minutes |

---

## 🔧 Troubleshooting

### Monitor Won't Start

**Check Python installation:**
```bash
python --version
```

**Check required modules:**
```bash
pip install -r requirements.txt
```

### No Alerts Received

**Verify configuration:**
```python
python -c "
from models.scheduling.alert_dispatcher import AlertDispatcher
dispatcher = AlertDispatcher(config_file='config/intraday_rescan_config.json')
print(dispatcher.get_alert_stats())
"
```

**Test email:**
```python
python models/scheduling/alert_dispatcher.py
```

**For Twilio SMS:**
```bash
pip install twilio
```

### Market Hours Detection Issues

**Test market detection:**
```python
python -c "
from models.screening.market_hours_detector import MarketHoursDetector
detector = MarketHoursDetector()
print(f'US Market Open: {detector.is_us_market_open()}')
print(f'ASX Market Open: {detector.is_asx_market_open()}')
"
```

### High API Costs

**Increase scan interval:**
```json
{
  "intraday_rescan": {
    "scan_interval_minutes": 30
  }
}
```

**Increase rescan thresholds:**
```json
{
  "incremental_scanning": {
    "price_change_threshold": 3.0,
    "min_rescan_interval": 20
  }
}
```

---

## 📚 Component Testing

### Test Incremental Scanner
```bash
python models/screening/incremental_scanner.py
```

### Test Breakout Detector
```bash
python models/screening/breakout_detector.py
```

### Test Alert Dispatcher
```bash
python models/scheduling/alert_dispatcher.py
```

### Test Rescan Manager
```bash
python models/scheduling/intraday_rescan_manager.py
```

---

## 🎓 Example Workflow

**Morning Routine (Day Trader):**

1. **9:00 AM** - Start intraday monitor
   ```bash
   RUN_INTRADAY_MONITOR_US.bat
   ```

2. **9:30 AM** - Market opens, auto-starts scanning

3. **9:45 AM** - First rescan completes, opportunities detected

4. **Throughout Day** - Receive alerts for breakouts:
   - Email: High-strength signals (≥80/100)
   - SMS: Critical signals (≥90/100)
   - Slack: All signals (≥70/100)

5. **4:00 PM** - Market closes, auto-stops scanning

6. **Review** - Check tracked opportunities:
   ```python
   manager.get_tracked_opportunities(min_strength=75)
   ```

---

## 🌟 Best Practices

### For Day Traders

✅ **Start 15 minutes before market open** - Ensures system is ready  
✅ **Use alert threshold ≥70** - Reduces noise, focuses on strong signals  
✅ **Enable SMS for critical alerts** - Fastest notification method  
✅ **Monitor console during first hour** - Highest volatility period  
✅ **Review session stats at end of day** - Track performance  

### For Swing Traders

✅ **Scan interval: 30 minutes** - Lower frequency, still effective  
✅ **Higher thresholds: 3% price, 2.5x volume** - Focus on significant moves  
✅ **Email alerts only** - Less urgent, review periodically  

### API Cost Optimization

✅ **Use incremental scanning** - Enabled by default, 80-90% savings  
✅ **Adjust scan interval** - 30 min vs 15 min = 50% cost reduction  
✅ **Focus on top stocks** - Monitor 50-100 stocks vs all 240  
✅ **Increase rescan thresholds** - 3% vs 2% = fewer rescans  

---

## 🔗 Related Documentation

- **Phase 3 Implementation Plan**: `PHASE_3_AUTO_RESCAN_IMPLEMENTATION.md`
- **Intraday Feature README**: `INTRADAY_FEATURE_README.md`
- **Configuration Reference**: `config/intraday_rescan_config.json`
- **Component Documentation**:
  - Incremental Scanner: `models/screening/incremental_scanner.py`
  - Breakout Detector: `models/screening/breakout_detector.py`
  - Alert Dispatcher: `models/scheduling/alert_dispatcher.py`
  - Rescan Manager: `models/scheduling/intraday_rescan_manager.py`

---

## 🆘 Support

For issues or questions:
1. Check troubleshooting section above
2. Review component test outputs
3. Check `logs/intraday_rescan.log`
4. Open GitHub issue with error details

---

## 📝 License

Part of FinBERT Enhanced Stock Screener - Phase 3 Auto-Rescan  
Version 1.0.0

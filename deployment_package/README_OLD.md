# ASX Overnight Stock Scanner v4.4.4 - Deployment Package

**Complete System with Email Notifications & 5:00 AM Scheduler**

---

## 📦 Package Contents

This deployment package includes:

- ✅ **Complete source code** (models + finbert_v4.4.4)
- ✅ **Email notification system** (Gmail/Outlook/SendGrid support)
- ✅ **5:00 AM AEST scheduler** (automated daily runs)
- ✅ **Configuration files** (ready to customize)
- ✅ **Test scripts** (email & pipeline testing)
- ✅ **Comprehensive documentation** (8 guides)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install yahooquery pandas numpy yfinance pytz schedule

# For full ML features (optional)
pip install tensorflow keras transformers torch
```

### Step 2: Configure Email (5 minutes)

**Choose an SMTP provider:**

- **Option A: Gmail** (Recommended)
  - Get app password: https://myaccount.google.com/apppasswords
  - Configure: `smtp.gmail.com:587`

- **Option B: Outlook** (Easiest)
  - Use your Outlook account
  - Configure: `smtp-mail.outlook.com:587`

- **Option C: SendGrid** (High volume)
  - Free tier: 100 emails/day
  - Configure: `smtp.sendgrid.net:587`

**Edit configuration:**
```bash
nano models/config/screening_config.json
```

Update lines 87-94:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_email@gmail.com",
  "smtp_password": "your_password_or_app_password",
  "sender_email": "your_email@gmail.com",
  "recipient_emails": [
    "finbert_morning_report@proton.me",
    "your_backup@gmail.com"
  ]
}
```

### Step 3: Test & Start (1 minute)

```bash
# Test email configuration
python3 test_email_quick.py

# Start scheduler (5:00 AM daily)
python3 schedule_pipeline.py
```

**Done!** Check your inbox tomorrow at 5:45 AM. ✅

---

## 📊 What You'll Receive

**Daily Morning Report (5:45 AM AEST)**:
- Subject: `📊 ASX Morning Report - YYYY-MM-DD`
- Summary of 240 stocks scanned
- Top 5 opportunities with scores (0-100)
- BUY/SELL/HOLD signals with confidence
- Full HTML report attached

**High-Confidence Alerts** (when applicable):
- Subject: `🚨 HIGH CONFIDENCE OPPORTUNITIES`
- Sent when opportunities ≥80 score found
- Immediate attention opportunities

**Error Notifications** (if pipeline fails):
- Subject: `❌ PIPELINE ERROR`
- Error details and traceback

---

## 📁 File Structure

```
deployment_package/
├── models/                              # Core application
│   ├── config/
│   │   └── screening_config.json       # Email & scheduler config
│   └── screening/
│       ├── overnight_pipeline.py       # Main orchestrator
│       ├── stock_scanner.py            # Stock screening
│       ├── batch_predictor.py          # ML predictions
│       ├── send_notification.py        # Email system
│       └── ... (other modules)
│
├── finbert_v4.4.4/                     # FinBERT integration
│   ├── models/
│   │   ├── news_sentiment_real.py      # News & sentiment
│   │   └── trained/                    # LSTM models
│   └── ...
│
├── schedule_pipeline.py                # 5:00 AM scheduler
├── test_email_quick.py                 # Email test script
├── run_overnight_pipeline.py           # Manual runner
├── requirements_scheduler.txt          # Dependencies
│
├── Installation Scripts/               # Automated installers
│   ├── INSTALL_DEPENDENCIES.bat        # Windows installer
│   └── INSTALL_DEPENDENCIES.sh         # Linux/Mac installer
│
├── Gmail Setup/                        # Email configuration
│   └── GMAIL_APP_PASSWORD_SETUP.md     # Step-by-step guide
│
└── Documentation/
    ├── README.md                       # This file
    ├── EMAIL_AND_SCHEDULER_SETUP.md    # Complete setup guide
    ├── QUICK_START_EMAIL_SCHEDULER.md  # Quick reference
    ├── FINAL_EMAIL_SETUP_INSTRUCTIONS.md
    ├── PROTONMAIL_SMTP_SOLUTION.md
    ├── PROTONMAIL_RECEIVING_EXPLAINED.md
    ├── EMAIL_SCHEDULER_DELIVERY_SUMMARY.md
    └── COMMAND_REFERENCE.txt           # Quick commands
```

---

## ⚙️ System Features

### Stock Screening
- **240 ASX stocks** across 8 sectors
- **5-component scoring** (0-100):
  - Liquidity (trading volume)
  - Momentum (price trends)
  - RSI (overbought/oversold)
  - Volatility (price stability)
  - Sector weight

### Prediction System (Ensemble)
- **LSTM Neural Networks** (45% weight)
- **FinBERT Sentiment** (15% weight)
- **Trend Analysis** (25% weight)
- **Technical Indicators** (15% weight)

### Market Sentiment
- **SPI 200 Futures** monitoring
- **US Market Integration** (S&P 500, Nasdaq, Dow)
- **Gap prediction** (overnight market moves)

### News & Sentiment
- **Real news collection** (Yahoo Finance, RBA)
- **FinBERT analysis** (financial sentiment AI)
- **15-minute caching** (performance optimization)
- **Australian context detection** (RBA, government, indicators)

---

## 🕐 Daily Execution Timeline

| Time | Activity |
|------|----------|
| **5:00 AM** | Scheduler triggers pipeline |
| 5:00-5:02 | Fetch market sentiment (SPI 200, US markets) |
| 5:02-5:20 | Scan 240 ASX stocks (8 sectors) |
| 5:20-5:40 | Generate predictions (LSTM, sentiment, technical) |
| 5:40-5:45 | Score opportunities, generate HTML report |
| **5:45 AM** | 📧 Email sent to configured recipients |

**Total Duration**: ~45 minutes

---

## 🔧 Configuration

### Email Settings

**File**: `models/config/screening_config.json` (lines 85-100)

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your_email@gmail.com",
    "smtp_password": "your_password",
    "use_tls": true,
    "sender_email": "your_email@gmail.com",
    "recipient_emails": [
      "finbert_morning_report@proton.me"
    ],
    "send_morning_report": true,
    "send_alerts": true,
    "send_errors": true,
    "alert_threshold": 80
  }
}
```

### Scheduler Settings

**File**: `models/config/screening_config.json` (lines 2-8)

```json
{
  "schedule": {
    "start_time": "22:00",        # Not used (schedule_pipeline.py runs at 5AM)
    "timezone": "Australia/Sydney",
    "frequency": "daily",
    "enabled": true
  }
}
```

**Actual scheduler**: `schedule_pipeline.py` runs at 5:00 AM AEST/AEDT

---

## 🧪 Testing

### Test Email Notification

```bash
python3 test_email_quick.py
```

**Expected**:
```
✅ TEST EMAIL SENT SUCCESSFULLY!
Check your inbox: your_email@gmail.com
```

### Test Full Pipeline

```bash
python3 schedule_pipeline.py --test
```

Runs full pipeline immediately (~45 minutes).

### Manual Pipeline Run

```bash
python3 run_overnight_pipeline.py
```

Or test mode (Financials only, 5 stocks):
```bash
python3 run_overnight_pipeline.py --mode test
```

---

## 🚀 Running the Scheduler

### Foreground (Testing/Monitoring)

```bash
python3 schedule_pipeline.py
```

Output:
```
================================================================================
OVERNIGHT PIPELINE SCHEDULER STARTED
================================================================================
Schedule Time: 05:00 Australia/Sydney
Next scheduled run: 2025-11-13 05:00:00
Scheduler is running... Press Ctrl+C to stop
```

**Stop**: Press `Ctrl+C`

### Background (Production)

```bash
nohup python3 schedule_pipeline.py > logs/scheduler/nohup.log 2>&1 &
echo $! > logs/scheduler/scheduler.pid
```

**Check Status**:
```bash
ps aux | grep schedule_pipeline
tail -20 logs/scheduler/scheduler.log
```

**Stop**:
```bash
kill $(cat logs/scheduler/scheduler.pid)
rm logs/scheduler/scheduler.pid
```

### Systemd Service (Recommended)

Create `/etc/systemd/system/stock-scanner.service`:

```ini
[Unit]
Description=ASX Overnight Stock Scanner
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/deployment_package
ExecStart=/usr/bin/python3 /path/to/deployment_package/schedule_pipeline.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-scanner.service
sudo systemctl start stock-scanner.service
sudo systemctl status stock-scanner.service
```

---

## 📊 Reports & Logs

### Generated Reports

```
reports/morning_reports/YYYY-MM-DD_market_report.html
reports/pipeline_state/YYYY-MM-DD_pipeline_state.json
```

### Log Files

```
logs/scheduler/scheduler.log              # Scheduler execution
logs/screening/overnight_pipeline.log     # Pipeline execution
logs/screening/email_notifications.log    # Email delivery
```

**View Logs**:
```bash
tail -20 logs/scheduler/scheduler.log
tail -50 logs/screening/overnight_pipeline.log
tail -20 logs/screening/email_notifications.log
```

---

## 🔍 Monitoring

### Check Scheduler Status

```bash
ps aux | grep schedule_pipeline
```

### View Recent Logs

```bash
# Last 20 lines of scheduler log
tail -20 logs/scheduler/scheduler.log

# Follow logs in real-time
tail -f logs/scheduler/scheduler.log
```

### Check Next Scheduled Run

```bash
grep "Next scheduled run" logs/scheduler/scheduler.log | tail -1
```

### View Recent Reports

```bash
ls -lht reports/morning_reports/ | head -6
```

---

## 📧 Email Configuration Options

### Option 1: Gmail (Recommended)

**Requirements**:
- Gmail account
- 2-Step Verification enabled
- App password generated

**Setup**:
1. Visit https://myaccount.google.com/apppasswords
2. Create app password: "ASX Stock Scanner"
3. Copy 16-character password
4. Update `screening_config.json`

**Configuration**:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_gmail@gmail.com",
  "smtp_password": "abcdabcdabcdabcd",
  "use_tls": true
}
```

### Option 2: Outlook/Hotmail

**Requirements**:
- Outlook/Hotmail account
- No app password needed

**Configuration**:
```json
{
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_username": "your_email@outlook.com",
  "smtp_password": "your_outlook_password",
  "use_tls": true
}
```

### Option 3: SendGrid (High Volume)

**Requirements**:
- SendGrid account (free tier: 100 emails/day)
- API key generated

**Setup**:
1. Sign up at https://sendgrid.com
2. Generate API key
3. Update configuration

**Configuration**:
```json
{
  "smtp_server": "smtp.sendgrid.net",
  "smtp_port": 587,
  "smtp_username": "apikey",
  "smtp_password": "SG.your_api_key_here",
  "use_tls": true
}
```

---

## 📚 Documentation Guide

### Quick Start
- **README.md** (this file) - Overview & quick start

### Email Setup
- **FINAL_EMAIL_SETUP_INSTRUCTIONS.md** - Step-by-step email setup
- **PROTONMAIL_RECEIVING_EXPLAINED.md** - ProtonMail receiving explained
- **PROTONMAIL_SMTP_SOLUTION.md** - All SMTP options

### Scheduler Setup
- **EMAIL_AND_SCHEDULER_SETUP.md** - Complete setup guide
- **QUICK_START_EMAIL_SCHEDULER.md** - Quick reference
- **EMAIL_SCHEDULER_DELIVERY_SUMMARY.md** - Full summary

### Commands
- **COMMAND_REFERENCE.txt** - Quick command reference

---

## 🛠️ Troubleshooting

### Email Not Sending

**Check configuration**:
```bash
python3 -c "
import json
with open('models/config/screening_config.json') as f:
    config = json.load(f)
    email = config['email_notifications']
    print(f'Enabled: {email[\"enabled\"]}')
    print(f'SMTP: {email[\"smtp_server\"]}:{email[\"smtp_port\"]}')
    print(f'Username: {email[\"smtp_username\"]}')
    print(f'Recipients: {email[\"recipient_emails\"]}')"
```

**Test SMTP connection**:
```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email@gmail.com', 'your_password')
print("✅ SMTP login successful!")
server.quit()
```

### Scheduler Not Running

**Check process**:
```bash
ps aux | grep schedule_pipeline
```

**Restart**:
```bash
python3 schedule_pipeline.py
```

### Pipeline Errors

**Check logs**:
```bash
grep ERROR logs/screening/overnight_pipeline.log | tail -20
```

**Common issues**:
- Network connectivity
- Missing dependencies
- Insufficient memory

---

## 📋 System Requirements

### Python Version
- Python 3.8 or higher

### Required Packages
```
yahooquery>=2.3.0       # Yahoo Finance API
pandas>=2.0.0           # Data manipulation
numpy>=1.24.0           # Numerical computing
yfinance>=0.2.28        # Market data
pytz>=2023.3            # Timezone handling
schedule>=1.2.0         # Job scheduling
```

### Optional Packages (ML Features)
```
tensorflow>=2.10.0      # LSTM models
keras>=2.10.0           # Neural networks
transformers>=4.25.0    # FinBERT sentiment
torch>=1.13.0           # PyTorch backend
```

### Disk Space
- Minimum: 500 MB
- Recommended: 2 GB (for logs and reports)

### Memory
- Minimum: 2 GB RAM
- Recommended: 4 GB RAM (for ML features)

---

## 🎯 Next Steps

1. **Extract package** to your desired location
2. **Install dependencies**: `pip install -r requirements_scheduler.txt`
3. **Configure email**: Edit `models/config/screening_config.json`
4. **Test email**: `python3 test_email_quick.py`
5. **Start scheduler**: `python3 schedule_pipeline.py`
6. **Check tomorrow** at 5:45 AM for first report!

---

## 📞 Support

### Log Files for Debugging
When reporting issues, provide:
1. `logs/scheduler/scheduler.log` (last 50 lines)
2. `logs/screening/overnight_pipeline.log` (full file)
3. `logs/screening/email_notifications.log` (last 20 lines)
4. Error message and timestamp

### Configuration Check
```bash
python3 -c "
import json
with open('models/config/screening_config.json') as f:
    config = json.load(f)
    print('Email enabled:', config['email_notifications']['enabled'])
    print('Recipients:', config['email_notifications']['recipient_emails'])
    print('SMTP server:', config['email_notifications']['smtp_server'])"
```

---

## 📄 License

This software is provided as-is for personal use.

---

## 🎊 Version Information

**Version**: 4.4.4  
**Release Date**: 2025-11-12  
**Package**: Complete Deployment with Email & Scheduler

**Features**:
- ✅ Full stock screening system
- ✅ LSTM neural network predictions
- ✅ FinBERT sentiment analysis
- ✅ Email notifications (Gmail/Outlook/SendGrid)
- ✅ 5:00 AM AEST scheduler
- ✅ Comprehensive documentation

---

**Enjoy automated stock screening reports every morning!** 📊📧🚀
is
- ✅ Email notifications (Gmail/Outlook/SendGrid)
- ✅ 5:00 AM AEST scheduler
- ✅ Comprehensive documentation

---

**Enjoy automated stock screening reports every morning!** 📊📧🚀

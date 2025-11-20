# ASX Overnight Stock Scanner v4.4.4 - Deployment Package

**Complete System with Email Notifications & 5:00 AM Scheduler**

---

## 📦 Package Contents

This deployment package includes:

- ✅ **Complete source code** (models + finbert_v4.4.4)
- ✅ **Email notification system** (Gmail pre-configured!)
- ✅ **5:00 AM AEST scheduler** (automated daily runs)
- ✅ **Automated installers** (Windows .bat & Linux/Mac .sh)
- ✅ **Gmail account ready** (finbertmorningreport@gmail.com)
- ✅ **Configuration files** (ready to use)
- ✅ **Test scripts** (email & pipeline testing)
- ✅ **Comprehensive documentation** (10 guides)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies (2 minutes)

**Automated Installation** (Recommended):

- **Windows**: Double-click `INSTALL_DEPENDENCIES.bat`
- **Linux/Mac**: Run `./INSTALL_DEPENDENCIES.sh`

**Manual Installation**:

```bash
# Install Python packages
pip install yahooquery pandas numpy yfinance pytz schedule

# For full ML features (optional)
pip install tensorflow keras transformers torch
```

### Step 2: Configure Email (5 minutes)

**Pre-configured Gmail Account** (Ready to use):
- **Account**: finbertmorningreport@gmail.com
- **Password**: Finbert@295
- **Recipients**: finbert_morning_report@proton.me, david.osland@gmail.com

**⚠️ IMPORTANT**: You must generate a Gmail App Password first!

1. **Read the setup guide**: `GMAIL_APP_PASSWORD_SETUP.md`
2. **Generate app password**: https://myaccount.google.com/apppasswords
3. **Update configuration**: Replace password in `models/config/screening_config.json` line 90

**Alternative SMTP Providers**:

- **Option A: Gmail** (Recommended - Already Configured!)
  - Get app password: https://myaccount.google.com/apppasswords
  - Configure: `smtp.gmail.com:587`

- **Option B: Outlook** (Easiest)
  - Use your Outlook account
  - Configure: `smtp-mail.outlook.com:587`

- **Option C: SendGrid** (High volume)
  - Free tier: 100 emails/day
  - Configure: `smtp.sendgrid.net:587`

**Edit configuration**:
```bash
nano models/config/screening_config.json
```

Update lines 87-94:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "finbertmorningreport@gmail.com",
  "smtp_password": "YOUR_16_CHARACTER_APP_PASSWORD_HERE",
  "sender_email": "finbertmorningreport@gmail.com",
  "recipient_emails": [
    "finbert_morning_report@proton.me",
    "david.osland@gmail.com"
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
├── INSTALL_DEPENDENCIES.bat            # Windows installer
├── INSTALL_DEPENDENCIES.sh             # Linux/Mac installer
├── GMAIL_APP_PASSWORD_SETUP.md         # Gmail setup guide
│
└── Documentation/
    ├── README.md                       # This file
    ├── EMAIL_AND_SCHEDULER_SETUP.md    # Complete setup guide
    ├── QUICK_START_EMAIL_SCHEDULER.md  # Quick reference
    ├── FINAL_EMAIL_SETUP_INSTRUCTIONS.md
    ├── PROTONMAIL_SMTP_SOLUTION.md
    ├── PROTONMAIL_RECEIVING_EXPLAINED.md
    ├── EMAIL_SCHEDULER_DELIVERY_SUMMARY.md
    ├── DEPLOYMENT_MANIFEST.txt         # Package inventory
    └── COMMAND_REFERENCE.txt           # Quick commands
```

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

## 🧪 Testing

### Test Email Notification

```bash
python3 test_email_quick.py
```

**Expected**:
```
✅ TEST EMAIL SENT SUCCESSFULLY!
Check your inbox: finbertmorningreport@gmail.com
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

## 🛠️ Troubleshooting

### Email Not Sending

**Most Common Issue**: Gmail requires App Password (not regular password)

1. Read `GMAIL_APP_PASSWORD_SETUP.md`
2. Visit https://myaccount.google.com/apppasswords
3. Generate app password
4. Update `models/config/screening_config.json` line 90

**Test SMTP connection**:
```bash
python3 test_email_quick.py
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
2. **Install dependencies**: Run `INSTALL_DEPENDENCIES.bat` (Windows) or `./INSTALL_DEPENDENCIES.sh` (Linux/Mac)
3. **Generate Gmail App Password**: Follow `GMAIL_APP_PASSWORD_SETUP.md`
4. **Update config**: Replace password in `models/config/screening_config.json` line 90
5. **Test email**: `python3 test_email_quick.py`
6. **Start scheduler**: `python3 schedule_pipeline.py`
7. **Check tomorrow** at 5:45 AM for first report!

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
- ✅ Email notifications (Gmail pre-configured!)
- ✅ 5:00 AM AEST scheduler
- ✅ Automated installers (Windows/Linux/Mac)
- ✅ Gmail setup guide included
- ✅ Comprehensive documentation

---

**Enjoy automated stock screening reports every morning!** 📊📧🚀

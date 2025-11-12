# 🚀 Windows 11 Deployment Guide - Overnight Stock Screening System

Complete deployment and setup instructions for Windows 11.

---

## 📦 Package Contents

```
overnight-stock-screener/
├── models/                          # Core modules
│   ├── screening/                  # Screening system
│   │   ├── stock_scanner.py       # Stock validation & analysis
│   │   ├── spi_monitor.py         # SPI 200 futures tracking
│   │   ├── batch_predictor.py     # Ensemble prediction
│   │   ├── opportunity_scorer.py  # Composite scoring
│   │   ├── report_generator.py    # HTML report generation
│   │   ├── overnight_pipeline.py  # Main orchestrator
│   │   ├── send_notification.py   # Email notifications ⭐ NEW
│   │   └── lstm_trainer.py        # LSTM training ⭐ NEW
│   ├── config/                     # Configuration files
│   │   ├── asx_sectors.json       # 240 ASX stocks
│   │   └── screening_config.json  # System configuration
│   └── lstm/                       # LSTM models directory
├── scripts/                         # Test scripts
│   └── screening/                  # Screening tests
│       ├── test_email_notifications.py  ⭐ NEW
│       ├── test_lstm_training.py        ⭐ NEW
│       └── test_full_pipeline.py
├── reports/                         # Output directory
│   ├── morning_reports/            # HTML reports
│   └── pipeline_state/             # JSON state files
├── logs/                            # Log files
│   ├── screening/                  # Pipeline logs
│   └── lstm_training/              # Training logs
├── RUN_OVERNIGHT_SCREENER.bat      # Main execution
├── RUN_OVERNIGHT_SCREENER_TEST.bat # Test mode
├── RUN_LSTM_TRAINING.bat           # LSTM training ⭐ NEW
├── SCHEDULE_SCREENER.bat           # Task Scheduler setup
├── CHECK_SCREENER_STATUS.bat       # Status dashboard
├── CHECK_MODEL_STATUS.bat          # Model status ⭐ NEW
└── requirements.txt                # Python dependencies
```

---

## 🔧 System Requirements

### **Hardware**
- **CPU**: Intel Core i5 or AMD Ryzen 5 (minimum)
- **RAM**: 8GB (16GB recommended)
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### **Software**
- **OS**: Windows 11 (Windows 10 compatible)
- **Python**: 3.8 or higher
- **Administrator**: Required for Task Scheduler setup

---

## 📥 Installation Steps

### **Step 1: Extract Package**

Extract the ZIP file to a permanent location:
```
C:\OvernightStockScreener\
```

⚠️ **Important**: Do not use temporary folders or Desktop.

### **Step 2: Install Python**

1. Download Python 3.11 from https://www.python.org/downloads/
1. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
   - Click "Install Now"
1. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### **Step 3: Create Virtual Environment**

Open Command Prompt as Administrator:

```cmd
cd C:\OvernightStockScreener
python -m venv venv
venv\Scripts\activate
```

### **Step 4: Install Dependencies**

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**Key Dependencies**:
- `tensorflow` - LSTM models
- `yfinance` - Stock data
- `pandas`, `numpy` - Data processing
- `scikit-learn` - ML utilities
- `pytz` - Timezone handling

### **Step 5: Configure Email Notifications** ⭐ NEW

Edit `models/config/screening_config.json`:

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your_email@gmail.com",
    "smtp_password": "your_app_password",
    "use_tls": true,
    "sender_email": "your_email@gmail.com",
    "recipient_emails": [
      "recipient1@example.com",
      "recipient2@example.com"
    ],
    "send_morning_report": true,
    "send_alerts": true,
    "send_errors": true,
    "alert_threshold": 80
  }
}
```

**Gmail Setup**:
1. Enable 2-Factor Authentication
1. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the generated password
1. Use App Password in `smtp_password` field

**Other SMTP Providers**:
- **Outlook**: `smtp.office365.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's settings

### **Step 6: Run Tests**

Verify installation:

```cmd
REM Test email notifications
python scripts\screening\test_email_notifications.py

REM Test LSTM training system
python scripts\screening\test_lstm_training.py

REM Test full pipeline (quick test)
RUN_OVERNIGHT_SCREENER_TEST.bat
```

---

## ⚙️ Configuration

### **Core Settings** (`models/config/screening_config.json`)

```json
{
  "schedule": {
    "start_time": "22:00",
    "end_time": "07:00",
    "timezone": "Australia/Sydney"
  },
  "screening": {
    "stocks_per_sector": 30,
    "max_total_stocks": 240,
    "opportunity_threshold": 65,
    "top_picks_count": 10
  },
  "lstm_training": {
    "enabled": true,
    "max_models_per_night": 20,
    "stale_threshold_days": 7,
    "epochs": 50,
    "batch_size": 32
  }
}
```

### **Email Notification Types**

1. **Morning Report** (Daily at 7 AM)
   - HTML report attachment
   - Summary statistics
   - Top 10 opportunities
   - Sector performance

2. **High-Confidence Alerts** (Score ≥ 80)
   - Immediate notification
   - Detailed opportunity analysis
   - Price and confidence data

3. **Error Notifications**
   - Pipeline failures
   - Stack trace included
   - Phase information

---

## 🏃 Running the System

### **Manual Execution**

#### **1. Quick Test** (5 stocks, ~7 seconds)
```cmd
RUN_OVERNIGHT_SCREENER_TEST.bat
```

#### **2. Full Run** (240 stocks, ~10 minutes)
```cmd
RUN_OVERNIGHT_SCREENER.bat
```

#### **3. LSTM Training** ⭐ NEW
```cmd
RUN_LSTM_TRAINING.bat

REM Train specific stocks
RUN_LSTM_TRAINING.bat --symbols ANZ.AX CBA.AX

REM Limit training count
RUN_LSTM_TRAINING.bat --max-stocks 10
```

#### **4. Check Status**
```cmd
REM Pipeline status
CHECK_SCREENER_STATUS.bat

REM Model status
CHECK_MODEL_STATUS.bat
```

### **Scheduled Execution**

Setup nightly runs at 10 PM:

```cmd
REM Run as Administrator
SCHEDULE_SCREENER.bat
```

This creates a Windows Task Scheduler task:
- **Name**: `OvernightStockScreener`
- **Schedule**: Daily at 10:00 PM
- **Action**: Run `RUN_OVERNIGHT_SCREENER.bat`
- **Priority**: Highest

**Verify Task**:
1. Open Task Scheduler (`taskschd.msc`)
1. Find `OvernightStockScreener`
1. Right-click → Run (test)

---

## 📊 Output Files

### **HTML Reports** (`reports/morning_reports/`)

```
2025-11-07_market_report.html
```

**Sections**:
1. Market Overview (SPI sentiment, US markets)
1. Top 10 Opportunities (detailed cards)
1. Sector Performance (8 sectors)
1. Watch List (near-buy signals)
1. Caution Stocks (sell signals)
1. System Performance (statistics)

### **Pipeline State** (`reports/pipeline_state/`)

```
2025-11-07_pipeline_state.json
```

**Contents**:
- Summary statistics
- Top opportunities (full list)
- Sector breakdown
- SPI sentiment data
- Timestamp and duration

### **Log Files** (`logs/`)

```
logs/screening/overnight_pipeline.log
logs/screening/email_notifications.log  ⭐ NEW
logs/lstm_training/lstm_training.log    ⭐ NEW
```

---

## 🧪 Testing

### **Email Notification Test**

```cmd
python scripts\screening\test_email_notifications.py
```

**Expected Output**:
```
✅ Email notifier initialized
✅ Test notification sent
✅ Morning report email sent
✅ Alert email sent
✅ Error notification sent
```

### **LSTM Training Test**

```cmd
python scripts\screening\test_lstm_training.py
```

**Expected Output**:
```
✅ LSTM trainer initialized
✅ Training statistics retrieved
✅ Stale model check completed
✅ Training queue created
✅ Training system validated
```

### **Full Pipeline Test**

```cmd
python scripts\screening\test_full_pipeline.py
```

**Expected Output**:
```
✅ Phase 1: Market Sentiment
✅ Phase 2: Stock Scanning
✅ Phase 3: Batch Prediction
✅ Phase 4: Opportunity Scoring
✅ Phase 5: Report Generation
✅ Phase 6: Email Notifications  ⭐ NEW
```

---

## 🔧 Troubleshooting

### **Email Not Sending**

**Problem**: Emails not being delivered

**Solutions**:
1. Check `enabled: true` in config
1. Verify SMTP credentials
1. Use App Password (not regular password)
1. Check firewall settings (port 587)
1. Test with: `python models\screening\send_notification.py --type test`

**Test Command**:
```cmd
python models\screening\send_notification.py --type test
```

### **LSTM Training Fails**

**Problem**: Model training errors

**Solutions**:
1. Check GPU/CPU availability
1. Verify TensorFlow installation
1. Ensure sufficient RAM (8GB minimum)
1. Check disk space (2GB per model)
1. Review logs: `logs\lstm_training\lstm_training.log`

**Test Command**:
```cmd
python models\screening\lstm_trainer.py --mode stats
```

### **Pipeline Hangs**

**Problem**: Pipeline doesn't complete

**Solutions**:
1. Check internet connection
1. Verify yfinance can access data
1. Review timeout settings in config
1. Check logs for specific errors
1. Run test mode first

### **Reports Not Generating**

**Problem**: HTML reports missing

**Solutions**:
1. Check `reports/` directory permissions
1. Verify report_generator module
1. Check disk space
1. Review error logs

---

## 🎯 Daily Workflow

### **Automated Overnight Process**

```
10:00 PM - Task Scheduler triggers
   ↓
10:00-10:15 PM - Stock scanning (240 stocks)
   ↓
10:15-10:20 PM - Batch prediction
   ↓
10:20-10:21 PM - Opportunity scoring
   ↓
10:21-10:22 PM - Report generation
   ↓
10:22-10:23 PM - Email notifications ⭐ NEW
   ↓
10:23 PM - [OPTIONAL] LSTM training (20 stocks, ~2 hours)
   ↓
7:00 AM - Morning report email delivered
```

### **Morning Review**

1. **Check Email**
   - Review morning report (HTML attachment)
   - Check high-confidence alerts

2. **Review Reports**
   - Open latest HTML report
   - Review top opportunities
   - Check sector performance

3. **Verify Status**
   - Run `CHECK_SCREENER_STATUS.bat`
   - Check for errors
   - Verify completion time

---

## 📈 Performance Metrics

### **Test Mode** (5 stocks, 1 sector)
- **Duration**: 6-7 seconds
- **Memory**: ~200MB
- **Output**: Small HTML report (~20KB)

### **Full Mode** (240 stocks, 8 sectors)
- **Duration**: 8-12 minutes
- **Memory**: ~500MB
- **Output**: Full HTML report (~2MB)

### **LSTM Training** (20 stocks)
- **Duration**: 1.5-2 hours
- **Memory**: ~2GB per model
- **Output**: .h5 model files

---

## 🔒 Security Best Practices

1. **Email Credentials**
   - Use App Passwords (never regular passwords)
   - Store config file securely
   - Don't commit credentials to git

2. **File Permissions**
   - Restrict config file access
   - Use Windows file encryption
   - Regular backups

3. **Network Security**
   - Use TLS/SSL (port 587)
   - Verify SMTP certificate
   - Monitor email logs

---

## 🆘 Support & Resources

### **Documentation**
- **Main README**: `README.md`
- **Phase 3 Plan**: `OVERNIGHT_STOCK_SCREENER_PLAN.md`
- **This Guide**: `README_DEPLOYMENT.md`

### **Logs Location**
- Pipeline: `logs/screening/overnight_pipeline.log`
- Emails: `logs/screening/email_notifications.log`
- Training: `logs/lstm_training/lstm_training.log`

### **Common Commands**

```cmd
REM Run overnight screener (test mode)
RUN_OVERNIGHT_SCREENER_TEST.bat

REM Run overnight screener (full mode)
RUN_OVERNIGHT_SCREENER.bat

REM Train LSTM models
RUN_LSTM_TRAINING.bat

REM Check pipeline status
CHECK_SCREENER_STATUS.bat

REM Check model status
CHECK_MODEL_STATUS.bat

REM Schedule nightly runs
SCHEDULE_SCREENER.bat

REM Send test email
python models\screening\send_notification.py --type test

REM Check LSTM model statistics
python models\screening\lstm_trainer.py --mode stats
```

---

## ✅ Post-Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Email configuration complete
- [ ] Test mode successful
- [ ] Email notifications working
- [ ] LSTM training tested
- [ ] Task Scheduler configured
- [ ] First overnight run completed
- [ ] Morning report received

---

## 🎉 You're Ready!

The Overnight Stock Screening System is now fully deployed with:

✅ **Email Notifications** - Morning reports, alerts, errors
✅ **LSTM Training** - Automated model updates
✅ **Full Automation** - Scheduled nightly execution
✅ **Professional Reports** - HTML with charts and analysis
✅ **240 ASX Stocks** - Complete market coverage
✅ **8 Sectors** - Diversified screening

**Next Steps**:
1. Run test mode to verify setup
1. Review first morning report
1. Adjust configuration as needed
1. Monitor daily execution
1. Review and act on opportunities

---

**Version**: Phase 3 Complete
**Last Updated**: 2025-11-07
**Features**: Parts 1-4 (Report Generation, Pipeline Orchestration, Email Notifications, LSTM Training)

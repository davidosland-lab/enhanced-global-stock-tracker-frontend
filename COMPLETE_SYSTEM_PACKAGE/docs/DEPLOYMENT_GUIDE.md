# Overnight Stock Screening System - Deployment Guide

## Windows 11 Deployment Package

This guide explains how to deploy and run the Overnight Stock Screening System on Windows 11.

## 📦 Package Contents

### Core System Files
```
overnight-stock-screener/
├── models/
│   ├── screening/              # Screening modules
│   │   ├── stock_scanner.py
│   │   ├── spi_monitor.py
│   │   ├── batch_predictor.py
│   │   ├── opportunity_scorer.py
│   │   ├── report_generator.py
│   │   ├── send_notification.py     ⭐ NEW (Phase 3 Part 3)
│   │   ├── lstm_trainer.py          ⭐ NEW (Phase 3 Part 4)
│   │   └── overnight_pipeline.py
│   ├── config/                 # Configuration files
│   │   ├── asx_sectors.json
│   │   └── screening_config.json
│   └── lstm/                   # LSTM models directory
├── scripts/
│   └── screening/              # Test scripts
│       ├── test_stock_scanner.py
│       ├── test_spi_monitor.py
│       ├── test_batch_predictor.py
│       ├── test_opportunity_scorer.py
│       ├── test_report_generator.py
│       ├── test_email_notifications.py  ⭐ NEW
│       ├── test_lstm_trainer.py         ⭐ NEW
│       └── test_full_pipeline.py
├── RUN_OVERNIGHT_SCREENER.bat
├── RUN_OVERNIGHT_SCREENER_TEST.bat
├── RUN_LSTM_TRAINING.bat           ⭐ NEW
├── SCHEDULE_SCREENER.bat
├── CHECK_SCREENER_STATUS.bat
├── CHECK_MODEL_STATUS.bat          ⭐ NEW
├── requirements.txt
└── DEPLOYMENT_GUIDE.md
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Extract Package
```bash
# Extract the ZIP file to a location like:
C:\Users\YourName\overnight-stock-screener\
```

### Step 2: Install Python
- Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
- ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

### Step 3: Install Dependencies
```batch
cd C:\Users\YourName\overnight-stock-screener
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Run Test Mode
```batch
# Quick test (5 stocks, ~7 seconds)
RUN_OVERNIGHT_SCREENER_TEST.bat
```

### Step 5: Check Output
```batch
# View generated report
cd reports\morning_reports
# Open the latest HTML file in your browser
```

## ⚙️ Configuration

### Basic Configuration

Edit `models/config/screening_config.json`:

```json
{
  "screening": {
    "stocks_per_sector": 30,
    "opportunity_threshold": 65,
    "top_picks_count": 10
  },
  "schedule": {
    "start_time": "22:00",
    "timezone": "Australia/Sydney"
  }
}
```

### Email Notifications (Optional) ⭐ NEW

To enable email notifications, edit `models/config/screening_config.json`:

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your_email@gmail.com",
    "smtp_password": "your_app_password",
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
1. Enable 2-factor authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular Gmail password)

### LSTM Training (Optional) ⭐ NEW

LSTM training is enabled by default. Configuration in `screening_config.json`:

```json
{
  "lstm_training": {
    "enabled": true,
    "max_models_per_night": 20,
    "stale_threshold_days": 7,
    "epochs": 50,
    "batch_size": 32
  }
}
```

## 🎯 Usage

### Daily Operations

#### 1. Manual Run (Full Mode)
```batch
# Run complete screening (240 stocks, ~10 minutes)
RUN_OVERNIGHT_SCREENER.bat
```

#### 2. Test Run (Quick)
```batch
# Test with 5 stocks (~7 seconds)
RUN_OVERNIGHT_SCREENER_TEST.bat
```

#### 3. Check Status
```batch
# View execution logs and recent reports
CHECK_SCREENER_STATUS.bat
```

#### 4. Train LSTM Models ⭐ NEW
```batch
# Train priority stocks based on opportunity scores
RUN_LSTM_TRAINING.bat

# Check model staleness status
CHECK_MODEL_STATUS.bat

# Train specific stocks
RUN_LSTM_TRAINING.bat --symbols ANZ.AX CBA.AX BHP.AX

# Limit training to 10 stocks
RUN_LSTM_TRAINING.bat --max-stocks 10
```

#### 5. Test Email Notifications ⭐ NEW
```batch
# Test email configuration
python scripts/screening/test_email_notifications.py

# Send test email
python models/screening/send_notification.py --type test
```

### Automated Scheduling

#### Schedule Nightly Run (10 PM)
```batch
# Run as Administrator (right-click → Run as administrator)
SCHEDULE_SCREENER.bat
```

This creates a Windows Task Scheduler job that:
- Runs at 10:00 PM daily
- Completes overnight processing
- Generates morning report by 7:00 AM
- Sends email notifications (if enabled)
- Trains priority LSTM models (if enabled)

#### View Scheduled Task
```batch
# Open Task Scheduler
taskschd.msc

# Look for: "OvernightStockScreener"
```

#### Modify Schedule
```batch
# In Task Scheduler, right-click the task → Properties
# Change triggers, actions, or conditions as needed
```

## 📊 Output Files

### Morning Reports
```
reports/morning_reports/
├── 2025-11-07_market_report.html    # Daily HTML report
├── 2025-11-07_market_report.json    # JSON data export
└── ...
```

### Pipeline State
```
reports/pipeline_state/
└── 2025-11-07_pipeline_state.json   # Execution state
```

### Logs
```
logs/screening/
├── overnight_pipeline.log           # Main execution log
├── email_notifications.log          # Email log ⭐ NEW
└── lstm_training.log                # Training log ⭐ NEW

logs/lstm_training/
└── 2025-11-07_training_log.jsonl    # Detailed training log ⭐ NEW
```

### LSTM Models ⭐ NEW
```
models/lstm/
├── ANZ.AX_lstm_model.h5
├── CBA.AX_lstm_model.h5
├── BHP.AX_lstm_model.h5
└── ...
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Not Found
```
Error: 'python' is not recognized...
```
**Solution**: 
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python39\python.exe`

#### 2. Module Import Error
```
Error: No module named 'yfinance'
```
**Solution**:
```batch
venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Email Sending Fails ⭐ NEW
```
Error: Authentication failed
```
**Solutions**:
- Use Gmail App Password (not regular password)
- Enable "Less secure app access" (not recommended)
- Check SMTP settings in config
- Run test: `python models/screening/send_notification.py --type test`

#### 4. LSTM Training Errors ⭐ NEW
```
Error: Failed to load LSTM model
```
**Solutions**:
- Check `models/lstm/` directory exists
- Verify TensorFlow/Keras installation: `pip install tensorflow`
- Check training logs: `logs/lstm_training/lstm_training.log`
- Run model status check: `CHECK_MODEL_STATUS.bat`

#### 5. Permission Denied (Scheduler)
```
Error: Access is denied
```
**Solution**: Run `SCHEDULE_SCREENER.bat` as Administrator

#### 6. Network/API Errors
```
Error: Unable to fetch stock data
```
**Solutions**:
- Check internet connection
- Verify Yahoo Finance is accessible
- Try running test mode first
- Check firewall settings

#### 7. Report Generation Fails
```
Error: Failed to generate report
```
**Solutions**:
- Check `reports/morning_reports/` directory exists
- Verify write permissions
- Check available disk space
- Review logs: `logs/screening/overnight_pipeline.log`

### Log Analysis

View recent errors:
```batch
# Last 50 lines of main log
powershell Get-Content logs\screening\overnight_pipeline.log -Tail 50

# Search for errors
findstr /C:"ERROR" logs\screening\overnight_pipeline.log
```

### Performance Issues

If the pipeline is slow:
1. Reduce `stocks_per_sector` in config (default: 30)
2. Decrease `max_workers` in config (default: 4)
3. Run during off-peak hours
4. Check CPU/memory usage

## 🔐 Security Best Practices

### 1. Email Credentials
- Never commit `screening_config.json` with real passwords
- Use App Passwords instead of account passwords
- Restrict file permissions:
  ```batch
  icacls models\config\screening_config.json /inheritance:r /grant:r %USERNAME%:F
  ```

### 2. API Keys (if applicable)
- Store in environment variables
- Never hardcode in scripts
- Use `.env` file (add to `.gitignore`)

### 3. File Permissions
- Restrict access to config directory
- Secure log files (may contain sensitive data)
- Use Windows User Account Control (UAC)

## 📈 Performance Metrics

### Typical Execution Times

| Mode | Stocks | Time | Description |
|------|--------|------|-------------|
| Test | 5 | ~7s | Quick validation |
| Single Sector | 30 | ~2min | One sector only |
| Full Run | 240 | ~10min | All 8 sectors |
| LSTM Training | 20 | ~30-60min | Priority models ⭐ NEW |

### System Requirements

- **OS**: Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: 2+ cores recommended
- **Disk**: 2GB free space
- **Network**: Stable internet connection

## 🆘 Support

### Getting Help

1. **Check Logs**: Review execution logs for error details
2. **Test Mode**: Run test mode to isolate issues
3. **Documentation**: Read inline code comments
4. **Email Test**: Verify email configuration with test command
5. **Model Status**: Check LSTM model health with status script

### Contact Information

For technical support or questions:
- Review logs: `logs/screening/`
- Check status: `CHECK_SCREENER_STATUS.bat`
- Test components individually
- Email test: `python models/screening/send_notification.py --type test`
- Model check: `CHECK_MODEL_STATUS.bat`

## 📋 System Architecture

### Complete Workflow (7 Phases) ⭐ UPDATED

```
10:00 PM - Task Scheduler Triggers
    ↓
Phase 1: Market Sentiment Analysis
    → SPI 200 futures data
    → US market indices
    ↓
Phase 2: Stock Scanning (240 stocks, 8 sectors)
    → Technical validation
    → Price pattern analysis
    ↓
Phase 3: Batch Prediction (4 workers)
    → LSTM model (45% weight)
    → Trend analysis (25%)
    → Technical indicators (15%)
    → Sentiment analysis (15%)
    ↓
Phase 4: Opportunity Scoring (0-100)
    → Composite ranking
    ↓
Phase 5: Report Generation
    → HTML morning report
    → JSON data export
    ↓
Phase 6: Email Notifications ⭐ NEW
    → Morning report delivery
    → High-confidence alerts
    → Error notifications
    ↓
Phase 7: LSTM Model Training ⭐ NEW
    → Detect stale models (>7 days)
    → Train priority stocks
    → Update model files
    ↓
7:00 AM - Report Ready
```

### Module Dependencies

```
overnight_pipeline.py
├── stock_scanner.py
├── spi_monitor.py
├── batch_predictor.py
├── opportunity_scorer.py
├── report_generator.py
├── send_notification.py      ⭐ NEW
└── lstm_trainer.py           ⭐ NEW
```

## 🎓 Advanced Features

### Custom Stock Lists

Edit `models/config/asx_sectors.json`:
```json
{
  "sectors": {
    "Financials": {
      "stocks": ["ANZ.AX", "CBA.AX", "WBC.AX", "NAB.AX"]
    }
  }
}
```

### Priority Training ⭐ NEW

The LSTM trainer automatically prioritizes stocks based on:
1. Opportunity score (higher score = higher priority)
2. Model staleness (older models = higher priority)
3. Recent trading activity

You can manually specify stocks:
```batch
RUN_LSTM_TRAINING.bat --symbols ANZ.AX CBA.AX BHP.AX RIO.AX
```

### Email Alert Customization ⭐ NEW

Adjust alert threshold in `screening_config.json`:
```json
{
  "email_notifications": {
    "alert_threshold": 80,    # Only alert for scores >= 80
    "send_alerts": true       # Enable/disable alerts
  }
}
```

### Custom Reporting

Modify `models/screening/report_generator.py` to:
- Add custom sections
- Change styling/colors
- Include additional metrics
- Customize email templates

## 📝 Version History

### Phase 3 Complete (2025-11-07) ⭐ CURRENT
- ✅ Email notification system with SMTP
- ✅ LSTM training automation with staleness detection
- ✅ Priority-based training queue
- ✅ HTML email templates
- ✅ Training progress tracking
- ✅ Complete Windows deployment package

### Phase 2 Complete (2025-11-06)
- ✅ Report generation (HTML + JSON)
- ✅ Pipeline orchestration
- ✅ Windows batch scripts
- ✅ Task Scheduler integration

### Phase 2 Complete (2025-11-05)
- ✅ Stock scanner
- ✅ SPI monitor
- ✅ Batch predictor
- ✅ Opportunity scorer

### Phase 1 Complete (2025-11-04)
- ✅ Core ML models
- ✅ Database infrastructure
- ✅ Data collection

## 🎯 Next Steps

After deployment:

1. **Run Test Mode**: Verify everything works
   ```batch
   RUN_OVERNIGHT_SCREENER_TEST.bat
   ```

2. **Configure Email** (Optional): Set up SMTP settings

3. **Schedule Overnight Run**: Set up automated execution
   ```batch
   SCHEDULE_SCREENER.bat
   ```

4. **Monitor First Run**: Check logs and reports

5. **Train LSTM Models**: Initialize priority models
   ```batch
   RUN_LSTM_TRAINING.bat
   ```

6. **Review Morning Report**: Check HTML output quality

7. **Optimize Settings**: Adjust config based on results

---

## 📞 Need Help?

- **Logs**: Check `logs/screening/` for detailed execution logs
- **Status**: Run `CHECK_SCREENER_STATUS.bat` for system health
- **Models**: Run `CHECK_MODEL_STATUS.bat` for LSTM model status
- **Test**: Use test scripts in `scripts/screening/`
- **Email**: Test with `python models/screening/send_notification.py --type test`

**System Status**: ✅ PRODUCTION READY
**Phase 3**: ✅ COMPLETE
**Last Updated**: 2025-11-07

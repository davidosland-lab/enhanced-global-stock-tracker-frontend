# Email Notifications & Scheduler Setup Guide

**Version**: 4.4.4  
**Date**: 2025-11-12  
**For**: david.osland@gmail.com

---

## 📧 Email Notifications Setup

### Overview

The system is now configured to send three types of email notifications:

1. **Morning Report** - Daily HTML report with top opportunities
2. **High-Confidence Alerts** - Urgent alerts for opportunities ≥80 score
3. **Error Notifications** - Alerts when pipeline fails

---

## ⚙️ Configuration Status

### Current Configuration

✅ **Email enabled**: `true`  
✅ **Recipient**: `david.osland@gmail.com`  
✅ **SMTP Server**: `smtp.gmail.com:587`  
✅ **All notification types enabled**: Morning report, alerts, errors

**Configuration File**: `models/config/screening_config.json`

---

## 🔐 Gmail App Password Setup

### IMPORTANT: You Need a Gmail App Password

Google requires "App Passwords" for third-party applications accessing Gmail SMTP.

### Steps to Generate App Password:

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/
   - Sign in with `david.osland@gmail.com`

2. **Enable 2-Step Verification** (if not already enabled)
   - Go to: Security → 2-Step Verification
   - Follow prompts to enable

3. **Generate App Password**
   - Go to: Security → 2-Step Verification → App passwords
   - Or direct link: https://myaccount.google.com/apppasswords
   
4. **Create New App Password**
   - App name: "ASX Stock Scanner"
   - Click "Generate"
   - **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)

5. **Add Password to Configuration**

   ```bash
   cd /home/user/webapp
   nano models/config/screening_config.json
   ```

   Find this line:
   ```json
   "smtp_password": "YOUR_GMAIL_APP_PASSWORD_HERE",
   ```

   Replace with your app password (remove spaces):
   ```json
   "smtp_password": "xxxxxxxxxxxxxxxx",
   ```

   Save and exit: `Ctrl+X`, `Y`, `Enter`

---

## ✅ Test Email Notifications

### Quick Test

```bash
cd /home/user/webapp
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'models' / 'screening'))
from send_notification import EmailNotifier
notifier = EmailNotifier()
result = notifier.send_notification(
    notification_type='success',
    subject='🧪 Test Email - Stock Scanner System',
    body='This is a test email from your overnight stock screening system. If you receive this, email notifications are working correctly!'
)
print('✅ Test email sent!' if result else '❌ Email failed - check app password')
"
```

### Expected Output

**If successful**:
```
✅ Email notification sent: success - 🧪 Test Email - Stock Scanner System
✅ Test email sent!
```

**If failed**:
```
❌ Failed to send email notification: (535, b'5.7.8 Username and Password not accepted...')
❌ Email failed - check app password
```

---

## 🕐 Scheduler Setup (5:00 AM AEST)

### Overview

The scheduler runs the overnight pipeline automatically at **5:00 AM Australian Eastern Time** daily.

**Features**:
- Automatic timezone handling (AEST/AEDT)
- Error recovery and logging
- Email notifications on completion/error
- Process monitoring

---

## 📝 Scheduler Usage

### Method 1: Manual Start (Testing)

**Run immediately (test mode)**:
```bash
cd /home/user/webapp
python3 schedule_pipeline.py --test
```

**Start scheduler (runs at 5:00 AM daily)**:
```bash
cd /home/user/webapp
python3 schedule_pipeline.py
```

Output:
```
================================================================================
OVERNIGHT PIPELINE SCHEDULER STARTED
================================================================================
Schedule Time: 05:00 Australia/Sydney
Current Time: 2025-11-12 14:30:00 AEDT
Log File: logs/scheduler/scheduler.log

Scheduler is running... Press Ctrl+C to stop
================================================================================
Next scheduled run: 2025-11-13 05:00:00
```

**Stop scheduler**: Press `Ctrl+C`

---

### Method 2: Background Process (Recommended)

**Start in background with nohup**:
```bash
cd /home/user/webapp
nohup python3 schedule_pipeline.py > logs/scheduler/nohup.log 2>&1 &
echo $! > logs/scheduler/scheduler.pid
```

**Check status**:
```bash
ps aux | grep schedule_pipeline.py
cat logs/scheduler/scheduler.log | tail -20
```

**Stop scheduler**:
```bash
kill $(cat logs/scheduler/scheduler.pid)
rm logs/scheduler/scheduler.pid
```

---

### Method 3: Systemd Service (Production)

**Create service file**:
```bash
sudo nano /etc/systemd/system/stock-scanner.service
```

**Service configuration**:
```ini
[Unit]
Description=Overnight Stock Scanner Pipeline
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/user/webapp
ExecStart=/usr/bin/python3 /home/user/webapp/schedule_pipeline.py
Restart=always
RestartSec=60
StandardOutput=append:/home/user/webapp/logs/scheduler/service.log
StandardError=append:/home/user/webapp/logs/scheduler/service_error.log

[Install]
WantedBy=multi-user.target
```

**Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-scanner.service
sudo systemctl start stock-scanner.service
```

**Check service status**:
```bash
sudo systemctl status stock-scanner.service
```

**View logs**:
```bash
journalctl -u stock-scanner.service -f
```

---

### Method 4: Cron Job (Alternative)

**Edit crontab**:
```bash
crontab -e
```

**Add this line** (runs at 5:00 AM daily):
```cron
0 5 * * * cd /home/user/webapp && /usr/bin/python3 /home/user/webapp/run_overnight_pipeline.py >> /home/user/webapp/logs/scheduler/cron.log 2>&1
```

**Verify cron job**:
```bash
crontab -l
```

---

## 📊 What Happens at 5:00 AM

### Pipeline Execution Flow

1. **5:00 AM** - Scheduler triggers pipeline
2. **5:00-5:02** - Fetch market sentiment (SPI, US markets)
3. **5:02-5:20** - Scan 240 stocks across 8 sectors
4. **5:20-5:40** - Generate predictions (LSTM, sentiment, technical)
5. **5:40-5:45** - Score opportunities and generate report
6. **5:45-5:46** - Send email notifications

**Total Duration**: ~45 minutes

### Email Notifications Sent

**Morning Report Email** (5:45 AM):
- Subject: `📊 ASX Morning Report - 2025-11-13`
- Includes: Top 5 opportunities, scores, signals
- Attachment: Full HTML report

**High-Confidence Alert** (if applicable):
- Subject: `🚨 HIGH CONFIDENCE OPPORTUNITIES - 2025-11-13`
- Only sent if opportunities ≥80 score found
- Lists urgent opportunities

**Error Notification** (if pipeline fails):
- Subject: `❌ PIPELINE ERROR - 2025-11-13`
- Includes error message and traceback

---

## 📁 File Locations

### Configuration
```
models/config/screening_config.json    # Email & scheduler config
```

### Scripts
```
schedule_pipeline.py                   # Scheduler script (5:00 AM)
run_overnight_pipeline.py              # Manual pipeline runner
models/screening/overnight_pipeline.py # Pipeline orchestrator
models/screening/send_notification.py  # Email notification system
```

### Logs
```
logs/scheduler/scheduler.log           # Scheduler execution log
logs/screening/overnight_pipeline.log  # Pipeline execution log
logs/screening/email_notifications.log # Email notification log
```

### Reports
```
reports/morning_reports/               # Daily HTML reports
reports/pipeline_state/                # Pipeline state JSON files
```

---

## 🔍 Monitoring & Troubleshooting

### Check Scheduler Status

```bash
# View scheduler log (last 20 lines)
tail -20 logs/scheduler/scheduler.log

# View full pipeline log
tail -50 logs/screening/overnight_pipeline.log

# View email notification log
tail -20 logs/screening/email_notifications.log

# Check if scheduler is running
ps aux | grep schedule_pipeline
```

### Common Issues

#### ❌ Email Not Sending

**Symptom**: `❌ Failed to send email notification`

**Solutions**:
1. Verify Gmail app password is correct
2. Check 2-Step Verification is enabled
3. Try regenerating app password
4. Test with simple Python script:

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('david.osland@gmail.com', 'YOUR_APP_PASSWORD')
print("✅ Login successful!")
server.quit()
```

#### ❌ Scheduler Not Running at 5:00 AM

**Check**:
```bash
# Is scheduler process running?
ps aux | grep schedule_pipeline

# Check scheduler log
grep "Next scheduled run" logs/scheduler/scheduler.log
```

**Solutions**:
1. Restart scheduler: `python3 schedule_pipeline.py`
2. Check system time: `date`
3. Verify timezone: `timedatectl`

#### ❌ Pipeline Fails

**Check logs**:
```bash
tail -100 logs/screening/overnight_pipeline.log | grep ERROR
```

**Common causes**:
- Network connectivity issues
- Missing dependencies
- Insufficient memory

---

## 🎯 Quick Start Checklist

### Initial Setup

- [ ] Generate Gmail app password at https://myaccount.google.com/apppasswords
- [ ] Add app password to `models/config/screening_config.json`
- [ ] Test email: `python3 -c "...test command..."`
- [ ] Test scheduler: `python3 schedule_pipeline.py --test`

### Daily Operation

- [ ] Start scheduler: `python3 schedule_pipeline.py` (or use systemd)
- [ ] Verify scheduled time: Check logs for "Next scheduled run"
- [ ] Check email at ~5:45 AM for morning report

### Weekly Maintenance

- [ ] Review logs: `tail -50 logs/scheduler/scheduler.log`
- [ ] Check disk space: `df -h`
- [ ] Verify reports generated: `ls -lh reports/morning_reports/`

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
cd /home/user/webapp
python3 -c "
import json
with open('models/config/screening_config.json') as f:
    config = json.load(f)
    email_config = config['email_notifications']
    print(f'Email Enabled: {email_config[\"enabled\"]}')
    print(f'Recipients: {email_config[\"recipient_emails\"]}')
    print(f'Morning Report: {email_config[\"send_morning_report\"]}')
    print(f'Alerts: {email_config[\"send_alerts\"]}')
    print(f'Errors: {email_config[\"send_errors\"]}')
"
```

---

## 🚀 Next Steps

1. **Set up Gmail app password** (see steps above)
2. **Test email notifications** (see test command above)
3. **Run test pipeline**: `python3 schedule_pipeline.py --test`
4. **Start scheduler**: `python3 schedule_pipeline.py` (or use systemd)
5. **Check tomorrow at 5:45 AM** for morning report email

---

## 📋 Email Templates Preview

### Morning Report Email

**Subject**: 📊 ASX Morning Report - 2025-11-13

**Body**:
```
================================================================================
ASX OVERNIGHT STOCK SCREENING - MORNING REPORT
================================================================================

📊 SUMMARY
----------------------------------------
Date: 2025-11-13
Stocks Scanned: 240
Opportunities Found: 45
SPI Sentiment: 72.5/100
Market Bias: BULLISH

🎯 TOP 5 OPPORTUNITIES
----------------------------------------
1. CBA.AX
   Score: 87.3/100
   Signal: BUY
   Confidence: 89.2%
   Sector: Financials

2. BHP.AX
   Score: 85.1/100
   Signal: BUY
   Confidence: 82.5%
   Sector: Materials

... (top 5 listed)

================================================================================
See attached HTML report for full details.
================================================================================
```

**Attachment**: `2025-11-13_market_report.html` (full interactive report)

---

**Configuration Complete!** ✅

You're now set up to receive automated stock screening reports every morning at 5:45 AM AEST.

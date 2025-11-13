# Quick Start: Email & Scheduler

**For**: david.osland@gmail.com  
**System**: ASX Overnight Stock Scanner

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Gmail App Password (5 minutes)

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in with `david.osland@gmail.com`
3. Create app password for "ASX Stock Scanner"
4. **Copy the 16-character password** (looks like: `xxxx xxxx xxxx xxxx`)

### Step 2: Add Password to Config (1 minute)

```bash
cd /home/user/webapp
nano models/config/screening_config.json
```

Find line 89 and replace `YOUR_GMAIL_APP_PASSWORD_HERE` with your app password (no spaces):

```json
"smtp_password": "abcdabcdabcdabcd",
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 3: Test Email (30 seconds)

```bash
cd /home/user/webapp
python3 test_email_quick.py
```

Expected: "✅ TEST EMAIL SENT SUCCESSFULLY!"

---

## 📧 Email Test Commands

### Quick Test
```bash
cd /home/user/webapp && python3 test_email_quick.py
```

### Detailed Test
```bash
cd /home/user/webapp
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'models' / 'screening'))
from send_notification import EmailNotifier
notifier = EmailNotifier()
print(f'Enabled: {notifier.enabled}')
print(f'Recipients: {notifier.recipient_emails}')
result = notifier.send_notification('success', 'Test', 'Test email')
print('✅ Sent!' if result else '❌ Failed')
"
```

---

## ⏰ Scheduler Commands

### Test Pipeline Now
```bash
cd /home/user/webapp
python3 schedule_pipeline.py --test
```
Runs full pipeline immediately (~45 min)

### Start 5:00 AM Scheduler
```bash
cd /home/user/webapp
python3 schedule_pipeline.py
```
Runs forever, executes at 5:00 AM daily  
Stop with: `Ctrl+C`

### Start in Background
```bash
cd /home/user/webapp
nohup python3 schedule_pipeline.py > logs/scheduler/nohup.log 2>&1 &
echo $! > logs/scheduler/scheduler.pid
```

### Check Background Status
```bash
ps aux | grep schedule_pipeline
tail -20 logs/scheduler/scheduler.log
```

### Stop Background Scheduler
```bash
kill $(cat logs/scheduler/scheduler.pid)
rm logs/scheduler/scheduler.pid
```

---

## 📋 What You'll Receive

### Daily at ~5:45 AM

**Morning Report Email**:
- Subject: `📊 ASX Morning Report - 2025-11-13`
- Summary: Stocks scanned, opportunities found, market sentiment
- Top 5 opportunities with scores
- Attached: Full HTML report

**High-Confidence Alert** (if applicable):
- Subject: `🚨 HIGH CONFIDENCE OPPORTUNITIES`
- Only if opportunities ≥80 score found
- Urgent opportunities list

**Error Notification** (if pipeline fails):
- Subject: `❌ PIPELINE ERROR`
- Error details and traceback

---

## 🔍 Check Logs

```bash
# Scheduler log
tail -20 logs/scheduler/scheduler.log

# Pipeline log
tail -50 logs/screening/overnight_pipeline.log

# Email log
tail -20 logs/screening/email_notifications.log
```

---

## ❓ Troubleshooting

### Email Not Sending?

1. **Check app password is correct**:
   ```bash
   grep smtp_password models/config/screening_config.json
   ```
   Should NOT show `YOUR_GMAIL_APP_PASSWORD_HERE`

2. **Test Gmail login**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('david.osland@gmail.com', 'YOUR_APP_PASSWORD')
   print("✅ Login OK!")
   ```

3. **Check 2-Step Verification**:
   - Visit: https://myaccount.google.com/security
   - Verify 2-Step Verification is ON

### Scheduler Not Running?

```bash
# Is it running?
ps aux | grep schedule_pipeline

# Restart it
cd /home/user/webapp
python3 schedule_pipeline.py
```

### No Morning Report?

Check if scheduler ran:
```bash
grep "SCHEDULED PIPELINE EXECUTION" logs/scheduler/scheduler.log
```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Test email | `python3 test_email_quick.py` |
| Run pipeline now | `python3 schedule_pipeline.py --test` |
| Start scheduler | `python3 schedule_pipeline.py` |
| Check scheduler | `tail logs/scheduler/scheduler.log` |
| Check pipeline | `tail logs/screening/overnight_pipeline.log` |
| View reports | `ls -lh reports/morning_reports/` |

---

## ✅ Verification Checklist

- [ ] Gmail app password generated
- [ ] App password added to `screening_config.json`
- [ ] Test email sent successfully: `python3 test_email_quick.py`
- [ ] Test pipeline executed: `python3 schedule_pipeline.py --test`
- [ ] Scheduler started: `python3 schedule_pipeline.py` (or background)
- [ ] Checked logs: `tail logs/scheduler/scheduler.log`
- [ ] Waiting for tomorrow's 5:45 AM email

---

**Next**: Wait for tomorrow morning at ~5:45 AM to receive your first automated report!

**Full Documentation**: See `EMAIL_AND_SCHEDULER_SETUP.md` for detailed instructions.

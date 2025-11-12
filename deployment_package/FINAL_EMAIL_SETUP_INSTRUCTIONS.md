# Final Email Setup Instructions

**Date**: 2025-11-12  
**System**: ASX Overnight Stock Scanner v4.4.4

---

## 🎯 Email Configuration Summary

### ⚠️ ProtonMail SMTP Issue

**ProtonMail does NOT support direct SMTP access** from external applications.

- ProtonMail requires **ProtonMail Bridge** (paid plan required)
- Bridge is a desktop application that creates a local SMTP server
- Without Bridge, ProtonMail cannot be used to **send** emails

### ✅ Recommended Solution: Hybrid Approach

**Use Gmail to SEND, ProtonMail to RECEIVE**

```
Gmail Account (with app password)
    ↓ [SENDS via SMTP]
    ↓
    ↓ → ProtonMail inbox (finbert_morning_report@proton.me)
    ↓ → Gmail inbox (david.osland@gmail.com)
    ↓
Both inboxes receive reports!
```

**Benefits**:
- ✅ ProtonMail receives reports (secure, encrypted inbox)
- ✅ Gmail also receives reports (backup)
- ✅ No ProtonMail Bridge needed
- ✅ No paid ProtonMail plan needed
- ✅ Works immediately with Gmail app password

---

## 📧 Current Configuration

**File**: `models/config/screening_config.json`

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "YOUR_GMAIL_ADDRESS@gmail.com",
    "smtp_password": "YOUR_GMAIL_APP_PASSWORD_HERE",
    "use_tls": true,
    "sender_email": "YOUR_GMAIL_ADDRESS@gmail.com",
    "recipient_emails": [
      "finbert_morning_report@proton.me",
      "david.osland@gmail.com"
    ]
  }
}
```

**Reports will be sent to BOTH**:
- ✅ `finbert_morning_report@proton.me` (secure ProtonMail inbox)
- ✅ `david.osland@gmail.com` (backup)

---

## 🔐 Setup Steps

### Step 1: Get Gmail App Password (5 minutes)

1. **Visit**: https://myaccount.google.com/apppasswords

2. **Sign in** with your Gmail account (e.g., `david.osland@gmail.com` or another Gmail)

3. **Enable 2-Step Verification** (if not already enabled):
   - Go to: Security → 2-Step Verification
   - Follow prompts

4. **Create App Password**:
   - App name: "ASX Stock Scanner"
   - Click "Generate"
   - **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)

### Step 2: Update Configuration (2 minutes)

```bash
cd /home/user/webapp
nano models/config/screening_config.json
```

**Find lines 89-92 and update**:

```json
"smtp_username": "YOUR_GMAIL_ADDRESS@gmail.com",
"smtp_password": "YOUR_GMAIL_APP_PASSWORD_HERE",
```

**Replace with**:

```json
"smtp_username": "your_actual_gmail@gmail.com",
"smtp_password": "abcdabcdabcdabcd",
```

(Remove spaces from app password)

**Save**: `Ctrl+X`, `Y`, `Enter`

---

## 🧪 Test Email (30 seconds)

```bash
cd /home/user/webapp
python3 test_email_quick.py
```

**Expected Output**:
```
================================================================================
EMAIL NOTIFICATION TEST
================================================================================

Initializing email notifier...
✓ Email Enabled: True
✓ SMTP Server: smtp.gmail.com:587
✓ Sender: your_gmail@gmail.com
✓ Recipients: finbert_morning_report@proton.me, david.osland@gmail.com

Sending test email...

================================================================================
✅ TEST EMAIL SENT SUCCESSFULLY!
================================================================================

Check both inboxes:
- finbert_morning_report@proton.me
- david.osland@gmail.com
```

---

## 📬 What You'll Receive

### ProtonMail Inbox (`finbert_morning_report@proton.me`)

**Login**: https://account.proton.me/login  
**Password**: `Charlotte@295`

**Daily Emails**:
1. **📊 Morning Report** (~5:45 AM)
   - Subject: `📊 ASX Morning Report - YYYY-MM-DD`
   - Top 5 opportunities
   - HTML report attachment
   
2. **🚨 High-Confidence Alerts** (when applicable)
   - Opportunities ≥80 score
   
3. **❌ Error Notifications** (if pipeline fails)

### Gmail Inbox (`david.osland@gmail.com`)

**Same emails as ProtonMail** (backup copy)

---

## 🚀 Start the Scheduler

### Option 1: Foreground (Testing)

```bash
cd /home/user/webapp
python3 schedule_pipeline.py
```

**Output**:
```
================================================================================
OVERNIGHT PIPELINE SCHEDULER STARTED
================================================================================
Schedule Time: 05:00 Australia/Sydney
Next scheduled run: 2025-11-13 05:00:00
```

Stop with: `Ctrl+C`

### Option 2: Background (Recommended)

```bash
cd /home/user/webapp
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

## 📊 Daily Timeline

| Time | Activity |
|------|----------|
| **5:00 AM** | Scheduler triggers |
| 5:00-5:02 | Fetch market sentiment |
| 5:02-5:20 | Scan 240 ASX stocks |
| 5:20-5:40 | Generate predictions |
| 5:40-5:45 | Score opportunities |
| **5:45 AM** | 📧 Emails sent to both inboxes |

---

## ✅ Quick Start Checklist

- [ ] 1. Get Gmail app password
     → https://myaccount.google.com/apppasswords

- [ ] 2. Update `screening_config.json` with Gmail credentials
     → Lines 89-92

- [ ] 3. Test email
     → `python3 test_email_quick.py`

- [ ] 4. Check both inboxes
     → ProtonMail & Gmail

- [ ] 5. Start scheduler
     → `python3 schedule_pipeline.py`

- [ ] 6. Verify next run
     → `grep "Next scheduled run" logs/scheduler/scheduler.log`

---

## 💡 Why This Setup is Best

### ProtonMail Benefits (Receiving)
- ✅ End-to-end encryption
- ✅ Privacy-focused storage
- ✅ Secure inbox for sensitive trading data
- ✅ No Bridge or paid plan needed (for receiving)

### Gmail Benefits (Sending)
- ✅ Reliable SMTP infrastructure
- ✅ Works from any server
- ✅ No additional software
- ✅ Free with app password
- ✅ Also receives backup copy

---

## 🔍 Troubleshooting

### Test Email Fails

**Check configuration**:
```bash
cd /home/user/webapp
python3 -c "
import json
with open('models/config/screening_config.json') as f:
    config = json.load(f)
    email = config['email_notifications']
    print(f'Enabled: {email[\"enabled\"]}')
    print(f'SMTP: {email[\"smtp_server\"]}:{email[\"smtp_port\"]}')
    print(f'Username: {email[\"smtp_username\"]}')
    print(f'Recipients: {email[\"recipient_emails\"]}')
    print(f'Password Set: {\"No\" if \"YOUR_GMAIL\" in email[\"smtp_password\"] else \"Yes\"}')"
```

### No Email Received

**Check spam/junk folders** in both inboxes.

**Verify sender**: Gmail might flag first email as suspicious.

**Check logs**:
```bash
tail -30 logs/screening/email_notifications.log
```

---

## 📞 Alternative: Use Different Gmail Account

If you don't want to use your personal Gmail:

1. **Create new Gmail** specifically for this: `asx.scanner.reports@gmail.com`
2. Generate app password for that account
3. Update config with new Gmail credentials
4. Reports still sent to ProtonMail & your personal Gmail

---

## 📚 Documentation Files

- **This Guide**: `FINAL_EMAIL_SETUP_INSTRUCTIONS.md`
- **ProtonMail Details**: `PROTONMAIL_SMTP_SOLUTION.md`
- **Full Setup**: `EMAIL_AND_SCHEDULER_SETUP.md`
- **Quick Reference**: `QUICK_START_EMAIL_SCHEDULER.md`
- **Commands**: `COMMAND_REFERENCE.txt`

---

## 🎯 Summary

**Configuration**:
- **Send FROM**: Gmail (with app password)
- **Send TO**: ProtonMail + Gmail
- **Schedule**: 5:00 AM AEST daily

**Next Action**:
1. Get Gmail app password (5 min)
2. Update config (2 min)
3. Test email (30 sec)
4. Start scheduler (10 sec)

**Tomorrow**: Check both inboxes at 5:45 AM for first report!

---

**Ready to go!** Just add your Gmail app password and you're set. 🚀📧

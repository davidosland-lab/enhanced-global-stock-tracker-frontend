# Gmail App Password Setup Guide

**Account**: finbertmorningreport@gmail.com  
**Password**: Finbert@295 (regular password)

---

## ⚠️ Important: Gmail Requires App Password

**Gmail does NOT allow regular passwords for SMTP access.**

You need to generate an **App Password** - a special 16-character password for third-party applications.

---

## 🔐 Step-by-Step Setup (5 minutes)

### Step 1: Sign in to Gmail Account

1. Go to: https://mail.google.com
2. Sign in with:
   - Email: `finbertmorningreport@gmail.com`
   - Password: `Finbert@295`

### Step 2: Enable 2-Step Verification

**Required before generating App Password**

1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification" section
3. Click "Get started" or "Turn on"
4. Follow prompts:
   - Enter password: `Finbert@295`
   - Add phone number for verification
   - Receive verification code via SMS
   - Enter code to verify

### Step 3: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords

2. You'll see "App passwords" page

3. Create new app password:
   - **App name**: "ASX Stock Scanner"
   - Click "Create"

4. **Copy the 16-character password**:
   ```
   Format: xxxx xxxx xxxx xxxx
   Example: abcd efgh ijkl mnop
   ```

5. **IMPORTANT**: Copy this password immediately - you won't see it again!

### Step 4: Update Configuration

1. Open configuration file:
   ```bash
   cd /home/user/webapp
   nano models/config/screening_config.json
   ```

2. Find line 90 (smtp_password)

3. Replace `Finbert@295` with your **16-character App Password** (remove spaces):
   ```json
   "smtp_password": "abcdefghijklmnop",
   ```

4. Save: `Ctrl+X`, `Y`, `Enter`

### Step 5: Test Email

```bash
cd /home/user/webapp
python3 test_email_quick.py
```

**Expected Output**:
```
✅ TEST EMAIL SENT SUCCESSFULLY!
Check your inbox: finbert_morning_report@proton.me
```

---

## 🖥️ Visual Guide

### Google Account Security Page

```
https://myaccount.google.com/security
    ↓
Scroll to "How you sign in to Google"
    ↓
Click "2-Step Verification"
    ↓
Follow setup wizard
    ↓
Enable 2-Step Verification ✓
```

### App Passwords Page

```
https://myaccount.google.com/apppasswords
    ↓
(Only available after 2-Step Verification is enabled)
    ↓
Select app: "Mail"
Select device: "Other (Custom name)"
Enter name: "ASX Stock Scanner"
    ↓
Click "Generate"
    ↓
Copy 16-character password ✓
```

---

## 📧 Current Configuration

**File**: `models/config/screening_config.json`

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "finbertmorningreport@gmail.com",
    "smtp_password": "Finbert@295",  ← NEEDS TO BE APP PASSWORD
    "use_tls": true,
    "sender_email": "finbertmorningreport@gmail.com",
    "recipient_emails": [
      "finbert_morning_report@proton.me",
      "david.osland@gmail.com"
    ]
  }
}
```

**What needs to change**:
- Line 90: Replace `Finbert@295` with 16-character App Password

---

## ✅ After Setup

### Test Email Immediately

```bash
cd /home/user/webapp
python3 test_email_quick.py
```

### Start Scheduler

```bash
# Foreground (testing)
python3 schedule_pipeline.py

# OR Background (recommended)
nohup python3 schedule_pipeline.py > logs/scheduler/nohup.log 2>&1 &
echo $! > logs/scheduler/scheduler.pid
```

### Check Tomorrow

- **Time**: 5:45 AM AEST
- **Check**: Both inboxes
  - finbert_morning_report@proton.me
  - david.osland@gmail.com

---

## 🔍 Verification

### Test SMTP Connection

```bash
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('finbertmorningreport@gmail.com', 'YOUR_APP_PASSWORD_HERE')
print('✅ SMTP login successful!')
server.quit()
"
```

Replace `YOUR_APP_PASSWORD_HERE` with your 16-character App Password (no spaces).

---

## ❓ Troubleshooting

### Problem: "Username and Password not accepted"

**Cause**: Using regular password instead of App Password

**Solution**:
1. Enable 2-Step Verification
2. Generate App Password
3. Use App Password in configuration

### Problem: Can't find "App passwords" option

**Cause**: 2-Step Verification not enabled

**Solution**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification first
3. Then App Passwords option will appear

### Problem: Lost App Password

**Solution**:
1. Go to https://myaccount.google.com/apppasswords
2. Revoke old password
3. Generate new App Password
4. Update configuration

---

## 📋 Quick Reference

| Task | Link |
|------|------|
| Gmail Login | https://mail.google.com |
| Security Settings | https://myaccount.google.com/security |
| 2-Step Verification | https://myaccount.google.com/security |
| App Passwords | https://myaccount.google.com/apppasswords |

**Account**:
- Email: finbertmorningreport@gmail.com
- Password: Finbert@295
- App Password: (generate this)

**Recipients**:
- finbert_morning_report@proton.me (primary)
- david.osland@gmail.com (backup)

---

## 🎯 Summary

**Current Status**:
- ✅ Gmail account configured in system
- ✅ SMTP settings correct
- ⚠️ **Need App Password** (not regular password)

**Next Steps**:
1. Enable 2-Step Verification (2 min)
2. Generate App Password (1 min)
3. Update configuration (30 sec)
4. Test email (30 sec)
5. Start scheduler (10 sec)

**Total Time**: ~5 minutes

---

## 🔐 Security Notes

**App Password vs Regular Password**:
- **Regular Password**: `Finbert@295` - For logging into Gmail website/app
- **App Password**: 16-character code - For third-party apps like this system

**Why App Password?**:
- More secure (separate from main password)
- Can be revoked without changing main password
- Specific to this application
- Required by Gmail for SMTP access

**Keep Both Passwords**:
- Regular password for Gmail login
- App password for stock scanner system

---

## 📞 Need Help?

**Gmail Support**:
- Help Center: https://support.google.com/mail
- App Passwords Guide: https://support.google.com/mail/?p=BadCredentials

**If stuck**:
1. Check that 2-Step Verification is enabled
2. Use the correct Gmail account (finbertmorningreport@gmail.com)
3. Copy App Password exactly (16 characters, no spaces)
4. Test with: `python3 test_email_quick.py`

---

**Once App Password is configured, the system will be fully operational!** ✅

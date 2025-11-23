# Gmail App Password Setup Guide

**Account**: finbertmorningreport@gmail.com  
**Password**: Finbert@295 (regular password - NOT for SMTP)

---

## ⚠️ Important: App Password Required

Gmail **does NOT accept regular passwords** for SMTP access. You need to generate an **App Password**.

**Current Status**:
- ❌ Regular password "Finbert@295" was rejected by Gmail SMTP
- ✅ Solution: Generate and use an App Password

---

## 🔐 Step-by-Step Setup

### Step 1: Enable 2-Step Verification (Required)

1. **Visit**: https://myaccount.google.com/security

2. **Sign in**:
   - Email: `finbertmorningreport@gmail.com`
   - Password: `Finbert@295`

3. **Find "2-Step Verification"** section

4. **Click "Get Started"** or "Turn On"

5. **Follow the setup process**:
   - Add phone number
   - Verify with code
   - Complete setup

6. **Verify it's enabled**: You should see "2-Step Verification: On"

---

### Step 2: Generate App Password

1. **Visit**: https://myaccount.google.com/apppasswords
   
   (Or: Google Account → Security → 2-Step Verification → App passwords)

2. **Sign in** (if asked):
   - Email: `finbertmorningreport@gmail.com`
   - Password: `Finbert@295`

3. **Select app and device**:
   - App: "Mail" or "Other"
   - Device: "Other (Custom name)"
   - Custom name: "ASX Stock Scanner"

4. **Click "Generate"**

5. **Copy the 16-character password**:
   - Format: `xxxx xxxx xxxx xxxx`
   - Example: `abcd efgh ijkl mnop`
   - **Save this somewhere safe!**

---

### Step 3: Update Configuration

**File**: `models/config/screening_config.json`

**Find line 90**:
```json
"smtp_password": "Finbert@295",
```

**Replace with your app password** (remove spaces):
```json
"smtp_password": "abcdefghijklmnop",
```

**Example**:
- App password shown: `abcd efgh ijkl mnop`
- Use in config: `abcdefghijklmnop`

---

### Step 4: Test Email

```bash
python3 test_email_quick.py
```

**Expected Output**:
```
✅ TEST EMAIL SENT SUCCESSFULLY!
Check your inbox: finbert_morning_report@proton.me
```

---

## 📧 Complete Configuration

After getting the app password, your configuration should look like this:

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "finbertmorningreport@gmail.com",
    "smtp_password": "YOUR_16_CHAR_APP_PASSWORD",
    "use_tls": true,
    "sender_email": "finbertmorningreport@gmail.com",
    "recipient_emails": [
      "finbert_morning_report@proton.me",
      "david.osland@gmail.com"
    ],
    "send_morning_report": true,
    "send_alerts": true,
    "send_errors": true,
    "alert_threshold": 80
  }
}
```

---

## ✅ Verification Checklist

- [ ] 2-Step Verification enabled on finbertmorningreport@gmail.com
- [ ] App password generated (16 characters)
- [ ] App password added to screening_config.json (line 90)
- [ ] Test email sent successfully
- [ ] Emails received in ProtonMail and Gmail

---

## ❓ Troubleshooting

### "Can't find App Passwords option"

**Solution**: Make sure 2-Step Verification is fully enabled first.

### "Invalid credentials" error

**Solutions**:
1. Double-check app password was copied correctly
2. Remove spaces from app password
3. Make sure using app password, not regular password

### "Authentication failed"

**Solutions**:
1. Regenerate app password
2. Wait 5-10 minutes after generating (Google sync delay)
3. Try signing out and back in to Google account

---

## 🔒 Security Notes

**App Password**:
- ✅ Use for SMTP access
- ✅ Can be revoked anytime
- ✅ Doesn't give full account access
- ✅ More secure than regular password

**Regular Password** (`Finbert@295`):
- ❌ Don't use for SMTP
- ✅ Use for signing into Google account
- ✅ Keep it secure

---

## 📝 Quick Reference

| Item | Value |
|------|-------|
| Gmail Account | finbertmorningreport@gmail.com |
| Regular Password | Finbert@295 |
| App Password | (Generate at link below) |
| SMTP Server | smtp.gmail.com:587 |
| Recipients | finbert_morning_report@proton.me, david.osland@gmail.com |

**Generate App Password**: https://myaccount.google.com/apppasswords

---

## 🚀 After Setup

Once app password is configured:

1. **Test email**: `python3 test_email_quick.py`
2. **Start scheduler**: `python3 schedule_pipeline.py`
3. **Check tomorrow at 5:45 AM** for morning report

---

**Need Help?** See `EMAIL_AND_SCHEDULER_SETUP.md` for detailed troubleshooting.

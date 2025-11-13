# ProtonMail SMTP Configuration Solutions

**Issue**: ProtonMail requires ProtonMail Bridge for SMTP access from external applications.

**Current Setup**:
- Email: `finbert_morning_report@proton.me`
- Password: `Charlotte@295`
- Recipient: `david.osland@gmail.com`

---

## ⚠️ ProtonMail SMTP Limitation

ProtonMail does **NOT** allow direct SMTP access for security reasons. You need:

1. **ProtonMail Bridge** (desktop application) running locally
2. Or use an alternative email provider for sending

**Direct SMTP is blocked** by ProtonMail for third-party applications.

---

## ✅ Solution 1: Use Gmail to Send (RECOMMENDED)

**Easiest approach**: Use Gmail to SEND emails, but use ProtonMail to RECEIVE.

### Configuration

The reports will be:
- **Sent FROM**: Your Gmail account (with app password)
- **Sent TO**: `finbert_morning_report@proton.me` (and `david.osland@gmail.com`)

### Steps

1. **Get Gmail App Password** (5 minutes):
   - Visit: https://myaccount.google.com/apppasswords
   - Sign in with your Gmail account
   - Create app password: "ASX Stock Scanner"
   - Copy 16-character password

2. **Update Configuration**:
   ```bash
   nano models/config/screening_config.json
   ```
   
   Update lines 87-94:
   ```json
   "smtp_server": "smtp.gmail.com",
   "smtp_port": 587,
   "smtp_username": "your_gmail@gmail.com",
   "smtp_password": "your_gmail_app_password",
   "use_tls": true,
   "sender_email": "your_gmail@gmail.com",
   "recipient_emails": [
     "finbert_morning_report@proton.me",
     "david.osland@gmail.com"
   ]
   ```

3. **Test**:
   ```bash
   python3 test_email_quick.py
   ```

**Advantages**:
- ✅ Works immediately
- ✅ No additional software needed
- ✅ Reliable Gmail infrastructure
- ✅ ProtonMail receives reports (secure inbox)

---

## 💡 Solution 2: ProtonMail Bridge (Advanced)

**For sending FROM ProtonMail**: Requires ProtonMail Bridge installed on your server.

### Requirements

1. **ProtonMail Bridge** (desktop app)
   - Download: https://proton.me/mail/bridge
   - Available for: Windows, macOS, Linux

2. **Paid ProtonMail Account**
   - Bridge requires ProtonMail Plus, Professional, or Visionary plan
   - Free accounts cannot use Bridge

### Installation Steps

#### Linux Server
```bash
# Download ProtonMail Bridge for Linux
wget https://proton.me/download/bridge/protonmail-bridge_latest_amd64.deb

# Install
sudo dpkg -i protonmail-bridge_latest_amd64.deb

# Run Bridge (creates local SMTP server)
protonmail-bridge --cli
```

#### Configuration After Bridge Setup
```json
{
  "smtp_server": "127.0.0.1",
  "smtp_port": 1025,
  "smtp_username": "finbert_morning_report@proton.me",
  "smtp_password": "bridge_generated_password",
  "use_tls": true,
  "sender_email": "finbert_morning_report@proton.me"
}
```

**Bridge generates a unique password** - use that, not your ProtonMail password.

---

## 🔧 Solution 3: Alternative Email Providers

### Option A: Outlook/Hotmail (Free, Easy)

**SMTP Settings**:
```json
{
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_username": "your_email@outlook.com",
  "smtp_password": "your_password",
  "use_tls": true
}
```

**Create Account**: https://outlook.com

### Option B: SendGrid (Free Tier: 100 emails/day)

**SMTP Settings**:
```json
{
  "smtp_server": "smtp.sendgrid.net",
  "smtp_port": 587,
  "smtp_username": "apikey",
  "smtp_password": "your_sendgrid_api_key",
  "use_tls": true
}
```

**Free Account**: https://sendgrid.com/pricing/

### Option C: Mailgun (Free Tier: 5,000 emails/month)

**SMTP Settings**:
```json
{
  "smtp_server": "smtp.mailgun.org",
  "smtp_port": 587,
  "smtp_username": "postmaster@your-domain.mailgun.org",
  "smtp_password": "your_mailgun_password",
  "use_tls": true
}
```

**Free Account**: https://www.mailgun.com/pricing/

---

## 📊 Comparison

| Solution | Complexity | Cost | Reliability | Setup Time |
|----------|-----------|------|-------------|------------|
| **Gmail (Recommended)** | Easy | Free | High | 5 min |
| ProtonMail Bridge | Hard | Paid plan | Medium | 30 min |
| Outlook/Hotmail | Easy | Free | High | 5 min |
| SendGrid | Medium | Free (100/day) | High | 10 min |
| Mailgun | Medium | Free (5K/mo) | High | 10 min |

---

## ✅ Recommended Configuration

**Best Setup**:
- **Send FROM**: Gmail (with app password)
- **Send TO**: `finbert_morning_report@proton.me` + `david.osland@gmail.com`
- **Receive**: ProtonMail inbox (secure)

### Final Configuration

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your_gmail@gmail.com",
    "smtp_password": "your_gmail_app_password",
    "use_tls": true,
    "sender_email": "your_gmail@gmail.com",
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

## 🚀 Quick Setup (Gmail Method)

1. **Get Gmail app password**:
   ```
   Visit: https://myaccount.google.com/apppasswords
   Create: "ASX Stock Scanner"
   Copy: 16-character password
   ```

2. **Update config**:
   ```bash
   cd /home/user/webapp
   nano models/config/screening_config.json
   ```
   
   Update SMTP settings with Gmail credentials

3. **Test**:
   ```bash
   python3 test_email_quick.py
   ```

4. **Start scheduler**:
   ```bash
   python3 schedule_pipeline.py
   ```

---

## 💡 Why This Works

**ProtonMail as Recipient**:
- ✅ Secure end-to-end encryption
- ✅ Privacy-focused inbox
- ✅ All reports stored securely
- ✅ No Bridge needed for receiving

**Gmail as Sender**:
- ✅ Works from any server
- ✅ Reliable delivery
- ✅ No additional software
- ✅ Free with app password

---

## 📧 What You'll Receive

**ProtonMail Inbox** (`finbert_morning_report@proton.me`):
- Daily morning reports at 5:45 AM
- High-confidence alerts
- Error notifications
- HTML attachments with full analysis

**Gmail Inbox** (`david.osland@gmail.com`):
- Same emails as ProtonMail
- Backup copy for redundancy

---

## ❓ FAQ

**Q: Can I only use ProtonMail without Gmail?**  
A: Yes, but you need ProtonMail Bridge (requires paid plan).

**Q: Is it secure to use Gmail to send to ProtonMail?**  
A: Yes. Once received, emails are encrypted in ProtonMail's secure storage.

**Q: Will ProtonMail work for receiving only?**  
A: Yes! ProtonMail works perfectly as a recipient without any setup.

**Q: What if I want to send from ProtonMail?**  
A: Install ProtonMail Bridge (requires paid account) and use Solution 2 above.

---

## 🎯 Next Steps

**Recommended**: Use Gmail to send, ProtonMail to receive

1. Get Gmail app password (5 min)
2. Update `screening_config.json` with Gmail settings
3. Add both emails to `recipient_emails` array
4. Test: `python3 test_email_quick.py`
5. Start: `python3 schedule_pipeline.py`

Both inboxes will receive reports!

---

**Need help?** Let me know which solution you prefer, and I'll help configure it.

# Email Password Configuration Guide

## Quick Answer: Where to Update Your Password

**YOU ONLY NEED TO UPDATE IT ONCE AFTER EXTRACTING THE ZIP FILE**

### Location
```
deployment_event_risk_guard/models/config/screening_config.json
```

### What to Edit
Open `screening_config.json` in Notepad and find line 90:

```json
"email_notifications": {
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "finbertmorningreport@gmail.com",
  "smtp_password": "YOUR_PASSWORD_HERE",     ← UPDATE THIS LINE
  "use_tls": true,
  "sender_email": "finbertmorningreport@gmail.com",
  "recipient_emails": [
    "finbert_morning_report@proton.me",
    "david.osland@gmail.com"
  ],
  ...
}
```

## Current Configuration (Pre-filled)

The deployment package comes with your password already configured:
- **Username**: `finbertmorningreport@gmail.com`
- **Password**: `Finbert@295` (already set in the config file)
- **Recipients**: 
  - `finbert_morning_report@proton.me`
  - `david.osland@gmail.com`

**This means**: The system will work immediately after extraction. You DON'T need to update anything unless your password changes.

## When Do You Need to Update?

### ❌ You DON'T Need to Update:
- After extracting a new ZIP deployment
- When I fix bugs and release new versions
- For routine updates and patches

**The password stays in your extracted folder** - it's not affected by new deployments.

### ✅ You DO Need to Update:
- When your Gmail password changes
- When you want to add/remove recipient emails
- When you want to use a different SMTP server

## How to Update (Step-by-Step)

### Option 1: Edit Manually (Recommended)

1. Navigate to extracted folder:
   ```
   C:\path\to\deployment_event_risk_guard\models\config\
   ```

2. Right-click `screening_config.json` → Open with Notepad

3. Find line 90 (search for `"smtp_password"`)

4. Change the password:
   ```json
   "smtp_password": "YourNewPassword123",
   ```

5. Save the file (Ctrl+S)

6. Test: Run `TEST_EVENT_RISK_GUARD.bat`

### Option 2: Use Search and Replace

1. Open `screening_config.json` in Notepad

2. Press Ctrl+H (Find and Replace)

3. Find: `"smtp_password": "Finbert@295"`

4. Replace with: `"smtp_password": "YourNewPassword"`

5. Click "Replace All"

6. Save (Ctrl+S)

## Gmail App Password (Recommended)

Instead of using your actual Gmail password, use an **App Password**:

### Why App Passwords?
- ✓ More secure than your main password
- ✓ Can be revoked without changing your Gmail password
- ✓ Specifically designed for apps that use SMTP

### How to Create Gmail App Password:

1. Go to Google Account settings: https://myaccount.google.com/security

2. Enable 2-Step Verification (if not already enabled)

3. Go to: https://myaccount.google.com/apppasswords

4. Select "Mail" and "Windows Computer"

5. Click "Generate"

6. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

7. Update `screening_config.json`:
   ```json
   "smtp_password": "xxxx xxxx xxxx xxxx",
   ```

## Testing Email Configuration

After updating your password, test it:

```batch
TEST_EVENT_RISK_GUARD.bat
```

Look for these log messages:
```
✓ Email notification sent successfully
✓ Morning report emailed to 2 recipients
```

If you see errors:
```
✗ SMTP authentication failed - Check password
✗ Could not connect to SMTP server
```

Then:
1. Verify password is correct in `screening_config.json`
2. Check Gmail settings allow SMTP access
3. Try using an App Password instead

## Deployment Workflow (No Password Re-entry Needed)

### When I Release a New Version:

**Step 1**: Extract new ZIP
```
Event_Risk_Guard_v1.0_FIXED_FIX10_FIX11_20251114_025951.zip
  └── deployment_event_risk_guard/
```

**Step 2**: Password is ALREADY in the config file
```
models/config/screening_config.json (contains "Finbert@295")
```

**Step 3**: Run immediately - no editing needed!
```batch
RUN_OVERNIGHT_PIPELINE.bat
```

### Your Password is Safe:
- ✓ Stays in your extracted folder
- ✓ Not overwritten by new deployments
- ✓ Only in YOUR copy on YOUR computer

## Security Note

**Current Setup**:
- Password is stored in plain text in `screening_config.json`
- File is on your local computer only
- Not transmitted anywhere except to Gmail SMTP server

**Best Practices**:
1. Use Gmail App Password (not your main password)
2. Keep `screening_config.json` file permissions restricted
3. Don't share ZIP files with password included
4. If password compromised, revoke App Password at https://myaccount.google.com/apppasswords

## Multiple Email Accounts

To add more recipients:

```json
"recipient_emails": [
  "finbert_morning_report@proton.me",
  "david.osland@gmail.com",
  "another.email@example.com",        ← Add here
  "more.emails@example.com"          ← And here
],
```

## Troubleshooting

### Error: "SMTP authentication failed"
- Check password is correct in line 90
- Try using Gmail App Password
- Verify 2-Step Verification is enabled

### Error: "Connection refused"
- Check `smtp_port` is 587 (line 88)
- Verify `smtp_server` is "smtp.gmail.com" (line 87)
- Check firewall isn't blocking port 587

### Error: "Sender address rejected"
- Verify `smtp_username` matches `sender_email`
- Both should be "finbertmorningreport@gmail.com"

### Error: "Recipient rejected"
- Check recipient emails have no typos
- Verify both recipients are valid email addresses

## Summary

✅ **Current password**: `Finbert@295` (pre-configured in deployment)  
✅ **Location**: `models/config/screening_config.json` line 90  
✅ **Update frequency**: Only when YOUR password changes  
✅ **New deployments**: Password persists in your extracted folder  

**You're good to go!** The system will work out of the box with current settings.

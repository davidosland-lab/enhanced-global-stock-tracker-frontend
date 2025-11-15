@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo EMAIL NOTIFICATION TEST
echo ================================================================
echo.
echo This will test the email notification system.
echo.
echo Configuration:
echo - SMTP Server: smtp.gmail.com:587
echo - From: finbertmorningreport@gmail.com
echo - To: finbert_morning_report@proton.me, david.osland@gmail.com
echo.
echo ================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo.

echo [2/3] Testing email configuration...
python -c "import json; config = json.load(open('models/config/screening_config.json')); email = config['email_notifications']; print(f\"Enabled: {email['enabled']}\"); print(f\"SMTP: {email['smtp_server']}:{email['smtp_port']}\"); print(f\"Username: {email['smtp_username']}\"); print(f\"Recipients: {', '.join(email['recipient_emails'])}\")"
if errorlevel 1 (
    echo [ERROR] Failed to read configuration
    pause
    exit /b 1
)
echo.

echo [3/3] Sending test email...
echo This may take 10-30 seconds...
echo.

python models/screening/send_notification.py --type test

if errorlevel 1 (
    echo.
    echo ================================================================
    echo [FAILED] Email test failed
    echo ================================================================
    echo.
    echo Common issues:
    echo 1. Gmail password incorrect or expired
    echo 2. "Less secure app access" disabled in Gmail
    echo 3. 2-Step Verification enabled without App Password
    echo 4. Firewall blocking SMTP port 587
    echo.
    echo Solution:
    echo 1. Go to https://myaccount.google.com/apppasswords
    echo 2. Generate new App Password
    echo 3. Update password in models/config/screening_config.json
    echo.
    echo See EMAIL_PASSWORD_CONFIGURATION.md for detailed instructions
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo [SUCCESS] Test email sent successfully!
    echo ================================================================
    echo.
    echo Check your inbox at:
    echo - finbert_morning_report@proton.me
    echo - david.osland@gmail.com
    echo.
    echo If you received the email, the system is working correctly.
    echo ================================================================
)

echo.
echo Press any key to close...
pause >nul

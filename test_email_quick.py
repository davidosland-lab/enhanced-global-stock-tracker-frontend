#!/usr/bin/env python3
"""
Quick Email Notification Test
Tests email configuration without running full pipeline
"""

import sys
from pathlib import Path

# Add models/screening to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / 'models' / 'screening'))

def test_email():
    """Test email notification system"""
    print("="*80)
    print("EMAIL NOTIFICATION TEST")
    print("="*80)
    print()
    
    try:
        from send_notification import EmailNotifier
        
        print("Initializing email notifier...")
        notifier = EmailNotifier()
        
        # Display configuration
        print(f"✓ Email Enabled: {notifier.enabled}")
        print(f"✓ SMTP Server: {notifier.smtp_server}:{notifier.smtp_port}")
        print(f"✓ Sender: {notifier.sender_email}")
        print(f"✓ Recipients: {', '.join(notifier.recipient_emails)}")
        print(f"✓ Morning Reports: {notifier.send_morning_report}")
        print(f"✓ Alerts: {notifier.send_alerts}")
        print(f"✓ Errors: {notifier.send_errors}")
        print()
        
        if not notifier.enabled:
            print("❌ Email notifications are DISABLED in configuration")
            print("   Enable in: models/config/screening_config.json")
            return False
        
        if not notifier.recipient_emails:
            print("❌ No recipient emails configured")
            return False
        
        if "YOUR_GMAIL_APP_PASSWORD_HERE" in notifier.smtp_password:
            print("❌ Gmail app password not set!")
            print()
            print("SETUP REQUIRED:")
            print("1. Go to: https://myaccount.google.com/apppasswords")
            print("2. Generate app password for 'ASX Stock Scanner'")
            print("3. Update models/config/screening_config.json")
            print("4. Replace 'YOUR_GMAIL_APP_PASSWORD_HERE' with your app password")
            print()
            return False
        
        # Send test email
        print("Sending test email...")
        print("(This may take 5-10 seconds...)")
        print()
        
        success = notifier.send_notification(
            notification_type='success',
            subject='🧪 Test Email - ASX Stock Scanner',
            body='''This is a test email from your ASX overnight stock screening system.

If you receive this email, your email notifications are configured correctly!

System Information:
- Recipient: david.osland@gmail.com
- SMTP Server: smtp.gmail.com:587
- Configured Reports: Morning reports, alerts, errors

Next Steps:
1. Run the scheduler: python3 schedule_pipeline.py --test
2. Check tomorrow at 5:45 AM for morning report

System is ready for automated overnight scanning!
'''
        )
        
        print()
        if success:
            print("="*80)
            print("✅ TEST EMAIL SENT SUCCESSFULLY!")
            print("="*80)
            print()
            print("Check your inbox: david.osland@gmail.com")
            print("Subject: 🧪 Test Email - ASX Stock Scanner")
            print()
            print("If you don't see the email:")
            print("1. Check spam/junk folder")
            print("2. Wait 1-2 minutes for delivery")
            print("3. Verify app password is correct")
            print()
            return True
        else:
            print("="*80)
            print("❌ TEST EMAIL FAILED")
            print("="*80)
            print()
            print("Common Issues:")
            print("1. Incorrect Gmail app password")
            print("2. 2-Step Verification not enabled on Google account")
            print("3. Network connectivity issues")
            print("4. SMTP server blocked by firewall")
            print()
            print("Check log: logs/screening/email_notifications.log")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("Make sure all dependencies are installed:")
        print("  pip install pytz")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_email()
    sys.exit(0 if success else 1)

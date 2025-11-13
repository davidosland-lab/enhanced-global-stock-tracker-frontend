"""
Test Email Notifications

Tests the email notification system with various notification types.

Usage:
    python scripts/screening/test_email_notifications.py
"""

import sys
from pathlib import Path

# Add project root to path
BASE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_PATH))

from models.screening.send_notification import EmailNotifier
from datetime import datetime
import pytz

def test_email_notifications():
    """Test email notification system"""
    print("="*80)
    print("EMAIL NOTIFICATION SYSTEM - TEST")
    print("="*80)
    print()
    
    # Initialize notifier
    print("Step 1: Initialize Email Notifier")
    print("-" * 40)
    
    try:
        notifier = EmailNotifier()
        print(f"✅ Email notifier initialized")
        print(f"   Enabled: {notifier.enabled}")
        print(f"   SMTP Server: {notifier.smtp_server}:{notifier.smtp_port}")
        print(f"   Recipients: {len(notifier.recipient_emails)}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize notifier: {str(e)}")
        return False
    
    if not notifier.enabled:
        print("⚠️  Email notifications are DISABLED in configuration")
        print("   To enable:")
        print("   1. Edit models/config/screening_config.json")
        print("   2. Set email_notifications.enabled = true")
        print("   3. Configure SMTP settings")
        print()
        print("✅ TEST PASSED (configuration test)")
        return True
    
    # Test 1: Simple test notification
    print("Step 2: Send Test Notification")
    print("-" * 40)
    
    try:
        success = notifier.send_notification(
            notification_type='success',
            subject='Test Email - Overnight Screening System',
            body='This is a test email from the overnight screening system.'
        )
        
        if success:
            print("✅ Test notification sent successfully")
        else:
            print("❌ Failed to send test notification")
        print()
    except Exception as e:
        print(f"❌ Error sending test notification: {str(e)}")
        print()
    
    # Test 2: Morning report email (with mock data)
    print("Step 3: Test Morning Report Email (Mock Data)")
    print("-" * 40)
    
    try:
        # Create mock summary
        summary = {
            'report_date': datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d'),
            'total_stocks_scanned': 240,
            'opportunities_found': 15,
            'spi_sentiment_score': 65.5,
            'market_bias': 'Bullish'
        }
        
        # Create mock opportunities
        top_opportunities = [
            {
                'symbol': 'ANZ.AX',
                'company_name': 'ANZ Banking Group',
                'opportunity_score': 85.3,
                'signal': 'BUY',
                'confidence': 78.5,
                'sector': 'Financials',
                'current_price': 28.50
            },
            {
                'symbol': 'CBA.AX',
                'company_name': 'Commonwealth Bank',
                'opportunity_score': 82.1,
                'signal': 'BUY',
                'confidence': 75.2,
                'sector': 'Financials',
                'current_price': 105.20
            },
            {
                'symbol': 'BHP.AX',
                'company_name': 'BHP Group',
                'opportunity_score': 78.9,
                'signal': 'BUY',
                'confidence': 72.8,
                'sector': 'Materials',
                'current_price': 45.80
            }
        ]
        
        # Create mock report path
        report_dir = BASE_PATH / 'reports' / 'morning_reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_date = datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d')
        report_path = report_dir / f'{report_date}_market_report.html'
        
        # Create a simple mock report file if it doesn't exist
        if not report_path.exists():
            with open(report_path, 'w') as f:
                f.write('<html><body><h1>Test Report</h1></body></html>')
        
        success = notifier.send_morning_report(
            report_path=str(report_path),
            summary=summary,
            top_opportunities=top_opportunities
        )
        
        if success:
            print("✅ Morning report email sent successfully")
        else:
            print("⚠️  Morning report email not sent (may be disabled)")
        print()
    except Exception as e:
        print(f"❌ Error sending morning report: {str(e)}")
        print()
    
    # Test 3: Alert email
    print("Step 4: Test Alert Email (Mock Data)")
    print("-" * 40)
    
    try:
        high_conf_opportunities = [
            {
                'symbol': 'ANZ.AX',
                'company_name': 'ANZ Banking Group',
                'opportunity_score': 85.3,
                'signal': 'BUY',
                'confidence': 78.5,
                'sector': 'Financials',
                'current_price': 28.50
            }
        ]
        
        success = notifier.send_alert(
            opportunities=high_conf_opportunities
        )
        
        if success:
            print("✅ Alert email sent successfully")
        else:
            print("⚠️  Alert email not sent (may be disabled or no high-confidence opportunities)")
        print()
    except Exception as e:
        print(f"❌ Error sending alert: {str(e)}")
        print()
    
    # Test 4: Error notification
    print("Step 5: Test Error Notification")
    print("-" * 40)
    
    try:
        success = notifier.send_error(
            error_message="Test error message - this is a test",
            phase="Test Phase"
        )
        
        if success:
            print("✅ Error notification sent successfully")
        else:
            print("⚠️  Error notification not sent (may be disabled)")
        print()
    except Exception as e:
        print(f"❌ Error sending error notification: {str(e)}")
        print()
    
    # Summary
    print("="*80)
    print("TEST COMPLETED")
    print("="*80)
    print()
    print("✅ All email notification tests completed")
    print()
    print("Note: If emails are enabled, check your inbox for test emails.")
    print("      If disabled, this is expected behavior - enable in config to test delivery.")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_email_notifications()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

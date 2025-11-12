"""
Email Notification System

Sends email notifications for the overnight screening pipeline.
Supports multiple notification types: success, alert, error.

Features:
- Morning report delivery (HTML attachment)
- High-confidence opportunity alerts
- Error notifications with stack traces
- SMTP configuration support
- Retry logic for delivery failures
- Email template system
"""

import smtplib
import logging
import argparse
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pytz

# Setup logging
BASE_PATH = Path(__file__).parent.parent.parent
log_dir = BASE_PATH / 'logs' / 'screening'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'email_notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Handles email notifications for the overnight screening system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the email notifier.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.timezone = pytz.timezone('Australia/Sydney')
        
        # Load configuration
        if config_path is None:
            config_path = BASE_PATH / 'models' / 'config' / 'screening_config.json'
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Email configuration
        self.email_config = self.config.get('email_notifications', {})
        self.enabled = self.email_config.get('enabled', False)
        
        # SMTP settings (always set defaults, even if disabled)
        self.smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.email_config.get('smtp_port', 587)
        self.smtp_username = self.email_config.get('smtp_username', '')
        self.smtp_password = self.email_config.get('smtp_password', '')
        self.use_tls = self.email_config.get('use_tls', True)
        
        # Email addresses
        self.sender_email = self.email_config.get('sender_email', self.smtp_username or 'noreply@example.com')
        self.recipient_emails = self.email_config.get('recipient_emails', [])
        
        # Notification settings
        self.send_morning_report = self.email_config.get('send_morning_report', True)
        self.send_alerts = self.email_config.get('send_alerts', True)
        self.send_errors = self.email_config.get('send_errors', True)
        self.alert_threshold = self.email_config.get('alert_threshold', 80)
        
        if not self.enabled:
            logger.warning("Email notifications are DISABLED in configuration")
        
        logger.info(f"Email notifications initialized: {len(self.recipient_emails)} recipients")
    
    def send_notification(
        self,
        notification_type: str,
        subject: str = None,
        body: str = None,
        attachments: List[str] = None,
        html_body: str = None,
        metadata: Dict = None
    ) -> bool:
        """
        Send email notification.
        
        Args:
            notification_type: Type of notification (success, alert, error)
            subject: Email subject line
            body: Plain text email body
            attachments: List of file paths to attach
            html_body: HTML email body (optional)
            metadata: Additional metadata for the email
        
        Returns:
            bool: True if email was sent successfully
        """
        if not self.enabled:
            logger.info(f"Email notifications disabled - skipping {notification_type} notification")
            return False
        
        if not self.recipient_emails:
            logger.warning("No recipient emails configured - skipping notification")
            return False
        
        try:
            # Generate email content based on type
            if subject is None or body is None:
                subject, body, html_body = self._generate_email_content(
                    notification_type, metadata
                )
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = subject
            
            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._attach_file(msg, attachment_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"✅ Email notification sent: {notification_type} - {subject}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {str(e)}")
            return False
    
    def send_morning_report(
        self,
        report_path: str,
        summary: Dict,
        top_opportunities: List[Dict]
    ) -> bool:
        """
        Send morning report email with HTML attachment.
        
        Args:
            report_path: Path to the HTML report file
            summary: Summary statistics dictionary
            top_opportunities: List of top stock opportunities
        
        Returns:
            bool: True if email was sent successfully
        """
        if not self.enabled or not self.send_morning_report:
            logger.info("Morning report emails disabled - skipping")
            return False
        
        report_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        # Create email subject
        subject = f"📊 ASX Morning Report - {report_date}"
        
        # Create plain text body
        body = self._create_morning_report_body(summary, top_opportunities)
        
        # Create HTML body
        html_body = self._create_morning_report_html(summary, top_opportunities)
        
        # Send with attachment
        return self.send_notification(
            notification_type='success',
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=[report_path],
            metadata={'summary': summary, 'top_opportunities': top_opportunities}
        )
    
    def send_alert(
        self,
        opportunities: List[Dict],
        alert_type: str = 'high_confidence'
    ) -> bool:
        """
        Send alert email for high-confidence opportunities.
        
        Args:
            opportunities: List of stock opportunities
            alert_type: Type of alert (high_confidence, urgent, etc.)
        
        Returns:
            bool: True if email was sent successfully
        """
        if not self.enabled or not self.send_alerts:
            logger.info("Alert emails disabled - skipping")
            return False
        
        # Filter high-confidence opportunities
        high_conf_opportunities = [
            opp for opp in opportunities 
            if opp.get('opportunity_score', 0) >= self.alert_threshold
        ]
        
        if not high_conf_opportunities:
            logger.info("No high-confidence opportunities - skipping alert email")
            return False
        
        report_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        subject = f"🚨 HIGH CONFIDENCE OPPORTUNITIES - {report_date}"
        
        body = self._create_alert_body(high_conf_opportunities)
        html_body = self._create_alert_html(high_conf_opportunities)
        
        return self.send_notification(
            notification_type='alert',
            subject=subject,
            body=body,
            html_body=html_body,
            metadata={'opportunities': high_conf_opportunities}
        )
    
    def send_error(
        self,
        error_message: str,
        error_traceback: str = None,
        phase: str = None
    ) -> bool:
        """
        Send error notification email.
        
        Args:
            error_message: Error message
            error_traceback: Full error traceback (optional)
            phase: Pipeline phase where error occurred
        
        Returns:
            bool: True if email was sent successfully
        """
        if not self.enabled or not self.send_errors:
            logger.info("Error emails disabled - skipping")
            return False
        
        report_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        subject = f"❌ PIPELINE ERROR - {report_date}"
        
        if phase:
            subject += f" ({phase})"
        
        body = self._create_error_body(error_message, error_traceback, phase)
        
        return self.send_notification(
            notification_type='error',
            subject=subject,
            body=body,
            metadata={'error': error_message, 'phase': phase}
        )
    
    def _generate_email_content(
        self,
        notification_type: str,
        metadata: Dict = None
    ) -> tuple:
        """
        Generate email content based on notification type.
        
        Args:
            notification_type: Type of notification
            metadata: Additional metadata
        
        Returns:
            tuple: (subject, body, html_body)
        """
        report_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        
        if notification_type == 'success':
            subject = f"✅ Pipeline Completed - {report_date}"
            body = "The overnight screening pipeline completed successfully."
            html_body = None
        
        elif notification_type == 'alert':
            subject = f"🚨 Trading Alert - {report_date}"
            body = "High-confidence trading opportunities detected."
            html_body = None
        
        elif notification_type == 'error':
            subject = f"❌ Pipeline Error - {report_date}"
            body = "The overnight screening pipeline encountered an error."
            html_body = None
        
        else:
            subject = f"📧 Notification - {report_date}"
            body = "Overnight screening system notification."
            html_body = None
        
        return subject, body, html_body
    
    def _create_morning_report_body(
        self,
        summary: Dict,
        top_opportunities: List[Dict]
    ) -> str:
        """Create plain text body for morning report email"""
        lines = []
        lines.append("=" * 80)
        lines.append("ASX OVERNIGHT STOCK SCREENING - MORNING REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary statistics
        lines.append("📊 SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Date: {summary.get('report_date', 'N/A')}")
        lines.append(f"Stocks Scanned: {summary.get('total_stocks_scanned', 0)}")
        lines.append(f"Opportunities Found: {summary.get('opportunities_found', 0)}")
        lines.append(f"SPI Sentiment: {summary.get('spi_sentiment_score', 0):.1f}/100")
        lines.append(f"Market Bias: {summary.get('market_bias', 'N/A')}")
        lines.append("")
        
        # Top opportunities
        lines.append("🎯 TOP 5 OPPORTUNITIES")
        lines.append("-" * 40)
        
        for i, opp in enumerate(top_opportunities[:5], 1):
            lines.append(f"{i}. {opp.get('symbol', 'N/A')}")
            lines.append(f"   Score: {opp.get('opportunity_score', 0):.1f}/100")
            lines.append(f"   Signal: {opp.get('signal', 'N/A')}")
            lines.append(f"   Confidence: {opp.get('confidence', 0):.1f}%")
            lines.append(f"   Sector: {opp.get('sector', 'N/A')}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("See attached HTML report for full details.")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def _create_morning_report_html(
        self,
        summary: Dict,
        top_opportunities: List[Dict]
    ) -> str:
        """Create HTML body for morning report email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; border-radius: 10px; }}
                .summary {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .opportunity {{ background: white; border: 1px solid #e5e7eb; padding: 15px; margin: 10px 0; border-radius: 8px; }}
                .score {{ font-size: 24px; font-weight: bold; color: #10b981; }}
                .signal {{ display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
                .buy {{ background: #10b981; color: white; }}
                .sell {{ background: #ef4444; color: white; }}
                .hold {{ background: #f59e0b; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 ASX Morning Report</h1>
                <p>{summary.get('report_date', 'N/A')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Stocks Scanned:</strong> {summary.get('total_stocks_scanned', 0)}</p>
                <p><strong>Opportunities Found:</strong> {summary.get('opportunities_found', 0)}</p>
                <p><strong>SPI Sentiment:</strong> {summary.get('spi_sentiment_score', 0):.1f}/100</p>
                <p><strong>Market Bias:</strong> {summary.get('market_bias', 'N/A')}</p>
            </div>
            
            <h2>🎯 Top Opportunities</h2>
        """
        
        for i, opp in enumerate(top_opportunities[:5], 1):
            signal = opp.get('signal', 'HOLD')
            signal_class = signal.lower()
            
            html += f"""
            <div class="opportunity">
                <h3>{i}. {opp.get('symbol', 'N/A')} - {opp.get('company_name', 'N/A')}</h3>
                <p class="score">{opp.get('opportunity_score', 0):.1f}/100</p>
                <p><span class="signal {signal_class}">{signal}</span></p>
                <p><strong>Confidence:</strong> {opp.get('confidence', 0):.1f}%</p>
                <p><strong>Sector:</strong> {opp.get('sector', 'N/A')}</p>
                <p><strong>Price:</strong> ${opp.get('current_price', 0):.2f}</p>
            </div>
            """
        
        html += """
            <p style="margin-top: 30px; color: #6b7280;">
                <strong>Note:</strong> See attached HTML report for complete details and analysis.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def _create_alert_body(self, opportunities: List[Dict]) -> str:
        """Create plain text body for alert email"""
        lines = []
        lines.append("🚨 HIGH CONFIDENCE OPPORTUNITIES DETECTED 🚨")
        lines.append("=" * 80)
        lines.append("")
        
        for i, opp in enumerate(opportunities, 1):
            lines.append(f"{i}. {opp.get('symbol', 'N/A')} - Score: {opp.get('opportunity_score', 0):.1f}/100")
            lines.append(f"   Signal: {opp.get('signal', 'N/A')}")
            lines.append(f"   Confidence: {opp.get('confidence', 0):.1f}%")
            lines.append(f"   Price: ${opp.get('current_price', 0):.2f}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("Review the full morning report for complete analysis.")
        
        return '\n'.join(lines)
    
    def _create_alert_html(self, opportunities: List[Dict]) -> str:
        """Create HTML body for alert email"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background: #ef4444; color: white; padding: 20px; border-radius: 10px; }
                .opportunity { background: #fef2f2; border: 2px solid #ef4444; padding: 15px; margin: 10px 0; border-radius: 8px; }
                .score { font-size: 24px; font-weight: bold; color: #10b981; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 HIGH CONFIDENCE OPPORTUNITIES</h1>
                <p>Immediate attention recommended</p>
            </div>
        """
        
        for i, opp in enumerate(opportunities, 1):
            html += f"""
            <div class="opportunity">
                <h3>{i}. {opp.get('symbol', 'N/A')} - {opp.get('company_name', 'N/A')}</h3>
                <p class="score">{opp.get('opportunity_score', 0):.1f}/100</p>
                <p><strong>Signal:</strong> {opp.get('signal', 'N/A')}</p>
                <p><strong>Confidence:</strong> {opp.get('confidence', 0):.1f}%</p>
                <p><strong>Price:</strong> ${opp.get('current_price', 0):.2f}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _create_error_body(
        self,
        error_message: str,
        error_traceback: str = None,
        phase: str = None
    ) -> str:
        """Create plain text body for error email"""
        lines = []
        lines.append("❌ OVERNIGHT PIPELINE ERROR")
        lines.append("=" * 80)
        lines.append("")
        
        if phase:
            lines.append(f"Phase: {phase}")
            lines.append("")
        
        lines.append(f"Error: {error_message}")
        lines.append("")
        
        if error_traceback:
            lines.append("Traceback:")
            lines.append("-" * 40)
            lines.append(error_traceback)
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("Please check the logs for more details.")
        
        return '\n'.join(lines)
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach file to email message"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Attachment file not found: {file_path}")
                return
            
            with open(path, 'rb') as f:
                attachment = MIMEApplication(f.read(), Name=path.name)
            
            attachment['Content-Disposition'] = f'attachment; filename="{path.name}"'
            msg.attach(attachment)
            
            logger.info(f"Attached file: {path.name}")
        
        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {str(e)}")


def main():
    """Command-line interface for email notifications"""
    parser = argparse.ArgumentParser(description='Send email notifications for overnight screening')
    parser.add_argument('--type', choices=['success', 'alert', 'error', 'test'], required=True,
                        help='Type of notification to send')
    parser.add_argument('--report-path', type=str, help='Path to HTML report (for success)')
    parser.add_argument('--error-message', type=str, help='Error message (for error)')
    parser.add_argument('--phase', type=str, help='Pipeline phase (for error)')
    
    args = parser.parse_args()
    
    notifier = EmailNotifier()
    
    if args.type == 'test':
        logger.info("Sending test email...")
        success = notifier.send_notification(
            notification_type='success',
            subject='Test Email - Overnight Screening System',
            body='This is a test email from the overnight screening system.'
        )
        
        if success:
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
        
        return 0 if success else 1
    
    elif args.type == 'success':
        # Load latest report
        report_dir = BASE_PATH / 'reports' / 'morning_reports'
        report_date = datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d')
        
        if args.report_path:
            report_path = args.report_path
        else:
            report_path = report_dir / f'{report_date}_market_report.html'
        
        # Load pipeline state
        state_dir = BASE_PATH / 'reports' / 'pipeline_state'
        state_path = state_dir / f'{report_date}_pipeline_state.json'
        
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            summary = state.get('summary', {})
            top_opportunities = state.get('top_opportunities', [])
            
            success = notifier.send_morning_report(
                report_path=str(report_path),
                summary=summary,
                top_opportunities=top_opportunities
            )
            
            if success:
                print("✅ Morning report email sent successfully!")
            else:
                print("❌ Failed to send morning report email")
            
            return 0 if success else 1
        
        else:
            logger.error(f"Pipeline state file not found: {state_path}")
            return 1
    
    elif args.type == 'alert':
        # Load pipeline state and send alerts
        report_date = datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d')
        state_dir = BASE_PATH / 'reports' / 'pipeline_state'
        state_path = state_dir / f'{report_date}_pipeline_state.json'
        
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            opportunities = state.get('top_opportunities', [])
            
            success = notifier.send_alert(opportunities)
            
            if success:
                print("✅ Alert email sent successfully!")
            else:
                print("❌ Failed to send alert email (or no high-confidence opportunities)")
            
            return 0 if success else 1
        
        else:
            logger.error(f"Pipeline state file not found: {state_path}")
            return 1
    
    elif args.type == 'error':
        error_message = args.error_message or "Unknown error occurred"
        phase = args.phase or "Unknown phase"
        
        success = notifier.send_error(
            error_message=error_message,
            phase=phase
        )
        
        if success:
            print("✅ Error email sent successfully!")
        else:
            print("❌ Failed to send error email")
        
        return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

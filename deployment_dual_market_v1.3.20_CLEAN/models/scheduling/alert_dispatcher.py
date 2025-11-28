"""
Alert Dispatcher for Phase 3 Auto-Rescan
=========================================

This module handles multi-channel alert dispatching for real-time
trading opportunities.

Alert Channels:
- Email (via SMTP)
- SMS (via Twilio)
- Webhook (Slack, Discord, Custom)
- Telegram (text + file attachments)
- Console (for development/testing)

Author: FinBERT Enhanced Stock Screener
Version: 1.1.0 (Phase 3 Auto-Rescan + Telegram)
"""

import logging
import smtplib
import json
import requests
import sys
from typing import Dict, List, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Add parent directory to path for imports
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from models.notifications.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class AlertDispatcher:
    """
    Multi-channel alert dispatcher for trading opportunities.
    
    Supports:
    - Email alerts (SMTP)
    - SMS alerts (Twilio)
    - Webhook alerts (Slack, Discord, custom)
    - Telegram alerts (text + file attachments)
    - Console logging
    """
    
    def __init__(
        self,
        config: Optional[Dict] = None,
        config_file: Optional[str] = None
    ):
        """
        Initialize alert dispatcher.
        
        Args:
            config: Alert configuration dictionary
            config_file: Path to JSON configuration file
        """
        self.config = config or {}
        
        # Load config from file if provided
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with provided config
                    self.config = {**file_config.get('alerts', {}), **self.config}
            except Exception as e:
                logger.error(f"Failed to load alert config: {e}")
        
        # Alert channels configuration
        self.email_enabled = self.config.get('email', {}).get('enabled', False)
        self.sms_enabled = self.config.get('sms', {}).get('enabled', False)
        self.webhook_enabled = self.config.get('webhook', {}).get('enabled', False)
        self.telegram_enabled = self.config.get('telegram', {}).get('enabled', False)
        
        # Initialize Telegram notifier
        if self.telegram_enabled:
            try:
                telegram_config = self.config.get('telegram', {})
                self.telegram = TelegramNotifier(
                    bot_token=telegram_config.get('bot_token'),
                    chat_id=telegram_config.get('chat_id')
                )
                if not self.telegram.enabled:
                    self.telegram_enabled = False
                    logger.warning("Telegram credentials not configured")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram: {e}")
                self.telegram_enabled = False
                self.telegram = None
        else:
            self.telegram = None
        
        # Alert history
        self.sent_alerts: List[Dict] = []
        
        logger.info(f"AlertDispatcher initialized:")
        logger.info(f"  Email alerts: {'ENABLED' if self.email_enabled else 'DISABLED'}")
        logger.info(f"  SMS alerts: {'ENABLED' if self.sms_enabled else 'DISABLED'}")
        logger.info(f"  Webhook alerts: {'ENABLED' if self.webhook_enabled else 'DISABLED'}")
        logger.info(f"  Telegram alerts: {'ENABLED' if self.telegram_enabled else 'DISABLED'}")
    
    def send_email_alert(
        self,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """
        Send email alert via SMTP.
        
        Args:
            subject: Email subject
            body: Plain text body
            html: Optional HTML body
            
        Returns:
            True if sent successfully
        """
        if not self.email_enabled:
            logger.debug("Email alerts disabled, skipping")
            return False
        
        try:
            email_config = self.config.get('email', {})
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config.get('from_address', '')
            msg['To'] = ', '.join(email_config.get('to_addresses', []))
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            # Send via SMTP
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            smtp_user = email_config.get('smtp_username', '')
            smtp_pass = email_config.get('smtp_password', '')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_sms_alert(
        self,
        message: str,
        phone_numbers: Optional[List[str]] = None
    ) -> bool:
        """
        Send SMS alert via Twilio.
        
        Args:
            message: SMS message text
            phone_numbers: Optional list of phone numbers (uses config if not provided)
            
        Returns:
            True if sent successfully
        """
        if not self.sms_enabled:
            logger.debug("SMS alerts disabled, skipping")
            return False
        
        try:
            sms_config = self.config.get('sms', {})
            
            # Get Twilio credentials
            account_sid = sms_config.get('twilio_account_sid', '')
            auth_token = sms_config.get('twilio_auth_token', '')
            from_number = sms_config.get('twilio_from_number', '')
            
            if not all([account_sid, auth_token, from_number]):
                logger.warning("Twilio credentials incomplete")
                return False
            
            # Use provided numbers or config numbers
            to_numbers = phone_numbers or sms_config.get('to_numbers', [])
            
            if not to_numbers:
                logger.warning("No phone numbers configured")
                return False
            
            # Import Twilio (optional dependency)
            try:
                from twilio.rest import Client
            except ImportError:
                logger.error("Twilio library not installed. Install with: pip install twilio")
                return False
            
            client = Client(account_sid, auth_token)
            
            # Send to each number
            success_count = 0
            for to_number in to_numbers:
                try:
                    message_obj = client.messages.create(
                        body=message,
                        from_=from_number,
                        to=to_number
                    )
                    success_count += 1
                    logger.debug(f"SMS sent to {to_number}: {message_obj.sid}")
                except Exception as e:
                    logger.error(f"Failed to send SMS to {to_number}: {e}")
            
            if success_count > 0:
                logger.info(f"SMS alert sent to {success_count}/{len(to_numbers)} numbers")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False
    
    def send_webhook_alert(
        self,
        data: Dict,
        webhook_url: Optional[str] = None
    ) -> bool:
        """
        Send webhook alert (Slack, Discord, custom).
        
        Args:
            data: Alert data dictionary
            webhook_url: Optional webhook URL (uses config if not provided)
            
        Returns:
            True if sent successfully
        """
        if not self.webhook_enabled:
            logger.debug("Webhook alerts disabled, skipping")
            return False
        
        try:
            webhook_config = self.config.get('webhook', {})
            url = webhook_url or webhook_config.get('url', '')
            
            if not url:
                logger.warning("No webhook URL configured")
                return False
            
            webhook_type = webhook_config.get('type', 'slack')
            
            # Format payload based on webhook type
            if webhook_type == 'slack':
                payload = self._format_slack_payload(data)
            elif webhook_type == 'discord':
                payload = self._format_discord_payload(data)
            else:
                payload = data  # Custom webhook
            
            # Send POST request
            response = requests.post(
                url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook alert sent to {webhook_type}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def send_telegram_alert(
        self,
        data: Dict
    ) -> bool:
        """
        Send Telegram alert.
        
        Args:
            data: Alert data dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.telegram_enabled or not self.telegram:
            logger.debug("Telegram alerts disabled, skipping")
            return False
        
        try:
            symbol = data.get('symbol', 'Unknown')
            breakout_type = data.get('breakout_type', 'alert')
            strength = data.get('strength', 0)
            price = data.get('price', 0)
            details = data.get('details', {})
            
            return self.telegram.send_breakout_alert(
                symbol=symbol,
                breakout_type=breakout_type,
                strength=strength,
                price=price,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def _format_slack_payload(self, data: Dict) -> Dict:
        """Format data for Slack webhook"""
        symbol = data.get('symbol', 'Unknown')
        breakout_type = data.get('breakout_type', 'alert')
        strength = data.get('strength', 0)
        price = data.get('price', 0)
        
        return {
            "text": f"🚨 Trading Alert: {symbol}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 {symbol} - {breakout_type}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Strength:*\n{strength:.1f}/100"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Price:*\n${price:.2f}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Detected at {datetime.now().strftime('%H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
    
    def _format_discord_payload(self, data: Dict) -> Dict:
        """Format data for Discord webhook"""
        symbol = data.get('symbol', 'Unknown')
        breakout_type = data.get('breakout_type', 'alert')
        strength = data.get('strength', 0)
        price = data.get('price', 0)
        
        return {
            "content": f"🚨 **Trading Alert: {symbol}**",
            "embeds": [
                {
                    "title": f"{symbol} - {breakout_type}",
                    "color": 0xff6b6b if strength >= 80 else 0xfeca57,
                    "fields": [
                        {
                            "name": "Strength",
                            "value": f"{strength:.1f}/100",
                            "inline": True
                        },
                        {
                            "name": "Price",
                            "value": f"${price:.2f}",
                            "inline": True
                        }
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    def dispatch_breakout_alert(
        self,
        breakout_signal: Dict,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Dispatch alert for a breakout signal.
        
        Args:
            breakout_signal: Breakout signal dictionary
            channels: List of channels to use ('email', 'sms', 'webhook', 'all')
                     If None, uses all enabled channels
            
        Returns:
            Dictionary with success status for each channel
        """
        channels = channels or ['all']
        if 'all' in channels:
            channels = ['email', 'sms', 'webhook', 'telegram']
        
        results = {}
        
        symbol = breakout_signal.get('symbol', 'Unknown')
        breakout_type = breakout_signal.get('breakout_type', 'alert')
        strength = breakout_signal.get('strength', 0)
        price = breakout_signal.get('price', 0)
        
        # Format messages
        subject = f"🚨 Trading Alert: {symbol} - {breakout_type}"
        body = f"""
Trading Opportunity Detected
============================

Symbol: {symbol}
Type: {breakout_type}
Strength: {strength:.1f}/100
Price: ${price:.2f}

Details: {json.dumps(breakout_signal.get('details', {}), indent=2)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        sms_message = f"🚨 {symbol}: {breakout_type} (Strength: {strength:.0f}/100, Price: ${price:.2f})"
        
        # Dispatch to channels
        if 'email' in channels:
            results['email'] = self.send_email_alert(subject, body)
        
        if 'sms' in channels:
            results['sms'] = self.send_sms_alert(sms_message)
        
        if 'webhook' in channels:
            results['webhook'] = self.send_webhook_alert(breakout_signal)
        
        if 'telegram' in channels:
            results['telegram'] = self.send_telegram_alert(breakout_signal)
        
        # Log to console
        logger.info(f"ALERT DISPATCHED: {symbol} - {breakout_type} (Strength: {strength:.1f})")
        
        # Record alert
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'signal': breakout_signal,
            'channels': results
        }
        self.sent_alerts.append(alert_record)
        
        return results
    
    def get_alert_history(
        self,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get recent alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.sent_alerts[-limit:]
    
    def get_alert_stats(self) -> Dict:
        """
        Get alert statistics.
        
        Returns:
            Dictionary with alert stats
        """
        total = len(self.sent_alerts)
        
        # Count by channel
        email_count = sum(
            1 for alert in self.sent_alerts
            if alert.get('channels', {}).get('email', False)
        )
        sms_count = sum(
            1 for alert in self.sent_alerts
            if alert.get('channels', {}).get('sms', False)
        )
        webhook_count = sum(
            1 for alert in self.sent_alerts
            if alert.get('channels', {}).get('webhook', False)
        )
        telegram_count = sum(
            1 for alert in self.sent_alerts
            if alert.get('channels', {}).get('telegram', False)
        )
        
        return {
            'total_alerts': total,
            'email_sent': email_count,
            'sms_sent': sms_count,
            'webhook_sent': webhook_count,
            'telegram_sent': telegram_count,
            'email_enabled': self.email_enabled,
            'sms_enabled': self.sms_enabled,
            'webhook_enabled': self.webhook_enabled,
            'telegram_enabled': self.telegram_enabled
        }


def test_alert_dispatcher():
    """Test alert dispatcher functionality"""
    print("\n" + "="*80)
    print("TESTING ALERT DISPATCHER")
    print("="*80)
    
    # Test configuration (all disabled for testing)
    test_config = {
        'email': {
            'enabled': False,
            'from_address': 'alerts@finbert.com',
            'to_addresses': ['trader@example.com'],
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        },
        'sms': {
            'enabled': False,
            'to_numbers': ['+1234567890']
        },
        'webhook': {
            'enabled': False,
            'url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            'type': 'slack'
        }
    }
    
    dispatcher = AlertDispatcher(config=test_config)
    
    # Test breakout alert
    test_signal = {
        'symbol': 'AAPL',
        'breakout_type': 'price_breakout_up',
        'strength': 85.3,
        'price': 180.50,
        'volume': 75_000_000,
        'details': {
            'change_from_prev': 3.2,
            'prev_close': 175.00
        }
    }
    
    print("\n--- Dispatching Test Alert ---")
    results = dispatcher.dispatch_breakout_alert(test_signal)
    
    print("\nDispatch Results:")
    for channel, success in results.items():
        print(f"  {channel}: {'✓ Success' if success else '✗ Skipped/Failed'}")
    
    # Show stats
    print("\n--- Alert Statistics ---")
    stats = dispatcher.get_alert_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run test
    test_alert_dispatcher()

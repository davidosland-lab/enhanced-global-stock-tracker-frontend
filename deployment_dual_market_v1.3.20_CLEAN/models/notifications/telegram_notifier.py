"""
Telegram Notifier for Stock Screener
=====================================

This module provides Telegram bot integration for sending:
- Real-time trading alerts (text messages)
- Morning/overnight reports (HTML/PDF/CSV attachments)
- Breakout notifications with rich formatting

Setup:
1. Create bot via BotFather in Telegram: /newbot
2. Get bot token: 123456789:AA...your_bot_token_here
3. Start chat with your bot: /start
4. Get chat ID from: https://api.telegram.org/bot<TOKEN>/getUpdates
5. Add to .env:
   TELEGRAM_BOT_TOKEN=123456789:AA...your_bot_token_here
   TELEGRAM_CHAT_ID=123456789

Author: FinBERT Enhanced Stock Screener
Version: 1.0.0 (Phase 3 Telegram Integration)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram bot notifier for stock screener alerts and reports.
    
    Supports:
    - Text messages (plain and Markdown)
    - Document attachments (HTML, PDF, CSV, etc.)
    - Rich formatting for trading alerts
    - Batch notifications
    """
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown"
    ):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token (from BotFather)
            chat_id: Telegram chat ID (where to send messages)
            parse_mode: Default parse mode ('Markdown' or 'HTML')
        """
        # Load from environment if not provided
        self.token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.parse_mode = parse_mode
        
        if not self.token or not self.chat_id:
            logger.warning(
                "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. "
                "Telegram notifications disabled."
            )
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.telegram.org/bot{self.token}"
            logger.info(f"TelegramNotifier initialized (chat_id: {self.chat_id})")
    
    def send_message(
        self,
        text: str,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False
    ) -> bool:
        """
        Send a text message to Telegram.
        
        Args:
            text: Message text (max 4096 characters)
            parse_mode: Optional parse mode override ('Markdown', 'HTML', or None)
            disable_notification: If True, send silently
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug("Telegram disabled, skipping message")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            
            # Truncate if too long
            if len(text) > 4096:
                text = text[:4090] + "..."
                logger.warning("Message truncated to 4096 chars")
            
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "disable_notification": disable_notification
            }
            
            # Use provided parse_mode or default
            mode = parse_mode if parse_mode is not None else self.parse_mode
            if mode:
                payload["parse_mode"] = mode
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.ok:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_document(
        self,
        file_path: str | Path,
        caption: Optional[str] = None,
        disable_notification: bool = False
    ) -> bool:
        """
        Send a document/file to Telegram.
        
        Supports: HTML, PDF, CSV, ZIP, images, etc.
        
        Args:
            file_path: Path to file to send
            caption: Optional caption text (max 1024 chars)
            disable_notification: If True, send silently
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug("Telegram disabled, skipping document")
            return False
        
        try:
            url = f"{self.base_url}/sendDocument"
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Prepare payload
            data = {
                "chat_id": self.chat_id,
                "disable_notification": disable_notification
            }
            
            if caption:
                # Truncate caption if too long
                if len(caption) > 1024:
                    caption = caption[:1020] + "..."
                data["caption"] = caption
            
            # Send file
            with file_path.open("rb") as f:
                files = {"document": (file_path.name, f)}
                response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.ok:
                logger.info(f"Telegram document sent: {file_path.name}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram document: {e}")
            return False
    
    def send_photo(
        self,
        photo_path: str | Path,
        caption: Optional[str] = None,
        disable_notification: bool = False
    ) -> bool:
        """
        Send a photo to Telegram.
        
        Args:
            photo_path: Path to image file (JPG, PNG, etc.)
            caption: Optional caption text
            disable_notification: If True, send silently
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug("Telegram disabled, skipping photo")
            return False
        
        try:
            url = f"{self.base_url}/sendPhoto"
            photo_path = Path(photo_path)
            
            if not photo_path.exists():
                logger.error(f"Photo not found: {photo_path}")
                return False
            
            data = {
                "chat_id": self.chat_id,
                "disable_notification": disable_notification
            }
            
            if caption:
                if len(caption) > 1024:
                    caption = caption[:1020] + "..."
                data["caption"] = caption
            
            with photo_path.open("rb") as f:
                files = {"photo": (photo_path.name, f)}
                response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.ok:
                logger.info(f"Telegram photo sent: {photo_path.name}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
    
    def send_breakout_alert(
        self,
        symbol: str,
        breakout_type: str,
        strength: float,
        price: float,
        details: Dict
    ) -> bool:
        """
        Send a formatted breakout alert.
        
        Args:
            symbol: Stock symbol
            breakout_type: Type of breakout
            strength: Signal strength (0-100)
            price: Current price
            details: Additional details dictionary
            
        Returns:
            True if sent successfully
        """
        # Format message with Markdown
        emoji = "🚀" if strength >= 80 else "📈" if strength >= 70 else "📊"
        
        message = f"{emoji} *BREAKOUT ALERT*\n\n"
        message += f"*Symbol:* `{symbol}`\n"
        message += f"*Type:* {breakout_type.replace('_', ' ').title()}\n"
        message += f"*Strength:* {strength:.1f}/100\n"
        message += f"*Price:* ${price:.2f}\n"
        message += f"*Time:* {datetime.now().strftime('%H:%M:%S')}\n"
        
        # Add key details
        if details:
            message += f"\n*Details:*\n"
            for key, value in list(details.items())[:3]:  # Top 3 details
                if isinstance(value, (int, float)):
                    message += f"• {key}: {value:.2f}\n"
                else:
                    message += f"• {key}: {value}\n"
        
        return self.send_message(message, parse_mode="Markdown")
    
    def send_morning_report(
        self,
        report_path: str | Path,
        market: str = "US",
        summary: Optional[Dict] = None
    ) -> bool:
        """
        Send morning/overnight report as attachment.
        
        Args:
            report_path: Path to report file (HTML, PDF, CSV)
            market: Market name (US or ASX)
            summary: Optional summary dictionary
            
        Returns:
            True if sent successfully
        """
        report_path = Path(report_path)
        
        if not report_path.exists():
            logger.error(f"Report not found: {report_path}")
            return False
        
        # Format caption with summary
        caption = f"📊 *{market} Morning Report*\n"
        caption += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
        
        if summary:
            caption += f"\n"
            if 'stocks_scanned' in summary:
                caption += f"Stocks Scanned: {summary['stocks_scanned']}\n"
            if 'top_opportunities' in summary:
                caption += f"Top Picks: {summary['top_opportunities']}\n"
            if 'execution_time' in summary:
                caption += f"Scan Time: {summary['execution_time']:.1f} min\n"
        
        return self.send_document(report_path, caption=caption)
    
    def send_batch_alerts(
        self,
        alerts: List[Dict],
        max_alerts: int = 10
    ) -> Dict[str, int]:
        """
        Send multiple alerts in batch.
        
        Args:
            alerts: List of alert dictionaries
            max_alerts: Maximum alerts to send
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        # Limit to max_alerts
        if len(alerts) > max_alerts:
            logger.warning(f"Too many alerts ({len(alerts)}), limiting to {max_alerts}")
            results["skipped"] = len(alerts) - max_alerts
            alerts = alerts[:max_alerts]
        
        for alert in alerts:
            success = self.send_breakout_alert(
                symbol=alert.get('symbol', 'Unknown'),
                breakout_type=alert.get('breakout_type', 'alert'),
                strength=alert.get('strength', 0),
                price=alert.get('price', 0),
                details=alert.get('details', {})
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Batch alerts: {results['success']} sent, {results['failed']} failed, {results['skipped']} skipped")
        return results
    
    def test_connection(self) -> bool:
        """
        Test Telegram connection and bot token.
        
        Returns:
            True if connection successful
        """
        if not self.enabled:
            logger.error("Telegram not configured")
            return False
        
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.ok:
                bot_info = response.json()
                username = bot_info.get('result', {}).get('username', 'Unknown')
                logger.info(f"Telegram connection OK - Bot: @{username}")
                return True
            else:
                logger.error(f"Telegram connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test Telegram connection: {e}")
            return False


def test_telegram_notifier():
    """Test Telegram notifier functionality"""
    print("\n" + "="*80)
    print("TESTING TELEGRAM NOTIFIER")
    print("="*80)
    
    # Check environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("\n⚠️  Telegram not configured!")
        print("\nTo test, add to .env:")
        print("  TELEGRAM_BOT_TOKEN=123456789:AA...your_bot_token")
        print("  TELEGRAM_CHAT_ID=123456789")
        print("\nSee module docstring for setup instructions.")
        return
    
    # Initialize notifier
    notifier = TelegramNotifier()
    
    # Test connection
    print("\n--- Testing Connection ---")
    if notifier.test_connection():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
        return
    
    # Test text message
    print("\n--- Testing Text Message ---")
    test_msg = "🧪 *Test Alert*\n\nThis is a test message from the Stock Screener.\n\nTime: " + datetime.now().strftime('%H:%M:%S')
    if notifier.send_message(test_msg):
        print("✓ Text message sent")
    else:
        print("✗ Failed to send text message")
    
    # Test breakout alert
    print("\n--- Testing Breakout Alert ---")
    if notifier.send_breakout_alert(
        symbol="AAPL",
        breakout_type="price_breakout_up",
        strength=85.3,
        price=180.50,
        details={
            "change_from_prev": 3.2,
            "volume_multiple": 2.1,
            "momentum_15m": 4.5
        }
    ):
        print("✓ Breakout alert sent")
    else:
        print("✗ Failed to send breakout alert")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("Check your Telegram chat for the test messages!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_telegram_notifier()

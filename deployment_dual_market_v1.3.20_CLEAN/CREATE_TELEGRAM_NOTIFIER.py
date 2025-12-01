"""
Create Telegram Notifier File
==============================

This script creates the missing telegram_notifier.py file that's causing
the pipeline to fail.

Error fixed:
    name 'TelegramNotifier' is not defined

Usage:
    python CREATE_TELEGRAM_NOTIFIER.py
"""

import os
from pathlib import Path

# The complete telegram_notifier.py content
TELEGRAM_NOTIFIER_CONTENT = '''"""
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
        file_path: str,
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
    
    def send_morning_report(
        self,
        report_path: str,
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
        caption = f"📊 *{market} Morning Report*\\n"
        caption += f"_{datetime.now().strftime('%Y-%m-%d %H:%M')}_\\n"
        
        if summary:
            caption += f"\\n"
            if 'stocks_scanned' in summary:
                caption += f"Stocks Scanned: {summary['stocks_scanned']}\\n"
            if 'top_opportunities' in summary:
                caption += f"Top Picks: {summary['top_opportunities']}\\n"
            if 'execution_time' in summary:
                caption += f"Scan Time: {summary['execution_time']:.1f} min\\n"
        
        return self.send_document(report_path, caption=caption)


if __name__ == "__main__":
    # Test
    print("TelegramNotifier module loaded successfully")
'''

def main():
    print("\n" + "="*80)
    print("CREATE TELEGRAM NOTIFIER FILE")
    print("="*80)
    print("\nThis will create the missing telegram_notifier.py file")
    print("that's causing your pipeline to fail.\n")
    
    # Check current directory
    current_dir = Path.cwd()
    target_dir = current_dir / "models" / "notifications"
    target_file = target_dir / "telegram_notifier.py"
    
    print(f"Current directory: {current_dir}")
    print(f"Target file: {target_file}")
    
    # Check if we're in the right place
    if not (current_dir / "models" / "screening").exists():
        print("\n❌ ERROR: Not in the correct directory!")
        print("\nPlease run this from: C:\\Users\\david\\AATelS")
        print(f"Current directory: {current_dir}")
        input("\nPress Enter to exit...")
        return 1
    
    # Create directory if needed
    print("\n[1/3] Creating directories...")
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Directory created: {target_dir}")
    
    # Create __init__.py if missing
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")
        print(f"✓ Created: {init_file}")
    
    # Check if file already exists
    if target_file.exists():
        print(f"\n⚠️  File already exists: {target_file}")
        response = input("Overwrite it? (y/n): ").lower()
        if response != 'y':
            print("\nCancelled. No changes made.")
            input("\nPress Enter to exit...")
            return 0
        
        # Backup existing file
        backup_file = target_file.parent / f"{target_file.name}.backup"
        import shutil
        shutil.copy2(target_file, backup_file)
        print(f"✓ Backup created: {backup_file}")
    
    # Write the file
    print("\n[2/3] Writing telegram_notifier.py...")
    target_file.write_text(TELEGRAM_NOTIFIER_CONTENT, encoding='utf-8')
    print(f"✓ File created: {target_file}")
    print(f"  Size: {target_file.stat().st_size:,} bytes")
    
    # Verify
    print("\n[3/3] Verifying installation...")
    if target_file.exists() and target_file.stat().st_size > 1000:
        print("✓ File exists and has content")
    else:
        print("✗ Verification failed")
        input("\nPress Enter to exit...")
        return 1
    
    # Success
    print("\n" + "="*80)
    print("INSTALLATION COMPLETE!")
    print("="*80)
    print("\n✓ telegram_notifier.py created successfully")
    print(f"✓ Location: {target_file}")
    print("\nYour pipeline should now work without the 'TelegramNotifier' error!")
    print("\nNext steps:")
    print("  1. Run: pipeline.bat")
    print("  2. Check for Phase 8: TELEGRAM NOTIFICATIONS")
    print("\n" + "="*80)
    
    input("\nPress Enter to exit...")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        exit(1)

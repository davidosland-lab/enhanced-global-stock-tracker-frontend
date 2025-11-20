"""
Error Notification Script

Sends error notifications when the overnight screening pipeline fails.
Supports multiple notification channels: email, file logging, and console output.

Features:
- Error email notifications (if configured)
- Error log file generation
- Detailed error report with context
- Stack trace capture
- Recovery suggestions
- Configurable notification settings

Usage:
    python send_error_notification.py
    python send_error_notification.py --error "Custom error message"
    python send_error_notification.py --progress-file path/to/progress.json
"""

import json
import logging
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import pytz

logger = logging.getLogger(__name__)


class ErrorNotifier:
    """
    Handles error notifications for the overnight screening pipeline.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize error notifier.
        
        Args:
            config_file: Path to notification configuration JSON file
        """
        self.timezone = pytz.timezone('Australia/Sydney')
        self.config = self._load_config(config_file)
        
    def _load_config(self, config_file: Optional[Path]) -> Dict:
        """Load notification configuration"""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': '',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_address': '',
                'to_addresses': [],
                'use_tls': True
            },
            'log_file': {
                'enabled': True,
                'path': 'logs/screening/errors.log'
            },
            'console': {
                'enabled': True
            }
        }
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}, using defaults")
        
        return default_config
        
    def send_error_notification(self, error_message: str, 
                                progress_data: Optional[Dict] = None):
        """
        Send error notification via all enabled channels.
        
        Args:
            error_message: Main error message
            progress_data: Pipeline progress data for context
        """
        timestamp = datetime.now(self.timezone)
        
        # Build comprehensive error report
        report = self._build_error_report(error_message, progress_data, timestamp)
        
        # Send via enabled channels
        if self.config['console']['enabled']:
            self._send_console_notification(report)
        
        if self.config['log_file']['enabled']:
            self._send_log_notification(report)
        
        if self.config['email']['enabled']:
            self._send_email_notification(report, timestamp)
            
    def _build_error_report(self, error_message: str, 
                           progress_data: Optional[Dict],
                           timestamp: datetime) -> str:
        """Build detailed error report"""
        lines = []
        lines.append("="*80)
        lines.append("OVERNIGHT SCREENER - ERROR NOTIFICATION")
        lines.append("="*80)
        lines.append(f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        lines.append("")
        lines.append(f"ERROR: {error_message}")
        lines.append("")
        
        if progress_data:
            lines.append("Pipeline Status:")
            lines.append(f"  Overall Status: {progress_data.get('overall_status', 'unknown')}")
            lines.append(f"  Overall Progress: {progress_data.get('overall_progress', 0):.1f}%")
            
            start_time = progress_data.get('start_time')
            if start_time:
                lines.append(f"  Started: {start_time}")
            
            exec_time = progress_data.get('execution_time_formatted')
            if exec_time:
                lines.append(f"  Elapsed: {exec_time}")
            
            lines.append("")
            
            # Failed stage
            stages = progress_data.get('stages', {})
            for stage_name, stage_data in stages.items():
                if stage_data.get('status') == 'failed':
                    lines.append(f"Failed Stage: {stage_name}")
                    lines.append(f"  Progress: {stage_data.get('progress', 0)}%")
                    lines.append(f"  Message: {stage_data.get('message', 'N/A')}")
                    lines.append("")
            
            # Recent errors
            errors = progress_data.get('errors', [])
            if errors:
                lines.append("Recent Errors:")
                for err in errors[-5:]:  # Last 5 errors
                    lines.append(f"  [{err.get('timestamp')}] {err.get('message')}")
                lines.append("")
            
            # Metrics
            metrics = progress_data.get('metrics', {})
            if any(metrics.values()):
                lines.append("Metrics at Failure:")
                lines.append(f"  Stocks Scanned: {metrics.get('stocks_scanned', 0)}")
                lines.append(f"  Models Trained: {metrics.get('models_trained', 0)}")
                lines.append(f"  Predictions Generated: {metrics.get('predictions_generated', 0)}")
                lines.append("")
        
        # Recovery suggestions
        lines.append("Recovery Suggestions:")
        lines.append("  1. Check logs in: logs/screening/")
        lines.append("  2. Verify API credentials and rate limits")
        lines.append("  3. Check network connectivity")
        lines.append("  4. Ensure sufficient disk space")
        lines.append("  5. Review error messages above for specific issues")
        lines.append("  6. Try running manually: RUN_OVERNIGHT_SCREENER.bat")
        lines.append("")
        
        lines.append("="*80)
        
        return '\n'.join(lines)
        
    def _send_console_notification(self, report: str):
        """Print error report to console"""
        print("\n" + report + "\n")
        
    def _send_log_notification(self, report: str):
        """Write error report to log file"""
        try:
            base_path = Path(__file__).parent.parent.parent
            log_path = base_path / self.config['log_file']['path']
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to error log
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write('\n' + report + '\n')
            
            print(f"Error logged to: {log_path}")
            
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")
            
    def _send_email_notification(self, report: str, timestamp: datetime):
        """Send error notification via email"""
        config = self.config['email']
        
        if not all([config['smtp_server'], config['from_address'], config['to_addresses']]):
            logger.warning("Email configuration incomplete, skipping email notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config['from_address']
            msg['To'] = ', '.join(config['to_addresses'])
            msg['Subject'] = f"🚨 FinBERT Screener Failed - {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            # Add body
            msg.attach(MIMEText(report, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config['use_tls']:
                    server.starttls()
                
                if config['username'] and config['password']:
                    server.login(config['username'], config['password'])
                
                server.send_message(msg)
            
            logger.info(f"Error notification email sent to: {', '.join(config['to_addresses'])}")
            print(f"✓ Error notification email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send error notification email: {e}")
            print(f"✗ Failed to send email notification: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Send error notification for overnight screening pipeline'
    )
    
    parser.add_argument(
        '--error', '-e',
        type=str,
        help='Custom error message'
    )
    
    parser.add_argument(
        '--progress-file', '-p',
        type=Path,
        help='Path to progress JSON file for context'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Path to notification configuration file'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Load progress data if available
    progress_data = None
    if args.progress_file:
        progress_file = args.progress_file
    else:
        base_path = Path(__file__).parent.parent.parent
        progress_file = base_path / 'reports' / 'screener_progress.json'
    
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load progress file: {e}")
    
    # Determine error message
    if args.error:
        error_message = args.error
    elif progress_data and progress_data.get('errors'):
        # Use most recent error from progress data
        last_error = progress_data['errors'][-1]
        error_message = last_error.get('message', 'Unknown error')
    else:
        error_message = "Overnight screening pipeline failed (no error details available)"
    
    # Send notification
    notifier = ErrorNotifier(config_file=args.config)
    notifier.send_error_notification(error_message, progress_data)
    
    print("\nError notification process complete.")


if __name__ == '__main__':
    main()

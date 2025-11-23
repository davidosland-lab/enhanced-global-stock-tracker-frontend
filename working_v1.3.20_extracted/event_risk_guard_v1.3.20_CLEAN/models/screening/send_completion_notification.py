"""
Completion Notification Script

Sends success notifications when the overnight screening pipeline completes successfully.
Provides summary of results and links to generated reports.

Features:
- Success email notifications (if configured)
- Completion log generation
- Summary of opportunities found
- Links to report files
- Performance metrics
- Configurable notification settings

Usage:
    python send_completion_notification.py
    python send_completion_notification.py --progress-file path/to/progress.json
    python send_completion_notification.py --report-path path/to/report.html
"""

import json
import logging
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import pytz

logger = logging.getLogger(__name__)


class CompletionNotifier:
    """
    Handles completion notifications for the overnight screening pipeline.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize completion notifier.
        
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
                'use_tls': True,
                'attach_report': False
            },
            'log_file': {
                'enabled': True,
                'path': 'logs/screening/completions.log'
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
        
    def send_completion_notification(self, progress_data: Optional[Dict] = None,
                                     report_path: Optional[Path] = None):
        """
        Send completion notification via all enabled channels.
        
        Args:
            progress_data: Pipeline progress data
            report_path: Path to generated HTML report
        """
        timestamp = datetime.now(self.timezone)
        
        # Build summary report
        summary = self._build_summary_report(progress_data, report_path, timestamp)
        
        # Send via enabled channels
        if self.config['console']['enabled']:
            self._send_console_notification(summary)
        
        if self.config['log_file']['enabled']:
            self._send_log_notification(summary)
        
        if self.config['email']['enabled']:
            self._send_email_notification(summary, timestamp, report_path)
            
    def _build_summary_report(self, progress_data: Optional[Dict],
                             report_path: Optional[Path],
                             timestamp: datetime) -> str:
        """Build completion summary report"""
        lines = []
        lines.append("="*80)
        lines.append("OVERNIGHT SCREENER - COMPLETION NOTIFICATION")
        lines.append("="*80)
        lines.append(f"Completion Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        lines.append("")
        lines.append("✓ Pipeline completed successfully!")
        lines.append("")
        
        if progress_data:
            # Timing information
            start_time = progress_data.get('start_time')
            end_time = progress_data.get('end_time')
            exec_time = progress_data.get('execution_time_formatted')
            
            if start_time and end_time:
                lines.append("Execution Timeline:")
                lines.append(f"  Started:  {start_time}")
                lines.append(f"  Finished: {end_time}")
                if exec_time:
                    lines.append(f"  Duration: {exec_time}")
                lines.append("")
            
            # Metrics
            metrics = progress_data.get('metrics', {})
            if any(metrics.values()):
                lines.append("Processing Metrics:")
                lines.append(f"  Stocks Scanned:         {metrics.get('stocks_scanned', 0)}")
                lines.append(f"  Models Trained:         {metrics.get('models_trained', 0)}")
                lines.append(f"  Predictions Generated:  {metrics.get('predictions_generated', 0)}")
                lines.append(f"  Opportunities Found:    {metrics.get('opportunities_found', 0)}")
                lines.append("")
            
            # Stage completion status
            stages = progress_data.get('stages', {})
            completed_stages = [name for name, data in stages.items() 
                              if data.get('status') == 'complete']
            
            lines.append(f"Completed Stages: {len(completed_stages)}/{len(stages)}")
            for stage_name in completed_stages:
                lines.append(f"  ✓ {stage_name.replace('_', ' ').title()}")
            lines.append("")
            
            # Warnings (if any)
            warnings = progress_data.get('warnings', [])
            if warnings:
                lines.append(f"Warnings: {len(warnings)}")
                for warning in warnings[-5:]:  # Last 5 warnings
                    lines.append(f"  ⚠ {warning.get('message', 'Unknown warning')}")
                lines.append("")
        
        # Report location
        if report_path and report_path.exists():
            lines.append("Generated Report:")
            lines.append(f"  Location: {report_path}")
            lines.append(f"  Size: {self._format_file_size(report_path.stat().st_size)}")
            lines.append("")
            lines.append("View the report by opening it in your web browser.")
            lines.append("")
        
        # Next steps
        lines.append("Next Steps:")
        lines.append("  1. Review the morning report for top opportunities")
        lines.append("  2. Validate high-confidence predictions")
        lines.append("  3. Check risk ratings before trading")
        lines.append("  4. Monitor market open alignment with predictions")
        lines.append("")
        
        lines.append("="*80)
        
        return '\n'.join(lines)
        
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def _send_console_notification(self, summary: str):
        """Print summary to console"""
        print("\n" + summary + "\n")
        
    def _send_log_notification(self, summary: str):
        """Write summary to log file"""
        try:
            base_path = Path(__file__).parent.parent.parent
            log_path = base_path / self.config['log_file']['path']
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to completion log
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write('\n' + summary + '\n')
            
            print(f"Completion logged to: {log_path}")
            
        except Exception as e:
            logger.error(f"Failed to write completion log: {e}")
            
    def _send_email_notification(self, summary: str, timestamp: datetime,
                                 report_path: Optional[Path] = None):
        """Send completion notification via email"""
        config = self.config['email']
        
        if not all([config['smtp_server'], config['from_address'], config['to_addresses']]):
            logger.warning("Email configuration incomplete, skipping email notification")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config['from_address']
            msg['To'] = ', '.join(config['to_addresses'])
            msg['Subject'] = f"✓ FinBERT Screener Complete - {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            # Add body
            msg.attach(MIMEText(summary, 'plain'))
            
            # Attach report if configured and available
            if config.get('attach_report', False) and report_path and report_path.exists():
                try:
                    with open(report_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={report_path.name}'
                    )
                    msg.attach(part)
                    logger.info(f"Attached report: {report_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to attach report: {e}")
            
            # Send via SMTP
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                if config['use_tls']:
                    server.starttls()
                
                if config['username'] and config['password']:
                    server.login(config['username'], config['password'])
                
                server.send_message(msg)
            
            logger.info(f"Completion notification email sent to: {', '.join(config['to_addresses'])}")
            print(f"✓ Completion notification email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send completion notification email: {e}")
            print(f"✗ Failed to send email notification: {e}")


def find_latest_report() -> Optional[Path]:
    """Find the most recently generated report"""
    base_path = Path(__file__).parent.parent.parent
    reports_dir = base_path / 'reports' / 'screening_results'
    
    if not reports_dir.exists():
        return None
    
    # Find all HTML reports
    report_files = list(reports_dir.glob('screening_report_*.html'))
    
    if not report_files:
        return None
    
    # Return most recent by modification time
    return max(report_files, key=lambda p: p.stat().st_mtime)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Send completion notification for overnight screening pipeline'
    )
    
    parser.add_argument(
        '--progress-file', '-p',
        type=Path,
        help='Path to progress JSON file'
    )
    
    parser.add_argument(
        '--report-path', '-r',
        type=Path,
        help='Path to generated report HTML file'
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
    
    # Load progress data
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
    
    # Determine report path
    if args.report_path:
        report_path = args.report_path
    else:
        # Try to find latest report
        report_path = find_latest_report()
    
    # Send notification
    notifier = CompletionNotifier(config_file=args.config)
    notifier.send_completion_notification(progress_data, report_path)
    
    print("\nCompletion notification process complete.")


if __name__ == '__main__':
    main()

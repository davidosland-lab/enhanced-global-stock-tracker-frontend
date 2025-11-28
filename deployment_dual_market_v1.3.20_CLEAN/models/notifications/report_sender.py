"""
Report Sender for Morning/Overnight Reports
============================================

This module handles sending daily/overnight reports via Telegram.

Supports:
- Morning report HTML attachments
- Summary notifications
- Multi-market reports (US + ASX)

Author: FinBERT Enhanced Stock Screener
Version: 1.0.0 (Telegram Integration)
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from .telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class ReportSender:
    """
    Sends overnight/morning reports via Telegram.
    
    Automatically attaches HTML reports and includes summary.
    """
    
    def __init__(
        self,
        telegram_notifier: Optional[TelegramNotifier] = None
    ):
        """
        Initialize report sender.
        
        Args:
            telegram_notifier: Optional TelegramNotifier instance
        """
        self.telegram = telegram_notifier or TelegramNotifier()
        
        if self.telegram.enabled:
            logger.info("ReportSender initialized with Telegram")
        else:
            logger.warning("Telegram not configured, reports won't be sent")
    
    def send_morning_report(
        self,
        report_path: str | Path,
        market: str = "US",
        pipeline_results: Optional[Dict] = None
    ) -> bool:
        """
        Send morning/overnight report via Telegram.
        
        Args:
            report_path: Path to HTML report file
            market: Market identifier ('US' or 'ASX')
            pipeline_results: Optional pipeline results dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.telegram.enabled:
            logger.debug("Telegram disabled, skipping morning report")
            return False
        
        report_path = Path(report_path)
        
        if not report_path.exists():
            logger.error(f"Report file not found: {report_path}")
            return False
        
        # Extract summary from pipeline results
        summary = self._extract_summary(pipeline_results, market)
        
        # Send report
        try:
            success = self.telegram.send_morning_report(
                report_path=report_path,
                market=market,
                summary=summary
            )
            
            if success:
                logger.info(f"{market} morning report sent via Telegram")
            else:
                logger.warning(f"Failed to send {market} morning report via Telegram")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending morning report: {e}")
            return False
    
    def send_summary_notification(
        self,
        market: str,
        summary: Dict
    ) -> bool:
        """
        Send a text summary notification (without report attachment).
        
        Args:
            market: Market identifier
            summary: Summary dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.telegram.enabled:
            return False
        
        try:
            # Format summary message
            message = self._format_summary_message(market, summary)
            
            return self.telegram.send_message(
                text=message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error sending summary notification: {e}")
            return False
    
    def send_dual_market_summary(
        self,
        us_report_path: Optional[str | Path] = None,
        asx_report_path: Optional[str | Path] = None,
        us_summary: Optional[Dict] = None,
        asx_summary: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """
        Send reports for both US and ASX markets.
        
        Args:
            us_report_path: Path to US report
            asx_report_path: Path to ASX report
            us_summary: US pipeline summary
            asx_summary: ASX pipeline summary
            
        Returns:
            Dictionary with success status for each market
        """
        results = {}
        
        # Send US report
        if us_report_path:
            results['us'] = self.send_morning_report(
                us_report_path,
                market="US",
                pipeline_results=us_summary
            )
        
        # Send ASX report
        if asx_report_path:
            results['asx'] = self.send_morning_report(
                asx_report_path,
                market="ASX",
                pipeline_results=asx_summary
            )
        
        return results
    
    def _extract_summary(
        self,
        pipeline_results: Optional[Dict],
        market: str
    ) -> Dict:
        """Extract key metrics from pipeline results"""
        if not pipeline_results:
            return {}
        
        summary = {}
        
        # Common fields
        if 'total_stocks' in pipeline_results:
            summary['stocks_scanned'] = pipeline_results['total_stocks']
        
        if 'top_opportunities' in pipeline_results:
            top_opps = pipeline_results['top_opportunities']
            if isinstance(top_opps, list):
                summary['top_opportunities'] = len(top_opps)
            elif isinstance(top_opps, int):
                summary['top_opportunities'] = top_opps
        
        if 'execution_time_minutes' in pipeline_results:
            summary['execution_time'] = pipeline_results['execution_time_minutes']
        elif 'execution_time' in pipeline_results:
            summary['execution_time'] = pipeline_results['execution_time']
        
        # Market sentiment
        if 'market_sentiment' in pipeline_results:
            sentiment = pipeline_results['market_sentiment']
            if isinstance(sentiment, dict):
                summary['sentiment_score'] = sentiment.get('score', sentiment.get('overall_score'))
                summary['sentiment_label'] = sentiment.get('label', sentiment.get('sentiment'))
        
        # Regime data
        if 'regime_data' in pipeline_results:
            regime = pipeline_results['regime_data']
            if isinstance(regime, dict):
                summary['market_regime'] = regime.get('regime_label')
                summary['crash_risk'] = regime.get('crash_risk_score')
        
        return summary
    
    def _format_summary_message(
        self,
        market: str,
        summary: Dict
    ) -> str:
        """Format summary as Telegram message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        message = f"📊 *{market} Market Summary*\n"
        message += f"_{timestamp}_\n\n"
        
        if 'stocks_scanned' in summary:
            message += f"📈 Stocks Scanned: *{summary['stocks_scanned']}*\n"
        
        if 'top_opportunities' in summary:
            message += f"⭐ Top Opportunities: *{summary['top_opportunities']}*\n"
        
        if 'execution_time' in summary:
            message += f"⏱️ Scan Time: *{summary['execution_time']:.1f} min*\n"
        
        if 'sentiment_label' in summary:
            sentiment_emoji = {
                'bullish': '🟢',
                'bearish': '🔴',
                'neutral': '🟡'
            }.get(summary['sentiment_label'].lower(), '⚪')
            message += f"\n{sentiment_emoji} Sentiment: *{summary['sentiment_label']}*"
            if 'sentiment_score' in summary:
                message += f" ({summary['sentiment_score']:.1f})"
            message += "\n"
        
        if 'market_regime' in summary:
            message += f"📊 Regime: *{summary['market_regime']}*\n"
        
        if 'crash_risk' in summary:
            risk_emoji = '🔴' if summary['crash_risk'] > 70 else '🟡' if summary['crash_risk'] > 40 else '🟢'
            message += f"{risk_emoji} Crash Risk: *{summary['crash_risk']:.1f}%*\n"
        
        return message


def test_report_sender():
    """Test report sender functionality"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("\n" + "="*80)
    print("TESTING REPORT SENDER")
    print("="*80)
    
    # Check Telegram configuration
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        print("\n⚠️  Telegram not configured!")
        print("\nConfigure in .env first (see .env.example)")
        return
    
    sender = ReportSender()
    
    # Test summary notification
    print("\n--- Testing Summary Notification ---")
    test_summary = {
        'stocks_scanned': 240,
        'top_opportunities': 15,
        'execution_time': 47.3,
        'sentiment_label': 'Bullish',
        'sentiment_score': 68.5,
        'market_regime': 'Bull Market',
        'crash_risk': 12.3
    }
    
    if sender.send_summary_notification("US", test_summary):
        print("✓ Summary notification sent")
    else:
        print("✗ Failed to send summary")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("Check your Telegram for the test message!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_report_sender()

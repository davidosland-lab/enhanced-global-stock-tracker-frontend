"""
Intraday Scheduler for Day Trading

Automatically rescans markets every 15-30 minutes during trading hours.
Detects breakouts, momentum shifts, and generates real-time alerts.

Features:
- Auto-start at market open
- Rescan every N minutes (configurable)
- Auto-stop at market close
- Breakout detection
- Alert generation
- Session tracking

Usage:
    # Start monitoring ASX (15-min intervals)
    python intraday_scheduler.py --market ASX --interval 15
    
    # Schedule for daily market open
    python intraday_scheduler.py --market ASX --schedule
"""

import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys

# Add parent directories to path
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from models.screening.market_hours_detector import MarketHoursDetector
from models.scheduling.intraday_rescan_manager import IntradayRescanManager

logger = logging.getLogger(__name__)


class IntradayScheduler:
    """
    Manages automated intraday rescanning for active trading.
    
    Features:
    - Auto-start at market open
    - Rescan every N minutes (configurable)
    - Auto-stop at market close
    - Breakout detection
    - Alert generation
    """
    
    def __init__(self, market: str = 'ASX', rescan_interval: int = 15):
        """
        Initialize intraday scheduler.
        
        Args:
            market: 'ASX' or 'US'
            rescan_interval: Minutes between rescans (default: 15)
        """
        self.market = market
        self.rescan_interval = rescan_interval
        self.market_detector = MarketHoursDetector()
        self.rescan_manager = IntradayRescanManager(market=market)
        
        self.is_running = False
        self.scan_count = 0
        self.session_start = None
        self.last_scan_time = None
        
        logger.info(f"Intraday Scheduler initialized: {market} market")
        logger.info(f"Rescan interval: {rescan_interval} minutes")
    
    def start_intraday_monitoring(self):
        """
        Start continuous intraday monitoring.
        
        Runs rescans every N minutes during market hours.
        Auto-stops when market closes.
        """
        logger.info("="*80)
        logger.info("STARTING INTRADAY MONITORING SESSION")
        logger.info("="*80)
        
        # Check if market is open
        market_status = self.market_detector.is_market_open(market=self.market)
        
        if not market_status['is_open']:
            logger.warning("❌ Market is closed. Intraday monitoring not started.")
            logger.info(f"   Market phase: {market_status.get('market_phase', 'Unknown')}")
            logger.info(f"   Next open: {market_status.get('time_until_open', 'Unknown')}")
            return False
        
        # Market is open - start monitoring
        self.is_running = True
        self.session_start = datetime.now()
        self.scan_count = 0
        
        logger.info(f"✅ {self.market} Market is OPEN")
        logger.info(f"⏰ Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🔄 Rescan interval: {self.rescan_interval} minutes")
        logger.info(f"⏱️  Time until close: {market_status.get('time_until_close', 'Unknown')}")
        
        # Schedule the first scan immediately
        logger.info("\n🚀 Running initial scan...")
        self._run_scan()
        
        # Schedule periodic rescans
        schedule.every(self.rescan_interval).minutes.do(self._run_scan)
        
        # Main monitoring loop
        try:
            while self.is_running:
                # Check if market is still open
                market_status = self.market_detector.is_market_open(market=self.market)
                
                if not market_status['is_open']:
                    logger.info("\n🔔 Market has closed. Stopping intraday monitoring.")
                    self.stop_monitoring()
                    break
                
                # Run any scheduled scans
                schedule.run_pending()
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Monitoring interrupted by user.")
            self.stop_monitoring()
        except Exception as e:
            logger.error(f"\n❌ Monitoring error: {e}")
            logger.exception(e)
            self.stop_monitoring()
        
        return True
    
    def _run_scan(self):
        """Run a single intraday scan"""
        self.scan_count += 1
        scan_start = datetime.now()
        
        logger.info("\n" + "="*80)
        logger.info(f"INTRADAY SCAN #{self.scan_count}")
        logger.info(f"Timestamp: {scan_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Run the rescan
            results = self.rescan_manager.run_incremental_scan()
            
            scan_end = datetime.now()
            duration = (scan_end - scan_start).total_seconds()
            
            # Log results
            logger.info(f"\n✅ Scan #{self.scan_count} completed:")
            logger.info(f"   Stocks scanned: {results.get('stocks_scanned', 0)}")
            logger.info(f"   Changed stocks: {results.get('changed_stocks', 0)}")
            logger.info(f"   New opportunities: {results.get('new_opportunities', 0)}")
            logger.info(f"   Breakouts detected: {results.get('breakouts_detected', 0)}")
            logger.info(f"   Alerts sent: {results.get('alerts_sent', 0)}")
            logger.info(f"   Scan duration: {duration:.1f}s")
            
            # Log top opportunities
            if results.get('top_opportunities'):
                logger.info(f"\n   📈 Top Opportunities:")
                for i, opp in enumerate(results.get('top_opportunities', [])[:5], 1):
                    symbol = opp.get('symbol', 'N/A')
                    score = opp.get('opportunity_score', 0)
                    change = opp.get('price_change_pct', 0)
                    logger.info(f"      {i}. {symbol}: {score:.1f}/100 ({change:+.1f}%)")
            
            # Log breakouts
            if results.get('breakouts'):
                logger.info(f"\n   🚨 Breakouts Detected:")
                for breakout in results.get('breakouts', [])[:5]:
                    symbol = breakout.get('symbol', 'N/A')
                    btype = breakout.get('type', 'N/A')
                    strength = breakout.get('signal_strength', 0)
                    logger.info(f"      • {symbol}: {btype} ({strength:.0f}/100)")
            
            # Next scan time
            next_scan = scan_end + timedelta(minutes=self.rescan_interval)
            time_until_next = (next_scan - datetime.now()).total_seconds() / 60
            logger.info(f"\n   ⏭️  Next scan: {next_scan.strftime('%H:%M:%S')} ({time_until_next:.0f} min)")
            
            self.last_scan_time = scan_end
            
        except Exception as e:
            logger.error(f"❌ Scan #{self.scan_count} failed: {e}")
            logger.exception(e)
    
    def stop_monitoring(self):
        """Stop intraday monitoring"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        self.is_running = False
        schedule.clear()
        
        # Session summary
        if self.session_start:
            session_end = datetime.now()
            session_duration = session_end - self.session_start
            
            logger.info("\n" + "="*80)
            logger.info("INTRADAY MONITORING SESSION ENDED")
            logger.info("="*80)
            logger.info(f"Session start: {self.session_start.strftime('%H:%M:%S')}")
            logger.info(f"Session end: {session_end.strftime('%H:%M:%S')}")
            logger.info(f"Duration: {session_duration}")
            logger.info(f"Total scans: {self.scan_count}")
            
            if self.scan_count > 0:
                avg_interval = session_duration.total_seconds() / self.scan_count / 60
                logger.info(f"Average scan interval: {avg_interval:.1f} minutes")
        
        logger.info("✅ Monitoring stopped")
    
    def schedule_for_market_open(self):
        """
        Schedule monitoring to start at market open tomorrow.
        
        Uses Windows Task Scheduler for overnight scheduling.
        """
        try:
            from models.scheduling.overnight_scheduler import OvernightScheduler
        except ImportError:
            logger.error("OvernightScheduler not available")
            return False
        
        # Determine market open time
        if self.market == 'US':
            hour, minute = 9, 30  # 9:30 AM EST
        else:  # ASX
            hour, minute = 10, 0  # 10:00 AM AEST
        
        # Create batch file for intraday monitoring
        batch_path = BASE_PATH / f'RUN_INTRADAY_MONITOR_{self.market}.bat'
        
        batch_content = f"""@echo off
cd /d "%~dp0"
echo Starting {self.market} Intraday Monitoring...
python models\\scheduling\\intraday_scheduler.py --market {self.market} --interval {self.rescan_interval}
pause
"""
        
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        logger.info(f"Created batch file: {batch_path}")
        
        # Create scheduled task
        scheduler = OvernightScheduler(script_path=batch_path)
        scheduler.TASK_NAME = f"FinBERT_Intraday_Monitor_{self.market}"
        
        success = scheduler.create_daily_task(hour=hour, minute=minute)
        
        if success:
            logger.info(f"✅ Scheduled intraday monitoring for {hour:02d}:{minute:02d} daily")
            logger.info(f"   Task: {scheduler.TASK_NAME}")
            logger.info(f"   Script: {batch_path}")
        else:
            logger.error("❌ Failed to schedule intraday monitoring")
        
        return success


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intraday monitoring for day trading')
    parser.add_argument('--market', choices=['ASX', 'US'], default='ASX',
                       help='Market to monitor (default: ASX)')
    parser.add_argument('--interval', type=int, default=15,
                       help='Rescan interval in minutes (default: 15)')
    parser.add_argument('--schedule', action='store_true',
                       help='Schedule for daily market open (instead of running now)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BASE_PATH / 'logs' / 'intraday_monitoring.log')
        ]
    )
    
    print("\n" + "="*80)
    print(f"INTRADAY MONITORING - {args.market} MARKET")
    print("="*80)
    
    scheduler = IntradayScheduler(
        market=args.market,
        rescan_interval=args.interval
    )
    
    if args.schedule:
        # Schedule for tomorrow
        print(f"\nScheduling {args.market} monitoring for market open...")
        success = scheduler.schedule_for_market_open()
        if success:
            print(f"\n✅ Successfully scheduled!")
            print(f"   Monitoring will start automatically at market open")
            print(f"   Rescan interval: {args.interval} minutes")
        else:
            print(f"\n❌ Failed to schedule monitoring")
        return 0 if success else 1
    else:
        # Start monitoring now
        print(f"\nStarting {args.market} intraday monitoring...")
        print(f"Rescan interval: {args.interval} minutes")
        print(f"\nPress Ctrl+C to stop monitoring\n")
        
        success = scheduler.start_intraday_monitoring()
        return 0 if success else 1


if __name__ == '__main__':
    exit(main())

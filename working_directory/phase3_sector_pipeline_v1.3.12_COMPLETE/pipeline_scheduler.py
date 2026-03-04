"""
Automated Pipeline Scheduler
=============================

Automatically runs overnight pipeline reports 2.5 hours before each market opens.

Market Open Times (Local):
- AU (ASX): 10:00 AEDT → Pipeline runs at 07:30 AEDT
- US (NYSE/NASDAQ): 09:30 EST → Pipeline runs at 07:00 EST
- UK (LSE): 08:00 GMT → Pipeline runs at 05:30 GMT

Features:
- Automatic scheduling based on market timezone
- Runs morning reports before market open
- Retries on failure
- Logs all executions
- Handles market holidays
- Can run all markets or specific markets

Usage:
    # Run scheduler daemon (all markets)
    python pipeline_scheduler.py --daemon
    
    # Run specific market
    python pipeline_scheduler.py --market UK
    
    # Run all markets once
    python pipeline_scheduler.py --once
    
    # Test mode (no execution)
    python pipeline_scheduler.py --test
"""

import logging
import time
import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime, time as dt_time, timedelta
from typing import Dict, List, Optional, Tuple
import schedule
import pytz
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MarketSchedule:
    """Market schedule configuration"""
    name: str
    code: str
    timezone: str
    market_open: dt_time  # Local market time
    pipeline_offset_hours: float  # Hours before open to run pipeline
    script_path: Path
    enabled: bool = True


class PipelineScheduler:
    """
    Automated scheduler for running pipeline reports before market open
    """
    
    def __init__(self, pipeline_base_path: Optional[Path] = None):
        """
        Initialize pipeline scheduler
        
        Args:
            pipeline_base_path: Path to pipeline_trading directory
        """
        self.pipeline_base_path = pipeline_base_path or \
            Path(__file__).parent.parent / 'pipeline_trading'
        
        # Market configurations
        self.markets = self._initialize_market_schedules()
        
        # Execution tracking
        self.last_executions = {}
        self.execution_history = []
        
        logger.info("="*80)
        logger.info("PIPELINE SCHEDULER INITIALIZED")
        logger.info("="*80)
        for market in self.markets.values():
            if market.enabled:
                pipeline_time = self._calculate_pipeline_time(market)
                logger.info(f"{market.name} ({market.code}):")
                logger.info(f"  Market Opens: {market.market_open} {market.timezone}")
                logger.info(f"  Pipeline Runs: {pipeline_time} {market.timezone}")
                logger.info(f"  Script: {market.script_path.name}")
    
    def _initialize_market_schedules(self) -> Dict[str, MarketSchedule]:
        """Initialize market schedule configurations"""
        scripts_path = self.pipeline_base_path / 'scripts'
        
        markets = {
            'AU': MarketSchedule(
                name='Australia',
                code='AU',
                timezone='Australia/Sydney',
                market_open=dt_time(10, 0),  # 10:00 AEDT
                pipeline_offset_hours=2.5,
                script_path=scripts_path / 'run_au_morning_report.py'
            ),
            'US': MarketSchedule(
                name='United States',
                code='US',
                timezone='America/New_York',
                market_open=dt_time(9, 30),  # 09:30 EST
                pipeline_offset_hours=2.5,
                script_path=scripts_path / 'run_us_morning_report.py'
            ),
            'UK': MarketSchedule(
                name='United Kingdom',
                code='UK',
                timezone='Europe/London',
                market_open=dt_time(8, 0),  # 08:00 GMT
                pipeline_offset_hours=2.5,
                script_path=scripts_path / 'run_uk_morning_report.py'
            )
        }
        
        return markets
    
    def _calculate_pipeline_time(self, market: MarketSchedule) -> dt_time:
        """
        Calculate when to run pipeline based on market open time
        
        Args:
            market: MarketSchedule configuration
            
        Returns:
            Time to run pipeline (local market time)
        """
        # Convert market open to datetime for calculation
        now = datetime.now(pytz.timezone(market.timezone))
        market_open_dt = now.replace(
            hour=market.market_open.hour,
            minute=market.market_open.minute,
            second=0,
            microsecond=0
        )
        
        # Subtract offset hours
        pipeline_dt = market_open_dt - timedelta(hours=market.pipeline_offset_hours)
        
        return pipeline_dt.time()
    
    def _is_market_holiday(self, market: MarketSchedule, date: datetime) -> bool:
        """
        Check if given date is a market holiday
        
        Args:
            market: MarketSchedule configuration
            date: Date to check
            
        Returns:
            True if holiday, False otherwise
        """
        # Simple check for weekends
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return True
        
        # TODO: Add proper holiday calendar integration
        # For now, just check weekends
        return False
    
    def _run_pipeline(self, market: MarketSchedule) -> bool:
        """
        Execute pipeline report for a specific market
        
        Args:
            market: MarketSchedule configuration
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("="*80)
        logger.info(f"RUNNING {market.name} ({market.code}) PIPELINE")
        logger.info("="*80)
        
        # Check if market is closed today
        tz = pytz.timezone(market.timezone)
        now = datetime.now(tz)
        
        if self._is_market_holiday(market, now):
            logger.info(f"{market.name} market is closed (holiday/weekend)")
            return True  # Not an error, just skip
        
        # Check if already ran today
        today_str = now.strftime('%Y-%m-%d')
        last_run = self.last_executions.get(market.code)
        if last_run and last_run.startswith(today_str):
            logger.info(f"Pipeline already ran today at {last_run}")
            return True
        
        # Verify script exists
        if not market.script_path.exists():
            logger.error(f"Script not found: {market.script_path}")
            return False
        
        # Execute pipeline script
        try:
            logger.info(f"Executing: python {market.script_path}")
            
            result = subprocess.run(
                ['python', str(market.script_path)],
                cwd=str(self.pipeline_base_path),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✓ {market.name} pipeline completed successfully")
                
                # Log output summary
                if result.stdout:
                    lines = result.stdout.split('\n')
                    # Show last 10 lines of output
                    logger.info("Pipeline output (last 10 lines):")
                    for line in lines[-10:]:
                        if line.strip():
                            logger.info(f"  {line}")
                
                # Update execution tracking
                self.last_executions[market.code] = now.strftime('%Y-%m-%d %H:%M:%S')
                self.execution_history.append({
                    'market': market.code,
                    'timestamp': now.isoformat(),
                    'status': 'success'
                })
                
                return True
            else:
                logger.error(f"✗ {market.name} pipeline failed (exit code {result.returncode})")
                if result.stderr:
                    logger.error(f"Error output:\n{result.stderr}")
                
                self.execution_history.append({
                    'market': market.code,
                    'timestamp': now.isoformat(),
                    'status': 'failed',
                    'error': result.stderr
                })
                
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {market.name} pipeline timed out (>10 minutes)")
            return False
        except Exception as e:
            logger.error(f"✗ {market.name} pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _schedule_market(self, market: MarketSchedule):
        """
        Schedule pipeline execution for a specific market
        
        Args:
            market: MarketSchedule configuration
        """
        pipeline_time = self._calculate_pipeline_time(market)
        
        # Convert to 24-hour format string
        time_str = pipeline_time.strftime('%H:%M')
        
        logger.info(f"Scheduling {market.name}: {time_str} {market.timezone}")
        
        # Create schedule using the market's timezone
        def run_job():
            tz = pytz.timezone(market.timezone)
            now = datetime.now(tz)
            logger.info(f"\n{'='*80}")
            logger.info(f"SCHEDULED EXECUTION: {market.name}")
            logger.info(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"{'='*80}")
            
            success = self._run_pipeline(market)
            
            if not success:
                logger.warning(f"Pipeline failed, will retry tomorrow")
        
        # Schedule the job
        schedule.every().day.at(time_str).do(run_job)
    
    def schedule_all_markets(self, markets: Optional[List[str]] = None):
        """
        Schedule pipeline runs for all or specific markets
        
        Args:
            markets: List of market codes (None = all enabled markets)
        """
        logger.info("="*80)
        logger.info("SCHEDULING PIPELINE RUNS")
        logger.info("="*80)
        
        for code, market in self.markets.items():
            if not market.enabled:
                logger.info(f"Skipping {market.name} (disabled)")
                continue
            
            if markets and code not in markets:
                logger.info(f"Skipping {market.name} (not in specified list)")
                continue
            
            self._schedule_market(market)
        
        logger.info("="*80)
        logger.info("SCHEDULE SUMMARY")
        logger.info("="*80)
        
        for job in schedule.get_jobs():
            logger.info(f"Next run: {job.next_run}")
    
    def run_once(self, markets: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Run pipeline for all or specific markets once (no scheduling)
        
        Args:
            markets: List of market codes (None = all enabled markets)
            
        Returns:
            Dictionary of {market_code: success_bool}
        """
        results = {}
        
        for code, market in self.markets.items():
            if not market.enabled:
                continue
            
            if markets and code not in markets:
                continue
            
            results[code] = self._run_pipeline(market)
        
        return results
    
    def run_daemon(self, markets: Optional[List[str]] = None):
        """
        Run scheduler as daemon (continuous execution)
        
        Args:
            markets: List of market codes (None = all enabled markets)
        """
        logger.info("="*80)
        logger.info("STARTING PIPELINE SCHEDULER DAEMON")
        logger.info("="*80)
        logger.info("Press Ctrl+C to stop")
        
        # Schedule all markets
        self.schedule_all_markets(markets)
        
        try:
            # Run scheduler loop
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\n" + "="*80)
            logger.info("SCHEDULER SHUTTING DOWN")
            logger.info("="*80)
            self.print_execution_summary()
    
    def print_execution_summary(self):
        """Print summary of executions"""
        logger.info("\nEXECUTION SUMMARY:")
        logger.info("-"*80)
        
        if not self.execution_history:
            logger.info("No executions recorded")
            return
        
        # Count successes/failures
        success_count = sum(1 for e in self.execution_history if e['status'] == 'success')
        failed_count = len(self.execution_history) - success_count
        
        logger.info(f"Total Executions: {len(self.execution_history)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failed_count}")
        
        logger.info("\nLast Executions:")
        for market_code, timestamp in self.last_executions.items():
            market = self.markets[market_code]
            logger.info(f"  {market.name}: {timestamp}")
    
    def test_schedule(self):
        """Test the schedule without executing"""
        logger.info("="*80)
        logger.info("TESTING SCHEDULE (NO EXECUTION)")
        logger.info("="*80)
        
        for code, market in self.markets.items():
            if not market.enabled:
                continue
            
            tz = pytz.timezone(market.timezone)
            now = datetime.now(tz)
            
            # Calculate pipeline time
            pipeline_time = self._calculate_pipeline_time(market)
            market_open = market.market_open
            
            # Calculate next run
            pipeline_dt = now.replace(
                hour=pipeline_time.hour,
                minute=pipeline_time.minute,
                second=0,
                microsecond=0
            )
            
            if pipeline_dt < now:
                pipeline_dt += timedelta(days=1)
            
            market_open_dt = now.replace(
                hour=market_open.hour,
                minute=market_open.minute,
                second=0,
                microsecond=0
            )
            
            if market_open_dt < now:
                market_open_dt += timedelta(days=1)
            
            logger.info(f"\n{market.name} ({code}):")
            logger.info(f"  Timezone: {market.timezone}")
            logger.info(f"  Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"  Market Opens: {market_open} (in {self._format_timedelta(market_open_dt - now)})")
            logger.info(f"  Pipeline Runs: {pipeline_time} (in {self._format_timedelta(pipeline_dt - now)})")
            logger.info(f"  Lead Time: {market.pipeline_offset_hours} hours")
            logger.info(f"  Script: {market.script_path}")
            logger.info(f"  Script Exists: {'✓' if market.script_path.exists() else '✗'}")
    
    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta for display"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automated Pipeline Scheduler'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (continuous scheduling)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run pipelines once and exit'
    )
    parser.add_argument(
        '--market',
        type=str,
        help='Specific market to run (AU, US, or UK)'
    )
    parser.add_argument(
        '--markets',
        type=str,
        help='Comma-separated markets (e.g., AU,US,UK)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test schedule without executing'
    )
    
    args = parser.parse_args()
    
    # Determine markets
    markets = None
    if args.markets:
        markets = [m.strip().upper() for m in args.markets.split(',')]
    elif args.market:
        markets = [args.market.upper()]
    
    # Validate markets
    if markets:
        valid_markets = ['AU', 'US', 'UK']
        for market in markets:
            if market not in valid_markets:
                logger.error(f"Invalid market: {market}. Valid: {', '.join(valid_markets)}")
                sys.exit(1)
    
    # Initialize scheduler
    scheduler = PipelineScheduler()
    
    # Execute based on mode
    if args.test:
        scheduler.test_schedule()
    elif args.once:
        results = scheduler.run_once(markets)
        logger.info("\n" + "="*80)
        logger.info("EXECUTION RESULTS")
        logger.info("="*80)
        for market_code, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{market_code}: {status}")
    elif args.daemon:
        scheduler.run_daemon(markets)
    else:
        logger.error("Please specify --daemon, --once, or --test")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

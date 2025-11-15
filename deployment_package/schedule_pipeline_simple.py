#!/usr/bin/env python3
"""
Simple Overnight Pipeline Scheduler
Simplified version with better error handling

Usage:
    python schedule_pipeline_simple.py          # Run scheduler
    python schedule_pipeline_simple.py --test   # Test run immediately
"""

import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging first
log_dir = Path(__file__).parent / 'logs' / 'scheduler'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the overnight pipeline"""
    logger.info("="*80)
    logger.info("PIPELINE EXECUTION STARTING")
    logger.info("="*80)
    
    try:
        # Add models/screening to path
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir / 'models' / 'screening'))
        
        # Import and run pipeline
        from overnight_pipeline import OvernightPipeline
        
        pipeline = OvernightPipeline()
        logger.info("Pipeline initialized")
        
        # Run full pipeline
        results = pipeline.run_full_pipeline(sectors=None, stocks_per_sector=30)
        
        logger.info("="*80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Status: {results.get('status', 'Unknown')}")
        logger.info(f"Stocks Scanned: {results.get('statistics', {}).get('total_stocks_scanned', 'N/A')}")
        logger.info(f"Report: {results.get('report_path', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error("="*80)
        logger.error("PIPELINE FAILED")
        logger.error("="*80)
        logger.error(f"Error: {str(e)}")
        
        # Try to send error email
        try:
            sys.path.insert(0, str(Path(__file__).parent / 'models' / 'screening'))
            from send_notification import EmailNotifier
            
            notifier = EmailNotifier()
            if notifier.enabled:
                notifier.send_error(str(e), "", "pipeline_execution")
                logger.info("Error notification sent")
        except:
            logger.warning("Could not send error notification")
        
        return False


def main():
    """Main scheduler"""
    # Check for test mode
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        logger.info("TEST MODE - Running immediately")
        success = run_pipeline()
        return 0 if success else 1
    
    # Import schedule library
    try:
        import schedule
        import pytz
    except ImportError:
        logger.error("Required packages not installed!")
        logger.error("Please run: pip install schedule pytz")
        return 1
    
    # Setup timezone and schedule
    TIMEZONE = pytz.timezone('Australia/Sydney')
    SCHEDULE_TIME = "05:00"
    
    logger.info("="*80)
    logger.info("SCHEDULER STARTED")
    logger.info("="*80)
    logger.info(f"Schedule: Daily at {SCHEDULE_TIME} {TIMEZONE}")
    logger.info(f"Current Time: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*80)
    
    # Schedule the job
    def job():
        logger.info(f"Scheduled job triggered at {datetime.now(TIMEZONE).strftime('%H:%M:%S')}")
        success = run_pipeline()
        if success:
            logger.info("✅ Pipeline completed successfully")
        else:
            logger.error("❌ Pipeline failed")
        
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    schedule.every().day.at(SCHEDULE_TIME).do(job)
    
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Overnight Pipeline Scheduler
Schedules the overnight pipeline to run at 5:00 AM Australian Eastern Standard Time (AEST/AEDT)

This script handles:
- Automatic timezone adjustment (AEST/AEDT)
- Daily scheduling at 5:00 AM
- Logging of execution
- Error handling and recovery
- Runs the pipeline once per day

Usage:
    # Run scheduler (keeps running and executes pipeline daily at 5:00 AM)
    python3 schedule_pipeline.py

    # Test mode (runs immediately once)
    python3 schedule_pipeline.py --test

    # Setup as systemd service (recommended for production)
    See SCHEDULER_SETUP.md for instructions
"""

import sys
import os
from pathlib import Path
import time
import schedule
import logging
from datetime import datetime
import pytz
import argparse
import traceback

# Add project to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / 'models' / 'screening'))

# Setup logging
log_dir = script_dir / 'logs' / 'scheduler'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Australian Eastern Time (handles both AEST and AEDT automatically)
TIMEZONE = pytz.timezone('Australia/Sydney')
SCHEDULE_TIME = "05:00"  # 5:00 AM


def run_pipeline():
    """
    Execute the overnight pipeline
    
    Returns:
        bool: True if pipeline completed successfully
    """
    logger.info("="*80)
    logger.info("SCHEDULED PIPELINE EXECUTION STARTING")
    logger.info("="*80)
    
    current_time = datetime.now(TIMEZONE)
    logger.info(f"Execution Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Timezone: {TIMEZONE}")
    
    try:
        # Import pipeline components
        from overnight_pipeline import OvernightPipeline
        
        # Initialize and run pipeline
        pipeline = OvernightPipeline()
        logger.info("Pipeline initialized successfully")
        
        # Run full pipeline (all sectors, 30 stocks per sector)
        results = pipeline.run_full_pipeline(
            sectors=None,  # All sectors
            stocks_per_sector=30
        )
        
        # Log results
        logger.info("="*80)
        logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Execution Time: {results['execution_time_minutes']} minutes")
        logger.info(f"Stocks Scanned: {results['statistics']['total_stocks_scanned']}")
        logger.info(f"Opportunities Found: {results['statistics']['top_opportunities_count']}")
        logger.info(f"Report Path: {results['report_path']}")
        
        # Check for email notifications
        if results.get('summary'):
            logger.info(f"Email Summary: {results['summary']}")
        
        return True
        
    except Exception as e:
        logger.error("="*80)
        logger.error("PIPELINE EXECUTION FAILED")
        logger.error("="*80)
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        
        # Try to send error notification
        try:
            from send_notification import EmailNotifier
            notifier = EmailNotifier()
            if notifier.enabled:
                notifier.send_error(
                    error_message=str(e),
                    error_traceback=traceback.format_exc(),
                    phase='scheduled_execution'
                )
                logger.info("Error notification email sent")
        except Exception as email_error:
            logger.warning(f"Failed to send error notification: {email_error}")
        
        return False


def job():
    """Wrapper function for schedule execution"""
    logger.info(f"Scheduled job triggered at {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    success = run_pipeline()
    
    if success:
        logger.info("✅ Scheduled pipeline execution completed successfully")
    else:
        logger.error("❌ Scheduled pipeline execution failed")
    
    # Calculate next run time
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main scheduler loop"""
    parser = argparse.ArgumentParser(description='Overnight Pipeline Scheduler')
    parser.add_argument('--test', action='store_true', help='Run pipeline immediately (test mode)')
    parser.add_argument('--time', type=str, default=SCHEDULE_TIME, 
                       help=f'Schedule time in HH:MM format (default: {SCHEDULE_TIME})')
    
    args = parser.parse_args()
    
    # Test mode: run immediately and exit
    if args.test:
        logger.info("="*80)
        logger.info("RUNNING IN TEST MODE (Immediate Execution)")
        logger.info("="*80)
        success = run_pipeline()
        return 0 if success else 1
    
    # Scheduler mode: run at specified time daily
    schedule_time = args.time
    
    logger.info("="*80)
    logger.info("OVERNIGHT PIPELINE SCHEDULER STARTED")
    logger.info("="*80)
    logger.info(f"Schedule Time: {schedule_time} {TIMEZONE}")
    logger.info(f"Current Time: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info(f"Log File: {log_dir / 'scheduler.log'}")
    logger.info("")
    logger.info("Scheduler is running... Press Ctrl+C to stop")
    logger.info("="*80)
    
    # Schedule the job
    schedule.every().day.at(schedule_time).do(job)
    
    # Display next run time
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("\n" + "="*80)
        logger.info("SCHEDULER STOPPED BY USER")
        logger.info("="*80)
        return 0
    
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

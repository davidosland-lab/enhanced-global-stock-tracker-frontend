"""
Prediction Scheduler
Handles scheduled validation of predictions at market close for multiple timezones
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


class PredictionScheduler:
    """Schedules prediction validation jobs for multiple market timezones"""
    
    def __init__(self, prediction_manager):
        """
        Initialize prediction scheduler
        
        Args:
            prediction_manager: PredictionManager instance
        """
        self.prediction_manager = prediction_manager
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
        logger.info("PredictionScheduler initialized")
    
    def start(self):
        """Start the scheduler with all validation jobs"""
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return
        
        # Schedule validation for each market at their close time
        self._schedule_us_validation()
        self._schedule_au_validation()
        self._schedule_uk_validation()
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("✓ Prediction scheduler started with jobs for US/AU/UK markets")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.scheduler.running:
            return
        
        self.scheduler.shutdown()
        logger.info("Prediction scheduler stopped")
    
    def _schedule_us_validation(self):
        """
        Schedule validation for US markets
        Runs at 4:15 PM EST (15 min after market close at 4:00 PM)
        """
        job = self.scheduler.add_job(
            func=self._validate_us_predictions,
            trigger=CronTrigger(
                hour=16,
                minute=15,
                timezone=pytz.timezone('US/Eastern'),
                day_of_week='mon-fri'
            ),
            id='us_validation',
            name='US Market Validation',
            replace_existing=True
        )
        
        self.jobs['US'] = job
        logger.info("✓ Scheduled US market validation: Daily at 16:15 EST (Mon-Fri)")
    
    def _schedule_au_validation(self):
        """
        Schedule validation for Australian markets
        Runs at 4:15 PM AEDT (15 min after market close at 4:00 PM)
        """
        job = self.scheduler.add_job(
            func=self._validate_au_predictions,
            trigger=CronTrigger(
                hour=16,
                minute=15,
                timezone=pytz.timezone('Australia/Sydney'),
                day_of_week='mon-fri'
            ),
            id='au_validation',
            name='AU Market Validation',
            replace_existing=True
        )
        
        self.jobs['AU'] = job
        logger.info("✓ Scheduled AU market validation: Daily at 16:15 AEDT (Mon-Fri)")
    
    def _schedule_uk_validation(self):
        """
        Schedule validation for UK markets
        Runs at 4:45 PM GMT (15 min after market close at 4:30 PM)
        """
        job = self.scheduler.add_job(
            func=self._validate_uk_predictions,
            trigger=CronTrigger(
                hour=16,
                minute=45,
                timezone=pytz.timezone('Europe/London'),
                day_of_week='mon-fri'
            ),
            id='uk_validation',
            name='UK Market Validation',
            replace_existing=True
        )
        
        self.jobs['UK'] = job
        logger.info("✓ Scheduled UK market validation: Daily at 16:45 GMT (Mon-Fri)")
    
    def _validate_us_predictions(self):
        """Validate US market predictions"""
        logger.info("=" * 80)
        logger.info("🇺🇸 Running US Market Validation (Scheduled)")
        logger.info("=" * 80)
        
        try:
            # Get active predictions for US symbols (no suffix or .US)
            active_preds = self.prediction_manager.prediction_db.get_active_predictions()
            us_preds = [p for p in active_preds if not p['symbol'].endswith('.AX') and not p['symbol'].endswith('.L')]
            
            logger.info(f"Found {len(us_preds)} active US predictions to validate")
            
            if us_preds:
                # Run validation
                result = self.prediction_manager.validate_predictions()
                logger.info(f"✓ Validated {result.get('validated_count', 0)} US predictions")
                logger.info(f"  Symbols updated: {', '.join(result.get('symbols_updated', []))}")
                
                if result.get('errors'):
                    logger.warning(f"  Errors: {len(result['errors'])}")
                    for error in result['errors'][:5]:  # Log first 5 errors
                        logger.warning(f"    - {error}")
            else:
                logger.info("No US predictions to validate")
                
        except Exception as e:
            logger.error(f"✗ Error in US validation: {e}", exc_info=True)
    
    def _validate_au_predictions(self):
        """Validate Australian market predictions"""
        logger.info("=" * 80)
        logger.info("🇦🇺 Running Australian Market Validation (Scheduled)")
        logger.info("=" * 80)
        
        try:
            # Get active predictions for AU symbols (.AX suffix)
            active_preds = self.prediction_manager.prediction_db.get_active_predictions()
            au_preds = [p for p in active_preds if p['symbol'].endswith('.AX')]
            
            logger.info(f"Found {len(au_preds)} active Australian predictions to validate")
            
            if au_preds:
                # Run validation (will validate all active, but AU preds are ready now)
                result = self.prediction_manager.validate_predictions()
                au_validated = [s for s in result.get('symbols_updated', []) if s.endswith('.AX')]
                logger.info(f"✓ Validated {len(au_validated)} Australian predictions")
                logger.info(f"  Symbols updated: {', '.join(au_validated)}")
                
                if result.get('errors'):
                    logger.warning(f"  Errors: {len(result['errors'])}")
                    for error in result['errors'][:5]:
                        logger.warning(f"    - {error}")
            else:
                logger.info("No Australian predictions to validate")
                
        except Exception as e:
            logger.error(f"✗ Error in AU validation: {e}", exc_info=True)
    
    def _validate_uk_predictions(self):
        """Validate UK market predictions"""
        logger.info("=" * 80)
        logger.info("🇬🇧 Running UK Market Validation (Scheduled)")
        logger.info("=" * 80)
        
        try:
            # Get active predictions for UK symbols (.L suffix)
            active_preds = self.prediction_manager.prediction_db.get_active_predictions()
            uk_preds = [p for p in active_preds if p['symbol'].endswith('.L')]
            
            logger.info(f"Found {len(uk_preds)} active UK predictions to validate")
            
            if uk_preds:
                # Run validation
                result = self.prediction_manager.validate_predictions()
                uk_validated = [s for s in result.get('symbols_updated', []) if s.endswith('.L')]
                logger.info(f"✓ Validated {len(uk_validated)} UK predictions")
                logger.info(f"  Symbols updated: {', '.join(uk_validated)}")
                
                if result.get('errors'):
                    logger.warning(f"  Errors: {len(result['errors'])}")
                    for error in result['errors'][:5]:
                        logger.warning(f"    - {error}")
            else:
                logger.info("No UK predictions to validate")
                
        except Exception as e:
            logger.error(f"✗ Error in UK validation: {e}", exc_info=True)
    
    def get_next_run_times(self):
        """Get next run times for all scheduled jobs"""
        next_runs = {}
        for market_code, job in self.jobs.items():
            if job:
                next_run = job.next_run_time
                next_runs[market_code] = next_run.isoformat() if next_run else None
        return next_runs
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'running': self.scheduler.running,
            'jobs_count': len(self.scheduler.get_jobs()),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }


# Module-level singleton
_prediction_scheduler = None

def get_prediction_scheduler(prediction_manager):
    """Get or create singleton prediction scheduler instance"""
    global _prediction_scheduler
    if _prediction_scheduler is None:
        _prediction_scheduler = PredictionScheduler(prediction_manager)
    return _prediction_scheduler

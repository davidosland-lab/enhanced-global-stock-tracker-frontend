"""
Progress Tracker Module

Real-time progress tracking and persistence for the overnight screening pipeline.
Tracks execution stages, completion percentages, errors, and timing information.

Features:
- JSON-based state persistence
- Stage-by-stage progress tracking
- Error and warning collection
- Time estimation and ETA calculation
- Status export for web dashboard integration
- Historical progress archival

Usage:
    tracker = ScreenerProgress()
    tracker.start()
    tracker.update_stage('data_collection', 50, 'running', 'Fetched 120/240 stocks')
    tracker.update_stage('data_collection', 100, 'complete')
    tracker.mark_failed('API timeout error')
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pytz

logger = logging.getLogger(__name__)


class ScreenerProgress:
    """
    Real-time progress tracking for overnight screening pipeline.
    Persists state to JSON file for monitoring by external tools.
    """
    
    def __init__(self, output_path: Optional[Path] = None):
        """
        Initialize progress tracker.
        
        Args:
            output_path: Path to save progress JSON. Defaults to reports/screener_progress.json
        """
        if output_path is None:
            # Default to reports directory
            base_path = Path(__file__).parent.parent.parent
            output_path = base_path / 'reports' / 'screener_progress.json'
        
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.timezone = pytz.timezone('Australia/Sydney')
        self.start_time = None
        self.end_time = None
        
        # Pipeline stages with expected duration (minutes)
        self.stages = {
            'initialization': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 2,
                'start_time': None,
                'end_time': None
            },
            'spi_monitoring': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 5,
                'start_time': None,
                'end_time': None
            },
            'stock_scanning': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 30,
                'start_time': None,
                'end_time': None
            },
            'lstm_training': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 180,  # 3 hours
                'start_time': None,
                'end_time': None
            },
            'batch_prediction': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 120,  # 2 hours
                'start_time': None,
                'end_time': None
            },
            'opportunity_scoring': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 30,
                'start_time': None,
                'end_time': None
            },
            'report_generation': {
                'status': 'pending',
                'progress': 0,
                'message': '',
                'expected_duration': 15,
                'start_time': None,
                'end_time': None
            }
        }
        
        self.errors = []
        self.warnings = []
        self.metrics = {
            'stocks_scanned': 0,
            'models_trained': 0,
            'predictions_generated': 0,
            'opportunities_found': 0
        }
        
    def start(self):
        """Mark the pipeline as started"""
        self.start_time = datetime.now(self.timezone)
        logger.info(f"Progress tracker started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.save_to_file()
        
    def update_stage(self, stage_name: str, progress: int, status: str = 'running', message: str = ''):
        """
        Update a specific pipeline stage.
        
        Args:
            stage_name: Name of the stage (must match keys in self.stages)
            progress: Progress percentage (0-100)
            status: Status string ('pending', 'running', 'complete', 'failed')
            message: Optional status message
        """
        if stage_name not in self.stages:
            logger.warning(f"Unknown stage: {stage_name}")
            return
        
        stage = self.stages[stage_name]
        old_status = stage['status']
        
        # Track when stage starts
        if old_status == 'pending' and status == 'running':
            stage['start_time'] = datetime.now(self.timezone).isoformat()
        
        # Track when stage completes
        if status == 'complete':
            stage['end_time'] = datetime.now(self.timezone).isoformat()
            progress = 100
        
        stage['status'] = status
        stage['progress'] = min(max(progress, 0), 100)  # Clamp 0-100
        stage['message'] = message
        
        logger.info(f"Stage '{stage_name}': {progress}% - {status} - {message}")
        self.save_to_file()
        
    def add_error(self, error_msg: str):
        """Add an error message to the log"""
        error_entry = {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'message': error_msg
        }
        self.errors.append(error_entry)
        logger.error(f"Error logged: {error_msg}")
        self.save_to_file()
        
    def add_warning(self, warning_msg: str):
        """Add a warning message to the log"""
        warning_entry = {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'message': warning_msg
        }
        self.warnings.append(warning_entry)
        logger.warning(f"Warning logged: {warning_msg}")
        self.save_to_file()
        
    def update_metrics(self, **kwargs):
        """
        Update pipeline metrics.
        
        Args:
            **kwargs: Metric key-value pairs to update
        """
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value
        self.save_to_file()
        
    def mark_failed(self, error_msg: str):
        """Mark the entire pipeline as failed"""
        self.add_error(error_msg)
        self.end_time = datetime.now(self.timezone)
        
        # Mark current running stage as failed
        for stage_name, stage in self.stages.items():
            if stage['status'] == 'running':
                stage['status'] = 'failed'
                stage['end_time'] = datetime.now(self.timezone).isoformat()
        
        logger.error(f"Pipeline marked as FAILED: {error_msg}")
        self.save_to_file()
        
    def mark_complete(self):
        """Mark the entire pipeline as successfully completed"""
        self.end_time = datetime.now(self.timezone)
        logger.info("Pipeline marked as COMPLETE")
        self.save_to_file()
        
    def calculate_overall_progress(self) -> float:
        """
        Calculate overall pipeline progress as weighted average.
        
        Returns:
            Overall progress percentage (0-100)
        """
        total_weight = sum(s['expected_duration'] for s in self.stages.values())
        weighted_progress = sum(
            (s['progress'] / 100) * s['expected_duration'] 
            for s in self.stages.values()
        )
        
        return round((weighted_progress / total_weight) * 100, 2)
        
    def estimate_remaining_time(self) -> Optional[timedelta]:
        """
        Estimate time remaining until pipeline completion.
        
        Returns:
            Estimated time remaining as timedelta, or None if cannot estimate
        """
        if not self.start_time:
            return None
        
        overall_progress = self.calculate_overall_progress()
        if overall_progress == 0:
            return None
        
        elapsed = datetime.now(self.timezone) - self.start_time
        total_estimated = elapsed / (overall_progress / 100)
        remaining = total_estimated - elapsed
        
        return remaining if remaining > timedelta(0) else timedelta(0)
        
    def get_status_summary(self) -> Dict:
        """
        Get comprehensive status summary.
        
        Returns:
            Dictionary with complete pipeline status
        """
        now = datetime.now(self.timezone)
        
        # Calculate execution time
        if self.start_time:
            if self.end_time:
                execution_time = (self.end_time - self.start_time).total_seconds()
            else:
                execution_time = (now - self.start_time).total_seconds()
        else:
            execution_time = 0
        
        # Determine overall status
        if any(s['status'] == 'failed' for s in self.stages.values()):
            overall_status = 'failed'
        elif all(s['status'] == 'complete' for s in self.stages.values()):
            overall_status = 'complete'
        elif any(s['status'] == 'running' for s in self.stages.values()):
            overall_status = 'running'
        else:
            overall_status = 'pending'
        
        summary = {
            'overall_status': overall_status,
            'overall_progress': self.calculate_overall_progress(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'current_time': now.isoformat(),
            'execution_time_seconds': execution_time,
            'execution_time_formatted': str(timedelta(seconds=int(execution_time))),
            'stages': self.stages,
            'metrics': self.metrics,
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        # Add ETA if running
        if overall_status == 'running':
            eta = self.estimate_remaining_time()
            if eta:
                eta_time = now + eta
                summary['estimated_remaining_seconds'] = eta.total_seconds()
                summary['estimated_remaining_formatted'] = str(timedelta(seconds=int(eta.total_seconds())))
                summary['estimated_completion_time'] = eta_time.isoformat()
        
        return summary
        
    def save_to_file(self):
        """Persist current state to JSON file"""
        try:
            summary = self.get_status_summary()
            
            with open(self.output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.debug(f"Progress saved to {self.output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save progress to file: {e}")
            
    def archive_to_history(self):
        """Archive completed progress to historical log"""
        if not self.end_time:
            logger.warning("Cannot archive incomplete progress")
            return
        
        try:
            # Create archive directory
            archive_dir = self.output_path.parent / 'history'
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Archive filename with timestamp
            archive_name = f"screener_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = archive_dir / archive_name
            
            # Save full summary
            summary = self.get_status_summary()
            with open(archive_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Progress archived to {archive_path}")
            
        except Exception as e:
            logger.error(f"Failed to archive progress: {e}")


def load_progress(progress_file: Optional[Path] = None) -> Optional[Dict]:
    """
    Load progress from JSON file.
    
    Args:
        progress_file: Path to progress JSON file
        
    Returns:
        Progress dictionary or None if file doesn't exist
    """
    if progress_file is None:
        base_path = Path(__file__).parent.parent.parent
        progress_file = base_path / 'reports' / 'screener_progress.json'
    
    progress_file = Path(progress_file)
    
    if not progress_file.exists():
        return None
    
    try:
        with open(progress_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load progress file: {e}")
        return None


# Example usage and testing
if __name__ == '__main__':
    # Demo progress tracking
    print("="*80)
    print("PROGRESS TRACKER DEMO")
    print("="*80)
    
    tracker = ScreenerProgress()
    tracker.start()
    
    # Simulate pipeline execution
    import time
    
    # Stage 1: Initialization
    tracker.update_stage('initialization', 0, 'running', 'Starting components...')
    time.sleep(1)
    tracker.update_stage('initialization', 50, 'running', 'Loading configurations...')
    time.sleep(1)
    tracker.update_stage('initialization', 100, 'complete', 'Initialization complete')
    
    # Stage 2: SPI Monitoring
    tracker.update_stage('spi_monitoring', 0, 'running', 'Fetching SPI 200 data...')
    time.sleep(1)
    tracker.update_stage('spi_monitoring', 100, 'complete', 'Market data collected')
    
    # Stage 3: Stock Scanning
    tracker.update_stage('stock_scanning', 0, 'running', 'Scanning ASX sectors...')
    time.sleep(1)
    tracker.update_stage('stock_scanning', 33, 'running', 'Scanned 3/8 sectors')
    tracker.update_metrics(stocks_scanned=90)
    time.sleep(1)
    tracker.update_stage('stock_scanning', 100, 'complete', 'All sectors scanned')
    tracker.update_metrics(stocks_scanned=240)
    
    # Add a warning
    tracker.add_warning('Low volume detected for 3 stocks')
    
    # Complete
    tracker.mark_complete()
    
    # Display final summary
    print("\nFinal Summary:")
    summary = tracker.get_status_summary()
    print(json.dumps(summary, indent=2))
    
    # Archive
    tracker.archive_to_history()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)

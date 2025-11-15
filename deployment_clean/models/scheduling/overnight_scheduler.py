"""
Overnight Scheduler Module

Windows Task Scheduler integration wrapper for automated pipeline execution.
Provides programmatic task creation, modification, and monitoring capabilities.

Features:
- Windows Task Scheduler integration via schtasks.exe
- Task creation, deletion, and status checking
- Flexible scheduling configuration
- Execution history tracking
- Error handling and logging
- User-friendly task management interface

Usage:
    scheduler = OvernightScheduler()
    scheduler.create_daily_task(hour=22, minute=0)  # Run at 10:00 PM daily
    scheduler.check_task_status()
    scheduler.get_last_run_result()
"""

import subprocess
import logging
import re
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional, List
import platform

logger = logging.getLogger(__name__)


class OvernightScheduler:
    """
    Wrapper for Windows Task Scheduler to manage overnight screening tasks.
    """
    
    TASK_NAME = "FinBERT_Overnight_Screener"
    
    def __init__(self, script_path: Optional[Path] = None):
        """
        Initialize the scheduler.
        
        Args:
            script_path: Path to the RUN_OVERNIGHT_SCREENER.bat script.
                        Defaults to project root.
        """
        # Verify Windows platform
        if platform.system() != 'Windows':
            logger.warning("Windows Task Scheduler only available on Windows platform")
        
        # Determine script path
        if script_path is None:
            base_path = Path(__file__).parent.parent.parent
            script_path = base_path / 'RUN_OVERNIGHT_SCREENER.bat'
        
        self.script_path = Path(script_path)
        
        if not self.script_path.exists():
            logger.warning(f"Script not found: {self.script_path}")
        
    def create_daily_task(self, hour: int = 22, minute: int = 0, 
                          run_level: str = 'HIGHEST') -> bool:
        """
        Create a daily scheduled task.
        
        Args:
            hour: Hour to run (0-23), default 22 (10 PM)
            minute: Minute to run (0-59), default 0
            run_level: Task priority ('HIGHEST' or 'LIMITED')
            
        Returns:
            True if task created successfully, False otherwise
        """
        if platform.system() != 'Windows':
            logger.error("Task creation only supported on Windows")
            return False
        
        # Format time string
        start_time = f"{hour:02d}:{minute:02d}"
        
        # Delete existing task first (ignore errors)
        self.delete_task()
        
        # Build schtasks command
        cmd = [
            'schtasks',
            '/Create',
            '/TN', self.TASK_NAME,
            '/TR', f'"{self.script_path}"',
            '/SC', 'DAILY',
            '/ST', start_time,
            '/RL', run_level,
            '/F'  # Force creation
        ]
        
        try:
            logger.info(f"Creating scheduled task: {self.TASK_NAME}")
            logger.info(f"Schedule: Daily at {start_time}")
            logger.info(f"Script: {self.script_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Task created successfully")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"Failed to create task: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Task creation timed out")
            return False
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False
            
    def delete_task(self) -> bool:
        """
        Delete the scheduled task.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if platform.system() != 'Windows':
            logger.error("Task deletion only supported on Windows")
            return False
        
        cmd = [
            'schtasks',
            '/Delete',
            '/TN', self.TASK_NAME,
            '/F'  # Force deletion without confirmation
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Task '{self.TASK_NAME}' deleted successfully")
                return True
            else:
                # Task might not exist, which is OK
                logger.debug(f"Task deletion returned: {result.stderr}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
            
    def enable_task(self) -> bool:
        """Enable the scheduled task"""
        return self._change_task_state('ENABLE')
        
    def disable_task(self) -> bool:
        """Disable the scheduled task"""
        return self._change_task_state('DISABLE')
        
    def _change_task_state(self, state: str) -> bool:
        """
        Change task enabled/disabled state.
        
        Args:
            state: 'ENABLE' or 'DISABLE'
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != 'Windows':
            logger.error("Task management only supported on Windows")
            return False
        
        cmd = [
            'schtasks',
            '/Change',
            '/TN', self.TASK_NAME,
            f'/{state}'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Task {state.lower()}d successfully")
                return True
            else:
                logger.error(f"Failed to {state.lower()} task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error changing task state: {e}")
            return False
            
    def check_task_status(self) -> Optional[Dict]:
        """
        Check current status of the scheduled task.
        
        Returns:
            Dictionary with task status information, or None if task doesn't exist
        """
        if platform.system() != 'Windows':
            logger.error("Task status checking only supported on Windows")
            return None
        
        cmd = [
            'schtasks',
            '/Query',
            '/TN', self.TASK_NAME,
            '/V',
            '/FO', 'LIST'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Task '{self.TASK_NAME}' not found")
                return None
            
            # Parse output
            output = result.stdout
            status = {}
            
            # Extract key fields using regex
            patterns = {
                'status': r'Status:\s+(.+)',
                'next_run_time': r'Next Run Time:\s+(.+)',
                'last_run_time': r'Last Run Time:\s+(.+)',
                'last_result': r'Last Result:\s+(.+)',
                'run_as_user': r'Run As User:\s+(.+)',
                'schedule': r'Schedule:\s+(.+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    status[key] = match.group(1).strip()
            
            logger.info(f"Task status retrieved: {status.get('status', 'Unknown')}")
            return status
            
        except Exception as e:
            logger.error(f"Error checking task status: {e}")
            return None
            
    def get_last_run_result(self) -> Optional[str]:
        """
        Get the result of the last task execution.
        
        Returns:
            Result code/message, or None if unavailable
        """
        status = self.check_task_status()
        if status and 'last_result' in status:
            last_result = status['last_result']
            
            # Interpret common result codes
            if '0x0' in last_result or 'success' in last_result.lower():
                return 'SUCCESS'
            elif '0x1' in last_result:
                return 'FAILED'
            else:
                return last_result
        
        return None
        
    def run_task_now(self) -> bool:
        """
        Run the scheduled task immediately.
        
        Returns:
            True if task started successfully, False otherwise
        """
        if platform.system() != 'Windows':
            logger.error("Task execution only supported on Windows")
            return False
        
        cmd = [
            'schtasks',
            '/Run',
            '/TN', self.TASK_NAME
        ]
        
        try:
            logger.info(f"Starting task '{self.TASK_NAME}' manually...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Task started successfully")
                return True
            else:
                logger.error(f"Failed to start task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running task: {e}")
            return False
            
    def list_all_finbert_tasks(self) -> List[str]:
        """
        List all FinBERT-related scheduled tasks.
        
        Returns:
            List of task names matching 'FinBERT' pattern
        """
        if platform.system() != 'Windows':
            logger.error("Task listing only supported on Windows")
            return []
        
        cmd = [
            'schtasks',
            '/Query',
            '/FO', 'LIST'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error("Failed to query tasks")
                return []
            
            # Find all task names containing 'FinBERT'
            tasks = []
            for line in result.stdout.split('\n'):
                if 'TaskName:' in line and 'FinBERT' in line:
                    task_name = line.split(':', 1)[1].strip()
                    tasks.append(task_name)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []
            
    def get_task_history(self, max_entries: int = 10) -> List[Dict]:
        """
        Get recent execution history of the task.
        
        Args:
            max_entries: Maximum number of history entries to retrieve
            
        Returns:
            List of execution history dictionaries
        """
        # Note: This is a placeholder. Full implementation would require
        # parsing Windows Event Log (Event ID 102, 103 for Task Scheduler)
        # or using PowerShell's Get-ScheduledTaskInfo
        
        logger.warning("Task history retrieval not fully implemented")
        logger.info("For detailed history, check: Event Viewer > Applications and Services Logs > Microsoft > Windows > TaskScheduler")
        
        return []


# Command-line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage overnight screening scheduled task')
    parser.add_argument('action', choices=['create', 'delete', 'enable', 'disable', 'status', 'run', 'list'],
                       help='Action to perform')
    parser.add_argument('--hour', type=int, default=22, help='Hour to run (0-23), default: 22')
    parser.add_argument('--minute', type=int, default=0, help='Minute to run (0-59), default: 0')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scheduler = OvernightScheduler()
    
    print("="*80)
    print("OVERNIGHT SCHEDULER MANAGEMENT")
    print("="*80)
    
    if args.action == 'create':
        success = scheduler.create_daily_task(hour=args.hour, minute=args.minute)
        if success:
            print(f"\n✓ Task created successfully!")
            print(f"  Schedule: Daily at {args.hour:02d}:{args.minute:02d}")
            print(f"  Script: {scheduler.script_path}")
        else:
            print("\n✗ Failed to create task")
            
    elif args.action == 'delete':
        success = scheduler.delete_task()
        if success:
            print("\n✓ Task deleted successfully!")
        else:
            print("\n✗ Failed to delete task")
            
    elif args.action == 'enable':
        success = scheduler.enable_task()
        if success:
            print("\n✓ Task enabled successfully!")
        else:
            print("\n✗ Failed to enable task")
            
    elif args.action == 'disable':
        success = scheduler.disable_task()
        if success:
            print("\n✓ Task disabled successfully!")
        else:
            print("\n✗ Failed to disable task")
            
    elif args.action == 'status':
        status = scheduler.check_task_status()
        if status:
            print("\nTask Status:")
            for key, value in status.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("\n✗ Task not found or error checking status")
            
    elif args.action == 'run':
        success = scheduler.run_task_now()
        if success:
            print("\n✓ Task started successfully!")
            print("  Check progress at: reports/screener_progress.json")
        else:
            print("\n✗ Failed to start task")
            
    elif args.action == 'list':
        tasks = scheduler.list_all_finbert_tasks()
        if tasks:
            print("\nFinBERT Scheduled Tasks:")
            for task in tasks:
                print(f"  - {task}")
        else:
            print("\nNo FinBERT tasks found")
    
    print("="*80)

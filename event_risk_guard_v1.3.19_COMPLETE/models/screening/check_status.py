"""
Status Checker Script

Interactive command-line tool to check the status of the overnight screening pipeline.
Displays real-time progress, stage completion, errors, and timing estimates.

Features:
- Load and display progress from JSON file
- Color-coded status display (if colorama available)
- Stage-by-stage breakdown
- ETA and elapsed time display
- Error and warning reporting
- Metrics summary
- Historical logs viewer

Usage:
    python check_status.py
    python check_status.py --watch  # Continuous monitoring
    python check_status.py --history  # View past runs
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback color classes
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''


def load_progress(progress_file: Path) -> Optional[Dict]:
    """Load progress from JSON file"""
    if not progress_file.exists():
        return None
    
    try:
        with open(progress_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading progress file: {e}")
        return None


def format_stage_status(stage: Dict) -> str:
    """Format stage status with color coding"""
    status = stage.get('status', 'pending')
    progress = stage.get('progress', 0)
    
    if status == 'complete':
        color = Fore.GREEN
        symbol = '✓'
    elif status == 'running':
        color = Fore.CYAN
        symbol = '▶'
    elif status == 'failed':
        color = Fore.RED
        symbol = '✗'
    else:
        color = Fore.WHITE
        symbol = '○'
    
    # Progress bar
    bar_length = 20
    filled = int(bar_length * progress / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    return f"{color}{symbol} [{bar}] {progress:3.0f}%{Style.RESET_ALL}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def display_status(progress: Dict, clear_screen: bool = False):
    """Display comprehensive status report"""
    if clear_screen:
        # Clear screen (works on most terminals)
        print('\033[2J\033[H', end='')
    
    print("="*80)
    print(f"{Style.BRIGHT}OVERNIGHT STOCK SCREENER - STATUS REPORT{Style.RESET_ALL}")
    print("="*80)
    
    # Overall status
    overall_status = progress.get('overall_status', 'unknown')
    overall_progress = progress.get('overall_progress', 0)
    
    if overall_status == 'complete':
        status_color = Fore.GREEN
        status_text = '✓ COMPLETE'
    elif overall_status == 'running':
        status_color = Fore.CYAN
        status_text = '▶ RUNNING'
    elif overall_status == 'failed':
        status_color = Fore.RED
        status_text = '✗ FAILED'
    else:
        status_color = Fore.WHITE
        status_text = '○ PENDING'
    
    print(f"\n{Style.BRIGHT}Overall Status:{Style.RESET_ALL} {status_color}{status_text}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}Overall Progress:{Style.RESET_ALL} {overall_progress:.1f}%")
    
    # Timing information
    start_time = progress.get('start_time')
    end_time = progress.get('end_time')
    current_time = progress.get('current_time')
    
    if start_time:
        print(f"\n{Style.BRIGHT}Timing:{Style.RESET_ALL}")
        print(f"  Started:  {start_time}")
        if end_time:
            print(f"  Finished: {end_time}")
        else:
            print(f"  Current:  {current_time}")
        
        exec_time = progress.get('execution_time_formatted', 'N/A')
        print(f"  Elapsed:  {exec_time}")
        
        if overall_status == 'running':
            eta_formatted = progress.get('estimated_remaining_formatted')
            eta_time = progress.get('estimated_completion_time')
            if eta_formatted:
                print(f"  Remaining: ~{eta_formatted}")
                print(f"  ETA:       {eta_time}")
    
    # Stage breakdown
    print(f"\n{Style.BRIGHT}Pipeline Stages:{Style.RESET_ALL}")
    print()
    
    stages = progress.get('stages', {})
    stage_names = {
        'initialization': 'Initialization',
        'spi_monitoring': 'SPI Monitoring',
        'stock_scanning': 'Stock Scanning',
        'lstm_training': 'LSTM Training',
        'batch_prediction': 'Batch Prediction',
        'opportunity_scoring': 'Opportunity Scoring',
        'report_generation': 'Report Generation'
    }
    
    for stage_key, stage_name in stage_names.items():
        if stage_key in stages:
            stage = stages[stage_key]
            status_bar = format_stage_status(stage)
            message = stage.get('message', '')
            
            print(f"  {stage_name:20} {status_bar}")
            if message:
                print(f"                       {Fore.YELLOW}{message}{Style.RESET_ALL}")
    
    # Metrics
    metrics = progress.get('metrics', {})
    if any(metrics.values()):
        print(f"\n{Style.BRIGHT}Metrics:{Style.RESET_ALL}")
        print(f"  Stocks Scanned:         {metrics.get('stocks_scanned', 0)}")
        print(f"  Models Trained:         {metrics.get('models_trained', 0)}")
        print(f"  Predictions Generated:  {metrics.get('predictions_generated', 0)}")
        print(f"  Opportunities Found:    {metrics.get('opportunities_found', 0)}")
    
    # Errors
    errors = progress.get('errors', [])
    if errors:
        print(f"\n{Style.BRIGHT}{Fore.RED}Errors ({len(errors)}):{Style.RESET_ALL}")
        for error in errors[-5:]:  # Show last 5 errors
            timestamp = error.get('timestamp', 'N/A')
            message = error.get('message', 'Unknown error')
            print(f"  {Fore.RED}[{timestamp}] {message}{Style.RESET_ALL}")
    
    # Warnings
    warnings = progress.get('warnings', [])
    if warnings:
        print(f"\n{Style.BRIGHT}{Fore.YELLOW}Warnings ({len(warnings)}):{Style.RESET_ALL}")
        for warning in warnings[-5:]:  # Show last 5 warnings
            timestamp = warning.get('timestamp', 'N/A')
            message = warning.get('message', 'Unknown warning')
            print(f"  {Fore.YELLOW}[{timestamp}] {message}{Style.RESET_ALL}")
    
    print("\n" + "="*80)


def watch_progress(progress_file: Path, interval: int = 5):
    """Continuously monitor progress"""
    print(f"Monitoring progress (Ctrl+C to stop)...")
    print(f"Update interval: {interval} seconds\n")
    
    try:
        while True:
            progress = load_progress(progress_file)
            
            if progress:
                display_status(progress, clear_screen=True)
                
                # Stop watching if complete or failed
                overall_status = progress.get('overall_status')
                if overall_status in ['complete', 'failed']:
                    print(f"\n{Fore.CYAN}Pipeline has finished. Stopping monitor.{Style.RESET_ALL}")
                    break
            else:
                print(f"{Fore.YELLOW}Waiting for pipeline to start...{Style.RESET_ALL}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Monitoring stopped by user.{Style.RESET_ALL}")


def list_historical_logs(history_dir: Path):
    """List historical screening logs"""
    if not history_dir.exists():
        print(f"{Fore.YELLOW}No historical logs found.{Style.RESET_ALL}")
        return
    
    # Find all JSON files
    log_files = sorted(history_dir.glob('screener_*.json'), reverse=True)
    
    if not log_files:
        print(f"{Fore.YELLOW}No historical logs found.{Style.RESET_ALL}")
        return
    
    print(f"\n{Style.BRIGHT}Historical Screening Logs:{Style.RESET_ALL}")
    print()
    
    for i, log_file in enumerate(log_files[:20], 1):  # Show last 20
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
            
            start_time = data.get('start_time', 'N/A')
            overall_status = data.get('overall_status', 'unknown')
            overall_progress = data.get('overall_progress', 0)
            exec_time = data.get('execution_time_formatted', 'N/A')
            
            if overall_status == 'complete':
                status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
            elif overall_status == 'failed':
                status_icon = f"{Fore.RED}✗{Style.RESET_ALL}"
            else:
                status_icon = f"{Fore.YELLOW}○{Style.RESET_ALL}"
            
            print(f"{i:2}. {status_icon} {start_time} - {overall_status.upper():10} ({overall_progress:.0f}%) - {exec_time}")
            
        except Exception as e:
            print(f"{i:2}. {Fore.RED}Error reading {log_file.name}: {e}{Style.RESET_ALL}")
    
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Check status of overnight stock screening pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Continuously monitor progress (updates every 5 seconds)'
    )
    
    parser.add_argument(
        '--history', '-H',
        action='store_true',
        help='View historical screening logs'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help='Update interval in seconds for watch mode (default: 5)'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=Path,
        help='Custom path to progress JSON file'
    )
    
    args = parser.parse_args()
    
    # Determine paths
    if args.file:
        progress_file = args.file
    else:
        base_path = Path(__file__).parent.parent.parent
        progress_file = base_path / 'reports' / 'screener_progress.json'
    
    history_dir = progress_file.parent / 'history'
    
    # Handle different modes
    if args.history:
        list_historical_logs(history_dir)
    elif args.watch:
        watch_progress(progress_file, interval=args.interval)
    else:
        # Single status check
        progress = load_progress(progress_file)
        
        if progress:
            display_status(progress)
        else:
            print(f"{Fore.YELLOW}No progress file found at: {progress_file}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}The pipeline may not have started yet.{Style.RESET_ALL}")
            print()
            print("To start the pipeline, run:")
            print("  RUN_OVERNIGHT_SCREENER.bat")
            print()


if __name__ == '__main__':
    main()

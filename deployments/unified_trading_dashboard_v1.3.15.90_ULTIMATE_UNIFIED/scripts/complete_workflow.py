# -*- coding: utf-8 -*-
"""
Complete Pipeline + Trading Integration Workflow
=================================================

This script demonstrates the complete integration of:
1. Overnight pipelines (US/UK/AU with FinBERT, LSTM, Event Risk, Regime)
2. Signal adapter V2 (reads pipeline JSON reports)
3. Live trading system (flexible position sizing, multi-market)

Usage:
    # Full workflow - overnight analysis + morning trading
    python complete_workflow.py --run-pipelines --execute-trades --markets AU,US,UK
    
    # Just run pipelines (overnight)
    python complete_workflow.py --run-pipelines
    
    # Just execute trades from existing reports
    python complete_workflow.py --execute-trades --markets US,UK
    
    # Dry run
    python complete_workflow.py --run-pipelines --execute-trades --dry-run
"""

import logging
import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/complete_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompleteWorkflow:
    """
    Complete integrated workflow combining overnight pipelines with live trading
    """
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.base_path = Path(__file__).parent
        
        logger.info("="*80)
        logger.info("COMPLETE PIPELINE + TRADING INTEGRATION WORKFLOW")
        logger.info("="*80)
        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Dry run: {dry_run}")
    
    def run_overnight_pipeline(self, market: str, capital: float = 100000) -> bool:
        """
        Run overnight pipeline for a specific market
        
        Args:
            market: 'AU', 'US', or 'UK'
            capital: Trading capital
            
        Returns:
            True if successful
        """
        logger.info("="*60)
        logger.info(f"RUNNING {market} OVERNIGHT PIPELINE")
        logger.info("="*60)
        
        # Determine which pipeline script to run
        pipeline_scripts = {
            'AU': 'run_au_pipeline_v1.3.13.py',  # Note: Keeping v1.3.13 as this is the actual filename
            'US': 'run_us_full_pipeline.py',
            'UK': 'run_uk_full_pipeline.py'
        }
        
        script = pipeline_scripts.get(market)
        if not script:
            logger.error(f"Unknown market: {market}")
            return False
        
        script_path = self.base_path / script
        if not script_path.exists():
            logger.error(f"Pipeline script not found: {script_path}")
            return False
        
        # Build command
        cmd = [
            sys.executable,
            str(script_path),
            '--full-scan',
            '--capital', str(capital),
            '--ignore-market-hours'  # Allow overnight runs
        ]
        
        # Only add --mode for US/UK pipelines (AU doesn't support it)
        if market in ['US', 'UK']:
            cmd.extend(['--mode', 'test' if self.dry_run else 'full'])
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return True
        
        try:
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"[OK] {market} pipeline completed successfully")
                # Log key output lines
                for line in result.stdout.split('\n')[-20:]:
                    if line.strip():
                        logger.info(f"  {line}")
                return True
            else:
                logger.error(f"[X] {market} pipeline failed with code {result.returncode}")
                logger.error(f"Error output:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"[X] {market} pipeline timed out after 1 hour")
            return False
        except Exception as e:
            logger.error(f"[X] Error running {market} pipeline: {e}")
            return False
    
    def run_all_pipelines(self, markets: list, capital: float = 100000) -> dict:
        """
        Run overnight pipelines for all specified markets
        
        Args:
            markets: List of market codes ['AU', 'US', 'UK']
            capital: Trading capital per market
            
        Returns:
            Dictionary of {market: success}
        """
        logger.info("="*80)
        logger.info("RUNNING ALL OVERNIGHT PIPELINES")
        logger.info("="*80)
        logger.info(f"Markets: {', '.join(markets)}")
        logger.info(f"Capital per market: ${capital:,.2f}")
        
        results = {}
        
        for market in markets:
            success = self.run_overnight_pipeline(market, capital)
            results[market] = success
            
            if not success:
                logger.warning(f"Pipeline failed for {market}, continuing with others...")
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("="*80)
        successful = [m for m, s in results.items() if s]
        failed = [m for m, s in results.items() if not s]
        
        logger.info(f"Successful: {len(successful)}/{len(markets)}")
        if successful:
            logger.info(f"  {', '.join(successful)}")
        if failed:
            logger.warning(f"Failed: {len(failed)}/{len(markets)}")
            logger.warning(f"  {', '.join(failed)}")
        
        return results
    
    def execute_morning_trades(self, markets: list, capital: float = 300000) -> bool:
        """
        Execute morning trading based on pipeline reports
        
        Args:
            markets: List of markets to trade
            capital: Total trading capital
            
        Returns:
            True if successful
        """
        logger.info("="*80)
        logger.info("EXECUTING MORNING TRADES")
        logger.info("="*80)
        logger.info(f"Markets: {', '.join(markets)}")
        logger.info(f"Total capital: ${capital:,.2f}")
        
        # Check if we have the enhanced trading script
        trading_script = self.base_path / 'run_pipeline_enhanced_trading.py'
        if not trading_script.exists():
            logger.error(f"Trading script not found: {trading_script}")
            return False
        
        # Build command
        cmd = [
            sys.executable,
            str(trading_script),
            '--markets', ','.join(markets),
            '--capital', str(capital),
            '--once'  # Run once, don't start continuous monitoring
        ]
        
        if self.dry_run:
            cmd.append('--dry-run')
        
        try:
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("[OK] Trading execution completed successfully")
                # Log key output
                for line in result.stdout.split('\n')[-30:]:
                    if line.strip():
                        logger.info(f"  {line}")
                return True
            else:
                logger.error(f"[X] Trading execution failed with code {result.returncode}")
                logger.error(f"Error output:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("[X] Trading execution timed out after 10 minutes")
            return False
        except Exception as e:
            logger.error(f"[X] Error executing trades: {e}")
            return False
    
    def verify_reports_exist(self, markets: list) -> dict:
        """Check if pipeline reports exist for all markets"""
        reports_dir = self.base_path / 'reports' / 'screening'
        results = {}
        
        logger.info("Verifying pipeline reports...")
        for market in markets:
            report_path = reports_dir / f'{market.lower()}_morning_report.json'
            exists = report_path.exists()
            results[market] = exists
            
            if exists:
                # Check age
                mod_time = datetime.fromtimestamp(report_path.stat().st_mtime)
                age_hours = (datetime.now() - mod_time).total_seconds() / 3600
                logger.info(f"  {market}: [OK] Found (age: {age_hours:.1f} hours)")
            else:
                logger.warning(f"  {market}: [X] Not found - pipeline needs to run")
        
        return results
    
    def run_complete_workflow(
        self,
        markets: list,
        run_pipelines: bool = True,
        execute_trades: bool = True,
        capital: float = 300000
    ) -> dict:
        """
        Run the complete workflow
        
        Args:
            markets: List of markets
            run_pipelines: Whether to run overnight pipelines
            execute_trades: Whether to execute trades
            capital: Total trading capital
            
        Returns:
            Results dictionary
        """
        logger.info("="*80)
        logger.info("STARTING COMPLETE WORKFLOW")
        logger.info("="*80)
        logger.info(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Markets: {', '.join(markets)}")
        logger.info(f"Run Pipelines: {run_pipelines}")
        logger.info(f"Execute Trades: {execute_trades}")
        logger.info(f"Total Capital: ${capital:,.2f}")
        
        results = {
            'pipelines': {},
            'trading': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Run overnight pipelines
        if run_pipelines:
            capital_per_market = capital / len(markets)
            results['pipelines'] = self.run_all_pipelines(markets, capital_per_market)
        else:
            logger.info("Skipping pipeline execution")
            # Just verify reports exist
            results['pipelines'] = self.verify_reports_exist(markets)
        
        # Step 2: Execute trades
        if execute_trades:
            # Check if we have reports
            report_status = self.verify_reports_exist(markets)
            available_markets = [m for m, exists in report_status.items() if exists]
            
            if not available_markets:
                logger.error("No pipeline reports available - cannot execute trades")
                results['trading'] = False
            else:
                if len(available_markets) < len(markets):
                    logger.warning(f"Only {len(available_markets)}/{len(markets)} markets have reports")
                
                results['trading'] = self.execute_morning_trades(available_markets, capital)
        else:
            logger.info("Skipping trade execution")
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("="*80)
        pipeline_success = sum(1 for s in results['pipelines'].values() if s)
        logger.info(f"Pipelines: {pipeline_success}/{len(markets)} successful")
        logger.info(f"Trading: {'SUCCESS' if results['trading'] else 'SKIPPED/FAILED'}")
        
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Complete Pipeline + Trading Integration Workflow'
    )
    parser.add_argument(
        '--run-pipelines',
        action='store_true',
        help='Run overnight pipelines'
    )
    parser.add_argument(
        '--execute-trades',
        action='store_true',
        help='Execute morning trades'
    )
    parser.add_argument(
        '--markets',
        type=str,
        default='AU,US,UK',
        help='Comma-separated markets (default: AU,US,UK)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=300000,
        help='Total trading capital (default: 300000)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (no actual execution)'
    )
    
    args = parser.parse_args()
    
    # Parse markets
    markets = [m.strip().upper() for m in args.markets.split(',')]
    
    # Validate
    valid_markets = ['AU', 'US', 'UK']
    for market in markets:
        if market not in valid_markets:
            logger.error(f"Invalid market: {market}")
            sys.exit(1)
    
    # Create workflow
    workflow = CompleteWorkflow(dry_run=args.dry_run)
    
    # Run
    results = workflow.run_complete_workflow(
        markets=markets,
        run_pipelines=args.run_pipelines,
        execute_trades=args.execute_trades,
        capital=args.capital
    )
    
    # Exit code based on results
    if args.execute_trades and not results['trading']:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Unified Screening Pipeline Launcher

Runs stock screening pipelines for multiple markets:
- ASX (Australian Securities Exchange)
- US (NYSE/NASDAQ)

Usage:
    python run_screening.py --market asx       # Run ASX pipeline only
    python run_screening.py --market us        # Run US pipeline only
    python run_screening.py --market both      # Run both pipelines
    python run_screening.py --market all       # Run both pipelines (alias)
    
Options:
    --market: Market to screen (asx, us, both, all)
    --stocks: Number of stocks per sector (default: 30)
    --sectors: Comma-separated list of sectors (default: all)
    --parallel: Run pipelines in parallel (for 'both' mode)
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import time
import traceback

# Setup Python paths for imports
import setup_paths

from models.screening.overnight_pipeline import OvernightPipeline
from models.screening.us_overnight_pipeline import USOvernightPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'logs' / 'screening' / 'launcher.log')
    ]
)
logger = logging.getLogger(__name__)


class ScreeningLauncher:
    """
    Unified launcher for ASX and US screening pipelines
    """
    
    def __init__(self):
        """Initialize launcher"""
        self.results = {}
    
    def run_asx_pipeline(self, stocks_per_sector: int = 30, sectors: list = None) -> dict:
        """
        Run ASX screening pipeline
        
        Args:
            stocks_per_sector: Number of stocks to screen per sector
            sectors: List of sectors to screen (None = all)
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING ASX MARKET SCREENING PIPELINE")
        logger.info("="*80)
        
        start_time = time.time()
        
        try:
            pipeline = OvernightPipeline()
            results = pipeline.run_full_pipeline(
                sectors=sectors,
                stocks_per_sector=stocks_per_sector
            )
            
            elapsed = time.time() - start_time
            
            logger.info("\n" + "="*80)
            logger.info(f"✓ ASX PIPELINE COMPLETED in {elapsed/60:.1f} minutes")
            logger.info("="*80)
            
            return {
                'market': 'ASX',
                'status': 'success',
                'elapsed_time': elapsed,
                'results': results
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"\n✗ ASX PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            
            return {
                'market': 'ASX',
                'status': 'failed',
                'elapsed_time': elapsed,
                'error': str(e)
            }
    
    def run_us_pipeline(self, stocks_per_sector: int = 30, sectors: list = None) -> dict:
        """
        Run US screening pipeline
        
        Args:
            stocks_per_sector: Number of stocks to screen per sector
            sectors: List of sectors to screen (None = all)
            
        Returns:
            Dictionary with pipeline results
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING US MARKET SCREENING PIPELINE")
        logger.info("="*80)
        
        start_time = time.time()
        
        try:
            pipeline = USOvernightPipeline()
            results = pipeline.run_full_pipeline(
                sectors=sectors,
                stocks_per_sector=stocks_per_sector
            )
            
            elapsed = time.time() - start_time
            
            logger.info("\n" + "="*80)
            logger.info(f"✓ US PIPELINE COMPLETED in {elapsed/60:.1f} minutes")
            logger.info("="*80)
            
            return {
                'market': 'US',
                'status': 'success',
                'elapsed_time': elapsed,
                'results': results
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"\n✗ US PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            
            return {
                'market': 'US',
                'status': 'failed',
                'elapsed_time': elapsed,
                'error': str(e)
            }
    
    def run_both_pipelines(self, stocks_per_sector: int = 30, sectors: list = None, 
                          parallel: bool = False) -> dict:
        """
        Run both ASX and US pipelines
        
        Args:
            stocks_per_sector: Number of stocks to screen per sector
            sectors: List of sectors to screen (None = all)
            parallel: Run pipelines in parallel (requires multiprocessing)
            
        Returns:
            Dictionary with both pipeline results
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING DUAL MARKET SCREENING (ASX + US)")
        logger.info("="*80)
        
        total_start = time.time()
        
        if parallel:
            logger.info("Running pipelines in PARALLEL mode...")
            try:
                from concurrent.futures import ThreadPoolExecutor
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    asx_future = executor.submit(self.run_asx_pipeline, stocks_per_sector, sectors)
                    us_future = executor.submit(self.run_us_pipeline, stocks_per_sector, sectors)
                    
                    asx_result = asx_future.result()
                    us_result = us_future.result()
                
            except Exception as e:
                logger.error(f"Parallel execution failed: {e}")
                logger.info("Falling back to SEQUENTIAL mode...")
                asx_result = self.run_asx_pipeline(stocks_per_sector, sectors)
                us_result = self.run_us_pipeline(stocks_per_sector, sectors)
        else:
            logger.info("Running pipelines in SEQUENTIAL mode...")
            # Run ASX first (closes before US)
            asx_result = self.run_asx_pipeline(stocks_per_sector, sectors)
            # Then run US
            us_result = self.run_us_pipeline(stocks_per_sector, sectors)
        
        total_elapsed = time.time() - total_start
        
        logger.info("\n" + "="*80)
        logger.info(f"✓ DUAL MARKET SCREENING COMPLETED in {total_elapsed/60:.1f} minutes")
        logger.info("="*80)
        
        return {
            'asx': asx_result,
            'us': us_result,
            'total_elapsed_time': total_elapsed
        }
    
    def print_summary(self, results: dict):
        """Print execution summary"""
        print("\n" + "="*80)
        print("SCREENING EXECUTION SUMMARY")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'asx' in results and 'us' in results:
            # Both pipelines
            print(f"\nMode: DUAL MARKET (ASX + US)")
            print(f"Total Time: {results['total_elapsed_time']/60:.1f} minutes")
            
            print(f"\n📊 ASX Pipeline:")
            print(f"   Status: {results['asx']['status'].upper()}")
            print(f"   Time: {results['asx']['elapsed_time']/60:.1f} minutes")
            if results['asx']['status'] == 'success':
                asx_data = results['asx']['results']
                print(f"   Stocks: {asx_data.get('total_stocks', 0)}")
                print(f"   Top Opportunities: {len(asx_data.get('top_opportunities', []))}")
            
            print(f"\n📊 US Pipeline:")
            print(f"   Status: {results['us']['status'].upper()}")
            print(f"   Time: {results['us']['elapsed_time']/60:.1f} minutes")
            if results['us']['status'] == 'success':
                us_data = results['us']['results']
                print(f"   Stocks: {us_data.get('total_stocks', 0)}")
                print(f"   Top Opportunities: {len(us_data.get('top_opportunities', []))}")
        
        elif 'market' in results:
            # Single pipeline
            print(f"\nMarket: {results['market']}")
            print(f"Status: {results['status'].upper()}")
            print(f"Time: {results['elapsed_time']/60:.1f} minutes")
            
            if results['status'] == 'success':
                data = results['results']
                print(f"Stocks Processed: {data.get('total_stocks', 0)}")
                print(f"Top Opportunities: {len(data.get('top_opportunities', []))}")
                print(f"Report: {data.get('report_path', 'N/A')}")
        
        print("="*80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Stock Screening Pipeline Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--market',
        type=str,
        default='both',
        choices=['asx', 'us', 'both', 'all'],
        help='Market to screen (asx, us, both, all)'
    )
    
    parser.add_argument(
        '--stocks',
        type=int,
        default=30,
        help='Number of stocks per sector (default: 30)'
    )
    
    parser.add_argument(
        '--sectors',
        type=str,
        default=None,
        help='Comma-separated list of sectors (default: all)'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run both pipelines in parallel (for both/all mode)'
    )
    
    args = parser.parse_args()
    
    # Parse sectors
    sectors = None
    if args.sectors:
        sectors = [s.strip() for s in args.sectors.split(',')]
    
    # Create launcher
    launcher = ScreeningLauncher()
    
    # Run appropriate pipeline(s)
    if args.market in ['both', 'all']:
        results = launcher.run_both_pipelines(
            stocks_per_sector=args.stocks,
            sectors=sectors,
            parallel=args.parallel
        )
    elif args.market == 'asx':
        results = launcher.run_asx_pipeline(
            stocks_per_sector=args.stocks,
            sectors=sectors
        )
    elif args.market == 'us':
        results = launcher.run_us_pipeline(
            stocks_per_sector=args.stocks,
            sectors=sectors
        )
    
    # Print summary
    launcher.print_summary(results)
    
    # Exit with appropriate code
    if isinstance(results, dict):
        if 'asx' in results and 'us' in results:
            # Both pipelines
            if results['asx']['status'] == 'success' and results['us']['status'] == 'success':
                return 0
            else:
                return 1
        elif results.get('status') == 'success':
            return 0
        else:
            return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())

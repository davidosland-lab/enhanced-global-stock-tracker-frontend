#!/usr/bin/env python3
"""
Run Full Market Scan - yahooquery ONLY (Windows-Compatible Version)
Scans all ASX sectors using yahooquery-only implementation

NO yfinance, NO Alpha Vantage - Pure yahooquery for maximum reliability
Uses ASCII symbols for Windows console compatibility
"""

import sys
import logging
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

# Setup logging (no Unicode symbols)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'screener_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.screening.stock_scanner import StockScanner


def print_banner():
    """Print startup banner"""
    logger.info("=" * 80)
    logger.info("FINBERT v4.4.4 - FULL MARKET SCAN (yahooquery ONLY)")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Data Source: yahooquery (NO yfinance, NO Alpha Vantage)")
    logger.info("=" * 80)
    logger.info("")


def run_full_market_scan(top_n_per_sector=10):
    """
    Run complete market scan on all sectors
    
    Args:
        top_n_per_sector: Number of top stocks to return per sector
        
    Returns:
        Dictionary of results by sector
    """
    start_time = time.time()
    
    print_banner()
    
    try:
        # Initialize scanner
        logger.info("Initializing Stock Scanner (yahooquery-only)...")
        scanner = StockScanner()
        logger.info(f"[OK] Loaded {len(scanner.sectors)} sectors")
        logger.info("")
        
        # Scan all sectors
        logger.info("=" * 80)
        logger.info("STARTING FULL MARKET SCAN")
        logger.info("=" * 80)
        logger.info("")
        
        results = scanner.scan_all_sectors(top_n_per_sector=top_n_per_sector)
        
        # Generate summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("SCAN COMPLETE - SUMMARY")
        logger.info("=" * 80)
        logger.info("")
        
        total_stocks = 0
        for sector_name, stocks in results.items():
            total_stocks += len(stocks)
            logger.info(f"  {sector_name}: {len(stocks)} stocks validated")
        
        logger.info("")
        logger.info(f"Total stocks across all sectors: {total_stocks}")
        logger.info("")
        
        # Save results to CSV
        logger.info("=" * 80)
        logger.info("SAVING RESULTS")
        logger.info("=" * 80)
        logger.info("")
        
        all_stocks = []
        for sector_name, stocks in results.items():
            for stock in stocks:
                stock['sector'] = sector_name
                all_stocks.append(stock)
        
        if all_stocks:
            # Sort by score
            all_stocks.sort(key=lambda x: x['score'], reverse=True)
            
            # Create DataFrame
            df = pd.DataFrame(all_stocks)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'screener_results_yahooquery_{timestamp}.csv'
            
            # Save
            df.to_csv(output_file, index=False)
            logger.info(f"[OK] Results saved to: {output_file}")
            logger.info(f"  Total rows: {len(df)}")
            logger.info("")
            
            # Display top 10 overall
            logger.info("=" * 80)
            logger.info("TOP 10 STOCKS (All Sectors)")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"{'Rank':<6} {'Symbol':<10} {'Sector':<15} {'Price':<10} {'Score':<8}")
            logger.info("-" * 70)
            
            for i, stock in enumerate(all_stocks[:10], 1):
                logger.info(
                    f"{i:<6} "
                    f"{stock['symbol']:<10} "
                    f"{stock['sector']:<15} "
                    f"${stock['price']:<9.2f} "
                    f"{stock['score']:<8.0f}"
                )
            logger.info("")
        else:
            logger.warning("No stocks passed validation!")
        
        # Duration
        duration = time.time() - start_time
        logger.info("=" * 80)
        logger.info("SCAN STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Duration: {duration/60:.1f} minutes ({duration:.0f} seconds)")
        logger.info(f"Stocks validated: {total_stocks}")
        if duration > 0:
            logger.info(f"Average: {duration/total_stocks if total_stocks > 0 else 0:.1f} seconds per stock")
        logger.info("=" * 80)
        logger.info("")
        logger.info("[COMPLETE] SCAN FINISHED SUCCESSFULLY!")
        logger.info("")
        
        return results
        
    except KeyboardInterrupt:
        logger.warning("\n\n[INTERRUPTED] Scan stopped by user\n")
        return None
        
    except Exception as e:
        logger.error(f"\n\n[ERROR] Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    try:
        # Run scan with top 10 stocks per sector
        results = run_full_market_scan(top_n_per_sector=10)
        
        if results:
            return 0
        else:
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

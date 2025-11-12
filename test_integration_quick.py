#!/usr/bin/env python3
"""
Quick Integration Test - yahooquery ONLY
Tests the integrated scanner with Financial sector
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from models.screening.stock_scanner import StockScanner
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("INTEGRATION TEST - yahooquery ONLY")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Initialize scanner
        logger.info("Initializing StockScanner...")
        scanner = StockScanner()
        logger.info(f"✓ Scanner loaded with {len(scanner.sectors)} sectors")
        logger.info("")
        
        # Test Financial sector
        logger.info("Testing Financial sector scan...")
        logger.info("")
        
        results = scanner.scan_sector('Financials', top_n=5)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)
        logger.info(f"Stocks validated: {len(results)}")
        logger.info("")
        
        if results:
            logger.info(f"{'Rank':<6} {'Symbol':<10} {'Price':<10} {'Score':<8}")
            logger.info("-" * 40)
            for i, stock in enumerate(results, 1):
                logger.info(
                    f"{i:<6} "
                    f"{stock['symbol']:<10} "
                    f"${stock['price']:<9.2f} "
                    f"{stock['score']:<8.0f}"
                )
            logger.info("")
            logger.info("✅ INTEGRATION TEST PASSED!")
            return 0
        else:
            logger.error("❌ No stocks validated!")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

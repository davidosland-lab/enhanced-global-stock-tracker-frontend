"""
Test Batch Fetching Integration
--------------------------------
Tests the new HybridDataFetcher integrated into StockScanner
to verify batch operations work correctly and avoid rate limiting.

This test compares:
1. Legacy mode (individual fetching) - slow, prone to rate limits
2. Batch mode (optimized fetching) - fast, avoids rate limits
"""

import sys
from pathlib import Path
import time
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.screening.stock_scanner import StockScanner
from models.screening.data_fetcher import HybridDataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_batch_vs_individual():
    """
    Compare batch fetching vs individual fetching
    """
    print("\n" + "="*80)
    print("BATCH FETCHING INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Test with a small subset of Financials sector
    test_tickers = ['CBA.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX', 'MQG.AX']
    
    print(f"Testing with {len(test_tickers)} tickers: {', '.join(test_tickers)}\n")
    
    # ========================================================================
    # TEST 1: Individual Fetching (Legacy Mode)
    # ========================================================================
    print("\n" + "-"*80)
    print("TEST 1: INDIVIDUAL FETCHING (Legacy Mode)")
    print("-"*80)
    
    scanner_individual = StockScanner(use_batch_fetching=False)
    
    start_time = time.time()
    results_individual = scanner_individual._scan_sector_individual(
        symbols=test_tickers,
        sector_weight=1.2,
        top_n=10
    )
    individual_time = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Valid stocks: {len(results_individual)}")
    print(f"  Time taken: {individual_time:.2f}s")
    if results_individual:
        print(f"  Top stock: {results_individual[0]['symbol']} (score: {results_individual[0]['score']:.1f})")
    
    # ========================================================================
    # TEST 2: Batch Fetching (Optimized Mode)
    # ========================================================================
    print("\n" + "-"*80)
    print("TEST 2: BATCH FETCHING (Optimized Mode)")
    print("-"*80)
    
    scanner_batch = StockScanner(use_batch_fetching=True, cache_ttl_minutes=30)
    
    # Clear cache to ensure fair comparison
    scanner_batch.data_fetcher.clear_cache(older_than_hours=0)
    
    start_time = time.time()
    results_batch = scanner_batch._scan_sector_batch(
        symbols=test_tickers,
        sector_weight=1.2,
        top_n=10
    )
    batch_time = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Valid stocks: {len(results_batch)}")
    print(f"  Time taken: {batch_time:.2f}s")
    if results_batch:
        print(f"  Top stock: {results_batch[0]['symbol']} (score: {results_batch[0]['score']:.1f})")
    
    # ========================================================================
    # TEST 3: Cached Batch Fetching (Should be instant)
    # ========================================================================
    print("\n" + "-"*80)
    print("TEST 3: CACHED BATCH FETCHING (Second Run)")
    print("-"*80)
    
    start_time = time.time()
    results_cached = scanner_batch._scan_sector_batch(
        symbols=test_tickers,
        sector_weight=1.2,
        top_n=10
    )
    cached_time = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Valid stocks: {len(results_cached)}")
    print(f"  Time taken: {cached_time:.2f}s")
    if results_cached:
        print(f"  Top stock: {results_cached[0]['symbol']} (score: {results_cached[0]['score']:.1f})")
    
    # ========================================================================
    # PERFORMANCE COMPARISON
    # ========================================================================
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    
    if individual_time > 0:
        speedup_first = individual_time / batch_time if batch_time > 0 else float('inf')
        speedup_cached = individual_time / cached_time if cached_time > 0 else float('inf')
        
        print(f"\nIndividual Fetching: {individual_time:.2f}s")
        print(f"Batch Fetching:      {batch_time:.2f}s  ({speedup_first:.1f}x faster)")
        print(f"Cached Fetching:     {cached_time:.2f}s  ({speedup_cached:.1f}x faster)")
        
        print(f"\nTime Savings:")
        print(f"  First run:  {individual_time - batch_time:.2f}s saved")
        print(f"  Cached run: {individual_time - cached_time:.2f}s saved")
    
    # ========================================================================
    # CACHE STATISTICS
    # ========================================================================
    print("\n" + "="*80)
    print("CACHE STATISTICS")
    print("="*80)
    
    stats = scanner_batch.data_fetcher.get_cache_stats()
    print(f"\nCache files: {stats['total_files']}")
    print(f"Cache size:  {stats['total_size_mb']:.2f} MB")
    print(f"Cache TTL:   {stats['ttl_minutes']} minutes")
    print(f"Cache dir:   {stats['cache_dir']}")
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    print("\n✓ Batch fetching is enabled by default in StockScanner")
    print("✓ Cache persists for 30 minutes to minimize API calls")
    print("✓ Overnight scans will benefit from significant speedup")
    
    if speedup_first > 2.0:
        print(f"\n🚀 EXCELLENT: Batch fetching is {speedup_first:.1f}x faster!")
        print("   This will dramatically reduce rate limiting issues")
    elif speedup_first > 1.5:
        print(f"\n✓ GOOD: Batch fetching is {speedup_first:.1f}x faster")
        print("  This should help with rate limiting")
    else:
        print(f"\n⚠ LIMITED: Batch fetching only {speedup_first:.1f}x faster")
        print("  May need additional optimization")
    
    print("\nFor overnight scans:")
    print("  - First sector: Uses batch fetching (some API calls)")
    print("  - Subsequent sectors: Reuses cache (minimal API calls)")
    print("  - After 30 min: Cache refreshes automatically")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


def test_full_sector_scan():
    """
    Test a full sector scan with batch fetching
    """
    print("\n" + "="*80)
    print("FULL SECTOR SCAN TEST (Financials)")
    print("="*80 + "\n")
    
    scanner = StockScanner(use_batch_fetching=True)
    
    start_time = time.time()
    results = scanner.scan_sector('Financials', top_n=10)
    scan_time = time.time() - start_time
    
    print(f"\nScan Results:")
    print(f"  Time taken: {scan_time:.2f}s")
    print(f"  Valid stocks: {len(results)}")
    
    if results:
        print(f"\nTop 5 stocks:")
        for i, stock in enumerate(results[:5], 1):
            print(f"  {i}. {stock['symbol']:8s} | Score: {stock['score']:5.1f} | "
                  f"Price: ${stock['price']:7.2f} | "
                  f"Market Cap: ${stock['market_cap']/1e9:.2f}B")
        
        summary = scanner.get_sector_summary(results)
        print(f"\nSector Summary:")
        print(f"  Average Score: {summary['avg_score']:.1f}")
        print(f"  Max Score:     {summary['max_score']:.1f}")
        print(f"  Top Stock:     {summary['top_stock']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        # Run comparison test
        test_batch_vs_individual()
        
        # Run full sector test
        print("\n\nProceed to full sector test? (y/n): ", end='')
        response = input().strip().lower()
        if response == 'y':
            test_full_sector_scan()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise

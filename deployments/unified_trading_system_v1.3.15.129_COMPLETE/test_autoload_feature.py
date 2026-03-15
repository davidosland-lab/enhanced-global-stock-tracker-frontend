"""
Test Auto-Load Pipeline Stocks Feature

This script tests the new dashboard feature that auto-loads
top 50 stocks from pipeline reports.

Feature: v1.3.15.164
Purpose: User requested ability to automatically load top stocks
         from overnight pipeline runs into the dashboard.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pipeline_report_loader import auto_load_pipeline_stocks

def test_autoload():
    """Test the auto-load feature"""
    
    print("\n" + "="*80)
    print("AUTO-LOAD PIPELINE STOCKS TEST")
    print("="*80 + "\n")
    
    # Test 1: Load top 50 from all markets
    print("Test 1: Load Top 50 (all markets)")
    print("-" * 80)
    
    symbols, metadata = auto_load_pipeline_stocks(
        top_n=50,
        markets=['AU', 'UK', 'US'],
        min_confidence=60.0,
        max_age_hours=48
    )
    
    if symbols:
        print(f"✓ Loaded {len(symbols)} symbols")
        
        # Count by market
        au_count = sum(1 for s in symbols if s.endswith('.AX'))
        uk_count = sum(1 for s in symbols if s.endswith('.L'))
        us_count = len(symbols) - au_count - uk_count
        
        print(f"  AU: {au_count} stocks")
        print(f"  UK: {uk_count} stocks")
        print(f"  US: {us_count} stocks")
        print()
        
        # Show symbols (comma-separated, ready for dashboard)
        symbols_str = ','.join(symbols)
        print("Symbols (dashboard format):")
        print(symbols_str)
        print()
    else:
        print("✗ No symbols loaded")
        print("  Check metadata:")
        for market, info in metadata.items():
            print(f"  {market}: {info}")
        print()
    
    # Test 2: Load top 20 from AU only
    print("\nTest 2: Load Top 20 (AU only)")
    print("-" * 80)
    
    symbols_au, metadata_au = auto_load_pipeline_stocks(
        top_n=20,
        markets=['AU'],
        min_confidence=60.0,
        max_age_hours=999999  # Accept any age for testing
    )
    
    if symbols_au:
        print(f"✓ Loaded {len(symbols_au)} AU symbols")
        print(f"  Symbols: {', '.join(symbols_au[:10])}{'...' if len(symbols_au) > 10 else ''}")
    else:
        print("✗ No AU symbols loaded")
    
    print()
    
    # Test 3: Show metadata
    print("\nTest 3: Report Metadata")
    print("-" * 80)
    
    for market, info in metadata.items():
        print(f"{market}:")
        if info.get('report_found'):
            print(f"  ✓ Report found (age: {info.get('report_age_hours', 0):.1f}h)")
            print(f"  Stocks: {info.get('stocks_loaded', 0)}/{info.get('stocks_total', 0)}")
        else:
            print(f"  ✗ {info.get('error', 'Unknown error')}")
    
    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    return symbols, metadata


if __name__ == "__main__":
    test_autoload()

"""
Data Collection Status Checker

Monitors Parquet data storage across all regions (US, UK, AU).
Run daily to verify data is being collected properly.

Usage:
    python scripts/check_data_collection.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.data_storage import ParquetTradeStore

def check_collection_status():
    """Check data collection status across all regions"""
    
    regions = ['us', 'uk']  # AU pipeline not present yet
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n{'='*80}")
    print(f"DATA COLLECTION STATUS - {today}")
    print(f"{'='*80}\n")
    
    all_good = True
    
    for region in regions:
        data_path = Path(f'data/{region}/trades')
        
        print(f"{region.upper()} Region:")
        print("-" * 40)
        
        if not data_path.exists():
            print(f"  ⚠️  No data directory found")
            print(f"     Run {region.upper()} pipeline to start collection")
            all_good = False
        else:
            try:
                store = ParquetTradeStore(f'data/{region}/trades')
                stats = store.get_storage_stats()
                
                if stats['total_symbols'] == 0:
                    print(f"  ⚠️  No data collected yet")
                    print(f"     Run {region.upper()} pipeline to start collection")
                    all_good = False
                else:
                    print(f"  [OK] Data collection active")
                    print(f"     Symbols: {stats['total_symbols']}")
                    print(f"     Files: {stats['total_files']}")
                    print(f"     Size: {stats['total_size_mb']:.2f} MB")
                    
                    # Show first 10 symbols
                    symbols = stats['symbols'][:10]
                    more = '...' if len(stats['symbols']) > 10 else ''
                    print(f"     Symbols: {', '.join(symbols)}{more}")
                    
                    # Check if data is recent
                    try:
                        # Try to get latest date for a symbol
                        if symbols:
                            min_date, max_date = store.get_date_range(symbols[0])
                            days_old = (today - max_date).days
                            
                            if days_old == 0:
                                print(f"     [OK] Latest data: TODAY ({max_date})")
                            elif days_old == 1:
                                print(f"     ⚠️  Latest data: YESTERDAY ({max_date})")
                                print(f"        Run pipeline to update")
                            else:
                                print(f"     ⚠️  Latest data: {days_old} days old ({max_date})")
                                print(f"        Run pipeline to update")
                                all_good = False
                    except:
                        pass
                
            except Exception as e:
                print(f"  ❌ Error reading data: {e}")
                all_good = False
        
        print()
    
    print("="*80)
    
    if all_good:
        print("[OK] All regions collecting data properly")
    else:
        print("⚠️  Some regions need attention - see details above")
    
    print("="*80)
    print()
    
    print("📋 NEXT STEPS:")
    print("  1. Run pipelines to collect/update data:")
    print("     • US: python scripts/run_us_full_pipeline.py --test-mode")
    print("     • UK: python scripts/run_uk_full_pipeline.py --test-mode")
    print()
    print("  2. After 3-7 days, generate baseline report:")
    print("     python scripts/generate_baseline_report.py us")
    print()
    print("  3. View this status daily to monitor collection")
    print()


if __name__ == '__main__':
    try:
        check_collection_status()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

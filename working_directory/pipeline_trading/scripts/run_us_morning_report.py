"""
US Morning Report Runner
========================

Runs the US (NYSE/NASDAQ) overnight screening pipeline
and generates morning report before market open.

Usage:
    python run_us_morning_report.py

Schedule:
    Run daily at 08:00 EST (before 09:30 market open)

Output:
    - Report: pipeline_trading/reports/us/morning_report_YYYYMMDD.html
    - Log: pipeline_trading/logs/screening/us/pipeline_YYYYMMDD.log
"""

import sys
from pathlib import Path

# Add parent directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'models'))

from models.screening.us_overnight_pipeline import USOvernightPipeline

def main():
    """Run US morning report"""
    print("=" * 80)
    print("US MORNING REPORT GENERATOR")
    print("=" * 80)
    print("Markets: NYSE, NASDAQ")
    print("Timezone: EST (America/New_York)")
    print("=" * 80)
    print()
    
    try:
        # Initialize and run pipeline
        pipeline = USOvernightPipeline()
        results = pipeline.run()
        
        print()
        print("=" * 80)
        print("US MORNING REPORT COMPLETE")
        print("=" * 80)
        print(f"Status: {results.get('status', 'Unknown')}")
        print(f"Stocks Scanned: {results.get('stocks_scanned', 0)}")
        print(f"Top Opportunities: {len(results.get('top_opportunities', []))}")
        print(f"Report: {results.get('report_path', 'N/A')}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR: US Morning Report Failed")
        print("=" * 80)
        print(f"Error: {e}")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())

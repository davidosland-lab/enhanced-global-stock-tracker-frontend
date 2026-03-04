"""
UK Morning Report Runner
========================

Runs the UK (LSE) overnight screening pipeline
and generates morning report before market open.

Usage:
    python run_uk_morning_report.py

Schedule:
    Run daily at 07:00 GMT (before 08:00 market open)

Output:
    - Report: pipeline_trading/reports/uk/morning_report_YYYYMMDD.html
    - Log: pipeline_trading/logs/screening/uk/pipeline_YYYYMMDD.log
"""

import sys
from pathlib import Path

# Add parent directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'models'))

from models.screening.uk_overnight_pipeline import UKOvernightPipeline

def main():
    """Run UK morning report"""
    print("=" * 80)
    print("UK MORNING REPORT GENERATOR")
    print("=" * 80)
    print("Market: London Stock Exchange (LSE)")
    print("Timezone: GMT (Europe/London)")
    print("=" * 80)
    print()
    
    try:
        # Initialize and run pipeline
        pipeline = UKOvernightPipeline()
        results = pipeline.run()
        
        print()
        print("=" * 80)
        print("UK MORNING REPORT COMPLETE")
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
        print("ERROR: UK Morning Report Failed")
        print("=" * 80)
        print(f"Error: {e}")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())

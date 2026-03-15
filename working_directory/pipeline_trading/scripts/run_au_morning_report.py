"""
AU Morning Report Runner
========================

Runs the Australian (ASX) overnight screening pipeline
and generates morning report before market open.

Usage:
    python run_au_morning_report.py

Schedule:
    Run daily at 09:00 AEDT (before 10:00 market open)

Output:
    - Report: pipeline_trading/reports/au/morning_report_YYYYMMDD.html
    - Log: pipeline_trading/logs/screening/au/pipeline_YYYYMMDD.log
"""

import sys
from pathlib import Path

# Add parent directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'models'))

from models.screening.overnight_pipeline import OvernightPipeline

def main():
    """Run AU morning report"""
    print("=" * 80)
    print("AU MORNING REPORT GENERATOR")
    print("=" * 80)
    print("Market: Australian Securities Exchange (ASX)")
    print("Timezone: AEDT (Australia/Sydney)")
    print("=" * 80)
    print()
    
    try:
        # Initialize and run pipeline
        pipeline = OvernightPipeline()
        results = pipeline.run()
        
        print()
        print("=" * 80)
        print("AU MORNING REPORT COMPLETE")
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
        print("ERROR: AU Morning Report Failed")
        print("=" * 80)
        print(f"Error: {e}")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())

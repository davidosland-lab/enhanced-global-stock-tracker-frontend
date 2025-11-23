#!/usr/bin/env python3
"""
Event Risk Guard - Overnight Pipeline Runner
Wrapper script to properly run the overnight pipeline with correct Python imports
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run the pipeline
from models.screening.overnight_pipeline import OvernightPipeline

if __name__ == "__main__":
    print("=" * 80)
    print("Event Risk Guard - Overnight Screening Pipeline")
    print("=" * 80)
    print()
    print("Starting overnight pipeline with Event Risk Guard enabled...")
    print()
    print("Pipeline phases:")
    print("  1. Market Sentiment Analysis (SPI 200)")
    print("  2. Stock Scanning (ASX stocks)")
    print("  3. Event Risk Assessment (Basel III, earnings, dividends)")
    print("  4. Prediction Generation (LSTM + FinBERT)")
    print("  5. Opportunity Scoring")
    print("  6. Report Generation + CSV Export")
    print()
    print("Reports will be saved to:")
    print("  - reports/html/ (HTML reports)")
    print("  - reports/csv/ (CSV exports with event risk data)")
    print()
    
    try:
        pipeline = OvernightPipeline()
        results = pipeline.run_full_pipeline()
        
        print()
        print("=" * 80)
        print("Pipeline Complete!")
        print("=" * 80)
        print()
        print("Check the following directories:")
        print("  reports/html/ - HTML morning reports")
        print("  reports/csv/ - CSV exports (full results + event risk summary)")
        print("  logs/screening/ - Execution logs")
        print()
        
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

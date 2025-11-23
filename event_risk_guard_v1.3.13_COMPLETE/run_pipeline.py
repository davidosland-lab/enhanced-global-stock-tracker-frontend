#!/usr/bin/env python3
"""
Event Risk Guard - Pipeline Runner
Main entry point for running the overnight screening pipeline.

Usage:
    python run_pipeline.py          # Run full pipeline
    python run_pipeline.py --test   # Run in test mode (single stock)
"""

import sys
import os
from pathlib import Path

# Add models directory to Python path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH))

# Import and run pipeline
from models.screening.overnight_pipeline import OvernightPipeline

def main():
    """Run the overnight screening pipeline"""
    print("="*80)
    print("EVENT RISK GUARD - OVERNIGHT SCREENING PIPELINE")
    print("="*80)
    print()
    
    # Check for test mode
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("[TEST MODE] Running with limited stocks...")
        print()
    
    # Initialize and run pipeline
    try:
        pipeline = OvernightPipeline()
        
        # Determine sectors to scan (test mode or full)
        sectors = None  # None = all sectors
        stocks_per_sector = 30 if not test_mode else 5
        
        # Run the pipeline
        results = pipeline.run_full_pipeline(sectors=sectors, stocks_per_sector=stocks_per_sector)
        
        print()
        print("="*80)
        print("PIPELINE COMPLETE")
        print("="*80)
        print()
        print(f"Status: {results.get('status', 'unknown')}")
        print(f"Opportunities found: {results.get('opportunities_count', 0)}")
        print(f"LSTM models trained: {results.get('lstm_trained', 0)}")
        print(f"Report saved: {results.get('report_path', 'N/A')}")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user")
        return 1
        
    except Exception as e:
        print(f"\n\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

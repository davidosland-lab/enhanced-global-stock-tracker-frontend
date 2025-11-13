"""
Overnight Pipeline Runner
Wrapper script to run the overnight pipeline with proper imports
"""

import sys
import os
from pathlib import Path

# Add models/screening to Python path
script_dir = Path(__file__).parent
screening_dir = script_dir / 'models' / 'screening'
sys.path.insert(0, str(screening_dir))

# Now import and run the pipeline
if __name__ == "__main__":
    print("="*80)
    print("FINBERT v4.4.4 - OVERNIGHT PREDICTION PIPELINE")
    print("="*80)
    print()
    print("Full System Features:")
    print("  - LSTM Neural Network Predictions (45% weight)")
    print("  - FinBERT Sentiment Analysis (15% weight)")
    print("  - Trend Analysis (25% weight)")
    print("  - Technical Analysis (15% weight)")
    print("  - SPI 200 Futures Monitoring")
    print("  - US Market Data Integration")
    print()
    print("This will run comprehensive overnight analysis")
    print("Results will include ML predictions and sentiment scores")
    print()
    print("="*80)
    print()
    
    try:
        # Import the overnight pipeline module
        from overnight_pipeline import OvernightPipeline, main
        
        # Run the main function
        main()
        
    except ImportError as e:
        print(f"ERROR: Import failed - {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure all dependencies are installed:")
        print("     pip install yahooquery pandas numpy yfinance pytz")
        print()
        print("  2. For full ML features, install:")
        print("     pip install tensorflow keras transformers torch")
        print()
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Pipeline failed - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

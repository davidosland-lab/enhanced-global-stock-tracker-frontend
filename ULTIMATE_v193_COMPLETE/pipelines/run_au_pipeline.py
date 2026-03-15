"""
Australian Market Overnight Pipeline Runner
Uses shared FinBERT v4.4.4 virtual environment

Phases:
1. Market Sentiment (SPI futures, US overnight)
2. Stock Scanning (8 sectors x 30 stocks = 240 stocks)
3. Event Risk Assessment (Basel III, earnings, dividends)
4. Batch Prediction (FinBERT + LSTM)
5. Opportunity Scoring (14-factor scoring)
6. Report Generation (JSON + CSV + Email)

Expected Runtime: 15-25 minutes
"""

import sys
import os
from pathlib import Path

# Add shared FinBERT venv to path
BASE_DIR = Path(__file__).parent.parent
FINBERT_VENV = BASE_DIR / 'finbert_v4.4.4' / 'venv'

# Add venv site-packages to sys.path (cross-platform)
if FINBERT_VENV.exists():
    if sys.platform == 'win32':
        site_packages = FINBERT_VENV / 'Lib' / 'site-packages'
    else:
        # Find python version dynamically
        lib_dir = FINBERT_VENV / 'lib'
        if lib_dir.exists():
            python_dirs = list(lib_dir.glob('python*'))
            if python_dirs:
                site_packages = python_dirs[0] / 'site-packages'
            else:
                site_packages = None
        else:
            site_packages = None
    
    if site_packages and site_packages.exists():
        sys.path.insert(0, str(site_packages))
        print(f"[OK] Using FinBERT venv: {site_packages}")
    else:
        print(f"[WARNING] FinBERT venv site-packages not found, using system Python")
else:
    print(f"[WARNING] FinBERT venv not found at {FINBERT_VENV}, using system Python")

# Add models directory to path
MODELS_DIR = BASE_DIR / 'pipelines' / 'models'
sys.path.insert(0, str(MODELS_DIR))

# Create required directories BEFORE importing pipeline modules
REQUIRED_DIRS = [
    BASE_DIR / 'logs',
    BASE_DIR / 'logs' / 'screening',
    BASE_DIR / 'logs' / 'screening' / 'errors',
    BASE_DIR / 'pipelines' / 'logs',
    BASE_DIR / 'reports',
    BASE_DIR / 'reports' / 'screening',
    BASE_DIR / 'data',
]

for directory in REQUIRED_DIRS:
    directory.mkdir(parents=True, exist_ok=True)

print(f"[OK] Created required directories")

# Now import pipeline modules
from screening.overnight_pipeline import OvernightPipeline
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for Australian market overnight pipeline"""
    parser = argparse.ArgumentParser(
        description='Australian Market Overnight Screening Pipeline'
    )
    parser.add_argument(
        '--sectors',
        nargs='+',
        help='Sectors to scan (default: all 8 sectors)'
    )
    parser.add_argument(
        '--stocks-per-sector',
        type=int,
        default=30,
        help='Number of stocks per sector (default: 30)'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'test'],
        default='full',
        help='Execution mode: full (all sectors) or test (Financials only, 5 stocks)'
    )
    parser.add_argument(
        '--full-scan',
        action='store_true',
        help='Force full scan (all sectors)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000,
        help='Initial capital in AUD (default: 100000)'
    )
    parser.add_argument(
        '--ignore-market-hours',
        action='store_true',
        help='Run pipeline even outside market hours'
    )
    
    args = parser.parse_args()
    
    # Display banner
    print("="*80)
    print("AUSTRALIAN MARKET OVERNIGHT PIPELINE - v1.3.15.87")
    print("="*80)
    print(f"Mode: {args.mode.upper()}")
    print(f"Initial Capital: USD{args.capital:,.2f} AUD")
    print(f"Using FinBERT v4.4.4 shared environment")
    print("="*80)
    print()
    
    try:
        # Initialize pipeline
        pipeline = OvernightPipeline()
        
        # Run appropriate mode
        if args.mode == 'test' or (not args.full_scan and args.sectors is None):
            logger.info("Running in TEST mode (Financials sector, 5 stocks)")
            results = pipeline.run_full_pipeline(
                sectors=['Financials'],
                stocks_per_sector=5
            )
        else:
            logger.info(f"Running in FULL mode")
            if args.sectors:
                logger.info(f"Selected sectors: {', '.join(args.sectors)}")
            else:
                logger.info(f"Scanning all 8 sectors")
            
            results = pipeline.run_full_pipeline(
                sectors=args.sectors,
                stocks_per_sector=args.stocks_per_sector
            )
        
        # Print summary
        print("\n" + "="*80)
        print("AUSTRALIAN PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Status: {results['status'].upper()}")
        print(f"Execution Time: {results['execution_time_minutes']:.1f} minutes")
        print(f"Stocks Scanned: {results['statistics']['total_stocks_scanned']}")
        print(f"Top Opportunities: {results['statistics']['top_opportunities_count']}")
        print(f"Buy Signals: {results['statistics']['buy_signals']}")
        print(f"Sell Signals: {results['statistics']['sell_signals']}")
        print(f"Market Sentiment: {results['market_sentiment']['score']:.1f}/100")
        print(f"Report: {results['report_path']}")
        if results.get('csv_paths', {}).get('full_results'):
            print(f"CSV Export: {results['csv_paths']['full_results']}")
        print("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

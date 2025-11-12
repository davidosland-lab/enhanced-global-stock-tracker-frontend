#!/usr/bin/env python3
"""
Overnight Stock Screener - Main Orchestration Script

Runs the complete overnight stock screening workflow:
1. Validate configuration
2. Get SPI market sentiment
3. Scan all sectors for valid stocks
4. Generate ensemble predictions
5. Score and rank opportunities
6. Generate morning report
7. Save results and logs

This script is designed to be run overnight (10 PM - 7 AM) either manually
or via Windows Task Scheduler.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pytz
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.screening import (
    StockScanner,
    SPIMonitor,
    BatchPredictor,
    OpportunityScorer,
    ReportGenerator
)

# Setup logging
def setup_logging(log_dir: str = None):
    """Setup logging configuration"""
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs" / "screening"
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log filename with date
    log_file = log_dir / f"overnight_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


class OvernightScreener:
    """
    Main orchestrator for overnight stock screening workflow
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Overnight Screener
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "models" / "config" / "screening_config.json"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = setup_logging()
        self.timezone = pytz.timezone(self.config['schedule']['timezone'])
        
        # Initialize components
        self.scanner = None
        self.spi_monitor = None
        self.predictor = None
        self.scorer = None
        self.report_generator = None
        
        # Results storage
        self.results = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': None,
            'spi_sentiment': None,
            'scanned_stocks': [],
            'predicted_stocks': [],
            'scored_opportunities': [],
            'top_opportunities': [],
            'report_path': None,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
    
    def _load_config(self) -> Dict:
        """Load screening configuration with validation"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate required top-level keys
            required_keys = ['schedule', 'screening', 'spi_monitoring', 'scoring', 'reporting']
            missing = [k for k in required_keys if k not in config]
            if missing:
                raise ValueError(f"Missing required config keys: {missing}")
            
            # Validate required nested keys
            if 'timezone' not in config['schedule']:
                raise ValueError("Missing 'schedule.timezone' in config")
            if 'ensemble_weights' not in config['screening']:
                raise ValueError("Missing 'screening.ensemble_weights' in config")
            if 'weights' not in config['scoring']:
                raise ValueError("Missing 'scoring.weights' in config")
            
            return config
        except Exception as e:
            print(f"ERROR: Failed to load or validate config: {e}")
            sys.exit(1)
    
    def run(self, sectors: List[str] = None, test_mode: bool = False):
        """
        Run complete overnight screening workflow
        
        Args:
            sectors: List of sectors to scan (default: all)
            test_mode: If True, scan only first 5 stocks per sector
        """
        self.logger.info("="*80)
        self.logger.info("OVERNIGHT STOCK SCREENER - Starting")
        self.logger.info("="*80)
        
        self.results['start_time'] = datetime.now(self.timezone).isoformat()
        
        try:
            # Step 1: Initialize components
            self._initialize_components()
            
            # Step 2: Get SPI market sentiment
            self._get_market_sentiment()
            
            # Step 3: Scan stocks
            self._scan_stocks(sectors, test_mode)
            
            # Step 4: Generate predictions
            self._generate_predictions()
            
            # Step 5: Score opportunities
            self._score_opportunities()
            
            # Step 6: Generate report
            self._generate_report()
            
            # Step 7: Save results
            self._save_results()
            
            # Calculate statistics
            self._calculate_statistics()
            
            self.logger.info("="*80)
            self.logger.info("✓ OVERNIGHT SCREENER COMPLETE")
            self.logger.info("="*80)
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"✗ Fatal error in overnight screener: {e}", exc_info=True)
            self.results['errors'].append(str(e))
            raise
        
        finally:
            self.results['end_time'] = datetime.now(self.timezone).isoformat()
            if self.results['start_time']:
                start = datetime.fromisoformat(self.results['start_time'])
                end = datetime.fromisoformat(self.results['end_time'])
                self.results['duration_seconds'] = (end - start).total_seconds()
    
    def _initialize_components(self):
        """Initialize all screening components"""
        self.logger.info("\nStep 1: Initializing components...")
        
        try:
            self.scanner = StockScanner()
            self.logger.info("  ✓ Stock Scanner initialized")
            
            self.spi_monitor = SPIMonitor()
            self.logger.info("  ✓ SPI Monitor initialized")
            
            self.predictor = BatchPredictor()
            self.logger.info("  ✓ Batch Predictor initialized")
            
            self.scorer = OpportunityScorer()
            self.logger.info("  ✓ Opportunity Scorer initialized")
            
            self.report_generator = ReportGenerator()
            self.logger.info("  ✓ Report Generator initialized")
            
        except Exception as e:
            self.logger.error(f"  ✗ Initialization failed: {e}")
            raise
    
    def _get_market_sentiment(self):
        """Get SPI market sentiment and US market data"""
        self.logger.info("\nStep 2: Getting market sentiment...")
        
        try:
            sentiment = self.spi_monitor.get_overnight_summary()
            self.results['spi_sentiment'] = sentiment
            
            self.logger.info(f"  ✓ Sentiment Score: {sentiment['sentiment_score']:.1f}/100")
            self.logger.info(f"  ✓ Gap Prediction: {sentiment['gap_prediction']['predicted_gap_pct']:+.2f}%")
            self.logger.info(f"  ✓ Direction: {sentiment['gap_prediction']['direction'].upper()}")
            
        except Exception as e:
            self.logger.error(f"  ✗ Failed to get sentiment: {e}")
            self.results['warnings'].append(f"SPI sentiment unavailable: {e}")
            self.results['spi_sentiment'] = None
    
    def _scan_stocks(self, sectors: List[str] = None, test_mode: bool = False):
        """Scan stocks from all sectors with optional parallel processing"""
        self.logger.info("\nStep 3: Scanning stocks...")
        
        # Determine sectors to scan
        if sectors is None:
            sectors = list(self.scanner.sectors.keys())
        
        self.logger.info(f"  Sectors to scan: {', '.join(sectors)}")
        if test_mode:
            self.logger.info("  ⚠ TEST MODE: Scanning only first 5 stocks per sector")
        
        # Get number of stocks per sector from config
        top_n = 5 if test_mode else self.config['screening'].get('stocks_per_sector', 30)
        
        # Check if parallel processing is enabled
        use_parallel = self.config.get('performance', {}).get('parallel_processing', False)
        max_workers = self.config.get('performance', {}).get('max_workers', 4)
        
        all_stocks = []
        
        if use_parallel and len(sectors) > 1:
            # Parallel sector scanning
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            self.logger.info(f"  Using parallel processing with {max_workers} workers")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all sector scanning jobs
                future_to_sector = {
                    executor.submit(self._scan_single_sector, sector_name, top_n): sector_name
                    for sector_name in sectors
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_sector):
                    sector_name = future_to_sector[future]
                    try:
                        stocks = future.result()
                        all_stocks.extend(stocks)
                        self.logger.info(f"  ✓ {sector_name}: {len(stocks)} valid stocks")
                    except Exception as e:
                        self.logger.error(f"  ✗ {sector_name} failed: {e}")
                        self.results['warnings'].append(f"Sector {sector_name} failed: {e}")
        else:
            # Sequential sector scanning (original behavior)
            if use_parallel:
                self.logger.info("  Only 1 sector - using sequential processing")
            
            for sector_name in sectors:
                try:
                    self.logger.info(f"\n  Scanning {sector_name}...")
                    stocks = self._scan_single_sector(sector_name, top_n)
                    all_stocks.extend(stocks)
                    self.logger.info(f"    ✓ Found {len(stocks)} valid stocks")
                except Exception as e:
                    self.logger.error(f"  ✗ Error scanning {sector_name}: {e}")
                    self.results['warnings'].append(f"Sector {sector_name} failed: {e}")
        
        self.results['scanned_stocks'] = all_stocks
        self.logger.info(f"\n  ✓ Total stocks scanned: {len(all_stocks)}")
    
    def _scan_single_sector(self, sector_name: str, top_n: int) -> List[Dict]:
        """
        Scan a single sector for stocks
        Helper method for parallel processing
        
        Args:
            sector_name: Name of the sector to scan
            top_n: Number of top stocks to scan
            
        Returns:
            List of stock dictionaries
        """
        return self.scanner.scan_sector(sector_name, top_n=top_n)
    
    def _generate_predictions(self):
        """Generate ensemble predictions for all stocks"""
        self.logger.info("\nStep 4: Generating predictions...")
        
        if not self.results['scanned_stocks']:
            self.logger.warning("  ⚠ No stocks to predict")
            return
        
        try:
            predicted_stocks = self.predictor.predict_batch(
                self.results['scanned_stocks'],
                self.results['spi_sentiment']
            )
            
            self.results['predicted_stocks'] = predicted_stocks
            
            # Summary
            summary = self.predictor.get_prediction_summary(predicted_stocks)
            self.logger.info(f"  ✓ Predictions generated: {summary['total']}")
            self.logger.info(f"    BUY: {summary['buy_count']} | SELL: {summary['sell_count']} | HOLD: {summary['hold_count']}")
            self.logger.info(f"    Avg Confidence: {summary['avg_confidence']:.1f}%")
            
        except Exception as e:
            self.logger.error(f"  ✗ Prediction failed: {e}", exc_info=True)
            self.results['errors'].append(f"Prediction failed: {e}")
            self.results['predicted_stocks'] = []
            self.logger.warning("  ⚠ Continuing with empty predictions (report will show scanned stocks only)")
            # Don't raise - allow workflow to continue with partial results
    
    def _score_opportunities(self):
        """Score and rank all opportunities"""
        self.logger.info("\nStep 5: Scoring opportunities...")
        
        if not self.results['predicted_stocks']:
            self.logger.warning("  ⚠ No predictions to score")
            return
        
        try:
            scored_stocks = self.scorer.score_opportunities(
                self.results['predicted_stocks'],
                self.results['spi_sentiment']
            )
            
            self.results['scored_opportunities'] = scored_stocks
            
            # Filter top opportunities
            top_opportunities = self.scorer.filter_top_opportunities(scored_stocks)
            self.results['top_opportunities'] = top_opportunities
            
            # Summary
            summary = self.scorer.get_opportunity_summary(scored_stocks)
            self.logger.info(f"  ✓ Opportunities scored: {summary['total']}")
            self.logger.info(f"    High (≥80): {summary['high_opportunity_count']}")
            self.logger.info(f"    Medium (65-80): {summary['medium_opportunity_count']}")
            self.logger.info(f"    Avg Score: {summary['avg_score']:.1f}/100")
            
            if top_opportunities:
                self.logger.info(f"\n  Top 3 Opportunities:")
                for i, opp in enumerate(top_opportunities[:3], 1):
                    self.logger.info(f"    {i}. {opp['symbol']}: {opp['opportunity_score']:.1f}/100 ({opp['prediction']})")
            
        except Exception as e:
            self.logger.error(f"  ✗ Scoring failed: {e}")
            self.results['errors'].append(f"Scoring failed: {e}")
            raise
    
    def _generate_report(self):
        """Generate HTML morning report"""
        self.logger.info("\nStep 6: Generating morning report...")
        
        if not self.results['scored_opportunities']:
            self.logger.warning("  ⚠ No opportunities to report")
            return
        
        try:
            # Build sector_summary from scanned stocks
            sector_summary = {}
            
            # Group stocks by sector
            sector_stocks = {}
            for stock in self.results['scanned_stocks']:
                # Extract sector from stock data (if available)
                sector = stock.get('sector', 'Unknown')
                if sector not in sector_stocks:
                    sector_stocks[sector] = []
                sector_stocks[sector].append(stock)
            
            # Calculate sector summaries
            for sector_name, stocks in sector_stocks.items():
                scores = [s.get('score', 0) for s in stocks if s.get('score')]
                sector_summary[sector_name] = {
                    'total_stocks': len(stocks),
                    'avg_score': sum(scores) / len(scores) if scores else 0,
                    'stocks_with_predictions': len([s for s in stocks if 'prediction' in s])
                }
            
            # Build system_stats
            # Get actual cache statistics from data fetcher
            cache_stats = {}
            if self.scanner and self.scanner.data_fetcher:
                cache_stats = self.scanner.data_fetcher.get_cache_stats()
            
            system_stats = {
                'total_stocks_scanned': len(self.results['scanned_stocks']),
                'total_predictions': len(self.results['predicted_stocks']),
                'total_opportunities': len(self.results['scored_opportunities']),
                'api_calls_used': cache_stats.get('api_calls_today', 0),
                'api_limit': cache_stats.get('api_limit', 500),
                'cache_hit_rate': cache_stats.get('cache_hit_rate', 0.0),
                'cache_hits': cache_stats.get('cache_hits', 0),
                'cache_misses': cache_stats.get('cache_misses', 0),
                'execution_time_seconds': (
                    (datetime.now(self.timezone) - datetime.fromisoformat(self.results['start_time'])).total_seconds()
                    if self.results['start_time'] else 0
                )
            }
            
            # Generate report with all required parameters
            report_path = self.report_generator.generate_morning_report(
                opportunities=self.results['scored_opportunities'],
                spi_sentiment=self.results['spi_sentiment'],
                sector_summary=sector_summary,
                system_stats=system_stats
            )
            
            self.results['report_path'] = report_path
            self.logger.info(f"  ✓ Report generated: {report_path}")
            self.logger.info(f"  ✓ API Calls Used: {system_stats['api_calls_used']}/{system_stats['api_limit']}")
            
        except Exception as e:
            self.logger.error(f"  ✗ Report generation failed: {e}")
            self.results['errors'].append(f"Report generation failed: {e}")
            # Don't raise - report is not critical
    
    def _save_results(self):
        """Save results to JSON file"""
        self.logger.info("\nStep 7: Saving results...")
        
        try:
            # Create results directory
            results_dir = Path(__file__).parent.parent.parent / "reports" / "screening_results"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now(self.timezone).strftime('%Y%m%d_%H%M%S')
            results_file = results_dir / f"screening_results_{timestamp}.json"
            
            # Prepare simplified results (remove large objects)
            simple_results = {
                'start_time': self.results['start_time'],
                'end_time': self.results['end_time'],
                'duration_seconds': self.results['duration_seconds'],
                'spi_sentiment': self.results['spi_sentiment'],
                'report_path': self.results['report_path'],
                'statistics': self.results.get('statistics', {}),
                'errors': self.results['errors'],
                'warnings': self.results['warnings'],
                'top_opportunities': [
                    {
                        'symbol': o['symbol'],
                        'name': o['name'],
                        'opportunity_score': o['opportunity_score'],
                        'prediction': o['prediction'],
                        'confidence': o['confidence']
                    }
                    for o in self.results['top_opportunities'][:10]
                ]
            }
            
            # Save to file
            with open(results_file, 'w') as f:
                json.dump(simple_results, f, indent=2)
            
            self.logger.info(f"  ✓ Results saved: {results_file}")
            
        except Exception as e:
            self.logger.error(f"  ✗ Failed to save results: {e}")
            self.results['warnings'].append(f"Results save failed: {e}")
    
    def _calculate_statistics(self):
        """Calculate final statistics"""
        stats = {
            'total_stocks_scanned': len(self.results['scanned_stocks']),
            'total_predictions': len(self.results['predicted_stocks']),
            'total_opportunities': len(self.results['scored_opportunities']),
            'top_opportunities_count': len(self.results['top_opportunities']),
            'buy_signals': len([s for s in self.results['predicted_stocks'] if s.get('prediction') == 'BUY']),
            'sell_signals': len([s for s in self.results['predicted_stocks'] if s.get('prediction') == 'SELL']),
            'hold_signals': len([s for s in self.results['predicted_stocks'] if s.get('prediction') == 'HOLD']),
            'error_count': len(self.results['errors']),
            'warning_count': len(self.results['warnings'])
        }
        
        if self.results['scored_opportunities']:
            scores = [s['opportunity_score'] for s in self.results['scored_opportunities']]
            stats['avg_opportunity_score'] = sum(scores) / len(scores)
            stats['max_opportunity_score'] = max(scores)
            stats['min_opportunity_score'] = min(scores)
        
        self.results['statistics'] = stats


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Overnight Stock Screener')
    parser.add_argument('--test', action='store_true', help='Test mode (scan only 5 stocks per sector)')
    parser.add_argument('--sectors', nargs='+', help='Specific sectors to scan')
    parser.add_argument('--config', type=str, help='Path to screening_config.json')
    
    args = parser.parse_args()
    
    # Run screener
    screener = OvernightScreener(config_path=args.config)
    
    try:
        results = screener.run(sectors=args.sectors, test_mode=args.test)
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
        print(f"Stocks Scanned: {results['statistics']['total_stocks_scanned']}")
        print(f"Predictions Generated: {results['statistics']['total_predictions']}")
        print(f"Top Opportunities: {results['statistics']['top_opportunities_count']}")
        print(f"Report: {results['report_path']}")
        print(f"Errors: {results['statistics']['error_count']}")
        print(f"Warnings: {results['statistics']['warning_count']}")
        
        if results['errors']:
            print("\n⚠ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("="*80)
        
        # Exit code
        sys.exit(0 if not results['errors'] else 1)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

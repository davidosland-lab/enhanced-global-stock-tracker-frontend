"""
Overnight Pipeline Orchestrator

Main orchestration module that runs the complete overnight screening workflow.
Coordinates all modules and handles error recovery, progress tracking, and logging.

Workflow:
1. Initialize all components
2. Fetch SPI market sentiment
3. Scan all sectors (240 stocks)
4. Generate batch predictions
5. Score opportunities
6. Generate morning report
7. Save results and logs

Features:
- Complete pipeline orchestration
- Progress tracking and logging
- Error recovery and retry logic
- Time estimation
- Status reporting
- JSON state export
"""

import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import traceback
import pytz

try:
    # Try relative imports first (when used as module)
    from .stock_scanner import StockScanner
    from .spi_monitor import SPIMonitor
    from .batch_predictor import BatchPredictor
    from .opportunity_scorer import OpportunityScorer
    from .report_generator import ReportGenerator
except ImportError:
    # Fall back to absolute imports (when run as script)
    from stock_scanner import StockScanner
    from spi_monitor import SPIMonitor
    from batch_predictor import BatchPredictor
    from opportunity_scorer import OpportunityScorer
    from report_generator import ReportGenerator

# Optional modules (email notifications and LSTM training)
try:
    from .send_notification import EmailNotifier
except ImportError:
    try:
        from send_notification import EmailNotifier
    except ImportError:
        EmailNotifier = None

try:
    from .lstm_trainer import LSTMTrainer
except ImportError:
    try:
        from lstm_trainer import LSTMTrainer
    except ImportError:
        LSTMTrainer = None

# 🆕 Event Risk Guard (optional)
try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    try:
        from event_risk_guard import EventRiskGuard
    except ImportError:
        EventRiskGuard = None

# 🆕 CSV Exporter (optional)
try:
    from .csv_exporter import CSVExporter
except ImportError:
    try:
        from csv_exporter import CSVExporter
    except ImportError:
        CSVExporter = None

# Setup logging with proper path handling
import sys
import os

# Determine base path (go up two levels from this file to reach project root)
if __name__ == "__main__":
    BASE_PATH = Path(__file__).parent.parent.parent
else:
    BASE_PATH = Path(__file__).parent.parent.parent

# Create logs directory
log_dir = BASE_PATH / 'logs' / 'screening'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'overnight_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OvernightPipeline:
    """
    Orchestrates the complete overnight screening pipeline.
    """
    
    def __init__(self):
        """Initialize the pipeline orchestrator"""
        self.timezone = pytz.timezone('Australia/Sydney')
        self.start_time = None
        self.status = {
            'phase': 'initializing',
            'progress': 0,
            'total_stocks': 0,
            'processed_stocks': 0,
            'errors': [],
            'warnings': []
        }
        
        # Initialize components
        logger.info("="*80)
        logger.info("OVERNIGHT STOCK SCREENING PIPELINE - STARTING")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        try:
            self.scanner = StockScanner()
            self.spi_monitor = SPIMonitor()
            self.predictor = BatchPredictor()
            self.scorer = OpportunityScorer()
            self.reporter = ReportGenerator()
            
            # Optional: Email notifications
            if EmailNotifier is not None:
                self.notifier = EmailNotifier()
                logger.info("✓ Email notifications enabled")
            else:
                self.notifier = None
                logger.info("  Email notifications disabled (send_notification module not found)")
            
            # Optional: LSTM training
            if LSTMTrainer is not None:
                self.trainer = LSTMTrainer()
                logger.info("✓ LSTM trainer enabled")
            else:
                self.trainer = None
                logger.info("  LSTM training disabled (lstm_trainer module not found)")
            
            # 🆕 Optional: Event Risk Guard
            if EventRiskGuard is not None:
                self.event_guard = EventRiskGuard()
                logger.info("✓ Event Risk Guard enabled (Basel III, earnings protection)")
            else:
                self.event_guard = None
                logger.info("  Event Risk Guard disabled (event_risk_guard module not found)")
            
            # 🆕 Optional: CSV Exporter
            if CSVExporter is not None:
                self.csv_exporter = CSVExporter()
                logger.info("✓ CSV Exporter enabled (enhanced event risk export)")
            else:
                self.csv_exporter = None
                logger.info("  CSV Exporter disabled (csv_exporter module not found)")
            
            logger.info("✓ All required components initialized successfully")
        except Exception as e:
            logger.error(f"✗ Component initialization failed: {e}")
            raise
    
    def run_full_pipeline(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> Dict:
        """
        Run the complete overnight screening pipeline
        
        Args:
            sectors: List of sector names to scan (None = all sectors)
            stocks_per_sector: Number of stocks to scan per sector
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        self.start_time = time.time()
        
        try:
            # Phase 1: Market Sentiment
            logger.info("\n" + "="*80)
            logger.info("PHASE 1: MARKET SENTIMENT ANALYSIS")
            logger.info("="*80)
            self.status['phase'] = 'market_sentiment'
            self.status['progress'] = 10
            
            spi_sentiment = self._fetch_market_sentiment()
            
            # Phase 2: Stock Scanning
            logger.info("\n" + "="*80)
            logger.info("PHASE 2: STOCK SCANNING")
            logger.info("="*80)
            self.status['phase'] = 'stock_scanning'
            self.status['progress'] = 20
            
            scanned_stocks = self._scan_all_stocks(sectors, stocks_per_sector)
            
            if not scanned_stocks:
                raise Exception("No valid stocks found during scanning")
            
            # 🆕 Phase 2.5: Event Risk Assessment
            logger.info("\n" + "="*80)
            logger.info("PHASE 2.5: EVENT RISK ASSESSMENT")
            logger.info("="*80)
            self.status['phase'] = 'event_risk_assessment'
            self.status['progress'] = 35
            
            event_risk_data = self._assess_event_risks(scanned_stocks)
            
            # Phase 3: Batch Prediction
            logger.info("\n" + "="*80)
            logger.info("PHASE 3: BATCH PREDICTION")
            logger.info("="*80)
            self.status['phase'] = 'prediction'
            self.status['progress'] = 50
            
            predicted_stocks = self._generate_predictions(scanned_stocks, spi_sentiment, event_risk_data)
            
            # Phase 4: Opportunity Scoring
            logger.info("\n" + "="*80)
            logger.info("PHASE 4: OPPORTUNITY SCORING")
            logger.info("="*80)
            self.status['phase'] = 'scoring'
            self.status['progress'] = 70
            
            scored_stocks = self._score_opportunities(predicted_stocks, spi_sentiment)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_report(scored_stocks, spi_sentiment)
            
            # Phase 6: Finalization
            logger.info("\n" + "="*80)
            logger.info("PHASE 6: FINALIZATION")
            logger.info("="*80)
            self.status['phase'] = 'complete'
            self.status['progress'] = 100
            
            results = self._finalize_pipeline(
                scored_stocks=scored_stocks,
                spi_sentiment=spi_sentiment,
                report_path=report_path
            )
            
            elapsed_time = time.time() - self.start_time
            logger.info("\n" + "="*80)
            logger.info("PIPELINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Total Time: {elapsed_time/60:.1f} minutes")
            logger.info(f"Stocks Processed: {len(scanned_stocks)}")
            logger.info(f"Report Generated: {report_path}")
            logger.info(f"End Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            # Send email notifications
            try:
                logger.info("\n" + "="*80)
                logger.info("PHASE 7: EMAIL NOTIFICATIONS")
                logger.info("="*80)
                
                if self.notifier is None:
                    logger.info("  Email notifications disabled (module not available)")
                else:
                    # Send morning report (method already checks if enabled)
                    if self.notifier.enabled:
                        logger.info("Sending morning report email...")
                        self.notifier.send_morning_report(
                            report_path=str(report_path),
                            summary=results.get('summary', {}),
                            top_opportunities=results.get('top_opportunities', [])
                        )
                    
                    # Send alerts for high-confidence opportunities (method already checks if enabled)
                    if self.notifier.enabled:
                        logger.info("Checking for high-confidence opportunities...")
                        self.notifier.send_alert(results.get('top_opportunities', []))
                    
                    logger.info("✓ Email notifications completed")
            except Exception as e:
                logger.warning(f"Email notification failed: {str(e)}")
                # Don't fail the pipeline if emails fail
            
            return results
            
        except Exception as e:
            logger.error(f"\n✗ PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            self.status['phase'] = 'failed'
            self.status['errors'].append(str(e))
            
            # Send error notification
            try:
                if self.notifier is not None and self.notifier.enabled:
                    logger.info("Sending error notification...")
                    self.notifier.send_error(
                        error_message=str(e),
                        error_traceback=traceback.format_exc(),
                        phase=self.status.get('phase', 'unknown')
                    )
            except Exception as email_error:
                logger.warning(f"Failed to send error notification: {str(email_error)}")
            
            # Save error state
            self._save_error_state(e)
            
            raise
    
    def _fetch_market_sentiment(self) -> Dict:
        """Fetch SPI and US market sentiment"""
        logger.info("Fetching market sentiment data...")
        
        try:
            sentiment = self.spi_monitor.get_overnight_summary()
            
            logger.info(f"✓ Market Sentiment Retrieved:")
            logger.info(f"  Sentiment Score: {sentiment['sentiment_score']:.1f}/100")
            logger.info(f"  Gap Prediction: {sentiment['gap_prediction']['predicted_gap_pct']:+.2f}%")
            logger.info(f"  Direction: {sentiment['gap_prediction']['direction'].upper()}")
            logger.info(f"  Recommendation: {sentiment['recommendation']['stance']}")
            
            return sentiment
            
        except Exception as e:
            logger.warning(f"⚠ Market sentiment retrieval failed: {e}")
            logger.warning("Continuing with default sentiment...")
            
            # Return default sentiment
            return {
                'sentiment_score': 50,
                'gap_prediction': {'predicted_gap_pct': 0, 'direction': 'neutral', 'confidence': 0},
                'recommendation': {'stance': 'NEUTRAL', 'message': 'Data unavailable'},
                'us_markets': {}
            }
    
    def _scan_all_stocks(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> List[Dict]:
        """Scan all stocks from specified sectors"""
        
        # Determine which sectors to scan
        if sectors is None:
            sectors_to_scan = list(self.scanner.sectors.keys())
        else:
            sectors_to_scan = sectors
        
        logger.info(f"Scanning {len(sectors_to_scan)} sectors...")
        logger.info(f"Target: {stocks_per_sector} stocks per sector")
        
        all_stocks = []
        sector_summaries = {}
        
        for i, sector_name in enumerate(sectors_to_scan, 1):
            logger.info(f"\n[{i}/{len(sectors_to_scan)}] Scanning {sector_name}...")
            
            try:
                # Scan sector
                stocks = self.scanner.scan_sector(sector_name, top_n=stocks_per_sector)
                
                if stocks:
                    all_stocks.extend(stocks)
                    sector_summaries[sector_name] = self.scanner.get_sector_summary(stocks)
                    
                    logger.info(f"  ✓ Found {len(stocks)} valid stocks")
                    logger.info(f"  Top 3: {', '.join([s['symbol'] for s in stocks[:3]])}")
                else:
                    logger.warning(f"  ⚠ No valid stocks found in {sector_name}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error scanning {sector_name}: {e}")
                self.status['errors'].append(f"Sector scan failed: {sector_name} - {str(e)}")
                continue
        
        logger.info(f"\n✓ Scanning Complete:")
        logger.info(f"  Total Valid Stocks: {len(all_stocks)}")
        logger.info(f"  Sectors Processed: {len(sector_summaries)}/{len(sectors_to_scan)}")
        
        self.status['total_stocks'] = len(all_stocks)
        
        return all_stocks
    
    def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
        """
        🆕 Assess event risks for all scanned stocks (Basel III, earnings, etc.)
        
        Args:
            stocks: List of scanned stock dictionaries
            
        Returns:
            Dictionary mapping ticker -> event risk data
        """
        if self.event_guard is None:
            logger.info("  Event Risk Guard not available - skipping event assessment")
            return {}
        
        logger.info(f"Assessing event risks for {len(stocks)} stocks...")
        logger.info(f"  Checking for: Basel III, Pillar 3, Earnings, Dividends")
        
        try:
            # Extract tickers
            tickers = [s['symbol'] for s in stocks]
            
            # Batch assess
            results = self.event_guard.assess_batch(tickers)
            
            # Summary stats
            total_events = sum(1 for r in results.values() if r.has_upcoming_event)
            sit_outs = sum(1 for r in results.values() if r.skip_trading)
            high_risk = sum(1 for r in results.values() if r.risk_score >= 0.7)
            regulatory = sum(1 for r in results.values() if r.event_type in ['basel_iii', 'regulatory', 'pillar_3'])
            
            logger.info(f"✓ Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  🚨 Regulatory Reports (Basel III/Pillar 3): {regulatory}")
            logger.info(f"  ⚠️  Sit-Out Recommendations: {sit_outs}")
            logger.info(f"  ⚡ High Risk Stocks (≥0.7): {high_risk}")
            
            # Log specific warnings
            warnings = [
                (ticker, r) for ticker, r in results.items()
                if r.warning_message and r.risk_score >= 0.5
            ]
            
            if warnings:
                logger.info(f"\n  Notable Warnings:")
                for ticker, r in sorted(warnings, key=lambda x: x[1].risk_score, reverse=True)[:5]:
                    logger.info(f"    {ticker}: {r.warning_message}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Event risk assessment failed: {e}")
            self.status['warnings'].append(f"Event risk assessment failed: {str(e)}")
            return {}
    
    def _generate_predictions(self, stocks: List[Dict], spi_sentiment: Dict, event_risk_data: Dict = None) -> List[Dict]:
        """
        Generate predictions for all stocks with event risk adjustments
        
        Args:
            stocks: List of scanned stocks
            spi_sentiment: Market sentiment data
            event_risk_data: Event risk assessment results (optional)
        """
        logger.info(f"Generating predictions for {len(stocks)} stocks...")
        logger.info(f"Using {self.predictor.max_workers} parallel workers")
        
        try:
            predicted_stocks = self.predictor.predict_batch(stocks, spi_sentiment)
            
            # 🆕 Apply event risk adjustments if available
            if event_risk_data:
                logger.info(f"\nApplying event risk adjustments...")
                adjusted_count = 0
                skip_count = 0
                
                for stock in predicted_stocks:
                    ticker = stock.get('symbol')
                    if ticker in event_risk_data:
                        risk = event_risk_data[ticker]
                        
                        # Add event risk fields to stock data
                        stock['event_risk_score'] = risk.risk_score
                        stock['event_warning'] = risk.warning_message or ''
                        stock['event_skip_trading'] = risk.skip_trading
                        stock['event_weight_haircut'] = risk.weight_haircut
                        stock['event_type'] = risk.event_type or ''
                        stock['days_to_event'] = risk.days_to_event
                        
                        # Apply weight haircut to confidence if needed
                        if risk.weight_haircut > 0:
                            original_conf = stock.get('confidence', 0)
                            stock['confidence'] = original_conf * (1 - risk.weight_haircut)
                            adjusted_count += 1
                            logger.debug(f"  {ticker}: Confidence {original_conf:.1f}% → {stock['confidence']:.1f}% (haircut: {risk.weight_haircut*100:.0f}%)")
                        
                        # Mark for skip if recommended
                        if risk.skip_trading:
                            stock['prediction'] = 'HOLD'  # Force to HOLD
                            stock['skip_reason'] = risk.warning_message
                            skip_count += 1
                
                logger.info(f"  Adjusted: {adjusted_count} stocks")
                logger.info(f"  Skipped: {skip_count} stocks (forced to HOLD)")
            else:
                # Add empty event risk fields
                for stock in predicted_stocks:
                    stock['event_risk_score'] = 0.0
                    stock['event_warning'] = ''
                    stock['event_skip_trading'] = False
                    stock['event_weight_haircut'] = 0.0
                    stock['event_type'] = ''
                    stock['days_to_event'] = None
            
            # Get summary
            summary = self.predictor.get_prediction_summary(predicted_stocks)
            
            logger.info(f"✓ Predictions Generated:")
            logger.info(f"  Total: {summary['total']}")
            logger.info(f"  BUY: {summary['buy_count']} | SELL: {summary['sell_count']} | HOLD: {summary['hold_count']}")
            logger.info(f"  Avg Confidence: {summary['avg_confidence']:.1f}%")
            logger.info(f"  High Confidence (≥70%): {summary['high_confidence_count']}")
            
            self.status['processed_stocks'] = len(predicted_stocks)
            
            return predicted_stocks
            
        except Exception as e:
            logger.error(f"✗ Prediction generation failed: {e}")
            raise
    
    def _score_opportunities(self, stocks: List[Dict], spi_sentiment: Dict) -> List[Dict]:
        """Score all opportunities"""
        logger.info(f"Scoring {len(stocks)} opportunities...")
        
        try:
            scored_stocks = self.scorer.score_opportunities(stocks, spi_sentiment)
            
            # Get summary
            summary = self.scorer.get_opportunity_summary(scored_stocks)
            
            logger.info(f"✓ Opportunities Scored:")
            logger.info(f"  Average Score: {summary['avg_score']:.1f}/100")
            logger.info(f"  High Opportunities (≥80): {summary['high_opportunity_count']}")
            logger.info(f"  Medium Opportunities (65-80): {summary['medium_opportunity_count']}")
            logger.info(f"  Low Opportunities (<65): {summary['low_opportunity_count']}")
            
            if summary['top_opportunities']:
                top_5 = summary['top_opportunities'][:5]
                logger.info(f"  Top 5:")
                for i, opp in enumerate(top_5, 1):
                    logger.info(f"    {i}. {opp['symbol']}: {opp['opportunity_score']:.1f}/100")
            
            return scored_stocks
            
        except Exception as e:
            logger.error(f"✗ Opportunity scoring failed: {e}")
            raise
    
    def _generate_report(self, stocks: List[Dict], spi_sentiment: Dict) -> str:
        """Generate morning report"""
        logger.info("Generating morning report...")
        
        try:
            # Prepare sector summary
            sector_summary = {}
            sectors_present = set([s.get('symbol', '').split('.')[0][:3] for s in stocks])
            
            # Group stocks by sector (simplified - based on scanner data)
            for sector_name in self.scanner.sectors.keys():
                sector_stocks = [s for s in stocks if s.get('symbol', '').startswith(tuple([
                    sym.split('.')[0][:3] for sym in self.scanner.sectors[sector_name]['stocks'][:5]
                ]))]
                if sector_stocks:
                    sector_summary[sector_name] = self.scanner.get_sector_summary(sector_stocks)
            
            # Prepare system stats
            elapsed_time = time.time() - self.start_time
            pred_summary = self.predictor.get_prediction_summary(stocks)
            
            system_stats = {
                'total_scanned': len(stocks),
                'buy_signals': pred_summary['buy_count'],
                'sell_signals': pred_summary['sell_count'],
                'processing_time_seconds': int(elapsed_time),
                'lstm_status': 'Available' if self.predictor.lstm_available else 'Not Available'
            }
            
            # Generate report
            report_path = self.reporter.generate_morning_report(
                opportunities=stocks,
                spi_sentiment=spi_sentiment,
                sector_summary=sector_summary,
                system_stats=system_stats
            )
            
            logger.info(f"✓ Report Generated: {report_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"✗ Report generation failed: {e}")
            raise
    
    def _finalize_pipeline(self, scored_stocks: List[Dict], spi_sentiment: Dict, report_path: str) -> Dict:
        """Finalize pipeline and save results"""
        logger.info("Finalizing pipeline...")
        
        elapsed_time = time.time() - self.start_time
        
        # Filter top opportunities
        top_opportunities = self.scorer.filter_top_opportunities(
            scored_stocks,
            min_score=65,
            top_n=10
        )
        
        # Prepare summary for email notifications
        report_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
        summary = {
            'report_date': report_date,
            'total_stocks_scanned': len(scored_stocks),
            'opportunities_found': len(top_opportunities),
            'spi_sentiment_score': spi_sentiment['sentiment_score'],
            'market_bias': spi_sentiment['recommendation']['stance']
        }
        
        # Prepare top opportunities with complete info for emails
        top_opps_detailed = [
            {
                'symbol': opp['symbol'],
                'company_name': opp['name'],
                'opportunity_score': opp['opportunity_score'],
                'signal': opp.get('prediction', 'HOLD'),
                'confidence': opp.get('confidence', 0),
                'sector': opp.get('sector', 'Unknown'),
                'current_price': opp['price']
            }
            for opp in top_opportunities
        ]
        
        # 🆕 Export CSV with event risk data
        csv_paths = {}
        if self.csv_exporter is not None:
            try:
                logger.info("Exporting results to CSV...")
                csv_paths['full_results'] = self.csv_exporter.export_screening_results(
                    scored_stocks, spi_sentiment
                )
                csv_paths['event_risk_summary'] = self.csv_exporter.export_event_risk_summary(
                    scored_stocks
                )
                logger.info(f"✓ CSV exports complete")
                if csv_paths['event_risk_summary']:
                    logger.info(f"  Full results: {csv_paths['full_results']}")
                    logger.info(f"  Event risk summary: {csv_paths['event_risk_summary']}")
                else:
                    logger.info(f"  Full results: {csv_paths['full_results']}")
                    logger.info(f"  Event risk summary: (no events detected)")
            except Exception as e:
                logger.warning(f"CSV export failed: {e}")
                csv_paths = {}
        
        # Prepare results
        results = {
            'status': 'success',
            'timestamp': datetime.now(self.timezone).isoformat(),
            'execution_time_seconds': int(elapsed_time),
            'execution_time_minutes': round(elapsed_time / 60, 2),
            'summary': summary,
            'statistics': {
                'total_stocks_scanned': len(scored_stocks),
                'top_opportunities_count': len(top_opportunities),
                'high_confidence_count': len([s for s in scored_stocks if s.get('confidence', 0) >= 70]),
                'buy_signals': len([s for s in scored_stocks if s.get('prediction') == 'BUY']),
                'sell_signals': len([s for s in scored_stocks if s.get('prediction') == 'SELL']),
                'hold_signals': len([s for s in scored_stocks if s.get('prediction') == 'HOLD']),
                'event_risk_stocks': len([s for s in scored_stocks if s.get('event_type')]),
                'skip_trading_count': len([s for s in scored_stocks if s.get('event_skip_trading', False)]),
            },
            'market_sentiment': {
                'score': spi_sentiment['sentiment_score'],
                'gap_prediction': spi_sentiment['gap_prediction']['predicted_gap_pct'],
                'direction': spi_sentiment['gap_prediction']['direction'],
                'recommendation': spi_sentiment['recommendation']['stance']
            },
            'top_opportunities': top_opps_detailed,
            'report_path': report_path,
            'csv_paths': csv_paths,
            'errors': self.status['errors'],
            'warnings': self.status['warnings']
        }
        
        # Save pipeline state
        self._save_pipeline_state(results)
        
        logger.info("✓ Pipeline finalized")
        
        return results
    
    def _save_pipeline_state(self, results: Dict):
        """Save pipeline execution state to JSON"""
        state_dir = BASE_PATH / 'reports' / 'pipeline_state'
        state_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now(self.timezone).strftime('%Y-%m-%d')
        state_file = state_dir / f"{date_str}_pipeline_state.json"
        
        with open(state_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Pipeline state saved: {state_file}")
    
    def _save_error_state(self, error: Exception):
        """Save error state for debugging"""
        error_dir = Path('logs/screening/errors')
        error_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(self.timezone).strftime('%Y%m%d_%H%M%S')
        error_file = error_dir / f"error_{timestamp}.json"
        
        error_state = {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'error': str(error),
            'traceback': traceback.format_exc(),
            'status': self.status
        }
        
        with open(error_file, 'w') as f:
            json.dump(error_state, f, indent=2, default=str)
        
        logger.error(f"Error state saved: {error_file}")
    
    def get_status(self) -> Dict:
        """Get current pipeline status"""
        return self.status


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for overnight pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Overnight Stock Screening Pipeline')
    parser.add_argument('--sectors', nargs='+', help='Sectors to scan (default: all)')
    parser.add_argument('--stocks-per-sector', type=int, default=30, help='Stocks per sector')
    parser.add_argument('--mode', choices=['full', 'test'], default='full', help='Execution mode')
    
    args = parser.parse_args()
    
    try:
        pipeline = OvernightPipeline()
        
        if args.mode == 'test':
            # Test mode: scan only Financials sector with 5 stocks
            logger.info("Running in TEST mode (Financials only, 5 stocks)")
            results = pipeline.run_full_pipeline(
                sectors=['Financials'],
                stocks_per_sector=5
            )
        else:
            # Full mode: scan all sectors
            logger.info("Running in FULL mode (all sectors)")
            results = pipeline.run_full_pipeline(
                sectors=args.sectors,
                stocks_per_sector=args.stocks_per_sector
            )
        
        # Print summary
        print("\n" + "="*80)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Status: {results['status'].upper()}")
        print(f"Execution Time: {results['execution_time_minutes']} minutes")
        print(f"Stocks Scanned: {results['statistics']['total_stocks_scanned']}")
        print(f"Top Opportunities: {results['statistics']['top_opportunities_count']}")
        print(f"Report: {results['report_path']}")
        print("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

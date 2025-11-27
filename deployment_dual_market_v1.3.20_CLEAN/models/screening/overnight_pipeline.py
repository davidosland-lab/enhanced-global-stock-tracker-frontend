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

# Market Hours Detector (optional)
try:
    from .market_hours_detector import MarketHoursDetector
except ImportError:
    try:
        from market_hours_detector import MarketHoursDetector
    except ImportError:
        MarketHoursDetector = None

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

# 🆕 ChatGPT Research (optional)
try:
    from .chatgpt_research import (
        run_chatgpt_research, 
        save_markdown,
        ai_quick_filter,
        ai_score_opportunity,
        ai_rerank_opportunities
    )
except ImportError:
    try:
        from chatgpt_research import (
            run_chatgpt_research,
            save_markdown,
            ai_quick_filter,
            ai_score_opportunity,
            ai_rerank_opportunities
        )
    except ImportError:
        run_chatgpt_research = None
        save_markdown = None
        ai_quick_filter = None
        ai_score_opportunity = None
        ai_rerank_opportunities = None

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
        
        # Initialize market hours detector (for intraday awareness)
        if MarketHoursDetector is not None:
            self.market_detector = MarketHoursDetector()
            logger.info("✓ Market Hours Detector initialized")
        else:
            self.market_detector = None
            logger.info("  Market Hours Detector disabled")
        
        # Add market hours tracking
        self.status.update({
            'market_hours': None,
            'pipeline_mode': 'overnight'  # or 'intraday'
        })
        
        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'screening_config.json'
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✓ Configuration loaded from {config_path}")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_path}, using defaults")
            self.config = {
                'lstm_training': {
                    'enabled': True,
                    'max_models_per_night': 100,
                    'stale_threshold_days': 7
                }
            }
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}, using defaults")
            self.config = {
                'lstm_training': {
                    'enabled': True,
                    'max_models_per_night': 100,
                    'stale_threshold_days': 7
                }
            }
        
        # Initialize components
        logger.info("="*80)
        logger.info("OVERNIGHT STOCK SCREENING PIPELINE - STARTING")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        try:
            self.scanner = StockScanner()
            self.spi_monitor = SPIMonitor()
            self.predictor = BatchPredictor(market='ASX')
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
            
            # Optional: ChatGPT Research
            self.research_config = self.config.get('research', {})
            if run_chatgpt_research is not None and self.research_config.get('enabled', False):
                logger.info("✓ ChatGPT research enabled")
                logger.info(f"  Model: {self.research_config.get('model', 'gpt-4o-mini')}")
                logger.info(f"  Max stocks: {self.research_config.get('max_stocks', 5)}")
            else:
                logger.info("  ChatGPT research disabled")
            
            # Optional: AI Integration (Full AI Pipeline)
            self.ai_config = self.config.get('ai_integration', {})
            if ai_quick_filter is not None and self.ai_config.get('enabled', False):
                logger.info("✓ AI Integration enabled (Full AI Pipeline)")
                stages = self.ai_config.get('stages', {})
                logger.info(f"  Quick Filter: {stages.get('quick_filter', {}).get('enabled', False)}")
                logger.info(f"  AI Scoring: {stages.get('ai_scoring', {}).get('enabled', False)}")
                logger.info(f"  AI Re-Ranking: {stages.get('ai_reranking', {}).get('enabled', False)}")
            else:
                logger.info("  AI Integration disabled")
            
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
            # Phase 0: Market Hours Detection (NEW)
            logger.info("\n" + "="*80)
            logger.info("PHASE 0: MARKET HOURS DETECTION")
            logger.info("="*80)
            
            if self.market_detector is not None:
                market_status = self.market_detector.is_market_open('ASX')
                self.status['market_hours'] = market_status
                
                # Log market status
                logger.info(self.market_detector.get_market_status_summary('ASX'))
                logger.info("")
                
                # Determine pipeline mode
                if market_status['is_open']:
                    self.status['pipeline_mode'] = 'intraday'
                    logger.warning("⚠️  INTRADAY MODE ACTIVE")
                    logger.warning("    • Market is currently open")
                    logger.warning("    • Using recent/live prices")
                    logger.warning("    • SPI gap predictions less relevant")
                    logger.warning("    • Consider running after market close for best results")
                else:
                    self.status['pipeline_mode'] = 'overnight'
                    logger.info("✓ OVERNIGHT MODE (Standard)")
                    logger.info("  • Market is closed")
                    logger.info("  • Using standard predictions")
            else:
                logger.info("Market hours detection disabled - using overnight mode")
                self.status['pipeline_mode'] = 'overnight'
                self.status['market_hours'] = {'is_open': False, 'market_phase': 'unknown'}
            
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
            
            # 🤖 Phase 2.3: AI Quick Filter (Optional)
            ai_filter_results = self._run_ai_quick_filter(scanned_stocks)
            
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
            
            # 🤖 Phase 3.5: AI Scoring (Optional)
            ai_scores = self._run_ai_scoring(predicted_stocks)
            
            # Phase 4: Opportunity Scoring
            logger.info("\n" + "="*80)
            logger.info("PHASE 4: OPPORTUNITY SCORING")
            logger.info("="*80)
            self.status['phase'] = 'scoring'
            self.status['progress'] = 70
            
            scored_stocks = self._score_opportunities(predicted_stocks, spi_sentiment, ai_scores)
            
            # Phase 4.5: LSTM Model Training (Optional)
            lstm_training_results = self._train_lstm_models(scored_stocks)
            
            # 🤖 Phase 4.6: AI Re-Ranking (Optional)
            final_opportunities = self._run_ai_reranking(scored_stocks)
            
            # Phase 4.7: ChatGPT Research (Optional)
            research_data = self._run_chatgpt_research(final_opportunities)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_report(
                final_opportunities, 
                spi_sentiment, 
                event_risk_data,
                research_data=research_data
            )
            
            # Phase 6: Finalization
            logger.info("\n" + "="*80)
            logger.info("PHASE 6: FINALIZATION")
            logger.info("="*80)
            self.status['phase'] = 'complete'
            self.status['progress'] = 100
            
            results = self._finalize_pipeline(
                scored_stocks=final_opportunities,
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
                    # Send morning report
                    if self.notifier.enabled and self.notifier.send_morning_report:
                        logger.info("Sending morning report email...")
                        self.notifier.send_morning_report(
                            report_path=str(report_path),
                            summary=results.get('summary', {}),
                            top_opportunities=results.get('top_opportunities', [])
                        )
                    
                    # Send alerts for high-confidence opportunities
                    if self.notifier.enabled and self.notifier.send_alerts:
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
                if self.notifier is not None and self.notifier.enabled and self.notifier.send_errors:
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
        """Scan all stocks from specified sectors (mode-aware)"""
        
        # Determine which sectors to scan
        if sectors is None:
            sectors_to_scan = list(self.scanner.sectors.keys())
        else:
            sectors_to_scan = sectors
        
        # Check if we should include intraday data
        include_intraday = self.status.get('pipeline_mode') == 'intraday'
        
        logger.info(f"Scanning {len(sectors_to_scan)} sectors...")
        logger.info(f"Target: {stocks_per_sector} stocks per sector")
        if include_intraday:
            logger.info(f"Mode: INTRADAY (fetching 1-minute bars)")
        
        all_stocks = []
        sector_summaries = {}
        
        for i, sector_name in enumerate(sectors_to_scan, 1):
            logger.info(f"\n[{i}/{len(sectors_to_scan)}] Scanning {sector_name}...")
            
            try:
                # Scan sector (with intraday data if market is open)
                stocks = self.scanner.scan_sector(
                    sector_name, 
                    top_n=stocks_per_sector,
                    include_intraday=include_intraday
                )
                
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
        if include_intraday:
            intraday_count = sum(1 for s in all_stocks if 'intraday_data' in s)
            logger.info(f"  📈 Intraday data: {intraday_count}/{len(all_stocks)} stocks")
        
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
            
            # Extract ticker results (filter out market_regime key)
            ticker_results = {k: v for k, v in results.items() if k != 'market_regime' and hasattr(v, 'has_upcoming_event')}
            
            # Summary stats
            total_events = sum(1 for r in ticker_results.values() if r.has_upcoming_event)
            sit_outs = sum(1 for r in ticker_results.values() if r.skip_trading)
            high_risk = sum(1 for r in ticker_results.values() if r.risk_score >= 0.7)
            regulatory = sum(1 for r in ticker_results.values() if r.event_type in ['basel_iii', 'regulatory', 'pillar_3'])
            
            logger.info(f"✓ Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  🚨 Regulatory Reports (Basel III/Pillar 3): {regulatory}")
            logger.info(f"  ⚠️  Sit-Out Recommendations: {sit_outs}")
            logger.info(f"  ⚡ High Risk Stocks (≥0.7): {high_risk}")
            
            # Log market regime if available
            if 'market_regime' in results:
                regime = results['market_regime']
                logger.info(f"  📊 Market Regime: {regime.get('regime_label', 'unknown')} | Crash Risk: {regime.get('crash_risk_score', 0)*100:.1f}%")
            
            # Log specific warnings
            warnings = [
                (ticker, r) for ticker, r in ticker_results.items()
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
        
        # Safety check for predictor
        if not hasattr(self, 'predictor') or self.predictor is None:
            logger.error("BatchPredictor not initialized - cannot generate predictions")
            raise RuntimeError("BatchPredictor not initialized")
        
        try:
            max_workers = getattr(self.predictor, 'max_workers', 4)
            logger.info(f"Using {max_workers} parallel workers")
        except Exception as e:
            logger.warning(f"Could not get max_workers: {e}, using default")
        
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
    
    def _score_opportunities(self, stocks: List[Dict], spi_sentiment: Dict, ai_scores: Dict = None) -> List[Dict]:
        """Score all opportunities (mode-aware)"""
        logger.info(f"Scoring {len(stocks)} opportunities...")
        
        try:
            # Pass market_status for mode-aware scoring
            market_status = self.status.get('market_hours')
            scored_stocks = self.scorer.score_opportunities(
                stocks, 
                spi_sentiment, 
                ai_scores,
                market_status=market_status
            )
            
            # Get summary
            summary = self.scorer.get_opportunity_summary(scored_stocks)
            
            logger.info(f"✓ Opportunities Scored:")
            logger.info(f"  Mode: {self.status.get('pipeline_mode', 'overnight').upper()}")
            logger.info(f"  Average Score: {summary['avg_score']:.1f}/100")
            logger.info(f"  High Opportunities (≥80): {summary['high_opportunity_count']}")
            logger.info(f"  Medium Opportunities (65-80): {summary['medium_opportunity_count']}")
            logger.info(f"  Low Opportunities (<65): {summary['low_opportunity_count']}")
            
            if summary['top_opportunities']:
                top_5 = summary['top_opportunities'][:5]
                logger.info(f"  Top 5:")
                for i, opp in enumerate(top_5, 1):
                    momentum_info = ""
                    if 'momentum_breakdown' in opp:
                        momentum_info = f" | Momentum: {opp['momentum_breakdown'].get('momentum', 0):.0f}"
                    logger.info(f"    {i}. {opp['symbol']}: {opp['opportunity_score']:.1f}/100{momentum_info}")
            
            return scored_stocks
            
        except Exception as e:
            logger.error(f"✗ Opportunity scoring failed: {e}")
            raise
    
    def _train_lstm_models(self, scored_stocks: List[Dict]) -> Dict:
        """
        Train LSTM models for top opportunity stocks
        
        Args:
            scored_stocks: List of scored stocks
            
        Returns:
            Dictionary with training results
        """
        if self.trainer is None:
            logger.info("  LSTM trainer not available - skipping training")
            return {'status': 'disabled', 'trained_count': 0}
        
        # Check if training is enabled in config
        lstm_config = self.config.get('lstm_training', {})
        training_enabled = lstm_config.get('enabled', True)
        
        logger.info(f"[DEBUG] LSTM Training Check:")
        logger.info(f"  self.trainer = {self.trainer}")
        logger.info(f"  config.lstm_training.enabled = {training_enabled}")
        logger.info(f"  config.lstm_training = {lstm_config}")
        
        if not training_enabled:
            logger.info("  LSTM training disabled in configuration")
            return {'status': 'disabled', 'trained_count': 0}
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 4.5: LSTM MODEL TRAINING")
        logger.info("="*80)
        self.status['phase'] = 'lstm_training'
        self.status['progress'] = 75
        
        try:
            # Create training queue from scored stocks
            max_models = lstm_config.get('max_models_per_night', 100)
            logger.info(f"Creating training queue (max {max_models} stocks)...")
            
            training_queue = self.trainer.create_training_queue(
                opportunities=scored_stocks,
                max_stocks=max_models
            )
            
            # Train the models
            if training_queue:
                logger.info(f"Training {len(training_queue)} LSTM models...")
                training_results = self.trainer.train_batch(
                    training_queue=training_queue,
                    max_stocks=max_models
                )
                
                logger.info(f"[SUCCESS] LSTM Training Complete:")
                logger.info(f"  Models trained: {training_results.get('trained_count', 0)}/{training_results.get('total_stocks', 0)}")
                logger.info(f"  Successful: {training_results.get('trained_count', 0)}")
                logger.info(f"  Failed: {training_results.get('failed_count', 0)}")
                logger.info(f"  Total Time: {training_results.get('total_time', 0)/60:.1f} minutes")
                
                return training_results
            else:
                logger.info("No stocks queued for training (all models are fresh)")
                return {'status': 'no_training_needed', 'trained_count': 0}
                
        except Exception as e:
            logger.error(f"✗ LSTM training failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"LSTM training failed: {str(e)}")
            return {'status': 'failed', 'trained_count': 0, 'error': str(e)}
    
    def _run_chatgpt_research(self, scored_stocks: List[Dict]) -> Dict:
        """
        Run ChatGPT research on top opportunity stocks
        
        Args:
            scored_stocks: List of scored stocks
            
        Returns:
            Dictionary with research results and markdown path
        """
        if run_chatgpt_research is None:
            logger.info("  ChatGPT research module not available - skipping research")
            return {'status': 'disabled', 'research_count': 0}
        
        # Check if research is enabled in config
        research_config = self.research_config
        research_enabled = research_config.get('enabled', False)
        
        if not research_enabled:
            logger.info("  ChatGPT research disabled in configuration")
            return {'status': 'disabled', 'research_count': 0}
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 4.7: CHATGPT RESEARCH")
        logger.info("="*80)
        self.status['phase'] = 'chatgpt_research'
        self.status['progress'] = 78
        
        try:
            # Extract config parameters
            model = research_config.get('model', 'gpt-4o-mini')
            max_stocks = research_config.get('max_stocks', 5)
            output_path_template = research_config.get('output_path', 'reports/chatgpt_research')
            
            logger.info(f"Running ChatGPT research for top {max_stocks} opportunities...")
            logger.info(f"  Model: {model}")
            logger.info(f"  Market: ASX")
            
            # Run research
            research_results = run_chatgpt_research(
                opportunities=scored_stocks,
                model=model,
                max_stocks=max_stocks,
                market='ASX'
            )
            
            if research_results:
                # Save markdown report
                date_str = datetime.now(self.timezone).strftime("%Y%m%d")
                output_dir = BASE_PATH / output_path_template
                output_file = output_dir / f"asx_research_{date_str}.md"
                
                # Prepare pipeline metadata
                pipeline_metadata = {
                    'run_id': date_str,
                    'total_opportunities': len(scored_stocks),
                    'market': 'ASX'
                }
                
                markdown_path = save_markdown(
                    research_results=research_results,
                    output_path=output_file,
                    market='ASX',
                    pipeline_metadata=pipeline_metadata
                )
                
                logger.info(f"[SUCCESS] ChatGPT Research Complete:")
                logger.info(f"  Stocks researched: {len(research_results)}/{max_stocks}")
                logger.info(f"  Report saved: {markdown_path}")
                
                return {
                    'status': 'success',
                    'research_count': len(research_results),
                    'markdown_path': str(markdown_path),
                    'research_results': research_results
                }
            else:
                logger.warning("  No research results generated")
                return {'status': 'no_results', 'research_count': 0}
                
        except Exception as e:
            logger.error(f"✗ ChatGPT research failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"ChatGPT research failed: {str(e)}")
            return {'status': 'failed', 'research_count': 0, 'error': str(e)}
    
    def _run_ai_quick_filter(self, scanned_stocks: List[Dict]) -> Dict:
        """
        Run AI quick filter on all scanned stocks
        
        Args:
            scanned_stocks: List of scanned stocks
            
        Returns:
            Dictionary with filter results {symbol: {risk_flag, opportunity_flag, quick_score}}
        """
        if ai_quick_filter is None:
            return {}
        
        # Check if AI integration is enabled
        ai_config = self.ai_config.get('stages', {}).get('quick_filter', {})
        if not ai_config.get('enabled', False):
            return {}
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 2.3: AI QUICK FILTER")
        logger.info("="*80)
        self.status['phase'] = 'ai_quick_filter'
        self.status['progress'] = 28
        
        try:
            model = self.ai_config.get('model', 'gpt-4o-mini')
            
            logger.info(f"Running AI Quick Filter on {len(scanned_stocks)} stocks...")
            logger.info(f"  Model: {model}")
            logger.info(f"  Market: ASX")
            
            filter_results = ai_quick_filter(
                stocks=scanned_stocks,
                model=model,
                market='ASX'
            )
            
            if filter_results:
                high_risk_count = sum(1 for v in filter_results.values() if v.get('risk_flag') == 'high')
                high_opp_count = sum(1 for v in filter_results.values() if v.get('opportunity_flag') == 'high')
                
                logger.info(f"[SUCCESS] AI Quick Filter Complete:")
                logger.info(f"  Stocks analyzed: {len(filter_results)}")
                logger.info(f"  High risk flags: {high_risk_count}")
                logger.info(f"  High opportunity flags: {high_opp_count}")
                
                # Add filter results to stocks
                for stock in scanned_stocks:
                    symbol = stock.get('symbol', '')
                    if symbol in filter_results:
                        stock['ai_filter'] = filter_results[symbol]
                
                return filter_results
            else:
                logger.warning("  No filter results generated")
                return {}
                
        except Exception as e:
            logger.error(f"✗ AI Quick Filter failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"AI Quick Filter failed: {str(e)}")
            return {}
    
    def _run_ai_scoring(self, predicted_stocks: List[Dict]) -> Dict:
        """
        Run AI scoring on top predicted stocks
        
        Args:
            predicted_stocks: List of stocks with predictions
            
        Returns:
            Dictionary with AI scores {symbol: {fundamental_score, risk_score, etc}}
        """
        if ai_score_opportunity is None:
            return {}
        
        # Check if AI scoring is enabled
        ai_config = self.ai_config.get('stages', {}).get('ai_scoring', {})
        if not ai_config.get('enabled', False):
            return {}
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 3.5: AI SCORING")
        logger.info("="*80)
        self.status['phase'] = 'ai_scoring'
        self.status['progress'] = 60
        
        try:
            model = self.ai_config.get('model', 'gpt-4o-mini')
            score_top_n = ai_config.get('score_top_n', 50)
            
            # Sort by prediction confidence to get top candidates
            top_stocks = sorted(predicted_stocks, key=lambda x: x.get('confidence', 0), reverse=True)[:score_top_n]
            
            logger.info(f"Running AI Scoring on top {len(top_stocks)} stocks...")
            logger.info(f"  Model: {model}")
            logger.info(f"  Market: ASX")
            
            ai_scores = {}
            
            for i, stock in enumerate(top_stocks, 1):
                symbol = stock.get('symbol', 'N/A')
                
                try:
                    score_data = ai_score_opportunity(
                        opportunity=stock,
                        model=model,
                        market='ASX'
                    )
                    
                    if score_data:
                        ai_scores[symbol] = score_data
                        logger.info(f"  ✓ {symbol}: AI Score = {score_data.get('overall_ai_score', 0)}/100 ({i}/{len(top_stocks)})")
                    
                except Exception as e:
                    logger.error(f"  ✗ AI scoring failed for {symbol}: {e}")
                    continue
            
            logger.info(f"[SUCCESS] AI Scoring Complete:")
            logger.info(f"  Stocks scored: {len(ai_scores)}/{len(top_stocks)}")
            
            return ai_scores
            
        except Exception as e:
            logger.error(f"✗ AI Scoring failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"AI Scoring failed: {str(e)}")
            return {}
    
    def _run_ai_reranking(self, scored_stocks: List[Dict]) -> List[Dict]:
        """
        Run AI re-ranking on top opportunities
        
        Args:
            scored_stocks: List of scored stocks
            
        Returns:
            Re-ranked list of top opportunities
        """
        if ai_rerank_opportunities is None:
            return scored_stocks
        
        # Check if AI re-ranking is enabled
        ai_config = self.ai_config.get('stages', {}).get('ai_reranking', {})
        if not ai_config.get('enabled', False):
            return scored_stocks
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 4.6: AI RE-RANKING")
        logger.info("="*80)
        self.status['phase'] = 'ai_reranking'
        self.status['progress'] = 77
        
        try:
            model = self.ai_config.get('model', 'gpt-4o-mini')
            rerank_top_n = ai_config.get('rerank_top_n', 20)
            final_picks = ai_config.get('final_picks', 10)
            
            # Get top N for re-ranking
            top_opportunities = scored_stocks[:rerank_top_n]
            
            logger.info(f"Running AI Re-Ranking on top {len(top_opportunities)} opportunities...")
            logger.info(f"  Model: {model}")
            logger.info(f"  Market: ASX")
            logger.info(f"  Final picks: {final_picks}")
            
            reranked = ai_rerank_opportunities(
                opportunities=top_opportunities,
                model=model,
                market='ASX',
                top_n=final_picks
            )
            
            logger.info(f"[SUCCESS] AI Re-Ranking Complete:")
            logger.info(f"  Final top picks: {len(reranked)}")
            
            # Combine reranked top picks with remaining stocks
            remaining = scored_stocks[rerank_top_n:]
            final_list = reranked + remaining
            
            return final_list
            
        except Exception as e:
            logger.error(f"✗ AI Re-Ranking failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"AI Re-Ranking failed: {str(e)}")
            return scored_stocks
    
    def _generate_report(self, stocks: List[Dict], spi_sentiment: Dict, event_risk_data: Dict = None, research_data: Dict = None) -> str:
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
                system_stats=system_stats,
                event_risk_data=event_risk_data,
                research_data=research_data
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

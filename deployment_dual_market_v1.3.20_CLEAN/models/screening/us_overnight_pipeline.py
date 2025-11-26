"""
US Overnight Pipeline Orchestrator

Main orchestration module for US market screening workflow.
Coordinates all modules and handles error recovery, progress tracking, and logging.

Workflow:
1. Initialize all components
2. Fetch US market sentiment (S&P 500, VIX)
3. Scan all sectors (240 stocks)
4. Generate batch predictions
5. Score opportunities
6. Generate morning report
7. Save results and logs
"""

import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import traceback
import pytz

# Import US-specific modules
try:
    from .us_stock_scanner import USStockScanner
    from .us_market_monitor import USMarketMonitor
    from .us_market_regime_engine import USMarketRegimeEngine
except ImportError:
    from us_stock_scanner import USStockScanner
    from us_market_monitor import USMarketMonitor
    from us_market_regime_engine import USMarketRegimeEngine

# Import shared modules (can be reused with market parameter)
try:
    from .batch_predictor import BatchPredictor
    from .opportunity_scorer import OpportunityScorer
    from .report_generator import ReportGenerator
except ImportError:
    from batch_predictor import BatchPredictor
    from opportunity_scorer import OpportunityScorer
    from report_generator import ReportGenerator

# Optional modules
try:
    from .send_notification import EmailNotifier
except ImportError:
    EmailNotifier = None

try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    EventRiskGuard = None

try:
    from .csv_exporter import CSVExporter
except ImportError:
    CSVExporter = None

try:
    from .lstm_trainer import LSTMTrainer
except ImportError:
    LSTMTrainer = None

# 🆕 ChatGPT Research (optional)
try:
    from .chatgpt_research import run_chatgpt_research, save_markdown
except ImportError:
    try:
        from chatgpt_research import run_chatgpt_research, save_markdown
    except ImportError:
        run_chatgpt_research = None
        save_markdown = None

# Setup logging
BASE_PATH = Path(__file__).parent.parent.parent
log_dir = BASE_PATH / 'logs' / 'screening' / 'us'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'us_overnight_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class USOvernightPipeline:
    """
    Orchestrates the complete US market overnight screening pipeline.
    """
    
    def __init__(self):
        """Initialize the US pipeline orchestrator"""
        self.timezone = pytz.timezone('America/New_York')
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
        logger.info("US OVERNIGHT STOCK SCREENING PIPELINE - STARTING")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        try:
            self.scanner = USStockScanner()
            self.market_monitor = USMarketMonitor()
            self.regime_engine = USMarketRegimeEngine()
            self.predictor = BatchPredictor(market='US')
            self.scorer = OpportunityScorer()
            self.reporter = ReportGenerator()
            
            # Optional: Email notifications
            if EmailNotifier is not None:
                self.notifier = EmailNotifier()
                logger.info("✓ Email notifications enabled")
            else:
                self.notifier = None
                logger.info("  Email notifications disabled")
            
            # Optional: Event Risk Guard
            if EventRiskGuard is not None:
                self.event_guard = EventRiskGuard()
                logger.info("✓ Event Risk Guard enabled")
            else:
                self.event_guard = None
                logger.info("  Event Risk Guard disabled")
            
            # Optional: CSV Exporter
            if CSVExporter is not None:
                self.csv_exporter = CSVExporter()
                logger.info("✓ CSV Exporter enabled")
            else:
                self.csv_exporter = None
                logger.info("  CSV Exporter disabled")
            
            # Optional: LSTM Training
            if LSTMTrainer is not None:
                self.trainer = LSTMTrainer()
                logger.info("✓ LSTM Trainer enabled")
                logger.info(f"  Training enabled: {self.config.get('lstm_training', {}).get('enabled', True)}")
                logger.info(f"  Max models per night: {self.config.get('lstm_training', {}).get('max_models_per_night', 100)}")
            else:
                self.trainer = None
                logger.info("  LSTM Trainer disabled (module not available)")
            
            # Optional: ChatGPT Research
            self.research_config = self.config.get('research', {})
            if run_chatgpt_research is not None and self.research_config.get('enabled', False):
                logger.info("✓ ChatGPT research enabled")
                logger.info(f"  Model: {self.research_config.get('model', 'gpt-4o-mini')}")
                logger.info(f"  Max stocks: {self.research_config.get('max_stocks', 5)}")
            else:
                logger.info("  ChatGPT research disabled")
            
            logger.info("✓ All required US market components initialized successfully")
        except Exception as e:
            logger.error(f"✗ Component initialization failed: {e}")
            raise
    
    def run_full_pipeline(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> Dict:
        """
        Run the complete US overnight screening pipeline
        
        Args:
            sectors: List of sector names to scan (None = all sectors)
            stocks_per_sector: Number of stocks to scan per sector
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        self.start_time = time.time()
        
        try:
            # Phase 1: US Market Sentiment
            logger.info("\n" + "="*80)
            logger.info("PHASE 1: US MARKET SENTIMENT ANALYSIS")
            logger.info("="*80)
            self.status['phase'] = 'market_sentiment'
            self.status['progress'] = 10
            
            us_sentiment = self._fetch_us_market_sentiment()
            
            # Phase 1.5: Market Regime Analysis
            logger.info("\n" + "="*80)
            logger.info("PHASE 1.5: MARKET REGIME ANALYSIS")
            logger.info("="*80)
            self.status['phase'] = 'regime_analysis'
            self.status['progress'] = 15
            
            regime_data = self._analyze_market_regime()
            
            # Phase 2: Stock Scanning
            logger.info("\n" + "="*80)
            logger.info("PHASE 2: US STOCK SCANNING")
            logger.info("="*80)
            self.status['phase'] = 'stock_scanning'
            self.status['progress'] = 20
            
            scanned_stocks = self._scan_all_us_stocks(sectors, stocks_per_sector)
            
            if not scanned_stocks:
                raise Exception("No valid US stocks found during scanning")
            
            # Phase 2.5: Event Risk Assessment (optional)
            event_risk_data = {}
            if self.event_guard is not None:
                logger.info("\n" + "="*80)
                logger.info("PHASE 2.5: EVENT RISK ASSESSMENT")
                logger.info("="*80)
                self.status['phase'] = 'event_risk_assessment'
                self.status['progress'] = 35
                
                event_risk_data = self._assess_event_risks(scanned_stocks)
            
            # Bundle market regime into event_risk_data (like ASX pipeline)
            event_risk_data['market_regime'] = regime_data
            
            # Phase 3: Batch Prediction
            logger.info("\n" + "="*80)
            logger.info("PHASE 3: BATCH PREDICTION")
            logger.info("="*80)
            self.status['phase'] = 'prediction'
            self.status['progress'] = 50
            
            predicted_stocks = self._generate_predictions(scanned_stocks, us_sentiment, event_risk_data)
            
            # Phase 4: Opportunity Scoring
            logger.info("\n" + "="*80)
            logger.info("PHASE 4: OPPORTUNITY SCORING")
            logger.info("="*80)
            self.status['phase'] = 'scoring'
            self.status['progress'] = 70
            
            scored_stocks = self._score_opportunities(predicted_stocks, us_sentiment, regime_data)
            
            # Phase 4.5: LSTM Model Training (Optional)
            logger.info("\n" + "="*80)
            logger.info("PHASE 4.5: US LSTM MODEL TRAINING (OPTIONAL)")
            logger.info("="*80)
            training_results = self._train_lstm_models(scored_stocks)
            
            # Phase 4.7: ChatGPT Research (Optional)
            research_data = self._run_chatgpt_research(scored_stocks)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: US MARKET REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_us_report(
                scored_stocks, 
                us_sentiment, 
                regime_data, 
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
                scored_stocks=scored_stocks,
                us_sentiment=us_sentiment,
                regime_data=regime_data,
                report_path=report_path
            )
            
            elapsed_time = time.time() - self.start_time
            logger.info("\n" + "="*80)
            logger.info("US PIPELINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Total Time: {elapsed_time/60:.1f} minutes")
            logger.info(f"Stocks Processed: {len(scanned_stocks)}")
            logger.info(f"Report Generated: {report_path}")
            logger.info(f"End Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            return results
            
        except Exception as e:
            logger.error(f"\n✗ US PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            self.status['phase'] = 'failed'
            self.status['errors'].append(str(e))
            self._save_error_state(e)
            raise
    
    def _fetch_us_market_sentiment(self) -> Dict:
        """Fetch US market sentiment (S&P 500, VIX, etc.)"""
        logger.info("Fetching US market sentiment data...")
        
        try:
            sentiment = self.market_monitor.get_market_overview()
            
            logger.info(f"✓ US Market Sentiment Retrieved:")
            logger.info(f"  Overall Sentiment: {sentiment['overall']['sentiment']}")
            logger.info(f"  Sentiment Score: {sentiment['overall']['score']:.1f}/100")
            logger.info(f"  S&P 500: {sentiment['sp500']['price']:.2f} ({sentiment['sp500']['day_change']:+.2f}%)")
            logger.info(f"  VIX: {sentiment['vix']['current_vix']:.2f} ({sentiment['vix']['level']})")
            logger.info(f"  Market Mood: {sentiment['vix']['market_mood']}")
            
            return sentiment
            
        except Exception as e:
            logger.warning(f"⚠ US market sentiment retrieval failed: {e}")
            logger.warning("Continuing with default sentiment...")
            
            return {
                'overall': {'sentiment': 'Neutral', 'score': 50.0, 'confidence': 'Low'},
                'sp500': {'sentiment': 'Neutral', 'sentiment_score': 50.0},
                'vix': {'current_vix': 20.0, 'level': 'Normal', 'market_mood': 'Healthy'}
            }
    
    def _analyze_market_regime(self) -> Dict:
        """Analyze market regime using HMM"""
        logger.info("Analyzing US market regime (S&P 500)...")
        
        try:
            regime = self.regime_engine.analyse()
            
            logger.info(f"✓ Market Regime Analysis Complete:")
            logger.info(f"  Regime: {regime['regime_label'].upper()}")
            logger.info(f"  Crash Risk: {regime['crash_risk_score']:.1%}")
            logger.info(f"  Annual Volatility: {regime['vol_annual']:.2%}")
            logger.info(f"  Method: {regime['method']}")
            
            return regime
            
        except Exception as e:
            logger.warning(f"⚠ Market regime analysis failed: {e}")
            return {
                'regime_label': 'medium_vol',
                'crash_risk_score': 0.20,
                'vol_annual': 0.18
            }
    
    def _scan_all_us_stocks(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> List[Dict]:
        """Scan all US stocks from specified sectors"""
        
        if sectors is None:
            sectors_to_scan = list(self.scanner.sectors.keys())
        else:
            sectors_to_scan = sectors
        
        logger.info(f"Scanning {len(sectors_to_scan)} US sectors...")
        logger.info(f"Target: {stocks_per_sector} stocks per sector")
        
        all_stocks = []
        
        for i, sector_name in enumerate(sectors_to_scan, 1):
            logger.info(f"\n[{i}/{len(sectors_to_scan)}] Scanning {sector_name}...")
            
            try:
                stocks = self.scanner.scan_sector(sector_name, max_stocks=stocks_per_sector)
                
                if stocks:
                    all_stocks.extend(stocks)
                    logger.info(f"  ✓ Found {len(stocks)} valid stocks")
                    logger.info(f"  Top 3: {', '.join([s['symbol'] for s in stocks[:3]])}")
                else:
                    logger.warning(f"  ⚠ No valid stocks found in {sector_name}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error scanning {sector_name}: {e}")
                self.status['errors'].append(f"Sector scan failed: {sector_name}")
                continue
        
        logger.info(f"\n✓ US Stock Scanning Complete:")
        logger.info(f"  Total Valid Stocks: {len(all_stocks)}")
        
        self.status['total_stocks'] = len(all_stocks)
        return all_stocks
    
    def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
        """Assess event risks for scanned stocks"""
        if self.event_guard is None:
            return {}
        
        logger.info(f"Assessing event risks for {len(stocks)} US stocks...")
        
        try:
            tickers = [s['symbol'] for s in stocks]
            results = self.event_guard.assess_batch(tickers)
            
            total_events = sum(1 for r in results.values() if hasattr(r, 'has_upcoming_event') and r.has_upcoming_event)
            sit_outs = sum(1 for r in results.values() if hasattr(r, 'skip_trading') and r.skip_trading)
            
            logger.info(f"✓ Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  Sit-Out Recommendations: {sit_outs}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Event risk assessment failed: {e}")
            return {}
    
    def _generate_predictions(self, stocks: List[Dict], sentiment: Dict, event_risk_data: Dict = None) -> List[Dict]:
        """Generate predictions for all stocks"""
        logger.info(f"Generating predictions for {len(stocks)} stocks...")
        
        try:
            # Use spi_sentiment parameter name (same as ASX pipeline)
            predicted = self.predictor.predict_batch(
                stocks=stocks,
                spi_sentiment=sentiment
            )
            
            logger.info(f"✓ Predictions Generated: {len(predicted)} stocks")
            return predicted
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return stocks  # Return stocks without predictions
    
    def _score_opportunities(self, stocks: List[Dict], sentiment: Dict, regime_data: Dict) -> List[Dict]:
        """Score trading opportunities"""
        logger.info(f"Scoring opportunities for {len(stocks)} stocks...")
        
        try:
            # Use score_opportunities method (same as ASX pipeline)
            scored = self.scorer.score_opportunities(
                stocks=stocks,
                market_sentiment=sentiment
            )
            
            # Sort by score
            scored.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            high_quality = sum(1 for s in scored if s.get('opportunity_score', 0) >= 75)
            logger.info(f"✓ Scoring Complete: {high_quality} high-quality opportunities (≥75)")
            
            return scored
            
        except Exception as e:
            logger.error(f"Opportunity scoring failed: {e}")
            return stocks
    
    def _train_lstm_models(self, scored_stocks: List[Dict]) -> Dict:
        """
        Train LSTM models for top opportunity US stocks
        
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
        
        logger.info(f"[DEBUG] US LSTM Training Check:")
        logger.info(f"  self.trainer = {self.trainer}")
        logger.info(f"  config.lstm_training.enabled = {training_enabled}")
        logger.info(f"  config.lstm_training = {lstm_config}")
        
        if not training_enabled:
            logger.info("  LSTM training disabled in configuration")
            return {'status': 'disabled', 'trained_count': 0}
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 4.5: US LSTM MODEL TRAINING")
        logger.info("="*80)
        self.status['phase'] = 'lstm_training'
        self.status['progress'] = 75
        
        try:
            # Create training queue from scored stocks
            max_models = lstm_config.get('max_models_per_night', 100)
            logger.info(f"Creating US training queue (max {max_models} stocks)...")
            
            training_queue = self.trainer.create_training_queue(
                opportunities=scored_stocks,
                max_stocks=max_models
            )
            
            # Train the models
            if training_queue:
                logger.info(f"Training {len(training_queue)} US LSTM models...")
                training_results = self.trainer.train_batch(
                    training_queue=training_queue,
                    max_stocks=max_models
                )
                
                logger.info(f"[SUCCESS] US LSTM Training Complete:")
                logger.info(f"  Models trained: {training_results.get('trained_count', 0)}/{training_results.get('total_stocks', 0)}")
                logger.info(f"  Successful: {training_results.get('trained_count', 0)}")
                logger.info(f"  Failed: {training_results.get('failed_count', 0)}")
                logger.info(f"  Total Time: {training_results.get('total_time', 0)/60:.1f} minutes")
                
                return training_results
            else:
                logger.info("No US stocks queued for training (all models are fresh)")
                return {'status': 'no_training_needed', 'trained_count': 0}
                
        except Exception as e:
            logger.error(f"✗ US LSTM training failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"US LSTM training failed: {str(e)}")
            return {'status': 'failed', 'trained_count': 0, 'error': str(e)}
    
    def _run_chatgpt_research(self, scored_stocks: List[Dict]) -> Dict:
        """
        Run ChatGPT research on top opportunity US stocks
        
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
        logger.info("PHASE 4.7: US CHATGPT RESEARCH")
        logger.info("="*80)
        self.status['phase'] = 'chatgpt_research'
        self.status['progress'] = 78
        
        try:
            # Extract config parameters
            model = research_config.get('model', 'gpt-4o-mini')
            max_stocks = research_config.get('max_stocks', 5)
            output_path_template = research_config.get('output_path', 'reports/chatgpt_research')
            
            logger.info(f"Running ChatGPT research for top {max_stocks} US opportunities...")
            logger.info(f"  Model: {model}")
            logger.info(f"  Market: US")
            
            # Run research
            research_results = run_chatgpt_research(
                opportunities=scored_stocks,
                model=model,
                max_stocks=max_stocks,
                market='US'
            )
            
            if research_results:
                # Save markdown report
                date_str = datetime.now(self.timezone).strftime("%Y%m%d")
                output_dir = BASE_PATH / output_path_template
                output_file = output_dir / f"us_research_{date_str}.md"
                
                # Prepare pipeline metadata
                pipeline_metadata = {
                    'run_id': date_str,
                    'total_opportunities': len(scored_stocks),
                    'market': 'US'
                }
                
                markdown_path = save_markdown(
                    research_results=research_results,
                    output_path=output_file,
                    market='US',
                    pipeline_metadata=pipeline_metadata
                )
                
                logger.info(f"[SUCCESS] US ChatGPT Research Complete:")
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
    
    def _generate_us_report(self, stocks: List[Dict], sentiment: Dict, 
                           regime_data: Dict, event_risk_data: Dict = None,
                           research_data: Dict = None) -> Path:
        """Generate US market morning report"""
        logger.info("Generating US market morning report...")
        
        try:
            # Prepare sector summary (group stocks by sector)
            sector_summary = {}
            
            # Group stocks by sector based on scanner's sector configuration
            for sector_name in self.scanner.sectors.keys():
                # Get stocks for this sector
                sector_stocks = [
                    s for s in stocks 
                    if s.get('symbol', '') in self.scanner.sectors[sector_name].get('stocks', [])
                ]
                
                # Calculate sector statistics
                if sector_stocks:
                    scores = [s['score'] for s in sector_stocks if 'score' in s]
                    sector_summary[sector_name] = {
                        'total_stocks': len(sector_stocks),
                        'avg_score': sum(scores) / len(scores) if scores else 0,
                        'top_score': max(scores) if scores else 0,
                        'bottom_score': min(scores) if scores else 0,
                        'score_range': (min(scores), max(scores)) if scores else (0, 0),
                        'high_quality_count': len([s for s in scores if s >= 75]),
                        'medium_quality_count': len([s for s in scores if 50 <= s < 75]),
                        'low_quality_count': len([s for s in scores if s < 50])
                    }
            
            # Prepare system stats
            elapsed_time = time.time() - self.start_time
            pred_summary = self.predictor.get_prediction_summary(stocks)
            
            system_stats = {
                'total_scanned': len(stocks),
                'buy_signals': pred_summary.get('buy_count', 0),
                'sell_signals': pred_summary.get('sell_count', 0),
                'processing_time_seconds': int(elapsed_time),
                'lstm_status': 'Available' if self.predictor.lstm_available else 'Not Available',
                'market_regime': regime_data.get('regime_label', 'Unknown'),
                'crash_risk': regime_data.get('crash_risk_score', 'Unknown')
            }
            
            # Generate report with correct parameters (matching ASX pipeline)
            report_path = self.reporter.generate_morning_report(
                opportunities=stocks,
                spi_sentiment=sentiment,  # US market sentiment
                sector_summary=sector_summary,
                system_stats=system_stats,
                event_risk_data=event_risk_data,  # Includes regime data
                research_data=research_data
            )
            
            logger.info(f"✓ Report generated: {report_path}")
            return Path(report_path)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            logger.error(f"Full error: {traceback.format_exc()}")
            
            # Create minimal fallback report
            report_dir = BASE_PATH / 'reports' / 'us'
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            fallback_path = report_dir / f'us_report_{timestamp}_error.txt'
            
            error_content = f"""US Market Report Generation Error
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Error: {e}

Stocks processed: {len(stocks)}
Sentiment: {sentiment}
Regime: {regime_data}

Full traceback:
{traceback.format_exc()}
"""
            fallback_path.write_text(error_content)
            return fallback_path
    
    def _finalize_pipeline(self, scored_stocks: List[Dict], us_sentiment: Dict, 
                          regime_data: Dict, report_path: Path) -> Dict:
        """Finalize pipeline and save results"""
        logger.info("Finalizing US pipeline...")
        
        # Get top opportunities
        top_opportunities = scored_stocks[:20]
        
        # Prepare summary
        results = {
            'market': 'US',
            'timestamp': datetime.now(self.timezone).isoformat(),
            'total_stocks': len(scored_stocks),
            'top_opportunities': top_opportunities,
            'sentiment': us_sentiment,
            'regime': regime_data,
            'report_path': str(report_path),
            'status': self.status
        }
        
        # Save JSON results
        results_dir = BASE_PATH / 'data' / 'us'
        results_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'us_pipeline_results_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"✓ Results saved: {results_file}")
        
        # Save pipeline state for tracking
        try:
            self._save_pipeline_state(results)
        except Exception as e:
            logger.warning(f"Pipeline state save failed: {e}")
        
        # Export CSV if available
        if self.csv_exporter is not None:
            try:
                csv_path = self.csv_exporter.export_screening_results(scored_stocks, us_sentiment)
                logger.info(f"✓ CSV exported: {csv_path}")
            except Exception as e:
                logger.warning(f"CSV export failed: {e}")
        
        return results
    
    def _save_error_state(self, error: Exception):
        """Save error state for debugging"""
        error_dir = BASE_PATH / 'logs' / 'screening' / 'us' / 'errors'
        error_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_file = error_dir / f'error_{timestamp}.json'
        
        error_data = {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'error': str(error),
            'traceback': traceback.format_exc(),
            'status': self.status
        }
        
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)
        
        logger.info(f"Error state saved: {error_file}")
    
    def _save_pipeline_state(self, results: Dict):
        """Save US pipeline execution state to JSON"""
        state_dir = BASE_PATH / 'reports' / 'us' / 'pipeline_state'
        state_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now(self.timezone).strftime('%Y-%m-%d')
        state_file = state_dir / f"{date_str}_us_pipeline_state.json"
        
        with open(state_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"US Pipeline state saved: {state_file}")
    
    def get_status(self) -> Dict:
        """Get current US pipeline status"""
        return self.status


def main():
    """Main entry point for US overnight pipeline"""
    pipeline = USOvernightPipeline()
    
    try:
        results = pipeline.run_full_pipeline(
            sectors=None,  # All sectors
            stocks_per_sector=30
        )
        
        print("\n" + "="*80)
        print("US PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Total Stocks Processed: {results['total_stocks']}")
        print(f"Top Opportunities: {len(results['top_opportunities'])}")
        print(f"Market Sentiment: {results['sentiment']['overall']['sentiment']}")
        print(f"Market Regime: {results['regime']['regime_label'].upper()}")
        print(f"Crash Risk: {results['regime']['crash_risk_score']:.1%}")
        print(f"Report: {results['report_path']}")
        print("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"US Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

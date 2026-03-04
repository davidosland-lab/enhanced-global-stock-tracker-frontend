"""
NYSE Overnight Pipeline Orchestrator - Complete Edition
========================================================

Complete overnight screening workflow for US markets (NYSE, NASDAQ) with:
- Original sophisticated features (FinBERT, LSTM, Event Risk, etc.)
- NEW regime intelligence (14 types, 15+ cross-market features)
- Professional-grade orchestration and error handling

Workflow:
1. Initialize all components (Original + Regime Intelligence)
2. Fetch US market sentiment and overnight data
3. Detect market regime (14 types)
4. Scan all sectors (240 stocks across 8 sectors)
5. Generate batch predictions (ML ensemble)
6. FinBERT sentiment analysis (news/earnings)
7. Event risk detection (earnings dates, dividends)
8. Score opportunities (Original + Regime-aware)
9. LSTM training for top opportunities
10. Generate morning report with regime context
11. Send notifications (Email/SMS)
12. Export CSV and JSON state

Features:
- Complete Original Pipeline (battle-tested)
- FinBERT sentiment analysis
- LSTM model training
- Event risk guard
- ML ensemble predictions
- 14 regime types detection
- 15+ cross-market features
- Regime-aware scoring
- Morning reports
- Email/SMS notifications
- CSV export
- Error recovery
- Progress tracking

Author: Trading System v1.3.13.8 - Complete System
Date: January 8, 2026
"""

import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import traceback
import pytz

# Original pipeline modules
try:
    from .us_stock_scanner import USStockScanner
    from .us_market_monitor import USMarketMonitor
    from .batch_predictor import BatchPredictor
    from .opportunity_scorer import OpportunityScorer
    from .report_generator import ReportGenerator
except ImportError:
    from us_stock_scanner import USStockScanner
    from us_market_monitor import USMarketMonitor
    from batch_predictor import BatchPredictor
    from opportunity_scorer import OpportunityScorer
    from report_generator import ReportGenerator

# Optional sophisticated modules
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

try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    try:
        from event_risk_guard import EventRiskGuard
    except ImportError:
        EventRiskGuard = None

try:
    from .csv_exporter import CSVExporter
except ImportError:
    try:
        from csv_exporter import CSVExporter
    except ImportError:
        CSVExporter = None

try:
    from .finbert_bridge import FinBERTBridge
except ImportError:
    try:
        from finbert_bridge import FinBERTBridge
    except ImportError:
        FinBERTBridge = None

# NEW: Regime Intelligence Modules
try:
    from ..market_data_fetcher import MarketDataFetcher
    from ..market_regime_detector import MarketRegimeDetector
    from ..cross_market_features import CrossMarketFeatures
    from ..regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer
    from ..enhanced_data_sources import EnhancedDataSources
    REGIME_INTELLIGENCE = True
except ImportError:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from market_data_fetcher import MarketDataFetcher
        from market_regime_detector import MarketRegimeDetector
        from cross_market_features import CrossMarketFeatures
        from regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer
        from enhanced_data_sources import EnhancedDataSources
        REGIME_INTELLIGENCE = True
    except ImportError:
        REGIME_INTELLIGENCE = False
        MarketDataFetcher = None
        MarketRegimeDetector = None
        CrossMarketFeatures = None
        RegimeAwareOpportunityScorer = None
        EnhancedDataSources = None

# Setup logging
import sys
if __name__ == "__main__":
    BASE_PATH = Path(__file__).parent.parent.parent
else:
    BASE_PATH = Path(__file__).parent.parent.parent

log_dir = BASE_PATH / 'logs' / 'screening'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'nyse_overnight_pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Windows console UTF-8 support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class NYSEOvernightPipeline:
    """
    Orchestrates the complete overnight screening pipeline for US markets.
    
    Combines original sophisticated features with NEW regime intelligence:
    - FinBERT sentiment analysis
    - LSTM model training
    - Event risk detection
    - ML ensemble predictions
    - 14 regime types detection
    - 15+ cross-market features
    - Regime-aware scoring
    """
    
    def __init__(self, enable_regime_intelligence=True):
        """Initialize the NYSE pipeline orchestrator"""
        self.timezone = pytz.timezone('America/New_York')
        self.start_time = None
        self.enable_regime_intelligence = enable_regime_intelligence and REGIME_INTELLIGENCE
        
        self.status = {
            'phase': 'initializing',
            'progress': 0,
            'total_stocks': 0,
            'processed_stocks': 0,
            'errors': [],
            'warnings': [],
            'regime_intelligence_enabled': self.enable_regime_intelligence
        }
        
        # Load configuration
        config_path = BASE_PATH / 'config' / 'screening_config.json'
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"[OK] Configuration loaded from {config_path}")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_path}, using defaults")
            self.config = self._default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}, using defaults")
            self.config = self._default_config()
        
        # Initialize components
        logger.info("=" * 80)
        logger.info("NYSE OVERNIGHT PIPELINE - COMPLETE EDITION v1.3.13.8")
        logger.info("=" * 80)
        logger.info("Market: NYSE / NASDAQ (US Markets)")
        logger.info("Trading Hours: 09:30-16:00 EST (14:30-21:00 GMT)")
        logger.info("Coverage: 240 stocks (8 sectors x 30 stocks)")
        logger.info("")
        
        # Original components
        try:
            self.scanner = USStockScanner()
            logger.info("[OK] US Stock Scanner initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize scanner: {e}")
            self.scanner = None
        
        try:
            self.market_monitor = USMarketMonitor()
            logger.info("[OK] US Market Monitor initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize market monitor: {e}")
            self.market_monitor = None
        
        try:
            self.predictor = BatchPredictor()
            logger.info("[OK] Batch Predictor initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize predictor: {e}")
            self.predictor = None
        
        try:
            self.scorer = OpportunityScorer()
            logger.info("[OK] Original Opportunity Scorer initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize scorer: {e}")
            self.scorer = None
        
        try:
            self.reporter = ReportGenerator()
            logger.info("[OK] Report Generator initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize reporter: {e}")
            self.reporter = None
        
        # Optional sophisticated modules
        if LSTMTrainer is not None:
            self.trainer = LSTMTrainer()
            logger.info("[OK] LSTM Trainer enabled")
        else:
            self.trainer = None
            logger.info("  LSTM training disabled (module not found)")
        
        if EventRiskGuard is not None:
            self.event_guard = EventRiskGuard()
            logger.info("[OK] Event Risk Guard enabled")
        else:
            self.event_guard = None
            logger.info("  Event Risk Guard disabled (module not found)")
        
        if FinBERTBridge is not None:
            self.finbert = FinBERTBridge()
            logger.info("[OK] FinBERT Sentiment Analysis enabled")
        else:
            self.finbert = None
            logger.info("  FinBERT disabled (module not found)")
        
        if CSVExporter is not None:
            self.csv_exporter = CSVExporter()
            logger.info("[OK] CSV Exporter enabled")
        else:
            self.csv_exporter = None
        
        if EmailNotifier is not None:
            self.notifier = EmailNotifier()
            logger.info("[OK] Email Notifier enabled")
        else:
            self.notifier = None
        
        # NEW: Regime Intelligence components
        if self.enable_regime_intelligence:
            logger.info("")
            logger.info("REGIME INTELLIGENCE MODULES:")
            logger.info("-" * 80)
            
            try:
                self.market_data_fetcher = MarketDataFetcher()
                logger.info("[OK] Market Data Fetcher initialized (overnight data)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize market data fetcher: {e}")
                self.market_data_fetcher = None
            
            try:
                self.regime_detector = MarketRegimeDetector()
                logger.info("[OK] Market Regime Detector initialized (14 regime types)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize regime detector: {e}")
                self.regime_detector = None
            
            try:
                self.cross_market = CrossMarketFeatures()
                logger.info("[OK] Cross-Market Features initialized (15+ features)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize cross-market features: {e}")
                self.cross_market = None
            
            try:
                self.regime_scorer = RegimeAwareOpportunityScorer()
                logger.info("[OK] Regime-Aware Scorer initialized (regime-adjusted)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize regime scorer: {e}")
                self.regime_scorer = None
            
            try:
                self.enhanced_sources = EnhancedDataSources()
                logger.info("[OK] Enhanced Data Sources initialized (Iron Ore, AU 10Y)")
            except Exception as e:
                logger.error(f"[ERROR] Failed to initialize enhanced sources: {e}")
                self.enhanced_sources = None
        else:
            logger.info("")
            logger.info("  Regime Intelligence disabled")
            self.market_data_fetcher = None
            self.regime_detector = None
            self.cross_market = None
            self.regime_scorer = None
            self.enhanced_sources = None
        
        logger.info("=" * 80)
        logger.info("")
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'lstm_training': {
                'enabled': True,
                'max_models_per_night': 100,
                'stale_threshold_days': 7
            },
            'finbert': {
                'enabled': True,
                'min_confidence': 0.7
            },
            'event_risk': {
                'enabled': True,
                'lookforward_days': 7
            },
            'regime_intelligence': {
                'enabled': True,
                'regime_weight': 0.40,
                'confidence_threshold': 0.30
            }
        }
    
    def run_pipeline(self) -> Dict:
        """
        Run the complete overnight pipeline for US markets.
        
        Returns:
            Dict with results, status, and metrics
        """
        self.start_time = time.time()
        
        try:
            logger.info("STARTING NYSE OVERNIGHT PIPELINE")
            logger.info("=" * 80)
            logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info("")
            
            # Phase 1: Market Intelligence & Regime Detection
            market_data, regime_data = self._fetch_market_intelligence()
            
            # Phase 2: Stock Scanning
            stocks = self._scan_stocks()
            
            # Phase 3: ML Predictions
            predictions = self._generate_predictions(stocks)
            
            # Phase 3.5: FinBERT Sentiment Analysis
            sentiment_data = self._analyze_sentiment(predictions)
            
            # Phase 4: Event Risk Assessment
            risk_data = self._assess_event_risk(predictions)
            
            # Phase 5: Opportunity Scoring (Original + Regime-Aware)
            scored_stocks = self._score_opportunities(predictions, regime_data, sentiment_data, risk_data)
            
            # Phase 6: LSTM Training
            lstm_results = self._train_lstm_models(scored_stocks)
            
            # Phase 7: Report Generation
            report = self._generate_report(scored_stocks, regime_data, market_data)
            
            # Phase 8: Export & Notifications
            self._export_results(scored_stocks, report)
            self._send_notifications(scored_stocks, regime_data)
            
            # Calculate metrics
            elapsed_time = time.time() - self.start_time
            
            results = {
                'status': 'success',
                'market': 'NYSE/NASDAQ',
                'total_stocks': len(stocks),
                'opportunities_found': len([s for s in scored_stocks if s.get('score', 0) > 60]),
                'regime': regime_data.get('primary_regime') if regime_data else None,
                'elapsed_time': elapsed_time,
                'timestamp': datetime.now(self.timezone).isoformat(),
                'top_picks': scored_stocks[:10] if scored_stocks else [],
                'lstm_training': lstm_results,
                'report_path': report.get('path') if report else None
            }
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE")
            logger.info(f"Total Stocks: {results['total_stocks']}")
            logger.info(f"Opportunities: {results['opportunities_found']}")
            logger.info(f"Elapsed Time: {elapsed_time:.1f}s")
            logger.info("=" * 80)
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Pipeline failed: {e}")
            logger.error(traceback.format_exc())
            return {
                'status': 'failed',
                'error': str(e),
                'elapsed_time': time.time() - self.start_time if self.start_time else 0
            }
    
    def _fetch_market_intelligence(self) -> tuple:
        """Fetch market data and detect regime"""
        logger.info("PHASE 1: MARKET INTELLIGENCE & REGIME DETECTION")
        logger.info("-" * 80)
        
        market_data = {}
        regime_data = {}
        
        if self.market_monitor:
            try:
                market_data = self.market_monitor.get_overnight_summary()
                logger.info(f"[OK] US Market data fetched")
            except Exception as e:
                logger.error(f"[ERROR] Failed to fetch market data: {e}")
        
        if self.enable_regime_intelligence and self.market_data_fetcher and self.regime_detector:
            try:
                # Fetch overnight market data
                overnight_data = self.market_data_fetcher.fetch_market_data()
                logger.info(f"[OK] Overnight market data fetched")
                
                # Fetch enhanced data
                if self.enhanced_sources:
                    enhanced_data = self.enhanced_sources.get_all_enhanced_data()
                    overnight_data.update({
                        'iron_ore_change': enhanced_data.get('iron_ore', {}).get('change_1d', 0),
                        'au_10y_change': enhanced_data.get('au_10y', {}).get('change_1d', 0)
                    })
                    logger.info(f"[OK] Enhanced data integrated")
                
                # Detect regime
                regime_data = self.regime_detector.detect_regime(overnight_data)
                logger.info(f"[OK] Regime detected: {regime_data.get('primary_regime')}")
                logger.info(f"  Confidence: {regime_data.get('confidence', 0)*100:.0f}%")
                logger.info(f"  Strength: {regime_data.get('regime_strength', 0):.2f}")
                logger.info(f"  Explanation: {regime_data.get('regime_explanation', 'N/A')}")
                
            except Exception as e:
                logger.error(f"[ERROR] Regime detection failed: {e}")
        
        logger.info("")
        return market_data, regime_data
    
    def _scan_stocks(self) -> List[Dict]:
        """Scan all US stocks (240 stocks, 8 sectors)"""
        logger.info("PHASE 2: STOCK SCANNING")
        logger.info("-" * 80)
        
        if not self.scanner:
            logger.error("[ERROR] Scanner not available")
            return []
        
        try:
            stocks = self.scanner.scan_all_sectors()
            logger.info(f"[OK] Scanned {len(stocks)} stocks across 8 sectors")
            self.status['total_stocks'] = len(stocks)
            return stocks
        except Exception as e:
            logger.error(f"[ERROR] Stock scanning failed: {e}")
            return []
    
    def _generate_predictions(self, stocks: List[Dict]) -> List[Dict]:
        """Generate ML predictions for all stocks"""
        logger.info("")
        logger.info("PHASE 3: ML PREDICTIONS")
        logger.info("-" * 80)
        
        if not self.predictor:
            logger.error("[ERROR] Predictor not available")
            return stocks
        
        try:
            predictions = self.predictor.predict_batch(stocks)
            logger.info(f"[OK] Generated predictions for {len(predictions)} stocks")
            return predictions
        except Exception as e:
            logger.error(f"[ERROR] Prediction failed: {e}")
            return stocks
    
    def _analyze_sentiment(self, stocks: List[Dict]) -> Dict:
        """Analyze sentiment using FinBERT"""
        logger.info("")
        logger.info("PHASE 3.5: FINBERT SENTIMENT ANALYSIS")
        logger.info("-" * 80)
        
        if not self.finbert:
            logger.info("  FinBERT disabled - skipping sentiment analysis")
            return {}
        
        try:
            finbert_config = self.config.get('finbert', {})
            if not finbert_config.get('enabled', True):
                logger.info("  FinBERT disabled in configuration")
                return {}
            
            sentiment_data = {}
            top_stocks = [s for s in stocks if s.get('prediction_confidence', 0) > 0.7][:50]
            
            logger.info(f"Analyzing sentiment for {len(top_stocks)} top stocks...")
            for stock in top_stocks:
                try:
                    sentiment = self.finbert.analyze_stock(stock['symbol'])
                    sentiment_data[stock['symbol']] = sentiment
                except Exception as e:
                    logger.warning(f"  Sentiment analysis failed for {stock['symbol']}: {e}")
            
            logger.info(f"[OK] Sentiment analysis complete for {len(sentiment_data)} stocks")
            return sentiment_data
            
        except Exception as e:
            logger.error(f"[ERROR] Sentiment analysis failed: {e}")
            return {}
    
    def _assess_event_risk(self, stocks: List[Dict]) -> Dict:
        """Assess event risk for all stocks"""
        logger.info("")
        logger.info("PHASE 4: EVENT RISK ASSESSMENT")
        logger.info("-" * 80)
        
        if not self.event_guard:
            logger.info("  Event Risk Guard disabled - skipping assessment")
            return {}
        
        try:
            event_config = self.config.get('event_risk', {})
            if not event_config.get('enabled', True):
                logger.info("  Event Risk Guard disabled in configuration")
                return {}
            
            risk_data = {}
            logger.info(f"Assessing event risk for {len(stocks)} stocks...")
            
            for stock in stocks:
                try:
                    risk = self.event_guard.check_events(stock['symbol'])
                    if risk.get('has_risk'):
                        risk_data[stock['symbol']] = risk
                except Exception as e:
                    logger.warning(f"  Event risk check failed for {stock['symbol']}: {e}")
            
            logger.info(f"[OK] Event risk assessment complete")
            logger.info(f"  High risk stocks: {len([r for r in risk_data.values() if r.get('risk_level') == 'high'])}")
            logger.info(f"  Medium risk stocks: {len([r for r in risk_data.values() if r.get('risk_level') == 'medium'])}")
            
            return risk_data
            
        except Exception as e:
            logger.error(f"[ERROR] Event risk assessment failed: {e}")
            return {}
    
    def _score_opportunities(self, stocks: List[Dict], regime_data: Dict, 
                            sentiment_data: Dict, risk_data: Dict) -> List[Dict]:
        """Score opportunities using both original and regime-aware scorers"""
        logger.info("")
        logger.info("PHASE 5: OPPORTUNITY SCORING")
        logger.info("-" * 80)
        
        if not self.scorer:
            logger.error("[ERROR] Scorer not available")
            return stocks
        
        try:
            # Original scoring
            scored = self.scorer.score_opportunities(stocks)
            logger.info(f"[OK] Original scoring complete for {len(scored)} stocks")
            
            # Add sentiment scores
            if sentiment_data:
                for stock in scored:
                    sentiment = sentiment_data.get(stock['symbol'], {})
                    if sentiment:
                        stock['sentiment_score'] = sentiment.get('score', 0)
                        stock['sentiment_label'] = sentiment.get('label', 'neutral')
                logger.info(f"[OK] Sentiment scores integrated")
            
            # Add event risk data
            if risk_data:
                for stock in scored:
                    risk = risk_data.get(stock['symbol'], {})
                    if risk:
                        stock['event_risk'] = risk.get('risk_level', 'low')
                        stock['risk_events'] = risk.get('events', [])
                logger.info(f"[OK] Event risk data integrated")
            
            # Regime-aware scoring
            if self.enable_regime_intelligence and self.regime_scorer and regime_data:
                logger.info("Applying regime-aware scoring...")
                regime_scored = self.regime_scorer.score_with_regime(scored, regime_data)
                logger.info(f"[OK] Regime-aware scoring complete")
                logger.info(f"  Average regime adjustment: {sum([s.get('regime_adjustment', 0) for s in regime_scored])/len(regime_scored):.2f}")
                scored = regime_scored
            
            # Sort by final score
            scored = sorted(scored, key=lambda x: x.get('final_score', x.get('score', 0)), reverse=True)
            
            logger.info(f"[OK] Final scoring complete")
            logger.info(f"  Top score: {scored[0].get('final_score', scored[0].get('score', 0)):.1f}")
            logger.info(f"  Opportunities (>60): {len([s for s in scored if s.get('final_score', s.get('score', 0)) > 60])}")
            
            return scored
            
        except Exception as e:
            logger.error(f"[ERROR] Scoring failed: {e}")
            return stocks
    
    def _train_lstm_models(self, stocks: List[Dict]) -> Dict:
        """Train LSTM models for top opportunities"""
        logger.info("")
        logger.info("PHASE 6: LSTM MODEL TRAINING")
        logger.info("-" * 80)
        
        if not self.trainer:
            logger.info("  LSTM trainer not available - skipping training")
            return {'trained': 0, 'skipped': True}
        
        try:
            lstm_config = self.config.get('lstm_training', {})
            if not lstm_config.get('enabled', True):
                logger.info("  LSTM training disabled in configuration")
                return {'trained': 0, 'skipped': True}
            
            max_models = lstm_config.get('max_models_per_night', 100)
            training_queue = [s for s in stocks if s.get('final_score', s.get('score', 0)) > 70][:max_models]
            
            if not training_queue:
                logger.info("  No stocks qualify for LSTM training (score > 70)")
                return {'trained': 0, 'skipped': True}
            
            logger.info(f"Training {len(training_queue)} LSTM models...")
            results = self.trainer.train_batch(training_queue)
            
            logger.info(f"[OK] LSTM training complete")
            logger.info(f"  Models trained: {results.get('trained', 0)}")
            logger.info(f"  Failures: {results.get('failures', 0)}")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] LSTM training failed: {e}")
            return {'trained': 0, 'error': str(e)}
    
    def _generate_report(self, stocks: List[Dict], regime_data: Dict, market_data: Dict) -> Dict:
        """Generate morning report"""
        logger.info("")
        logger.info("PHASE 7: REPORT GENERATION")
        logger.info("-" * 80)
        
        if not self.reporter:
            logger.info("  Reporter not available - skipping report")
            return {}
        
        try:
            report = self.reporter.generate_morning_report(
                stocks=stocks,
                regime_data=regime_data,
                market_data=market_data,
                market='NYSE/NASDAQ'
            )
            logger.info(f"[OK] Morning report generated")
            if report.get('path'):
                logger.info(f"  Report saved to: {report['path']}")
            
            return report
            
        except Exception as e:
            logger.error(f"[ERROR] Report generation failed: {e}")
            return {}
    
    def _export_results(self, stocks: List[Dict], report: Dict) -> None:
        """Export results to CSV"""
        logger.info("")
        logger.info("PHASE 8: EXPORT & NOTIFICATIONS")
        logger.info("-" * 80)
        
        if self.csv_exporter:
            try:
                csv_path = self.csv_exporter.export_opportunities(stocks, market='NYSE')
                logger.info(f"[OK] Results exported to CSV: {csv_path}")
            except Exception as e:
                logger.error(f"[ERROR] CSV export failed: {e}")
    
    def _send_notifications(self, stocks: List[Dict], regime_data: Dict) -> None:
        """Send email/SMS notifications"""
        if self.notifier:
            try:
                top_picks = stocks[:5]
                self.notifier.send_morning_alert(
                    opportunities=top_picks,
                    regime=regime_data.get('primary_regime'),
                    market='NYSE/NASDAQ'
                )
                logger.info(f"[OK] Notifications sent")
            except Exception as e:
                logger.error(f"[ERROR] Notification failed: {e}")


def main():
    """Main entry point"""
    pipeline = NYSEOvernightPipeline(enable_regime_intelligence=True)
    results = pipeline.run_pipeline()
    
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(json.dumps(results, indent=2, default=str))
    print("=" * 80)


if __name__ == "__main__":
    main()

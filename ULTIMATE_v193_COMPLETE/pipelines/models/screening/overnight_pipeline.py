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
import sys
import io
import numpy as np  # FIX v1.3.15.113: Add missing numpy import for _calculate_finbert_summary

# Setup UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except:
            pass

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

# [NEW] Event Risk Guard (optional)
try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    try:
        from event_risk_guard import EventRiskGuard
    except ImportError:
        EventRiskGuard = None

# [NEW] Dual Regime Analyzer (Multi-Factor + HMM)
try:
    from .dual_regime_analyzer import DualRegimeAnalyzer
except ImportError:
    try:
        from dual_regime_analyzer import DualRegimeAnalyzer
    except ImportError:
        DualRegimeAnalyzer = None

# [TOOL] FIX v1.3.15.171: Market Data Fetcher for regime detection
try:
    import sys
    from pathlib import Path
    # Add parent directory to path for models imports
    parent_dir = Path(__file__).resolve().parent.parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from models.market_data_fetcher import MarketDataFetcher
    MARKET_DATA_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[!] MarketDataFetcher not available: {e}")
    MarketDataFetcher = None
    MARKET_DATA_AVAILABLE = False

# [NEW] CSV Exporter (optional)
try:
    from .csv_exporter import CSVExporter
except ImportError:
    try:
        from csv_exporter import CSVExporter
    except ImportError:
        CSVExporter = None

# [NEW] Macro News Monitor (optional)
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    try:
        from macro_news_monitor import MacroNewsMonitor
    except ImportError:
        MacroNewsMonitor = None

# Setup logging with proper path handling
import sys
import os

# Determine base path (go up two levels from this file to reach project root)
if __name__ == "__main__":
    # FIX v1.3.15.118.2: Go up 4 levels to reach project root
    # Path: pipelines/models/screening/ -> pipelines/models/ -> pipelines/ -> root/
    BASE_PATH = Path(__file__).parent.parent.parent.parent
else:
    # FIX v1.3.15.118.2: Go up 4 levels to reach project root
    BASE_PATH = Path(__file__).parent.parent.parent.parent

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
        """Initialize the pipeline orchestrator for Australian markets"""
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
        
        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'screening_config.json'
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"[OK] Configuration loaded from {config_path}")
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
            self.predictor = BatchPredictor()
            self.scorer = OpportunityScorer()
            self.reporter = ReportGenerator()
            
            # Optional: Email notifications
            if EmailNotifier is not None:
                self.notifier = EmailNotifier()
                logger.info("[OK] Email notifications enabled")
            else:
                self.notifier = None
                logger.info("  Email notifications disabled (send_notification module not found)")
            
            # Optional: LSTM training
            if LSTMTrainer is not None:
                self.trainer = LSTMTrainer()
                logger.info("[OK] LSTM trainer enabled")
            else:
                self.trainer = None
                logger.info("  LSTM training disabled (lstm_trainer module not found)")
            
            # [NEW] v1.3.15.176: Dual Regime Analyzer (Multi-Factor + HMM)
            if DualRegimeAnalyzer is not None:
                self.regime_analyzer = DualRegimeAnalyzer(market='AU')
                logger.info("[OK] Dual Regime Analyzer enabled (Multi-Factor + HMM for AU market)")
                # Keep EventGuard reference for backward compatibility
                self.event_guard = self.regime_analyzer.event_guard
            elif EventRiskGuard is not None:
                # Fallback to EventGuard only (legacy mode)
                self.event_guard = EventRiskGuard(market='AU')
                self.regime_analyzer = None
                logger.info("[OK] Event Risk Guard enabled (AU market - Basel III, earnings protection)")
            else:
                self.event_guard = None
                self.regime_analyzer = None
                logger.info("  Event Risk Guard disabled (event_risk_guard module not found)")
            
            # [NEW] Optional: CSV Exporter
            if CSVExporter is not None:
                self.csv_exporter = CSVExporter()
                logger.info("[OK] CSV Exporter enabled (enhanced event risk export)")
            else:
                self.csv_exporter = None
                logger.info("  CSV Exporter disabled (csv_exporter module not found)")
            
            # [NEW] Optional: Macro News Monitor (ASX/RBA)
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='ASX')
                logger.info("[OK] Macro News Monitor enabled (ASX market - RBA + Global)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled (macro_news_monitor module not found)")
            
            # [NEW] v193: Optional: World Event Risk Monitor
            try:
                from pipelines.models.screening.world_event_monitor import WorldEventMonitor
                self.world_event_monitor = WorldEventMonitor()
                logger.info("[OK] World Event Risk Monitor enabled (Global geopolitical monitoring)")
            except ImportError:
                self.world_event_monitor = None
                logger.info("  World Event Risk Monitor disabled (world_event_monitor module not found)")
            
            logger.info("[OK] All required components initialized successfully")
        except Exception as e:
            logger.error(f"[X] Component initialization failed: {e}")
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
            # Phase 0.5: Fetch Overnight Market Data (FIX v1.3.15.171)
            logger.info("\n" + "="*80)
            logger.info("PHASE 0.5: OVERNIGHT MARKET DATA FETCH")
            logger.info("="*80)
            self.status['phase'] = 'market_data_fetch'
            self.status['progress'] = 5
            
            market_data = self._fetch_overnight_market_data()
            
            # Phase 1: Market Sentiment
            logger.info("\n" + "="*80)
            logger.info("PHASE 1: MARKET SENTIMENT ANALYSIS")
            logger.info("="*80)
            self.status['phase'] = 'market_sentiment'
            self.status['progress'] = 10
            
            spi_sentiment = self._fetch_market_sentiment(market_data)
            
            # Phase 2: Stock Scanning
            logger.info("\n" + "="*80)
            logger.info("PHASE 2: STOCK SCANNING")
            logger.info("="*80)
            self.status['phase'] = 'stock_scanning'
            self.status['progress'] = 20
            
            scanned_stocks = self._scan_all_stocks(sectors, stocks_per_sector)
            
            if not scanned_stocks:
                raise Exception("No valid stocks found during scanning")
            
            # [NEW] Phase 2.5: Event Risk Assessment
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
            
            # Phase 4.5: LSTM Model Training (Optional)
            lstm_training_results = self._train_lstm_models(scored_stocks)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_report(scored_stocks, spi_sentiment, event_risk_data, market_data)
            
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
                    
                    logger.info("[OK] Email notifications completed")
            except Exception as e:
                logger.warning(f"Email notification failed: {str(e)}")
                # Don't fail the pipeline if emails fail
            
            return results
            
        except Exception as e:
            logger.error(f"\n[X] PIPELINE FAILED: {e}")
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
    
    def _fetch_overnight_market_data(self) -> Dict:
        """
        Fetch overnight market data for regime detection
        FIX v1.3.15.171: Add missing market data fetch for regime detection
        
        Returns:
            Dictionary with overnight market data including:
            - US indices changes
            - Commodity changes (oil, iron ore proxy)
            - FX changes (AUD/USD, USD Index)
            - Rates changes (US 10Y, AU 10Y proxy)
            - VIX level
        """
        logger.info("[CHART] Fetching overnight market data for regime detection...")
        
        if not MARKET_DATA_AVAILABLE or MarketDataFetcher is None:
            logger.warning("[!] MarketDataFetcher not available - regime detection will use defaults")
            return {
                'sp500_change': 0.0,
                'nasdaq_change': 0.0,
                'iron_ore_change': 0.0,
                'oil_change': 0.0,
                'aud_usd_change': 0.0,
                'usd_index_change': 0.0,
                'us_10y_change': 0.0,
                'au_10y_change': 0.0,
                'vix_level': 15.0,
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'mock'
            }
        
        try:
            fetcher = MarketDataFetcher()
            market_data = fetcher.fetch_market_data(use_cache=False)
            
            logger.info(f"[OK] Overnight market data retrieved:")
            logger.info(f"  S&P 500: {market_data.get('sp500_change', 0):+.2f}%")
            logger.info(f"  NASDAQ: {market_data.get('nasdaq_change', 0):+.2f}%")
            logger.info(f"  Oil: {market_data.get('oil_change', 0):+.2f}%")
            logger.info(f"  AUD/USD: {market_data.get('aud_usd_change', 0):+.2f}%")
            logger.info(f"  VIX: {market_data.get('vix_level', 15):.1f}")
            
            market_data['data_quality'] = 'live'
            return market_data
            
        except Exception as e:
            logger.error(f"[X] Failed to fetch market data: {str(e)}")
            logger.warning("[!] Using default values for regime detection")
            return {
                'sp500_change': 0.0,
                'nasdaq_change': 0.0,
                'iron_ore_change': 0.0,
                'oil_change': 0.0,
                'aud_usd_change': 0.0,
                'usd_index_change': 0.0,
                'us_10y_change': 0.0,
                'au_10y_change': 0.0,
                'vix_level': 15.0,
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'error',
                'error': str(e)
            }
    
    def _fetch_overnight_market_data(self) -> Optional[Dict]:
        """
        Fetch overnight market data for regime detection
        FIX v1.3.15.171: Add missing market data fetch
        
        Returns:
            Dictionary with overnight market data or None if unavailable
        """
        if not MARKET_DATA_AVAILABLE or MarketDataFetcher is None:
            logger.warning("[!] MarketDataFetcher not available - regime detection will be limited")
            return None
        
        try:
            fetcher = MarketDataFetcher()
            market_data = fetcher.fetch_market_data(use_cache=False)
            
            logger.info(f"[OK] Overnight market data fetched:")
            logger.info(f"  S&P 500: {market_data.get('sp500_change', 0):.2f}%")
            logger.info(f"  NASDAQ: {market_data.get('nasdaq_change', 0):.2f}%")
            logger.info(f"  VIX: {market_data.get('vix_level', 0):.1f}")
            logger.info(f"  AUD/USD: {market_data.get('aud_usd_change', 0):.2f}%")
            logger.info(f"  Oil: {market_data.get('oil_change', 0):.2f}%")
            
            return market_data
            
        except Exception as e:
            logger.error(f"[X] Failed to fetch overnight market data: {e}")
            logger.warning("[!] Continuing without overnight data - regime detection will be limited")
            return None
    
    def _fetch_market_sentiment(self, market_data: Optional[Dict] = None) -> Dict:
        """
        Fetch SPI and US market sentiment + macro news
        FIX v1.3.15.172: Pass market_data for regime-aware gap prediction
        """
        logger.info("Fetching market sentiment data...")
        
        try:
            sentiment = self.spi_monitor.get_overnight_summary(market_data)  # FIX v1.3.15.172: Pass market_data
            
            logger.info(f"[OK] Market Sentiment Retrieved:")
            logger.info(f"  Sentiment Score: {sentiment['sentiment_score']:.1f}/100")
            logger.info(f"  Gap Prediction: {sentiment['gap_prediction']['predicted_gap_pct']:+.2f}%")
            logger.info(f"  Direction: {sentiment['gap_prediction']['direction'].upper()}")
            logger.info(f"  Recommendation: {sentiment['recommendation']['stance']}")
            
            # Initialize macro_news with default (v193.2 bugfix)
            macro_news = {
                'article_count': 0,
                'sentiment_score': 0.0,
                'sentiment_label': 'UNAVAILABLE',
                'articles': [],
                'summary': 'Macro news not available'
            }
            
            # [NEW] Phase 1.3: Macro News Monitoring (RBA/Global)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    logger.info("="*80)
                    logger.info("PHASE 1.3: MACRO NEWS MONITORING (RBA/Global)")
                    logger.info("="*80)
                    
                    macro_news = self.macro_monitor.get_macro_sentiment()
                    
                    # Add macro news to sentiment
                    sentiment['macro_news'] = macro_news
                    
                    # Log macro news results
                    logger.info(f"[OK] Macro News Analysis Complete:")
                    logger.info(f"  Articles Analyzed: {macro_news['article_count']}")
                    logger.info(f"  Sentiment Score: {macro_news['sentiment_score']:.3f} (-1 to +1)")
                    logger.info(f"  Sentiment Label: {macro_news['sentiment_label']}")
                    logger.info(f"  Summary: {macro_news['summary']}")
                    
                    if macro_news.get('top_articles'):
                        logger.info(f"\n  Recent ASX/Global News:")
                        for i, article in enumerate(macro_news['top_articles'][:3], 1):
                            logger.info(f"    {i}. {article['title'][:80]}")
                            logger.info(f"       Sentiment: {article.get('sentiment', 0.0):.3f}")
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        original_score = sentiment['sentiment_score']
                        
                        # Scale macro sentiment from [-1, 1] to impact points [-15, +15]
                        # Increased to better capture global uncertainty (US policies, trade, etc.)
                        macro_impact = macro_news['sentiment_score'] * 15
                        
                        # Apply weighted adjustment (macro news = 35% of overall sentiment)
                        # Increased from typical 20% to 35% due to heightened global uncertainty
                        # This better reflects impact of US administration policies, trade wars,
                        # geopolitical events on Australian markets
                        adjusted_score = original_score + (macro_impact * 0.35)
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to [0, 100]
                        
                        sentiment['sentiment_score'] = adjusted_score
                        sentiment['macro_adjusted'] = True
                        sentiment['macro_weight'] = 0.35  # Store weight for transparency
                        
                        logger.info(f"\n  [OK] Sentiment Adjusted for Macro News:")
                        logger.info(f"    Original Score: {original_score:.1f}")
                        logger.info(f"    Macro Impact: {macro_impact:+.1f} points (35% weight)")
                        logger.info(f"    Adjusted Score: {adjusted_score:.1f}")
                        
                        # Additional warning if macro news is strongly negative
                        if macro_news['sentiment_score'] < -0.30:
                            logger.warning(f"  [!] STRONG NEGATIVE MACRO SENTIMENT DETECTED")
                            logger.warning(f"      Global uncertainty may significantly impact ASX")
                        elif macro_news['sentiment_score'] > 0.30:
                            logger.info(f"  [+] Strong positive macro sentiment detected")
                    else:
                        sentiment['macro_adjusted'] = False
                        logger.info(f"  [INFO] No macro sentiment adjustment (neutral news)")
                    
                except Exception as e:
                    logger.warning(f"[!] Macro news monitoring failed: {e}")
                    logger.warning(f"Traceback: {traceback.format_exc()}")
                    # Set both local variable and sentiment dict (v193.2 bugfix)
                    macro_news = {
                        'article_count': 0,
                        'sentiment_score': 0.0,
                        'sentiment_label': 'UNAVAILABLE',
                        'articles': [],
                        'summary': 'Macro news monitoring failed'
                    }
                    sentiment['macro_news'] = macro_news
            
            # [NEW] v193 Phase 1.4: World Event Risk Monitoring
            if self.world_event_monitor is not None:
                try:
                    logger.info("")
                    logger.info("="*80)
                    logger.info("PHASE 1.4: WORLD EVENT RISK MONITORING")
                    logger.info("="*80)
                    
                    # Pass macro news articles for world risk analysis
                    macro_articles = macro_news.get('articles', [])
                    
                    # v193.2: Log warning if no articles available
                    if not macro_articles or len(macro_articles) == 0:
                        logger.warning(f"[!] No macro articles available for world risk analysis")
                        logger.warning(f"    Macro monitor enabled: {self.macro_monitor is not None}")
                        logger.warning(f"    Macro news article count: {macro_news.get('article_count', 0)}")
                        logger.warning(f"    Will return neutral baseline (50/100)")
                    else:
                        logger.info(f"[OK] Passing {len(macro_articles)} articles for world risk analysis")
                    
                    world_risk = self.world_event_monitor.get_world_event_risk(macro_articles)
                    
                    # Add world risk to sentiment
                    sentiment['world_event_risk'] = world_risk
                    
                    # Log world risk results
                    logger.info(f"[OK] World Event Risk Analysis Complete:")
                    logger.info(f"  World Risk Score: {world_risk['world_risk_score']:.1f}/100")
                    logger.info(f"  Risk Level: {world_risk['risk_level']}")
                    logger.info(f"  Fear Index: {world_risk['fear']:.2f}")
                    logger.info(f"  Anger Index: {world_risk['anger']:.2f}")
                    logger.info(f"  Negative Sentiment: {world_risk['neg_sent']:.2f}")
                    
                    if world_risk.get('top_topics'):
                        logger.info(f"\n  Top Risk Topics: {', '.join(world_risk['top_topics'][:5])}")
                    
                    if world_risk.get('top_headlines'):
                        logger.info(f"\n  Recent World Headlines:")
                        for i, headline in enumerate(world_risk['top_headlines'][:3], 1):
                            logger.info(f"    {i}. {headline[:80]}")
                    
                    # Adjust overall sentiment based on world risk
                    # Risk score 0-100, neutral at 50
                    risk_deviation = world_risk['world_risk_score'] - 50
                    
                    # Apply penalty for elevated risk (tune 0.25-0.50 based on testing)
                    risk_penalty = 0.35 * risk_deviation
                    
                    if abs(risk_penalty) > 2.0:  # Only adjust if meaningful
                        original_score = sentiment['sentiment_score']
                        adjusted_score = max(0, min(100, original_score - risk_penalty))
                        
                        sentiment['sentiment_score'] = adjusted_score
                        sentiment['world_risk_adjusted'] = True
                        sentiment['world_risk_weight'] = 0.35
                        
                        logger.info(f"\n  [OK] Sentiment Adjusted for World Risk:")
                        logger.info(f"    Original Score: {original_score:.1f}")
                        logger.info(f"    World Risk Penalty: {risk_penalty:+.1f} points (35% weight)")
                        logger.info(f"    Adjusted Score: {adjusted_score:.1f}")
                    else:
                        sentiment['world_risk_adjusted'] = False
                        logger.info(f"  [INFO] No world risk adjustment (risk near neutral)")
                    
                    # Critical risk warnings
                    if world_risk['world_risk_score'] >= 85:
                        logger.error(f"  [[ALERT]] CRITICAL WORLD RISK - DEFENSIVE STANCE REQUIRED")
                        logger.error(f"      Top Event: {world_risk['top_headlines'][0][:100] if world_risk['top_headlines'] else 'N/A'}")
                    elif world_risk['world_risk_score'] >= 75:
                        logger.warning(f"  [[!]] ELEVATED WORLD RISK - CAUTION ADVISED")
                    elif world_risk['world_risk_score'] <= 30:
                        logger.info(f"  [[OK]] LOW WORLD RISK - FAVORABLE GLOBAL CONDITIONS")
                    
                except Exception as e:
                    logger.warning(f"[!] World event risk monitoring failed: {e}")
                    logger.warning(f"Traceback: {traceback.format_exc()}")
                    sentiment['world_event_risk'] = {
                        'world_risk_score': 50,
                        'risk_level': 'UNAVAILABLE',
                        'fear': 0.0,
                        'anger': 0.0,
                        'neg_sent': 0.0,
                        'top_topics': [],
                        'top_headlines': []
                    }
            
            # FINAL ADJUSTMENT: Adjust gap prediction based on final sentiment score
            # If sentiment has been significantly adjusted by news/risk, modify gap prediction
            if sentiment.get('macro_adjusted') or sentiment.get('world_risk_adjusted'):
                original_gap = sentiment.get('predicted_gap_pct', 0)
                final_sentiment = sentiment.get('sentiment_score', 50)
                world_risk_score = sentiment.get('world_event_risk', {}).get('world_risk_score', 50)
                
                # Determine sentiment adjustment factor based on world risk regime
                # RISK-OFF (World Risk > 75): More aggressive adjustment (0.75)
                # NORMAL (World Risk 40-75): Moderate adjustment (0.50)
                # RISK-ON (World Risk < 40): Less adjustment (0.35)
                if world_risk_score > 75:
                    sentiment_factor = 0.75
                    regime_label = "RISK-OFF"
                elif world_risk_score < 40:
                    sentiment_factor = 0.35
                    regime_label = "RISK-ON"
                else:
                    sentiment_factor = 0.50
                    regime_label = "NORMAL"
                
                # Sentiment deviation from neutral
                sentiment_deviation = (final_sentiment - 50) / 50  # -1.0 to +1.0
                
                # FIX v193.11.6.9: Correct sentiment adjustment logic
                # When sentiment is bearish (< 50) and gap is negative: AMPLIFY the negative
                # When sentiment is bullish (> 50) and gap is positive: AMPLIFY the positive
                # When sentiment and gap disagree: DAMPEN the move
                
                # Determine if sentiment agrees with gap direction
                gap_is_negative = original_gap < 0
                sentiment_is_bearish = final_sentiment < 50
                signals_agree = (gap_is_negative and sentiment_is_bearish) or (not gap_is_negative and not sentiment_is_bearish)
                
                if signals_agree:
                    # Sentiment confirms gap direction -> AMPLIFY
                    # More extreme sentiment = stronger amplification
                    adjustment_magnitude = abs(sentiment_deviation) * sentiment_factor
                    adjusted_gap = original_gap * (1 + adjustment_magnitude)
                else:
                    # Sentiment contradicts gap direction -> DAMPEN
                    # Use negative adjustment to reduce gap magnitude
                    adjustment_magnitude = abs(sentiment_deviation) * sentiment_factor * 0.5  # Dampen less aggressively
                    adjusted_gap = original_gap * (1 - adjustment_magnitude)
                
                # CRITICAL RISK MULTIPLIER (when World Risk >= 85)
                # This amplifies moves during extreme events
                risk_multiplier = 1.0
                if world_risk_score >= 85:
                    # FIX v193.11.6.9: Correct extreme risk amplification
                    # Extreme risk should AMPLIFY negative sentiment, not dampen it
                    
                    risk_intensity = (world_risk_score - 85) / 15  # 0.0 at 85, 1.0 at 100
                    
                    if signals_agree:
                        # Sentiment and gap agree -> AMPLIFY even more
                        risk_multiplier = 1.0 + (risk_intensity * 0.5)  # Up to 1.5x at risk=100
                    else:
                        # Sentiment and gap disagree -> DAMPEN heavily
                        risk_multiplier = 1.0 - (risk_intensity * 0.4)  # Down to 0.6x at risk=100
                    
                    risk_multiplier = max(0.5, min(risk_multiplier, 1.8))  # Cap between 0.5x and 1.8x
                    adjusted_gap = adjusted_gap * risk_multiplier
                    
                    logger.warning(f"  [[ALERT]] CRITICAL RISK MULTIPLIER APPLIED: {risk_multiplier:.2f}x")
                    logger.warning(f"  World Risk: {world_risk_score:.0f}/100 - {'Amplifying' if signals_agree else 'Dampening'} gap for extreme conditions")
                
                sentiment['predicted_gap_pct'] = adjusted_gap
                sentiment['gap_adjusted'] = True
                sentiment['original_gap_pct'] = original_gap
                sentiment['sentiment_factor'] = sentiment_factor
                sentiment['risk_multiplier'] = risk_multiplier
                sentiment['regime_used'] = regime_label
                sentiment['signals_agree'] = signals_agree
                sentiment['adjustment_type'] = 'AMPLIFY' if signals_agree else 'DAMPEN'
                
                logger.info(f"\n[OK] Gap Prediction Adjusted for News/Risk:")
                logger.info(f"  Regime: {regime_label} (Sentiment Factor: {sentiment_factor:.2f})")
                logger.info(f"  Original Gap: {original_gap:+.2f}%")
                logger.info(f"  Sentiment Score: {final_sentiment:.1f}/100 (deviation: {sentiment_deviation:+.2f})")
                logger.info(f"  Sentiment & Gap: {'AGREE' if signals_agree else 'DISAGREE'} -> {'AMPLIFY' if signals_agree else 'DAMPEN'}")
                logger.info(f"  World Risk: {world_risk_score:.1f}/100")
                if risk_multiplier != 1.0:
                    logger.info(f"  Risk Multiplier: {risk_multiplier:.2f}x")
                logger.info(f"  Adjusted Gap: {adjusted_gap:+.2f}%")
                logger.info(f"  Total Impact: {(adjusted_gap - original_gap):+.2f} percentage points")
                
                # Update gap_prediction dict if it exists
                if 'gap_prediction' in sentiment:
                    sentiment['gap_prediction']['predicted_gap_pct'] = adjusted_gap
                    sentiment['gap_prediction']['adjusted'] = True
                    sentiment['gap_prediction']['original_gap'] = original_gap
                    sentiment['gap_prediction']['regime'] = regime_label
            
            return sentiment
            
        except Exception as e:
            logger.warning(f"[!] Market sentiment retrieval failed: {e}")
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
                    
                    logger.info(f"  [OK] Found {len(stocks)} valid stocks")
                    logger.info(f"  Top 3: {', '.join([s['symbol'] for s in stocks[:3]])}")
                else:
                    logger.warning(f"  [!] No valid stocks found in {sector_name}")
                    
            except Exception as e:
                logger.error(f"  [X] Error scanning {sector_name}: {e}")
                self.status['errors'].append(f"Sector scan failed: {sector_name} - {str(e)}")
                continue
        
        logger.info(f"\n[OK] Scanning Complete:")
        logger.info(f"  Total Valid Stocks: {len(all_stocks)}")
        logger.info(f"  Sectors Processed: {len(sector_summaries)}/{len(sectors_to_scan)}")
        
        self.status['total_stocks'] = len(all_stocks)
        
        return all_stocks
    
    def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
        """
        [NEW] v1.3.15.176: Assess event risks + Dual Regime Analysis (Multi-Factor + HMM)
        
        Args:
            stocks: List of scanned stock dictionaries
            
        Returns:
            Dictionary mapping ticker -> event risk data (includes 'dual_regime' key)
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
            
            logger.info(f"[OK] Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  [ALERT] Regulatory Reports (Basel III/Pillar 3): {regulatory}")
            logger.info(f"  [!]  Sit-Out Recommendations: {sit_outs}")
            logger.info(f"  [!] High Risk Stocks (>=0.7): {high_risk}")
            
            # [NEW] v1.3.15.176: Dual Regime Analysis (Multi-Factor + HMM)
            if self.regime_analyzer:
                logger.info(f"\n[DUAL] Running comprehensive regime analysis (Multi-Factor + HMM)...")
                dual_regime = self.regime_analyzer.analyze()
                results['dual_regime'] = dual_regime
                
                # Log both analyses
                combined = dual_regime.get('combined', {})
                logger.info(f"  [COMBINED] {combined.get('regime_summary', 'N/A')}")
                logger.info(f"  [COMBINED] Crash Risk: {combined.get('crash_risk_combined', 0)*100:.1f}% | Confidence: {combined.get('confidence', 'N/A')}")
                
                # Log multi-factor
                if dual_regime.get('multi_factor'):
                    mf = dual_regime['multi_factor']
                    logger.info(f"  [MF] {mf.get('regime_label', 'N/A')} | Risk: {mf.get('crash_risk_score', 0)*100:.1f}%")
                
                # Log HMM
                if dual_regime.get('hmm'):
                    hmm = dual_regime['hmm']
                    logger.info(f"  [HMM] {hmm.get('regime_label', 'N/A')} | Risk: {hmm.get('crash_risk_score', 0)*100:.1f}% | Method: {hmm.get('method', 'N/A')}")
                
                # Log trading guidance
                if combined.get('trading_guidance'):
                    logger.info(f"\n  [GUIDANCE] Trading Recommendations:")
                    for rec in combined['trading_guidance']:
                        logger.info(f"    {rec}")
                
                # Log warnings
                if combined.get('warnings'):
                    logger.info(f"\n  [WARNINGS]:")
                    for warning in combined['warnings']:
                        logger.info(f"    {warning}")
            
            # Legacy: Log market regime from EventGuard if no dual analyzer
            elif 'market_regime' in results:
                regime = results['market_regime']
                logger.info(f"  [#] Market Regime: {regime.get('regime_label', 'unknown')} | Crash Risk: {regime.get('crash_risk_score', 0)*100:.1f}%")
            
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
            logger.error(f"[X] Event risk assessment failed: {e}")
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
            
            # [NEW] Apply event risk adjustments if available
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
                            logger.debug(f"  {ticker}: Confidence {original_conf:.1f}% -> {stock['confidence']:.1f}% (haircut: {risk.weight_haircut*100:.0f}%)")
                        
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
            
            logger.info(f"[OK] Predictions Generated:")
            logger.info(f"  Total: {summary['total']}")
            logger.info(f"  BUY: {summary['buy_count']} | SELL: {summary['sell_count']} | HOLD: {summary['hold_count']}")
            logger.info(f"  Avg Confidence: {summary['avg_confidence']:.1f}%")
            logger.info(f"  High Confidence (>=70%): {summary['high_confidence_count']}")
            
            self.status['processed_stocks'] = len(predicted_stocks)
            
            return predicted_stocks
            
        except Exception as e:
            logger.error(f"[X] Prediction generation failed: {e}")
            raise
    
    def _score_opportunities(self, stocks: List[Dict], spi_sentiment: Dict) -> List[Dict]:
        """Score all opportunities"""
        logger.info(f"Scoring {len(stocks)} opportunities...")
        
        try:
            scored_stocks = self.scorer.score_opportunities(stocks, spi_sentiment)
            
            # [OK] NEW: Deduplicate by symbol (keep highest score)
            seen = {}
            for stock in scored_stocks:
                symbol = stock.get('symbol')
                score = stock.get('opportunity_score', 0)
                if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
                    seen[symbol] = stock
            
            deduplicated = list(seen.values())
            
            if len(deduplicated) < len(scored_stocks):
                duplicates_removed = len(scored_stocks) - len(deduplicated)
                logger.info(f"  [DEDUP] Removed {duplicates_removed} duplicate symbols (kept highest scores)")
            
            # Get summary
            summary = self.scorer.get_opportunity_summary(deduplicated)
            
            logger.info(f"[OK] Opportunities Scored:")
            logger.info(f"  Average Score: {summary['avg_score']:.1f}/100")
            logger.info(f"  High Opportunities (>=80): {summary['high_opportunity_count']}")
            logger.info(f"  Medium Opportunities (65-80): {summary['medium_opportunity_count']}")
            logger.info(f"  Low Opportunities (<65): {summary['low_opportunity_count']}")
            
            if summary['top_opportunities']:
                top_5 = summary['top_opportunities'][:5]
                logger.info(f"  Top 5:")
                for i, opp in enumerate(top_5, 1):
                    logger.info(f"    {i}. {opp['symbol']}: {opp['opportunity_score']:.1f}/100")
            
            return deduplicated
            
        except Exception as e:
            logger.error(f"[X] Opportunity scoring failed: {e}")
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
            logger.error(f"[X] LSTM training failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"LSTM training failed: {str(e)}")
            return {'status': 'failed', 'trained_count': 0, 'error': str(e)}
    
    def _generate_report(self, stocks: List[Dict], spi_sentiment: Dict, event_risk_data: Dict = None, market_data: Dict = None) -> str:
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
            
            # v193.6 FIX: Calculate and add aggregate FinBERT sentiment to spi_sentiment
            logger.info("[OK] Calculating aggregate FinBERT sentiment from all stocks...")
            finbert_summary = self._calculate_finbert_summary(stocks)
            
            # Add FinBERT data to spi_sentiment dict (so it's saved in report)
            spi_sentiment['finbert_sentiment'] = {
                'overall_scores': {
                    'negative': finbert_summary['avg_negative'],
                    'neutral': finbert_summary['avg_neutral'],
                    'positive': finbert_summary['avg_positive']
                },
                'compound': finbert_summary['avg_compound'],
                'confidence': finbert_summary['avg_confidence'],
                'dominant_sentiment': finbert_summary['dominant_sentiment'],
                'stock_count': finbert_summary['count']
            }
            logger.info(f"[OK] FinBERT Aggregate Sentiment: {finbert_summary['dominant_sentiment'].upper()}")
            logger.info(f"    Negative: {finbert_summary['avg_negative']:.3f} ({finbert_summary['avg_negative']*100:.1f}%)")
            logger.info(f"    Neutral:  {finbert_summary['avg_neutral']:.3f} ({finbert_summary['avg_neutral']*100:.1f}%)")
            logger.info(f"    Positive: {finbert_summary['avg_positive']:.3f} ({finbert_summary['avg_positive']*100:.1f}%)")
            logger.info(f"    Compound: {finbert_summary['avg_compound']:+.3f}")
            logger.info(f"    Stocks Analyzed: {finbert_summary['count']}")
            
            # Generate report
            report_path = self.reporter.generate_morning_report(
                opportunities=stocks,
                spi_sentiment=spi_sentiment,
                sector_summary=sector_summary,
                system_stats=system_stats,
                event_risk_data=event_risk_data,
                market_data=market_data  # FIX v1.3.15.171: Pass market data for regime detection
            )
            
            logger.info(f"[OK] Report Generated: {report_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"[X] Report generation failed: {e}")
            raise
    
    def _calculate_finbert_summary(self, stocks: List[Dict]) -> Dict:
        """
        Calculate aggregate FinBERT v4.4.4 sentiment from all stocks
        
        Args:
            stocks: List of stocks with sentiment data
        
        Returns:
            Aggregated FinBERT sentiment breakdown
        """
        sentiments = []
        for stock in stocks:
            # Check for sentiment_scores (from FinBERT bridge)
            if 'sentiment_scores' in stock:
                sentiments.append(stock['sentiment_scores'])
            # Fallback: check components for sentiment data
            elif 'components' in stock and 'sentiment' in stock['components']:
                comp = stock['components']['sentiment']
                if isinstance(comp, dict) and 'scores' in comp:
                    sentiments.append(comp['scores'])
        
        if not sentiments:
            logger.warning("[!] No FinBERT sentiment data found in stocks, using neutral defaults")
            return {
                'avg_negative': 0.33,
                'avg_neutral': 0.34,
                'avg_positive': 0.33,
                'avg_compound': 0.0,
                'avg_confidence': 50,
                'dominant_sentiment': 'neutral',
                'count': 0
            }
        
        # Aggregate scores
        avg_negative = np.mean([s.get('negative', 0.33) for s in sentiments])
        avg_neutral = np.mean([s.get('neutral', 0.34) for s in sentiments])
        avg_positive = np.mean([s.get('positive', 0.33) for s in sentiments])
        
        # Calculate compound from scores
        avg_compound = avg_positive - avg_negative
        
        # Calculate confidence (average of individual confidences if available)
        confidences = []
        for stock in stocks:
            if 'sentiment_scores' in stock and 'confidence' in stock['sentiment_scores']:
                confidences.append(stock['sentiment_scores']['confidence'])
            elif 'confidence' in stock:
                confidences.append(stock['confidence'])
        
        avg_confidence = np.mean(confidences) if confidences else 50
        
        # Determine dominant sentiment
        scores = {
            'negative': avg_negative,
            'neutral': avg_neutral,
            'positive': avg_positive
        }
        dominant = max(scores, key=scores.get)
        
        logger.info(f"[FINBERT v4.4.4] Sentiment summary: {dominant.upper()} "
                   f"(neg: {avg_negative:.2%}, neu: {avg_neutral:.2%}, pos: {avg_positive:.2%}, "
                   f"compound: {avg_compound:.3f}, analyzed: {len(sentiments)} stocks)")
        
        return {
            'avg_negative': round(avg_negative, 4),
            'avg_neutral': round(avg_neutral, 4),
            'avg_positive': round(avg_positive, 4),
            'avg_compound': round(avg_compound, 4),
            'avg_confidence': round(avg_confidence, 2),
            'dominant_sentiment': dominant,
            'count': len(sentiments)
        }
    
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
                # FIX v1.3.15.118.3: Try multiple keys for opportunity score
                'opportunity_score': opp.get('opportunity_score', opp.get('score', 0)),
                'signal': opp.get('prediction', 'HOLD'),
                'confidence': opp.get('confidence', 0),
                'sector': opp.get('sector', 'Unknown'),
                'current_price': opp['price']
            }
            for opp in top_opportunities
        ]
        
        # [NEW] Export CSV with event risk data
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
                logger.info(f"[OK] CSV exports complete")
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
        
        # [NEW] INTEGRATION FIX: Save in format expected by trading platform
        # Signal adapter looks for: reports/screening/au_morning_report.json
        try:
            trading_report_dir = BASE_PATH / 'reports' / 'screening'
            trading_report_dir.mkdir(parents=True, exist_ok=True)
            
            # AU market report (SPI-based sentiment)
            market_code = 'au'
            
            # Calculate FinBERT v4.4.4 sentiment summary (NEW in v1.3.15.45)
            finbert_summary = self._calculate_finbert_summary(scored_stocks)
            
            trading_report = {
                'generated_at': datetime.now(self.timezone).isoformat(),
                'report_date': datetime.now(self.timezone).strftime('%Y-%m-%d'),
                'overall_sentiment': spi_sentiment['sentiment_score'],
                'confidence': 'HIGH' if spi_sentiment['sentiment_score'] > 70 else 'MODERATE' if spi_sentiment['sentiment_score'] > 50 else 'LOW',
                'risk_rating': spi_sentiment['recommendation'].get('risk_rating', 'Moderate'),
                'volatility_level': 'High' if spi_sentiment.get('spi_volatility', 0) > 20 else 'Normal',
                'recommendation': spi_sentiment['recommendation']['stance'],
                
                # NEW: Full FinBERT v4.4.4 sentiment breakdown (like your screenshot)
                'finbert_sentiment': {
                    'overall_scores': {
                        'negative': finbert_summary['avg_negative'],
                        'neutral': finbert_summary['avg_neutral'],
                        'positive': finbert_summary['avg_positive']
                    },
                    'compound': finbert_summary['avg_compound'],
                    'sentiment_label': finbert_summary['dominant_sentiment'],
                    'confidence': finbert_summary['avg_confidence'],
                    'stocks_analyzed': finbert_summary['count'],
                    'method': 'FinBERT v4.4.4'
                },
                
                'top_opportunities': top_opps_detailed,
                'spi_sentiment': spi_sentiment,
                
                # v193.6: Explicitly add world_event_risk and macro_news for dashboard
                'world_event_risk': spi_sentiment.get('world_event_risk', {}),
                'macro_news': spi_sentiment.get('macro_news', {}),
                
                'summary': results['summary']
            }
            
            trading_report_path = trading_report_dir / f'{market_code}_morning_report.json'
            with open(trading_report_path, 'w') as f:
                json.dump(trading_report, f, indent=2, default=str)
            
            logger.info(f"[OK] Trading platform report saved: {trading_report_path}")
            logger.info(f"     This report will be used by run_pipeline_enhanced_trading.py")
            
        except Exception as e:
            logger.warning(f"[!]  Failed to save trading platform report: {e}")
            # Don't fail pipeline if this fails
        
        logger.info("[OK] Pipeline finalized")
        
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

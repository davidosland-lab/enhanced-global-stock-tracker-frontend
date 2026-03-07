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
    from .lstm_trainer import LSTMTrainer
except ImportError:
    try:
        from lstm_trainer import LSTMTrainer
    except ImportError:
        LSTMTrainer = None

try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    EventRiskGuard = None

# 🆕 Dual Regime Analyzer (Multi-Factor + HMM)
try:
    from .dual_regime_analyzer import DualRegimeAnalyzer
except ImportError:
    try:
        from dual_regime_analyzer import DualRegimeAnalyzer
    except ImportError:
        DualRegimeAnalyzer = None

try:
    from .csv_exporter import CSVExporter
except ImportError:
    CSVExporter = None

# Macro news monitoring
try:
    from .macro_news_monitor import MacroNewsMonitor
except ImportError:
    MacroNewsMonitor = None

# Setup logging
# FIX v1.3.15.118.2: Go up 4 levels to reach project root
# Path: pipelines/models/screening/ -> pipelines/models/ -> pipelines/ -> root/
BASE_PATH = Path(__file__).parent.parent.parent.parent
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
        
        # Load configuration (for LSTM training settings)
        config_path = BASE_PATH / 'pipelines' / 'config' / 'screening_config.json'
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"[OK] Configuration loaded from {config_path}")
        except FileNotFoundError:
            self.config = {
                'lstm_training': {
                    'enabled': True,
                    'max_models_per_night': 100
                }
            }
            logger.warning(f"[!] Configuration file not found at {config_path}, using defaults")
        
        # Initialize components
        logger.info("="*80)
        logger.info("US OVERNIGHT STOCK SCREENING PIPELINE - STARTING")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        try:
            self.scanner = USStockScanner()
            self.market_monitor = USMarketMonitor()
            
            # 🆕 v1.3.15.176: Dual Regime Analyzer (Multi-Factor + HMM)
            if DualRegimeAnalyzer is not None:
                self.regime_analyzer = DualRegimeAnalyzer(market='US')
                logger.info("[OK] Dual Regime Analyzer enabled (Multi-Factor + HMM for US market)")
                # Keep regime_engine reference for backward compatibility
                self.regime_engine = self.regime_analyzer.hmm_engine
            else:
                # Fallback to HMM only (legacy mode)
                self.regime_engine = USMarketRegimeEngine()
                self.regime_analyzer = None
                logger.info("[OK] US Market Regime Engine enabled (HMM only)")
            
            self.predictor = BatchPredictor()
            self.scorer = OpportunityScorer()
            self.reporter = ReportGenerator()
            
            # Optional: Email notifications
            if EmailNotifier is not None:
                self.notifier = EmailNotifier()
                logger.info("[OK] Email notifications enabled")
            else:
                self.notifier = None
                logger.info("  Email notifications disabled")
            
            # Optional: LSTM training
            if LSTMTrainer is not None:
                self.trainer = LSTMTrainer()
                logger.info("[OK] LSTM trainer enabled")
            else:
                self.trainer = None
                logger.info("  LSTM training disabled (lstm_trainer module not found)")
            
            # Optional: Event Risk Guard (US market)
            if EventRiskGuard is not None:
                self.event_guard = EventRiskGuard(market='US')
                logger.info("[OK] Event Risk Guard enabled (US market)")
            else:
                self.event_guard = None
                logger.info("  Event Risk Guard disabled")
            
            # Optional: CSV Exporter
            if CSVExporter is not None:
                self.csv_exporter = CSVExporter()
                logger.info("[OK] CSV Exporter enabled")
            else:
                self.csv_exporter = None
                logger.info("  CSV Exporter disabled")
            
            # Optional: Macro News Monitor
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='US')
                logger.info("[OK] Macro News Monitor enabled (Fed/economic data)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")
            
            # 🆕 v193: Optional: World Event Risk Monitor
            try:
                from .world_event_monitor import WorldEventMonitor
                self.world_event_monitor = WorldEventMonitor()
                logger.info("[OK] World Event Risk Monitor enabled (Global geopolitical monitoring)")
            except ImportError:
                self.world_event_monitor = None
                logger.info("  World Event Risk Monitor disabled (world_event_monitor module not found)")
            
            logger.info("[OK] All required US market components initialized successfully")
        except Exception as e:
            logger.error(f"[X] Component initialization failed: {e}")
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
            lstm_training_results = self._train_lstm_models(scored_stocks)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: US MARKET REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_us_report(scored_stocks, us_sentiment, regime_data, event_risk_data)
            
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
            logger.error(f"\n[X] US PIPELINE FAILED: {e}")
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
            
            logger.info(f"[OK] US Market Sentiment Retrieved:")
            logger.info(f"  Overall Sentiment: {sentiment['overall']['sentiment']}")
            logger.info(f"  Sentiment Score: {sentiment['overall']['score']:.1f}/100")
            logger.info(f"  S&P 500: {sentiment['sp500']['price']:.2f} ({sentiment['sp500']['day_change']:+.2f}%)")
            logger.info(f"  VIX: {sentiment['vix']['current_vix']:.2f} ({sentiment['vix']['level']})")
            logger.info(f"  Market Mood: {sentiment['vix']['market_mood']}")
            
            # Initialize macro_news with default (v193.2 bugfix)
            macro_news = {
                'article_count': 0,
                'sentiment_score': 0.0,
                'sentiment_label': 'UNAVAILABLE',
                'articles': [],
                'summary': 'Macro news not available'
            }
            
            # Phase 1.3: Macro News Monitoring (Fed announcements, economic data)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    logger.info("="*80)
                    logger.info("PHASE 1.3: MACRO NEWS MONITORING (Fed/Economic Data)")
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
                    
                    if macro_news['top_articles']:
                        logger.info(f"\n  Recent Fed News:")
                        for i, article in enumerate(macro_news['top_articles'][:3], 1):
                            logger.info(f"    {i}. {article['title'][:80]}")
                            # FIX v193.7: Use safe .get() to avoid KeyError if sentiment missing
                            sentiment_val = article.get('sentiment', 0.0)
                            logger.info(f"       Sentiment: {sentiment_val:.3f}")
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        original_score = sentiment['overall']['score']
                        
                        # Scale macro sentiment from [-1, 1] to impact points [-15, +15]
                        # Increased from ±10 to ±15 to better capture global uncertainty
                        macro_impact = macro_news['sentiment_score'] * 15
                        
                        # Apply weighted adjustment (macro news = 35% of overall sentiment)
                        # Increased from 20% to 35% due to heightened global political uncertainty
                        # This better reflects impact of administration policies, trade wars,
                        # geopolitical events on US markets
                        adjusted_score = original_score + (macro_impact * 0.35)
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to [0, 100]
                        
                        sentiment['overall']['score'] = adjusted_score
                        sentiment['overall']['macro_adjusted'] = True
                        sentiment['overall']['macro_weight'] = 0.35  # Store weight for transparency
                        
                        logger.info(f"\n  [OK] Sentiment Adjusted for Macro News:")
                        logger.info(f"    Original Score: {original_score:.1f}")
                        logger.info(f"    Macro Impact: {macro_impact:+.1f} points (35% weight)")
                        logger.info(f"    Adjusted Score: {adjusted_score:.1f}")
                        
                        # Additional warning if macro news is strongly negative
                        if macro_news['sentiment_score'] < -0.30:
                            logger.warning(f"  [!] STRONG NEGATIVE MACRO SENTIMENT DETECTED")
                            logger.warning(f"      Global uncertainty may significantly impact US markets")
                        elif macro_news['sentiment_score'] > 0.30:
                            logger.info(f"  [+] Strong positive macro sentiment detected")
                    else:
                        sentiment['overall']['macro_adjusted'] = False
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
            
            # 🆕 v193 Phase 1.4: World Event Risk Monitoring
            if hasattr(self, 'world_event_monitor') and self.world_event_monitor is not None:
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
                        original_score = sentiment['overall']['score']
                        adjusted_score = max(0, min(100, original_score - risk_penalty))
                        
                        sentiment['overall']['score'] = adjusted_score
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
            
            return sentiment
            
        except Exception as e:
            logger.warning(f"[!] US market sentiment retrieval failed: {e}")
            logger.warning("Continuing with default sentiment...")
            
            return {
                'overall': {'sentiment': 'Neutral', 'score': 50.0, 'confidence': 'Low'},
                'sp500': {'sentiment': 'Neutral', 'sentiment_score': 50.0},
                'vix': {'current_vix': 20.0, 'level': 'Normal', 'market_mood': 'Healthy'}
            }
    
    def _analyze_market_regime(self) -> Dict:
        """🆕 v1.3.15.176: Analyze market regime using Dual Method (Multi-Factor + HMM)"""
        logger.info("Analyzing US market regime...")
        
        try:
            # 🆕 v1.3.15.176: Use dual regime analyzer if available
            if hasattr(self, 'regime_analyzer') and self.regime_analyzer:
                logger.info("[DUAL] Running comprehensive regime analysis (Multi-Factor + HMM)...")
                dual_regime = self.regime_analyzer.analyze()
                
                # Log both analyses
                combined = dual_regime.get('combined', {})
                logger.info(f"[OK] Dual Regime Analysis Complete:")
                logger.info(f"  [COMBINED] {combined.get('regime_summary', 'N/A')}")
                logger.info(f"  [COMBINED] Crash Risk: {combined.get('crash_risk_combined', 0):.1%} | Confidence: {combined.get('confidence', 'N/A')}")
                
                # Log multi-factor
                if dual_regime.get('multi_factor'):
                    mf = dual_regime['multi_factor']
                    logger.info(f"  [MF] {mf.get('regime_label', 'N/A')} | Risk: {mf.get('crash_risk_score', 0):.1%}")
                
                # Log HMM
                if dual_regime.get('hmm'):
                    hmm = dual_regime['hmm']
                    logger.info(f"  [HMM] {hmm.get('regime_label', 'N/A')} | Risk: {hmm.get('crash_risk_score', 0):.1%} | Method: {hmm.get('method', 'N/A')}")
                    logger.info(f"  [HMM] Annual Volatility: {hmm.get('vol_annual', 0):.2%}")
                
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
                
                # Return combined regime for backward compatibility
                return {
                    'dual_regime': dual_regime,
                    'regime_label': dual_regime.get('hmm', {}).get('regime_label', 'medium_vol'),
                    'crash_risk_score': combined.get('crash_risk_combined', 0.20),
                    'vol_annual': dual_regime.get('hmm', {}).get('vol_annual', 0.18),
                    'method': 'Dual (Multi-Factor + HMM)',
                    'combined': combined
                }
            
            # Legacy: HMM only
            elif self.regime_engine:
                regime = self.regime_engine.analyse()
                
                logger.info(f"[OK] Market Regime Analysis Complete (HMM only):")
                logger.info(f"  Regime: {regime['regime_label'].upper()}")
                logger.info(f"  Crash Risk: {regime['crash_risk_score']:.1%}")
                logger.info(f"  Annual Volatility: {regime['vol_annual']:.2%}")
                logger.info(f"  Method: {regime['method']}")
                
                return regime
            
            else:
                # No regime engine available
                return {
                    'regime_label': 'medium_vol',
                    'crash_risk_score': 0.20,
                    'vol_annual': 0.18,
                    'method': 'Default'
                }
            
        except Exception as e:
            logger.warning(f"[!] Market regime analysis failed: {e}")
            return {
                'regime_label': 'medium_vol',
                'crash_risk_score': 0.20,
                'vol_annual': 0.18,
                'method': 'Fallback (Error)'
            }
    
    def _scan_all_us_stocks(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> List[Dict]:
        """Scan all US stocks from specified sectors"""
        
        if sectors is None:
            sectors_to_scan = list(self.scanner.sectors.keys())
        else:
            sectors_to_scan = sectors
        
        total_expected = len(sectors_to_scan) * stocks_per_sector
        logger.info(f"Scanning {len(sectors_to_scan)} US sectors...")
        logger.info(f"Target: {stocks_per_sector} stocks per sector (~{total_expected} total stocks)")
        logger.info("")
        
        all_stocks = []
        total_processed = 0
        
        for i, sector_name in enumerate(sectors_to_scan, 1):
            logger.info(f"[{i}/{len(sectors_to_scan)}] Scanning {sector_name}...")
            
            try:
                stocks = self.scanner.scan_sector(sector_name, max_stocks=stocks_per_sector)
                
                if stocks:
                    all_stocks.extend(stocks)
                    total_processed += len(stocks)
                    logger.info(f"  [OK] {sector_name}: {len(stocks)} stocks analyzed")
                    # Format top 3 stocks with scores
                    top_3 = ', '.join([f"{s['symbol']} ({s['score']:.0f})" for s in stocks[:3]])
                    logger.info(f"  Top 3: {top_3}")
                    logger.info(f"  Progress: {total_processed}/{total_expected} stocks ({total_processed/total_expected*100:.1f}%)")
                    logger.info("")
                else:
                    logger.warning(f"  [!] No valid stocks found in {sector_name}")
                    logger.info("")
                    
            except Exception as e:
                logger.error(f"  [X] Error scanning {sector_name}: {e}")
                self.status['errors'].append(f"Sector scan failed: {sector_name}")
                logger.info("")
                continue
        
        logger.info(f"\n[OK] US Stock Scanning Complete:")
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
            
            logger.info(f"[OK] Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  Sit-Out Recommendations: {sit_outs}")
            
            return results
            
        except Exception as e:
            logger.error(f"[X] Event risk assessment failed: {e}")
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
            
            logger.info(f"[OK] Predictions Generated: {len(predicted)} stocks")
            return predicted
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return stocks  # Return stocks without predictions
    
    def _score_opportunities(self, stocks: List[Dict], sentiment: Dict, regime_data: Dict) -> List[Dict]:
        """Score trading opportunities"""
        logger.info(f"Scoring opportunities for {len(stocks)} stocks...")
        
        try:
            # Call scorer with correct parameter names
            scored = self.scorer.score_opportunities(
                stocks_with_predictions=stocks,
                spi_sentiment=sentiment
            )
            
            # Sort by score
            scored.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            # [OK] NEW: Deduplicate by symbol (keep highest score)
            seen = {}
            for stock in scored:
                symbol = stock.get('symbol')
                score = stock.get('opportunity_score', 0)
                if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
                    seen[symbol] = stock
            
            deduplicated = list(seen.values())
            
            if len(deduplicated) < len(scored):
                duplicates_removed = len(scored) - len(deduplicated)
                logger.info(f"  [DEDUP] Removed {duplicates_removed} duplicate symbols (kept highest scores)")
            
            # Re-sort after deduplication
            deduplicated.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            high_quality = sum(1 for s in deduplicated if s.get('opportunity_score', 0) >= 75)
            logger.info(f"[OK] Scoring Complete: {high_quality} high-quality opportunities (>=75)")
            
            return deduplicated
            
        except Exception as e:
            logger.error(f"Opportunity scoring failed: {e}")
            return stocks
    
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
                return {'status': 'skipped', 'trained_count': 0}
                
        except Exception as e:
            logger.error(f"[X] LSTM training failed: {e}")
            logger.error(traceback.format_exc())
            self.status['warnings'].append(f"LSTM training failed: {str(e)}")
            return {'status': 'failed', 'trained_count': 0, 'error': str(e)}
    
    def _generate_us_report(self, stocks: List[Dict], sentiment: Dict, 
                           regime_data: Dict, event_risk_data: Dict = None) -> Path:
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
            
            # FIX v193.7: Add FinBERT sentiment aggregate to sentiment dict
            logger.info("[OK] Calculating aggregate FinBERT sentiment for US report...")
            finbert_summary = self._calculate_finbert_summary(stocks)
            
            # Add FinBERT sentiment to sentiment dict (same as AU pipeline v193.6)
            sentiment['finbert_sentiment'] = {
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
            
            logger.info(f"[OK] FinBERT sentiment added to sentiment dict: {finbert_summary['dominant_sentiment'].upper()}")
            logger.info(f"     Negative: {finbert_summary['avg_negative']:.2%}, "
                       f"Neutral: {finbert_summary['avg_neutral']:.2%}, "
                       f"Positive: {finbert_summary['avg_positive']:.2%}")
            
            # Generate report with correct parameters (matching ASX pipeline)
            report_path = self.reporter.generate_morning_report(
                opportunities=stocks,
                spi_sentiment=sentiment,  # US market sentiment
                sector_summary=sector_summary,
                system_stats=system_stats,
                event_risk_data=event_risk_data  # Includes regime data
            )
            
            logger.info(f"[OK] Report generated: {report_path}")
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
            'status': 'success',  # [OK] String instead of dict
            'execution_time_seconds': int(time.time() - self.start_time),
            'execution_time_minutes': round((time.time() - self.start_time) / 60, 2),
            'statistics': {
                'total_stocks_scanned': len(scored_stocks),
                'top_opportunities_count': len(top_opportunities),
                'high_confidence_count': len([s for s in scored_stocks if s.get('confidence', 0) >= 70]),
                'buy_signals': len([s for s in scored_stocks if s.get('prediction') == 'BUY']),
                'sell_signals': len([s for s in scored_stocks if s.get('prediction') == 'SELL']),
                'hold_signals': len([s for s in scored_stocks if s.get('prediction') == 'HOLD'])
            }
        }
        
        # Save JSON results
        results_dir = BASE_PATH / 'data' / 'us'
        results_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'us_pipeline_results_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"[OK] Results saved: {results_file}")
        
        # Export CSV if available
        if self.csv_exporter is not None:
            try:
                csv_path = self.csv_exporter.export_screening_results(scored_stocks, us_sentiment)
                logger.info(f"[OK] CSV exported: {csv_path}")
            except Exception as e:
                logger.warning(f"CSV export failed: {e}")
        
        # 🆕 INTEGRATION FIX: Save in format expected by trading platform
        # Signal adapter looks for: reports/screening/us_morning_report.json
        try:
            trading_report_dir = BASE_PATH / 'reports' / 'screening'
            trading_report_dir.mkdir(parents=True, exist_ok=True)
            
            trading_report = {
                'timestamp': datetime.now(self.timezone).isoformat(),
                'market': 'US',
                'market_sentiment': {
                    'sentiment_score': us_sentiment.get('overall', {}).get('sentiment_score', 50.0),
                    'confidence': 'HIGH' if us_sentiment.get('overall', {}).get('sentiment_score', 50.0) > 70 else 'MODERATE',
                    'risk_rating': 'Low' if regime_data.get('crash_risk_score', 0) < 0.3 else 'Moderate' if regime_data.get('crash_risk_score', 0) < 0.6 else 'High',
                    'volatility_level': 'High' if us_sentiment.get('vix', {}).get('current_level', 15) > 20 else 'Normal',
                    'recommendation': us_sentiment.get('overall', {}).get('sentiment', 'NEUTRAL')
                },
                # FIX v193.7: Add FinBERT sentiment for dashboard (matching AU pipeline v193.6)
                'finbert_sentiment': us_sentiment.get('finbert_sentiment', {
                    'overall_scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33},
                    'compound': 0.0,
                    'confidence': 50,
                    'dominant_sentiment': 'neutral',
                    'stock_count': 0
                }),
                # Also include macro_news and world_event_risk if available
                'macro_news': us_sentiment.get('macro_news', {}),
                'world_event_risk': us_sentiment.get('world_event_risk', {}),
                'top_opportunities': [
                    {
                        'symbol': opp['symbol'],
                        'name': opp.get('name', opp['symbol']),
                        # FIX v1.3.15.118.3: Try multiple keys for opportunity score
                        'opportunity_score': opp.get('opportunity_score', opp.get('score', 0)),
                        'prediction': opp.get('prediction', 'HOLD'),
                        'confidence': opp.get('confidence', 0),
                        'expected_return': opp.get('expected_return', 0),
                        'risk_level': opp.get('risk_level', 'Medium'),
                        'technical_strength': opp.get('technical_strength', 50),
                        'sector': opp.get('sector', 'Unknown'),
                        'current_price': opp.get('price', 0)
                    }
                    for opp in top_opportunities
                ]
            }
            
            trading_report_path = trading_report_dir / 'us_morning_report.json'
            with open(trading_report_path, 'w') as f:
                json.dump(trading_report, f, indent=2, default=str)
            
            logger.info(f"[OK] Trading platform report saved: {trading_report_path}")
            logger.info(f"     This report will be used by run_pipeline_enhanced_trading.py")
            results['trading_report_path'] = str(trading_report_path)
            
        except Exception as e:
            logger.warning(f"[!]  Failed to save trading platform report: {e}")
            # Don't fail pipeline if this fails
        
        return results
    
    def _calculate_finbert_summary(self, stocks: List[Dict]) -> Dict:
        """
        Calculate aggregate FinBERT v4.4.4 sentiment from all stocks
        
        Args:
            stocks: List of stocks with sentiment data
        
        Returns:
            Aggregated FinBERT sentiment breakdown
        """
        import numpy as np
        
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

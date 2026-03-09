"""
UK Overnight Pipeline Orchestrator

Main orchestration module for UK/LSE market screening workflow.
Coordinates all modules and handles error recovery, progress tracking, and logging.

Workflow:
1. Initialize all components
2. Fetch UK market sentiment (FTSE 100)
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

# Import shared modules (reuse with UK market parameter)
try:
    from .stock_scanner import StockScanner  # Generic scanner
    from .batch_predictor import BatchPredictor
    from .opportunity_scorer import OpportunityScorer
    from .report_generator import ReportGenerator
except ImportError:
    from stock_scanner import StockScanner
    from batch_predictor import BatchPredictor
    from opportunity_scorer import OpportunityScorer
    from report_generator import ReportGenerator

# Optional modules
try:
    from .send_notification import EmailNotifier
except ImportError:
    EmailNotifier = None

# FIX v1.3.15.193.11.6.10: Import Realtime FTSE Predictor for pre-market gap analysis
try:
    from .ftse_proxy_realtime import RealtimeFTSEPredictor
    REALTIME_FTSE_AVAILABLE = True
except ImportError:
    logger.warning("Realtime FTSE Predictor module not available")
    REALTIME_FTSE_AVAILABLE = False

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
log_dir = BASE_PATH / 'logs' / 'screening' / 'uk'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'uk_overnight_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class UKOvernightPipeline:
    """
    Orchestrates the complete UK/LSE market overnight screening pipeline.
    """
    
    def __init__(self):
        """Initialize the UK pipeline orchestrator"""
        self.timezone = pytz.timezone('Europe/London')
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
        logger.info("UK/LSE OVERNIGHT STOCK SCREENING PIPELINE - STARTING")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        try:
            # Use generic scanner with UK market config
            # FIX v1.3.15.118.4: Config file is in pipelines/config/
            uk_config_path = BASE_PATH / 'pipelines' / 'config' / 'uk_sectors.json'
            self.scanner = StockScanner(config_path=str(uk_config_path))
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
            
            # 🆕 v1.3.15.176: Dual Regime Analyzer (Multi-Factor + HMM)
            if DualRegimeAnalyzer is not None:
                self.regime_analyzer = DualRegimeAnalyzer(market='UK')
                logger.info("[OK] Dual Regime Analyzer enabled (Multi-Factor + HMM for UK market)")
                # Keep EventGuard reference for backward compatibility
                self.event_guard = self.regime_analyzer.event_guard
            elif EventRiskGuard is not None:
                # Fallback to EventGuard only (legacy mode)
                self.event_guard = EventRiskGuard(market='UK')
                self.regime_analyzer = None
                logger.info("[OK] Event Risk Guard enabled (UK market)")
            else:
                self.event_guard = None
                self.regime_analyzer = None
                logger.info("  Event Risk Guard disabled")
            
            # Optional: CSV Exporter
            if CSVExporter is not None:
                self.csv_exporter = CSVExporter()
                logger.info("[OK] CSV Exporter enabled")
            else:
                self.csv_exporter = None
                logger.info("  CSV Exporter disabled")
            
            # Optional: Macro News Monitor (UK + Global)
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='UK')
                logger.info("[OK] Macro News Monitor enabled (BoE/Treasury/Global)")
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
            
            # FIX v1.3.15.193.11.6.10: Initialize Realtime FTSE Predictor for pre-market gap analysis
            if REALTIME_FTSE_AVAILABLE:
                self.ftse_predictor = RealtimeFTSEPredictor()
                logger.info("[OK] Realtime FTSE Predictor initialized (Uses actual US/EU market closes)")
            else:
                self.ftse_predictor = None
                logger.warning("[!] Realtime FTSE Predictor unavailable")
            
            logger.info("[OK] All required UK market components initialized successfully")
        except Exception as e:
            logger.error(f"[X] Component initialization failed: {e}")
            raise
    
    def run_full_pipeline(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> Dict:
        """
        Run the complete UK overnight screening pipeline
        
        Args:
            sectors: List of sector names to scan (None = all sectors)
            stocks_per_sector: Number of stocks to scan per sector
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        self.start_time = time.time()
        
        try:
            # Phase 1: UK Market Sentiment
            logger.info("\n" + "="*80)
            logger.info("PHASE 1: UK MARKET SENTIMENT ANALYSIS")
            logger.info("="*80)
            self.status['phase'] = 'market_sentiment'
            self.status['progress'] = 10
            
            uk_sentiment = self._fetch_uk_market_sentiment()
            
            # Phase 2: Stock Scanning
            logger.info("\n" + "="*80)
            logger.info("PHASE 2: UK STOCK SCANNING")
            logger.info("="*80)
            self.status['phase'] = 'stock_scanning'
            self.status['progress'] = 20
            
            scanned_stocks = self._scan_all_uk_stocks(sectors, stocks_per_sector)
            
            if not scanned_stocks:
                raise Exception("No valid UK stocks found during scanning")
            
            # Phase 2.5: Event Risk Assessment (optional)
            event_risk_data = {}
            if self.event_guard is not None:
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
            
            predicted_stocks = self._generate_predictions(scanned_stocks, uk_sentiment, event_risk_data)
            
            # Phase 4: Opportunity Scoring
            logger.info("\n" + "="*80)
            logger.info("PHASE 4: OPPORTUNITY SCORING")
            logger.info("="*80)
            self.status['phase'] = 'scoring'
            self.status['progress'] = 70
            
            scored_stocks = self._score_opportunities(predicted_stocks, uk_sentiment)
            
            # Phase 4.5: LSTM Model Training (Optional)
            lstm_training_results = self._train_lstm_models(scored_stocks)
            
            # Phase 5: Report Generation
            logger.info("\n" + "="*80)
            logger.info("PHASE 5: UK MARKET REPORT GENERATION")
            logger.info("="*80)
            self.status['phase'] = 'report_generation'
            self.status['progress'] = 85
            
            report_path = self._generate_uk_report(scored_stocks, uk_sentiment, event_risk_data)
            
            # Phase 6: Finalization
            logger.info("\n" + "="*80)
            logger.info("PHASE 6: FINALIZATION")
            logger.info("="*80)
            self.status['phase'] = 'complete'
            self.status['progress'] = 100
            
            results = self._finalize_pipeline(
                scored_stocks=scored_stocks,
                uk_sentiment=uk_sentiment,
                report_path=report_path
            )
            
            elapsed_time = time.time() - self.start_time
            logger.info("\n" + "="*80)
            logger.info("UK PIPELINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Total Time: {elapsed_time/60:.1f} minutes")
            logger.info(f"Stocks Processed: {len(scanned_stocks)}")
            logger.info(f"Report Generated: {report_path}")
            logger.info(f"End Time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            return results
            
        except Exception as e:
            logger.error(f"\n[X] UK PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            self.status['phase'] = 'failed'
            self.status['errors'].append(str(e))
            self._save_error_state(e)
            raise
    
    def _fetch_uk_market_sentiment(self) -> Dict:
        """
        Fetch UK market sentiment using overnight/weekend trading data
        
        Data Sources:
        - FTSE 100 Index (^FTSE): Current/previous close
        - FTSE 100 Futures: Overnight direction indicator
        - VFTSE (^VFTSE): UK VIX equivalent - volatility/fear gauge
        - GBP/USD: Currency strength affecting UK stocks
        """
        logger.info("Fetching UK market sentiment data...")
        
        try:
            from yahooquery import Ticker
            import pandas as pd
            
            # Fetch UK market indicators
            symbols = ['^FTSE', '^VFTSE', 'GBPUSD=X']
            ticker = Ticker(symbols, asynchronous=True)
            
            # Get latest quotes
            quotes = ticker.quotes
            
            # Initialize sentiment components
            ftse_price = 7500.0  # Default
            ftse_change = 0.0
            vftse_value = 15.0  # Normal volatility ~15
            gbpusd_price = 1.27
            gbpusd_change = 0.0
            
            # Extract FTSE 100 data
            if isinstance(quotes, dict) and '^FTSE' in quotes:
                ftse_data = quotes['^FTSE']
                if 'regularMarketPrice' in ftse_data:
                    ftse_price = ftse_data.get('regularMarketPrice', 7500.0)
                    ftse_prev = ftse_data.get('regularMarketPreviousClose', ftse_price)
                    ftse_change = ((ftse_price - ftse_prev) / ftse_prev * 100) if ftse_prev else 0.0
                    logger.info(f"[OK] FTSE 100: {ftse_price:.2f} ({ftse_change:+.2f}%)")
            
            # Extract VFTSE (UK VIX)
            if isinstance(quotes, dict) and '^VFTSE' in quotes:
                vftse_data = quotes['^VFTSE']
                if 'regularMarketPrice' in vftse_data:
                    vftse_value = vftse_data.get('regularMarketPrice', 15.0)
                    logger.info(f"[OK] VFTSE (UK VIX): {vftse_value:.2f}")
            
            # Extract GBP/USD
            if isinstance(quotes, dict) and 'GBPUSD=X' in quotes:
                gbp_data = quotes['GBPUSD=X']
                if 'regularMarketPrice' in gbp_data:
                    gbpusd_price = gbp_data.get('regularMarketPrice', 1.27)
                    gbpusd_prev = gbp_data.get('regularMarketPreviousClose', gbpusd_price)
                    gbpusd_change = ((gbpusd_price - gbpusd_prev) / gbpusd_prev * 100) if gbpusd_prev else 0.0
                    logger.info(f"[OK] GBP/USD: {gbpusd_price:.4f} ({gbpusd_change:+.2f}%)")
            
            # Calculate sentiment score (0-100)
            sentiment_score = 50.0  # Start neutral
            
            # FTSE 100 change: ±30 points
            sentiment_score += ftse_change * 10  # +1% = +10 points
            
            # VFTSE impact: High volatility = negative
            # Normal VIX ~15, High >20, Very High >25
            if vftse_value > 25:
                sentiment_score -= 15  # Very high fear
            elif vftse_value > 20:
                sentiment_score -= 8   # High fear
            elif vftse_value < 12:
                sentiment_score += 5   # Low fear = positive
            
            # GBP/USD impact: Strong GBP hurts exporters (60% of FTSE 100)
            sentiment_score -= gbpusd_change * 5  # Strong GBP = negative for FTSE
            
            # Clamp to 0-100
            sentiment_score = max(0, min(100, sentiment_score))
            
            # Determine sentiment label and recommendation
            if sentiment_score >= 65:
                sentiment_label = 'Bullish'
                recommendation = 'BUY'
                confidence = 'HIGH'
            elif sentiment_score >= 55:
                sentiment_label = 'Slightly Bullish'
                recommendation = 'WATCH'
                confidence = 'MODERATE'
            elif sentiment_score >= 45:
                sentiment_label = 'Neutral'
                recommendation = 'HOLD'
                confidence = 'MODERATE'
            elif sentiment_score >= 35:
                sentiment_label = 'Slightly Bearish'
                recommendation = 'CAUTION'
                confidence = 'MODERATE'
            else:
                sentiment_label = 'Bearish'
                recommendation = 'AVOID'
                confidence = 'HIGH'
            
            # Determine risk rating based on VFTSE
            if vftse_value > 25:
                risk_rating = 'High'
                volatility_level = 'Very High'
            elif vftse_value > 20:
                risk_rating = 'Elevated'
                volatility_level = 'High'
            elif vftse_value < 12:
                risk_rating = 'Low'
                volatility_level = 'Low'
            else:
                risk_rating = 'Moderate'
                volatility_level = 'Normal'
            
            sentiment = {
                'overall': {
                    'sentiment': sentiment_label,
                    'score': sentiment_score,
                    'confidence': confidence
                },
                'sentiment_score': sentiment_score,
                'confidence': confidence,
                'risk_rating': risk_rating,
                'volatility_level': volatility_level,
                'recommendation': recommendation,
                'ftse100': {
                    'price': ftse_price,
                    'day_change': ftse_change,
                    'sentiment': sentiment_label
                },
                'vftse': {
                    'value': vftse_value,
                    'level': volatility_level
                },
                'gbpusd': {
                    'price': gbpusd_price,
                    'change': gbpusd_change
                }
            }
            
            logger.info(f"[OK] UK Market Sentiment Retrieved:")
            logger.info(f"  FTSE 100: {sentiment['ftse100']['price']:.2f} ({ftse_change:+.2f}%)")
            logger.info(f"  VFTSE (UK VIX): {vftse_value:.2f} ({volatility_level})")
            logger.info(f"  GBP/USD: {gbpusd_price:.4f} ({gbpusd_change:+.2f}%)")
            logger.info(f"  Sentiment Score: {sentiment_score:.1f}/100 ({sentiment_label})")
            logger.info(f"  Risk Rating: {risk_rating}")
            logger.info(f"  Recommendation: {recommendation}")
            
            # FIX v1.3.15.193.11.6.10: Add FTSE gap prediction using realtime market closes
            gap_prediction = None
            if self.ftse_predictor is not None:
                try:
                    logger.info("")
                    logger.info("[REALTIME FTSE] Computing pre-market gap prediction...")
                    realtime_result = self.ftse_predictor.compute_prediction()
                    
                    if realtime_result and realtime_result.get('available', False):
                        gap_prediction = {
                            'predicted_gap_pct': realtime_result['predicted_gap_pct'],
                            'confidence': realtime_result['confidence'],
                            'direction': realtime_result['direction'],
                            'method': realtime_result['method'],
                            'breakdown': realtime_result.get('breakdown', {})
                        }
                        
                        logger.info(f"[REALTIME FTSE] Gap Prediction: {realtime_result['predicted_gap_pct']:+.2f}%")
                        logger.info(f"[REALTIME FTSE] Confidence: {realtime_result['confidence']:.0%}")
                        logger.info(f"[REALTIME FTSE] Direction: {realtime_result['direction']}")
                        
                        # Log breakdown for transparency
                        if 'breakdown' in realtime_result:
                            bd = realtime_result['breakdown']
                            logger.info(f"[REALTIME FTSE] Breakdown: US={bd.get('us_component', 0):+.2f}%, "
                                      f"EU={bd.get('europe_component', 0):+.2f}%, "
                                      f"Futures={bd.get('futures_component', 0):+.2f}%, "
                                      f"FX={bd.get('fx_component', 0):+.2f}%, "
                                      f"Commodities={bd.get('commodity_component', 0):+.2f}%")
                        
                        # Add gap prediction to sentiment dict
                        sentiment['gap_prediction'] = gap_prediction
                        sentiment['predicted_gap_pct'] = realtime_result['predicted_gap_pct']
                    else:
                        logger.warning("[REALTIME FTSE] Prediction unavailable - no gap prediction")
                        gap_prediction = {
                            'predicted_gap_pct': 0.0,
                            'confidence': 0.0,
                            'direction': 'NEUTRAL'
                        }
                        sentiment['gap_prediction'] = gap_prediction
                        sentiment['predicted_gap_pct'] = 0.0
                        
                except Exception as e:
                    logger.warning(f"[REALTIME FTSE] Failed: {e}")
                    gap_prediction = {
                        'predicted_gap_pct': 0.0,
                        'confidence': 0.0,
                        'direction': 'NEUTRAL'
                    }
                    sentiment['gap_prediction'] = gap_prediction
                    sentiment['predicted_gap_pct'] = 0.0
            else:
                # No FTSE predictor available
                gap_prediction = {
                    'predicted_gap_pct': 0.0,
                    'confidence': 0.0,
                    'direction': 'NEUTRAL'
                }
                sentiment['gap_prediction'] = gap_prediction
                sentiment['predicted_gap_pct'] = 0.0
            
            # Initialize macro_news with default (v193.2 bugfix)
            macro_news = {
                'article_count': 0,
                'sentiment_score': 0.0,
                'sentiment_label': 'UNAVAILABLE',
                'articles': [],
                'summary': 'Macro news not available'
            }
            
            # Phase 1.3: Macro News Monitoring (BoE/Treasury/Global)
            if self.macro_monitor is not None:
                try:
                    logger.info("")
                    logger.info("="*80)
                    logger.info("PHASE 1.3: MACRO NEWS MONITORING (BoE/Treasury/Global)")
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
                        logger.info(f"\n  Recent UK/Global News:")
                        for i, article in enumerate(macro_news['top_articles'][:3], 1):
                            logger.info(f"    {i}. {article['title'][:80]}")
                            logger.info(f"       Sentiment: {article.get('sentiment', 0.0):.3f}")
                    
                    # Adjust overall sentiment based on macro news
                    if macro_news['sentiment_score'] != 0:
                        original_score = sentiment['overall']['score']
                        
                        # Scale macro sentiment from [-1, 1] to impact points [-15, +15]
                        # Increased from ±10 to ±15 to better capture global uncertainty
                        macro_impact = macro_news['sentiment_score'] * 15
                        
                        # Apply weighted adjustment (macro news = 35% of overall sentiment)
                        # Increased from 20% to 35% due to heightened global political uncertainty
                        # This better reflects impact of US administration policies, trade wars,
                        # geopolitical events, and central bank divergence on UK markets
                        adjusted_score = original_score + (macro_impact * 0.35)
                        adjusted_score = max(0, min(100, adjusted_score))  # Clamp to [0, 100]
                        
                        sentiment['overall']['score'] = adjusted_score
                        sentiment['sentiment_score'] = adjusted_score
                        sentiment['overall']['macro_adjusted'] = True
                        sentiment['overall']['macro_weight'] = 0.35  # Store weight for transparency
                        
                        logger.info(f"\n  [OK] Sentiment Adjusted for Macro News:")
                        logger.info(f"    Original Score: {original_score:.1f}")
                        logger.info(f"    Macro Impact: {macro_impact:+.1f} points (35% weight)")
                        logger.info(f"    Adjusted Score: {adjusted_score:.1f}")
                        
                        # Additional warning if macro news is strongly negative
                        if macro_news['sentiment_score'] < -0.30:
                            logger.warning(f"  [!] STRONG NEGATIVE MACRO SENTIMENT DETECTED")
                            logger.warning(f"      Global uncertainty may significantly impact UK markets")
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
                        original_score = sentiment['sentiment_score']
                        adjusted_score = max(0, min(100, original_score - risk_penalty))
                        
                        sentiment['sentiment_score'] = adjusted_score
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
                    
                    # FIX v1.3.15.193.11.6.10: Apply gap adjustment based on sentiment and world risk
                    if gap_prediction and gap_prediction['predicted_gap_pct'] != 0.0:
                        original_gap = gap_prediction['predicted_gap_pct']
                        final_sentiment = sentiment['sentiment_score']
                        world_risk_score = world_risk['world_risk_score']
                        
                        # Determine sentiment adjustment factor based on world risk regime
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
                        # When sentiment and gap agree: AMPLIFY
                        # When sentiment and gap disagree: DAMPEN
                        gap_is_negative = original_gap < 0
                        sentiment_is_bearish = final_sentiment < 50
                        signals_agree = (gap_is_negative and sentiment_is_bearish) or (not gap_is_negative and not sentiment_is_bearish)
                        
                        if signals_agree:
                            # AMPLIFY
                            adjustment_magnitude = abs(sentiment_deviation) * sentiment_factor
                            adjusted_gap = original_gap * (1 + adjustment_magnitude)
                        else:
                            # DAMPEN
                            adjustment_magnitude = abs(sentiment_deviation) * sentiment_factor * 0.5
                            adjusted_gap = original_gap * (1 - adjustment_magnitude)
                        
                        # Apply risk multiplier for extreme conditions
                        risk_multiplier = 1.0
                        if world_risk_score >= 85:
                            risk_intensity = (world_risk_score - 85) / 15
                            
                            if signals_agree:
                                risk_multiplier = 1.0 + (risk_intensity * 0.5)
                            else:
                                risk_multiplier = 1.0 - (risk_intensity * 0.4)
                            
                            risk_multiplier = max(0.5, min(risk_multiplier, 1.8))
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
                        
                        # Update gap_prediction dict
                        sentiment['gap_prediction']['predicted_gap_pct'] = adjusted_gap
                        sentiment['gap_prediction']['adjusted'] = True
                        sentiment['gap_prediction']['original_gap'] = original_gap
                        
                        logger.info(f"\n[OK] Gap Prediction Adjusted for News/Risk:")
                        logger.info(f"  Regime: {regime_label} (Sentiment Factor: {sentiment_factor:.2f})")
                        logger.info(f"  Original Gap: {original_gap:+.2f}%")
                        logger.info(f"  Sentiment Score: {final_sentiment:.1f}/100 (deviation: {sentiment_deviation:+.2f})")
                        logger.info(f"  Sentiment & Gap: {'AGREE' if signals_agree else 'DISAGREE'} → {'AMPLIFY' if signals_agree else 'DAMPEN'}")
                        logger.info(f"  World Risk: {world_risk_score:.1f}/100")
                        if risk_multiplier != 1.0:
                            logger.info(f"  Risk Multiplier: {risk_multiplier:.2f}x")
                        logger.info(f"  Adjusted Gap: {adjusted_gap:+.2f}%")
                        logger.info(f"  Total Impact: {(adjusted_gap - original_gap):+.2f} percentage points")
                    
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
            logger.warning(f"[!] UK market sentiment retrieval failed: {e}")
            logger.warning("Continuing with default sentiment...")
            
            return {
                'overall': {'sentiment': 'Neutral', 'score': 50.0, 'confidence': 'MODERATE'},
                'sentiment_score': 50.0,
                'confidence': 'MODERATE',
                'risk_rating': 'Moderate',
                'volatility_level': 'Normal',
                'recommendation': 'HOLD'
            }
    
    def _scan_all_uk_stocks(self, sectors: List[str] = None, stocks_per_sector: int = 30) -> List[Dict]:
        """Scan all UK stocks from specified sectors"""
        
        if sectors is None:
            sectors_to_scan = list(self.scanner.sectors.keys())
        else:
            sectors_to_scan = sectors
        
        total_expected = len(sectors_to_scan) * stocks_per_sector
        logger.info(f"Scanning {len(sectors_to_scan)} UK sectors...")
        logger.info(f"Target: {stocks_per_sector} stocks per sector (~{total_expected} total stocks)")
        logger.info("")
        
        all_stocks = []
        total_processed = 0
        
        for i, sector_name in enumerate(sectors_to_scan, 1):
            logger.info(f"[{i}/{len(sectors_to_scan)}] Scanning {sector_name}...")
            
            try:
                stocks = self.scanner.scan_sector(sector_name, top_n=stocks_per_sector)
                
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
                logger.error(f"  [X] Error scanning {sector_name}: {e}")
                self.status['errors'].append(f"Sector scan failed: {sector_name}")
                continue
        
        logger.info(f"\n[OK] UK Stock Scanning Complete:")
        logger.info(f"  Total Valid Stocks: {len(all_stocks)}")
        
        self.status['total_stocks'] = len(all_stocks)
        return all_stocks
    
    def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
        """🆕 v1.3.15.176: Assess event risks + Dual Regime Analysis (Multi-Factor + HMM)"""
        if self.event_guard is None:
            return {}
        
        logger.info(f"Assessing event risks for {len(stocks)} UK stocks...")
        
        try:
            tickers = [s['symbol'] for s in stocks]
            results = self.event_guard.assess_batch(tickers)
            
            # Extract ticker results (filter out market_regime key)
            ticker_results = {k: v for k, v in results.items() if k != 'market_regime' and hasattr(v, 'has_upcoming_event')}
            
            total_events = sum(1 for r in ticker_results.values() if r.has_upcoming_event)
            sit_outs = sum(1 for r in ticker_results.values() if r.skip_trading)
            
            logger.info(f"[OK] Event Risk Assessment Complete:")
            logger.info(f"  Upcoming Events: {total_events}")
            logger.info(f"  Sit-Out Recommendations: {sit_outs}")
            
            # 🆕 v1.3.15.176: Dual Regime Analysis (Multi-Factor + HMM)
            if hasattr(self, 'regime_analyzer') and self.regime_analyzer:
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
            
            return results
            
        except Exception as e:
            logger.error(f"[X] Event risk assessment failed: {e}")
            return {}
    
    def _generate_predictions(self, stocks: List[Dict], sentiment: Dict, event_risk_data: Dict = None) -> List[Dict]:
        """Generate predictions for all stocks"""
        logger.info(f"Generating predictions for {len(stocks)} stocks...")
        
        try:
            predicted = self.predictor.predict_batch(
                stocks=stocks,
                spi_sentiment=sentiment
            )
            
            logger.info(f"[OK] Predictions Generated: {len(predicted)} stocks")
            return predicted
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return stocks  # Return stocks without predictions
    
    def _score_opportunities(self, stocks: List[Dict], sentiment: Dict) -> List[Dict]:
        """Score trading opportunities"""
        logger.info(f"Scoring opportunities for {len(stocks)} stocks...")
        
        try:
            # Call scorer with positional arguments (not keyword arguments)
            scored = self.scorer.score_opportunities(stocks, sentiment)
            
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
    
    def _generate_uk_report(self, stocks: List[Dict], sentiment: Dict, event_risk_data: Dict = None) -> Path:
        """Generate UK market morning report"""
        logger.info("Generating UK market morning report...")
        
        try:
            # Prepare sector summary
            sector_summary = {}
            for sector_name in self.scanner.sectors.keys():
                sector_stocks = [
                    s for s in stocks 
                    if s.get('symbol', '') in self.scanner.sectors[sector_name].get('stocks', [])
                ]
                
                if sector_stocks:
                    scores = [s.get('opportunity_score', 0) for s in sector_stocks]
                    sector_summary[sector_name] = {
                        'total_stocks': len(sector_stocks),
                        'avg_score': sum(scores) / len(scores) if scores else 0,
                        'top_score': max(scores) if scores else 0
                    }
            
            # Prepare system stats
            elapsed_time = time.time() - self.start_time
            pred_summary = self.predictor.get_prediction_summary(stocks)
            
            system_stats = {
                'total_scanned': len(stocks),
                'buy_signals': pred_summary.get('buy_count', 0),
                'sell_signals': pred_summary.get('sell_count', 0),
                'processing_time_seconds': int(elapsed_time),
                'lstm_status': 'Available' if self.predictor.lstm_available else 'Not Available'
            }
            
            # Generate report
            report_path = self.reporter.generate_morning_report(
                opportunities=stocks,
                spi_sentiment=sentiment,
                sector_summary=sector_summary,
                system_stats=system_stats,
                event_risk_data=event_risk_data
            )
            
            logger.info(f"[OK] Report generated: {report_path}")
            return Path(report_path)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            logger.error(f"Full error: {traceback.format_exc()}")
            
            # Create minimal fallback report
            report_dir = BASE_PATH / 'reports' / 'uk'
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            fallback_path = report_dir / f'uk_report_{timestamp}_error.txt'
            
            error_content = f"""UK Market Report Generation Error
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Error: {e}

Stocks processed: {len(stocks)}
Sentiment: {sentiment}

Full traceback:
{traceback.format_exc()}
"""
            fallback_path.write_text(error_content)
            return fallback_path
    
    def _finalize_pipeline(self, scored_stocks: List[Dict], uk_sentiment: Dict, report_path: Path) -> Dict:
        """Finalize pipeline and save results"""
        logger.info("Finalizing UK pipeline...")
        
        # Get top opportunities
        top_opportunities = scored_stocks[:20]
        
        # Prepare summary
        results = {
            'market': 'UK',
            'timestamp': datetime.now(self.timezone).isoformat(),
            'total_stocks': len(scored_stocks),
            'top_opportunities': top_opportunities,
            'sentiment': uk_sentiment,
            'report_path': str(report_path),
            'status': self.status
        }
        
        # Save JSON results
        results_dir = BASE_PATH / 'data' / 'uk'
        results_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'uk_pipeline_results_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"[OK] Results saved: {results_file}")
        
        # Export CSV if available
        if self.csv_exporter is not None:
            try:
                csv_path = self.csv_exporter.export_screening_results(scored_stocks, uk_sentiment)
                logger.info(f"[OK] CSV exported: {csv_path}")
            except Exception as e:
                logger.warning(f"CSV export failed: {e}")
        
        # 🆕 INTEGRATION FIX: Save in format expected by trading platform
        # Signal adapter looks for: reports/screening/uk_morning_report.json
        try:
            trading_report_dir = BASE_PATH / 'reports' / 'screening'
            trading_report_dir.mkdir(parents=True, exist_ok=True)
            
            trading_report = {
                'timestamp': datetime.now(self.timezone).isoformat(),
                'market': 'UK',
                'market_sentiment': {
                    'sentiment_score': uk_sentiment.get('sentiment_score', 50.0),
                    'confidence': uk_sentiment.get('confidence', 'MODERATE'),
                    'risk_rating': uk_sentiment.get('risk_rating', 'Moderate'),
                    'volatility_level': uk_sentiment.get('volatility_level', 'Normal'),
                    'recommendation': uk_sentiment.get('recommendation', 'HOLD'),
                    'gap_prediction': uk_sentiment.get('gap_prediction', {})
                },
                'world_risk_score': uk_sentiment.get('world_risk_score', 50),
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
            
            trading_report_path = trading_report_dir / 'uk_morning_report.json'
            with open(trading_report_path, 'w') as f:
                json.dump(trading_report, f, indent=2, default=str)
            
            logger.info(f"[OK] Trading platform report saved: {trading_report_path}")
            logger.info(f"     This report will be used by run_pipeline_enhanced_trading.py")
            results['trading_report_path'] = str(trading_report_path)
            
        except Exception as e:
            logger.warning(f"[!]  Failed to save trading platform report: {e}")
            # Don't fail pipeline if this fails
        
        return results
    
    def _save_error_state(self, error: Exception):
        """Save error state for debugging"""
        error_dir = BASE_PATH / 'logs' / 'screening' / 'uk' / 'errors'
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
    """Main entry point for UK overnight pipeline"""
    pipeline = UKOvernightPipeline()
    
    try:
        results = pipeline.run_full_pipeline(
            sectors=None,  # All sectors
            stocks_per_sector=30
        )
        
        print("\n" + "="*80)
        print("UK PIPELINE EXECUTION SUMMARY")
        print("="*80)
        print(f"Total Stocks Processed: {results['total_stocks']}")
        print(f"Top Opportunities: {len(results['top_opportunities'])}")
        print(f"Market Sentiment: {results['sentiment']['recommendation']}")
        print(f"Report: {results['report_path']}")
        print("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"UK Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

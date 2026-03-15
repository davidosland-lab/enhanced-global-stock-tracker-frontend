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

try:
    from .event_risk_guard import EventRiskGuard
except ImportError:
    EventRiskGuard = None

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
            
            # Optional: Event Risk Guard (UK market)
            if EventRiskGuard is not None:
                self.event_guard = EventRiskGuard(market='UK')
                logger.info("[OK] Event Risk Guard enabled (UK market)")
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
            
            # Optional: Macro News Monitor (UK + Global)
            if MacroNewsMonitor is not None:
                self.macro_monitor = MacroNewsMonitor(market='UK')
                logger.info("[OK] Macro News Monitor enabled (BoE/Treasury/Global)")
            else:
                self.macro_monitor = None
                logger.info("  Macro News Monitor disabled")
            
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
                    sentiment['macro_news'] = {
                        'article_count': 0,
                        'sentiment_score': 0.0,
                        'sentiment_label': 'UNAVAILABLE',
                        'summary': 'Macro news monitoring failed'
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
        """Assess event risks for scanned stocks"""
        if self.event_guard is None:
            return {}
        
        logger.info(f"Assessing event risks for {len(stocks)} UK stocks...")
        
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
            scored = self.scorer.score_opportunities(
                stocks=stocks,
                market_sentiment=sentiment
            )
            
            # Sort by score
            scored.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            high_quality = sum(1 for s in scored if s.get('opportunity_score', 0) >= 75)
            logger.info(f"[OK] Scoring Complete: {high_quality} high-quality opportunities (≥75)")
            
            return scored
            
        except Exception as e:
            logger.error(f"Opportunity scoring failed: {e}")
            return stocks
    
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
                    'recommendation': uk_sentiment.get('recommendation', 'HOLD')
                },
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

# -*- coding: utf-8 -*-
"""
US Market Pipeline (NYSE/NASDAQ) - COMPLETE EDITION
====================================================

Professional overnight screening pipeline for US markets combining:
- Original sophisticated screening modules (FinBERT, LSTM, Event Risk Guard)
- NEW regime intelligence (14 regimes, 15+ cross-market features)
- Sector-based scanning (240 stocks across 8 sectors)
- ML ensemble prediction & smart filtering

Features:
- US market hours (09:30-16:00 EST / 14:30-21:00 GMT)
- FinBERT sentiment analysis on news & filings
- LSTM price prediction models
- Basel III / regulatory event risk protection
- Market regime detection (US tech rally, commodity rotation, rate cuts, etc.)
- Cross-market feature engineering (US/commodity/FX/rates)
- Regime-aware opportunity scoring (0-100)
- Morning report generation with email alerts
- CSV exports for further analysis

Workflow:
1. Fetch overnight market data (US futures, commodities, FX, rates)
2. Detect market regime (14 types)
3. Scan all sectors (240 stocks: 8 sectors × 30 stocks)
4. Generate batch predictions (ML ensemble + LSTM)
5. Apply FinBERT sentiment analysis
6. Assess event risks (Basel III, earnings, dividends)
7. Score opportunities with regime adjustments
8. Train/update LSTM models for top stocks
9. Generate comprehensive morning report
10. Send email notifications (optional)

Usage:
    # Full sector scan (240 stocks) - RECOMMENDED
    python run_us_full_pipeline.py --full-scan --capital 100000
    
    # Quick preset scan
    python run_us_full_pipeline.py --preset "US Tech Giants" --capital 100000
    
    # Custom symbols
    python run_us_full_pipeline.py --symbols AAPL,MSFT,GOOGL --capital 50000
    
    # Test mode (5 stocks from Financials)
    python run_us_full_pipeline.py --mode test
    
    # Disable regime intelligence
    python run_us_full_pipeline.py --full-scan --no-regime

Author: Trading System v1.3.15 - COMPLETE EDITION
Date: January 8, 2026
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pytz
import json
import time
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Core modules
try:
    from paper_trading_coordinator import PaperTradingCoordinator
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
except ImportError as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.error(f"Failed to import core modules: {e}")
    PaperTradingCoordinator = None
    MarketCalendar = None
    Exchange = None
    MarketStatus = None

# Sector scanner
try:
    from models.sector_stock_scanner import StockScanner
except ImportError:
    StockScanner = None

# Original sophisticated screening modules
try:
    # CRITICAL FIX: Import US-specific overnight pipeline, NOT Australian one!
    # overnight_pipeline.py = Australian (SPI monitor)
    # us_overnight_pipeline.py = US (S&P500, VIX, NASDAQ)
    from models.screening.us_overnight_pipeline import USOvernightPipeline as OvernightPipeline
    from models.screening.us_stock_scanner import USStockScanner as OriginalScanner
    from models.screening.us_market_monitor import USMarketMonitor as SPIMonitor  # Renamed for compatibility
    from models.screening.batch_predictor import BatchPredictor
    from models.screening.opportunity_scorer import OpportunityScorer
    from models.screening.report_generator import ReportGenerator
    from models.screening.finbert_bridge import FinBERTBridge
    from models.screening.lstm_trainer import LSTMTrainer
    from models.screening.event_risk_guard import EventRiskGuard
    ORIGINAL_MODULES_AVAILABLE = True
    logging.getLogger(__name__).info("[OK] US-specific screening modules imported successfully")
except ImportError as e:
    logging.getLogger(__name__).warning(f"Original screening modules not available: {e}")
    ORIGINAL_MODULES_AVAILABLE = False
    OvernightPipeline = None
    OriginalScanner = None
    SPIMonitor = None
    BatchPredictor = None
    OpportunityScorer = None
    ReportGenerator = None
    FinBERTBridge = None
    LSTMTrainer = None
    EventRiskGuard = None

# Regime intelligence modules
try:
    from models.market_data_fetcher import MarketDataFetcher
    from models.market_regime_detector import MarketRegimeDetector
    from models.regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer
    REGIME_INTELLIGENCE_AVAILABLE = True
except ImportError:
    REGIME_INTELLIGENCE_AVAILABLE = False
    MarketDataFetcher = None
    MarketRegimeDetector = None
    RegimeAwareOpportunityScorer = None

# Configure logging with UTF-8 encoding for Windows
Path('logs').mkdir(exist_ok=True)

# ASCII emoji mappings for Windows compatibility
EMOJI_MAP = {
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]',
    '[WARNING]': '[WARNING]',
    '[INFO]': '[INFO]',
    '[SUCCESS]': '[SUCCESS]',
    '[FAILED]': '[FAILED]'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/us_full_pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# US Stock Presets
US_PRESETS = {
    'US Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
    'US Banks': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC'],
    'US Healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY'],
    'US Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'PSX', 'VLO'],
    'US Industrials': ['BA', 'CAT', 'GE', 'HON', 'UNP', 'RTX', 'DE', 'LMT'],
    'US Consumer': ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'DIS'],
    'US Materials': ['LIN', 'APD', 'ECL', 'DD', 'NEM', 'FCX', 'DOW', 'NUE'],
    'S&P 500 Top 10': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JPM', 'V'],
    'Magnificent 7': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
}


class USFullPipelineRunner:
    """
    Complete US Market Pipeline combining original sophistication with new regime intelligence
    """
    
    def __init__(self, symbols=None, capital=100000, config_path='config/live_trading_config.json',
                 use_sector_scan=False, sectors_config='config/us_sectors.json',
                 use_regime_intelligence=True, use_original_modules=True):
        self.symbols = symbols or []
        self.capital = capital
        self.config_path = config_path
        self.use_sector_scan = use_sector_scan
        self.sectors_config = sectors_config
        self.use_regime_intelligence = use_regime_intelligence
        self.use_original_modules = use_original_modules
        self.market_calendar = MarketCalendar() if MarketCalendar else None
        self.coordinator = None
        self.scanner = None
        self.est = pytz.timezone('America/New_York')
        
        # Regime intelligence components
        self.market_data_fetcher = None
        self.regime_detector = None
        self.regime_scorer = None
        
        # Original sophisticated modules
        self.overnight_pipeline = None
        self.finbert_bridge = None
        self.lstm_trainer = None
        self.event_guard = None
        
        logger.info("=" * 80)
        logger.info("US MARKET PIPELINE - COMPLETE EDITION v1.3.15")
        logger.info("=" * 80)
        logger.info(f"Market: NYSE / NASDAQ")
        logger.info(f"Trading Hours: 09:30-16:00 EST (14:30-21:00 GMT)")
        
        if use_sector_scan:
            logger.info(f"Mode: FULL SECTOR SCAN")
            logger.info(f"Sectors Config: {sectors_config}")
            logger.info(f"Expected Stocks: ~240 (8 sectors x 30 stocks)")
        else:
            logger.info(f"Mode: PRESET/CUSTOM")
            logger.info(f"Symbols: {', '.join(symbols) if len(symbols) <= 10 else f'{len(symbols)} symbols'}")
        
        logger.info(f"Initial Capital: ${capital:,.2f} USD")
        
        # Feature status
        features_enabled = []
        features_disabled = []
        
        # Check regime intelligence
        if use_regime_intelligence and REGIME_INTELLIGENCE_AVAILABLE:
            features_enabled.append("Regime Intelligence (14 regimes, 15+ features)")
            self._initialize_regime_intelligence()
        else:
            if use_regime_intelligence:
                features_disabled.append("Regime Intelligence (modules not available)")
                self.use_regime_intelligence = False
        
        # Check original modules
        if use_original_modules and ORIGINAL_MODULES_AVAILABLE:
            self._check_original_modules_availability()
        else:
            if use_original_modules:
                features_disabled.append("Original Modules (not available)")
                self.use_original_modules = False
        
        # Log feature status
        if features_enabled:
            logger.info(f"\n[OK] ENABLED FEATURES:")
            for feature in features_enabled:
                logger.info(f"   - {feature}")
        
        if features_disabled:
            logger.info(f"\n[WARNING] DISABLED FEATURES:")
            for feature in features_disabled:
                logger.info(f"   - {feature}")
        
        logger.info("=" * 80)
    
    def _initialize_regime_intelligence(self):
        """Initialize regime intelligence components"""
        try:
            self.market_data_fetcher = MarketDataFetcher()
            self.regime_detector = MarketRegimeDetector()
            self.regime_scorer = RegimeAwareOpportunityScorer()
            logger.info("[OK] Regime Intelligence: Market regime detection, cross-market features, regime-aware scoring")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize regime intelligence: {e}")
            self.use_regime_intelligence = False
    
    def _check_original_modules_availability(self):
        """Check and initialize original sophisticated modules"""
        available_modules = []
        
        if FinBERTBridge:
            try:
                self.finbert_bridge = FinBERTBridge()
                available_modules.append("FinBERT Sentiment Analysis")
            except Exception as e:
                logger.warning(f"FinBERT initialization failed: {e}")
        
        if LSTMTrainer:
            try:
                self.lstm_trainer = LSTMTrainer()
                available_modules.append("LSTM Price Prediction")
            except Exception as e:
                logger.warning(f"LSTM Trainer initialization failed: {e}")
        
        if EventRiskGuard:
            try:
                self.event_guard = EventRiskGuard()
                available_modules.append("Event Risk Guard (Basel III, earnings)")
            except Exception as e:
                logger.warning(f"Event Risk Guard initialization failed: {e}")
        
        if OvernightPipeline:
            try:
                self.overnight_pipeline = OvernightPipeline()
                available_modules.append("Overnight Pipeline Orchestration")
            except Exception as e:
                logger.warning(f"Overnight Pipeline initialization failed: {e}")
        
        if available_modules:
            logger.info("[OK] Original Modules Available:")
            for module in available_modules:
                logger.info(f"   - {module}")
        else:
            logger.warning("[WARNING] No original modules available")
            self.use_original_modules = False
    
    def fetch_and_analyze_market_regime(self):
        """
        Fetch overnight market data and analyze regime
        
        Returns:
            Tuple of (market_data, regime_data) or (None, None) if failed
        """
        if not self.use_regime_intelligence:
            return None, None
        
        try:
            logger.info("\n" + "="*80)
            logger.info("OVERNIGHT MARKET ANALYSIS")
            logger.info("="*80)
            
            # Fetch market data
            market_data = self.market_data_fetcher.fetch_market_data()
            
            # Log market summary
            logger.info(self.market_data_fetcher.get_market_summary_text(market_data))
            
            # Detect regime
            regime_data = self.regime_detector.detect_regime(market_data)
            
            # Log regime analysis
            logger.info(self.regime_detector.get_regime_report())
            
            return market_data, regime_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error in market regime analysis: {e}", exc_info=True)
            return None, None
    
    def load_sector_stocks(self):
        """Load stocks from sector configuration"""
        if not StockScanner:
            logger.error("[ERROR] StockScanner not available - cannot perform sector scan")
            return False
        
        try:
            logger.info("\n" + "="*80)
            logger.info("LOADING SECTOR STOCKS")
            logger.info("="*80)
            
            self.scanner = StockScanner(config_path=self.sectors_config)
            
            # Get all sector stocks
            all_stocks = []
            for sector_name, sector_data in self.scanner.sectors.items():
                stocks = sector_data.get('stocks', [])
                all_stocks.extend(stocks)
                logger.info(f"  {sector_name}: {len(stocks)} stocks")
            
            self.symbols = all_stocks
            logger.info(f"\n[OK] Total stocks loaded: {len(self.symbols)}")
            logger.info("="*80 + "\n")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to load sector stocks: {e}")
            return False
    
    def check_market_status(self):
        """Check if US market is open"""
        try:
            status = self.market_calendar.get_market_status(Exchange.NYSE)
            now_est = datetime.now(self.est)
            
            logger.info(f"US Market Status: {status.name}")
            logger.info(f"Current Time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            if status == MarketStatus.OPEN:
                logger.info("[OK] US Markets are OPEN - Trading enabled")
                return True
            elif status == MarketStatus.CLOSED:
                logger.warning("[ERROR] US Markets are CLOSED - No trading")
                next_open = self.market_calendar.get_next_market_open(Exchange.NYSE)
                if next_open:
                    logger.info(f"Next open: {next_open.astimezone(self.est).strftime('%Y-%m-%d %H:%M %Z')}")
                return False
            else:
                logger.warning(f"[WARNING] US Market Status: {status.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def run_full_overnight_pipeline(self, mode='full'):
        """
        Run complete overnight pipeline with all sophisticated features
        
        Args:
            mode: 'full' or 'test' mode
        
        Returns:
            Dictionary with pipeline results
        """
        if not self.use_original_modules or not self.overnight_pipeline:
            logger.warning("[WARNING] Original modules not available - skipping full pipeline")
            return None
        
        try:
            logger.info("\n" + "="*80)
            logger.info("RUNNING COMPLETE OVERNIGHT PIPELINE")
            logger.info("="*80)
            logger.info("Features: FinBERT, LSTM, Event Risk Guard, Regime Intelligence")
            logger.info("="*80 + "\n")
            
            if mode == 'test':
                # Test mode: scan only Financials with 5 stocks
                logger.info("Running in TEST mode (Financials only, 5 stocks)")
                results = self.overnight_pipeline.run_full_pipeline(
                    sectors=['Financials'],
                    stocks_per_sector=5
                )
            else:
                # Full mode: scan all sectors
                logger.info("Running in FULL mode (all sectors, 30 stocks each)")
                results = self.overnight_pipeline.run_full_pipeline(
                    sectors=None,  # All sectors
                    stocks_per_sector=30
                )
            
            logger.info("\n" + "="*80)
            logger.info("OVERNIGHT PIPELINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Status: {results['status'].upper()}")
            logger.info(f"Execution Time: {results['execution_time_minutes']} minutes")
            logger.info(f"Stocks Scanned: {results['statistics']['total_stocks_scanned']}")
            logger.info(f"Top Opportunities: {results['statistics']['top_opportunities_count']}")
            logger.info(f"Report: {results['report_path']}")
            logger.info("="*80 + "\n")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Overnight pipeline failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def run(self, check_market_hours=True, mode='full'):
        """
        Run the US full pipeline
        
        Args:
            check_market_hours: Check if market is open
            mode: 'full' or 'test' execution mode
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING US MARKET COMPLETE PIPELINE")
        logger.info("="*80 + "\n")
        
        # Step 1: Fetch and analyze overnight market regime
        market_data, regime_data = None, None
        if self.use_regime_intelligence:
            market_data, regime_data = self.fetch_and_analyze_market_regime()
            if not market_data:
                logger.warning("[WARNING] Market regime analysis failed - proceeding without regime intelligence")
        
        # Step 2: Run complete overnight pipeline if original modules available
        if self.use_original_modules:
            results = self.run_full_overnight_pipeline(mode=mode)
            if results:
                logger.info("[SUCCESS] Complete pipeline executed successfully")
                logger.info(f"Report: {results.get('report_path', 'N/A')}")
                
                # Display top opportunities
                top_opps = results.get('top_opportunities', [])
                if top_opps:
                    logger.info("\n" + "="*80)
                    logger.info("TOP OPPORTUNITIES")
                    logger.info("="*80)
                    for i, opp in enumerate(top_opps[:10], 1):
                        logger.info(f"{i:2d}. {opp['symbol']:8s} | Score: {opp['opportunity_score']:5.1f}/100 | "
                                  f"Signal: {opp['signal']:4s} | Conf: {opp['confidence']:5.1f}%")
                    logger.info("="*80 + "\n")
                
                return True
            else:
                logger.error("[ERROR] Pipeline execution failed")
                return False
        else:
            logger.warning("[WARNING] Original modules not available - falling back to basic mode")
            
            # Fall back to basic paper trading coordinator mode
            if self.use_sector_scan:
                if not self.load_sector_stocks():
                    logger.error("Failed to load sector stocks. Exiting.")
                    return False
            
            if len(self.symbols) == 0:
                logger.error("No symbols to trade. Exiting.")
                return False
            
            if check_market_hours and self.market_calendar:
                if not self.check_market_status():
                    logger.warning("US Markets are currently closed.")
                    return False
            
            # Run sophisticated overnight pipeline (not live trading!)
            try:
                logger.info("\n" + "="*80)
                logger.info("RUNNING SOPHISTICATED US OVERNIGHT SCREENING PIPELINE")
                logger.info("="*80)
                logger.info(f"Processing {len(self.symbols)} US stocks")
                logger.info("="*80 + "\n")
                
                # Import the REAL US overnight pipeline
                from models.screening.us_overnight_pipeline import USOvernightPipeline
                
                # Initialize and run the sophisticated overnight pipeline
                overnight_pipeline = USOvernightPipeline()
                
                # Run FULL sophisticated pipeline with FinBERT + LSTM + Technical analysis
                results = overnight_pipeline.run_full_pipeline(
                    sectors=None,  # All sectors
                    stocks_per_sector=30  # 240 total stocks
                )
                
                logger.info("\n" + "="*80)
                logger.info("[OK] US OVERNIGHT PIPELINE COMPLETED SUCCESSFULLY")
                logger.info("="*80)
                logger.info(f"Stocks Analyzed: {results.get('total_stocks', 0)}")
                logger.info(f"Top Opportunities: {results.get('top_opportunities_count', 0)}")
                logger.info(f"Report: {results.get('report_path', 'N/A')}")
                logger.info("="*80)
                
                return True
                    
            except KeyboardInterrupt:
                logger.info("\n" + "="*80)
                logger.info("STOPPING US PIPELINE")
                logger.info("="*80)
                logger.info("[OK] US Pipeline stopped successfully")
                return True
            except Exception as e:
                logger.error(f"[ERROR] Pipeline error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='US Market Complete Pipeline - NYSE/NASDAQ with Full Features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline with full sector scan (RECOMMENDED)
  python run_us_full_pipeline.py --full-scan --capital 100000
  
  # Run with preset
  python run_us_full_pipeline.py --preset "US Tech Giants" --capital 100000
  
  # Test mode (quick test with 5 stocks)
  python run_us_full_pipeline.py --mode test
  
  # Disable regime intelligence
  python run_us_full_pipeline.py --full-scan --no-regime
  
  # List available presets
  python run_us_full_pipeline.py --list-presets
        """
    )
    
    parser.add_argument('--symbols', type=str,
                       help='Comma-separated list of US symbols')
    parser.add_argument('--preset', type=str, choices=list(US_PRESETS.keys()),
                       help='Use a predefined US stock preset')
    parser.add_argument('--full-scan', action='store_true',
                       help='Scan all 240 stocks using sector configuration')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial trading capital in USD (default: 100000)')
    parser.add_argument('--config', type=str, default='config/live_trading_config.json',
                       help='Path to trading configuration file')
    parser.add_argument('--sectors-config', type=str, default='config/us_sectors.json',
                       help='Path to sectors configuration file')
    parser.add_argument('--ignore-market-hours', action='store_true',
                       help='Run even when markets are closed (for testing)')
    parser.add_argument('--no-regime', action='store_true',
                       help='Disable regime intelligence')
    parser.add_argument('--no-original', action='store_true',
                       help='Disable original modules (FinBERT, LSTM, etc.)')
    parser.add_argument('--mode', choices=['full', 'test'], default='full',
                       help='Execution mode: full (all sectors) or test (5 stocks)')
    parser.add_argument('--list-presets', action='store_true',
                       help='List all available US stock presets')
    
    args = parser.parse_args()
    
    # List presets if requested
    if args.list_presets:
        print("\nAvailable US Stock Presets:")
        print("="*80)
        for name, symbols in US_PRESETS.items():
            print(f"\n{name}:")
            print(f"  Symbols: {', '.join(symbols)}")
            print(f"  Count: {len(symbols)} stocks")
        print("\n" + "="*80)
        return
    
    # Determine symbols and mode
    use_sector_scan = False
    symbols = None
    
    if args.full_scan:
        use_sector_scan = True
        logger.info("Using FULL SECTOR SCAN mode (240 stocks)")
    elif args.preset:
        symbols = US_PRESETS[args.preset]
        logger.info(f"Using preset: {args.preset}")
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    elif args.mode == 'test':
        # Test mode: use default test symbols
        symbols = ['JPM', 'BAC', 'WFC', 'C', 'GS']
        logger.info("Test mode: using 5 US bank stocks")
    else:
        logger.error("Error: Must specify --full-scan, --symbols, --preset, or --mode test")
        parser.print_help()
        sys.exit(1)
    
    # Create and run pipeline
    pipeline = USFullPipelineRunner(
        symbols=symbols,
        capital=args.capital,
        config_path=args.config,
        use_sector_scan=use_sector_scan,
        sectors_config=args.sectors_config,
        use_regime_intelligence=not args.no_regime,
        use_original_modules=not args.no_original
    )
    
    success = pipeline.run(
        check_market_hours=not args.ignore_market_hours,
        mode=args.mode
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

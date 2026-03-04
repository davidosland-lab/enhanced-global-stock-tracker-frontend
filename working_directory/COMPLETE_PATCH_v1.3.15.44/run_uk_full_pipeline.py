# -*- coding: utf-8 -*-
"""
UK Market Pipeline (London Stock Exchange) - COMPLETE EDITION
==============================================================

Professional overnight screening pipeline for UK markets combining:
- Original sophisticated screening modules (FinBERT, LSTM, Event Risk Guard)
- NEW regime intelligence (14 regimes, 15+ cross-market features)
- Sector-based scanning (240 stocks across 8 sectors)
- ML ensemble prediction & smart filtering

Features:
- LSE market hours (08:00-16:30 GMT / 08:00-16:30 UTC)
- FinBERT sentiment analysis on news & filings
- LSTM price prediction models
- Basel III / regulatory event risk protection (FCA reporting)
- Market regime detection (US tech rally, commodity rotation, GBP weakness, etc.)
- Cross-market feature engineering (US/commodity/FX/rates)
- Regime-aware opportunity scoring (0-100)
- Morning report generation with email alerts
- CSV exports for further analysis

Workflow:
1. Fetch overnight market data (US markets, commodities, FX, UK gilts)
2. Detect market regime (14 types)
3. Scan all sectors (240 stocks: 8 sectors × 30 stocks)
4. Generate batch predictions (ML ensemble + LSTM)
5. Apply FinBERT sentiment analysis
6. Assess event risks (Basel III, FCA reporting, earnings, dividends)
7. Score opportunities with regime adjustments
8. Train/update LSTM models for top stocks
9. Generate comprehensive morning report
10. Send email notifications (optional)

Usage:
    # Full sector scan (240 stocks) - RECOMMENDED
    python run_uk_full_pipeline.py --full-scan --capital 100000
    
    # Quick preset scan
    python run_uk_full_pipeline.py --preset "FTSE 100 Leaders" --capital 100000
    
    # Custom symbols
    python run_uk_full_pipeline.py --symbols BARC.L,HSBA.L,LLOY.L --capital 50000
    
    # Test mode (5 stocks from Financials)
    python run_uk_full_pipeline.py --mode test
    
    # Disable regime intelligence
    python run_uk_full_pipeline.py --full-scan --no-regime

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

# Configure logging EARLY (before imports that might log)
Path('logs').mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/uk_full_pipeline.log', encoding='utf-8'),
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
OvernightPipeline = None
OriginalScanner = None
BatchPredictor = None
OpportunityScorer = None
ReportGenerator = None
ORIGINAL_MODULES_AVAILABLE = False

try:
    from models.screening.uk_overnight_pipeline import UKOvernightPipeline as OvernightPipeline
    logger.info("[OK] UKOvernightPipeline imported")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import UKOvernightPipeline: {e}")
    OvernightPipeline = None

try:
    from models.screening.stock_scanner import StockScanner as OriginalScanner
    logger.info("[OK] StockScanner imported")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import StockScanner: {e}")
    OriginalScanner = None

try:
    from models.screening.batch_predictor import BatchPredictor
    logger.info("[OK] BatchPredictor imported")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import BatchPredictor: {e}")
    logger.error(f"     Common cause: Missing scipy/pandas (pip install scipy pandas)")
    BatchPredictor = None

try:
    from models.screening.opportunity_scorer import OpportunityScorer
    logger.info("[OK] OpportunityScorer imported")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import OpportunityScorer: {e}")
    OpportunityScorer = None

try:
    from models.screening.report_generator import ReportGenerator
    logger.info("[OK] ReportGenerator imported")
except ImportError as e:
    logger.error(f"[ERROR] Failed to import ReportGenerator: {e}")
    ReportGenerator = None

# Check if all required modules are available
if all([OvernightPipeline, OriginalScanner, BatchPredictor, OpportunityScorer, ReportGenerator]):
    ORIGINAL_MODULES_AVAILABLE = True
    logger.info("[OK] All UK overnight pipeline modules loaded successfully")
else:
    ORIGINAL_MODULES_AVAILABLE = False
    logger.warning("[!] Some UK overnight pipeline modules are missing")
    logger.warning("[!] If you see 'No module named' errors above:")
    logger.warning("[!]   pip install transformers torch feedparser beautifulsoup4 scipy pandas")

# Optional modules (not required for basic operation)
try:
    from models.screening.finbert_bridge import FinBERTBridge
except ImportError:
    FinBERTBridge = None

try:
    from models.screening.lstm_trainer import LSTMTrainer
except ImportError:
    LSTMTrainer = None

try:
    from models.screening.event_risk_guard import EventRiskGuard
except ImportError:
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

# ASCII emoji mappings for Windows compatibility (kept for potential future use)
EMOJI_MAP = {
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]',
    '[WARNING]': '[WARNING]',
    '[INFO]': '[INFO]',
    '[SUCCESS]': '[SUCCESS]',
    '[FAILED]': '[FAILED]'
}

# UK Stock Presets
UK_PRESETS = {
    'FTSE 100 Leaders': ['HSBA.L', 'SHEL.L', 'AZN.L', 'BP.L', 'ULVR.L', 'RIO.L', 'GSK.L', 'DGE.L'],
    'UK Banks': ['HSBA.L', 'LLOY.L', 'BARC.L', 'NWG.L', 'STAN.L', 'CBRY.L'],
    'UK Mining': ['RIO.L', 'GLEN.L', 'AAL.L', 'ANTO.L', 'KAZ.L', 'EVR.L'],
    'UK Energy': ['BP.L', 'SHEL.L', 'SSE.L', 'NG.L', 'CPG.L', 'CNE.L'],
    'UK Consumer': ['ULVR.L', 'DGE.L', 'BATS.L', 'RKT.L', 'TSCO.L', 'SBRY.L', 'MKS.L'],
    'UK Healthcare': ['AZN.L', 'GSK.L', 'SN.L', 'VOD.L', 'HIK.L', 'BT.A.L'],
    'UK Industrials': ['BA.L', 'RR.L', 'CRH.L', 'IMI.L', 'WPP.L', 'SPX.L'],
    'UK Financials': ['HSBA.L', 'LLOY.L', 'BARC.L', 'PRU.L', 'LSEG.L', 'AVST.L'],
    'FTSE 100 Top 10': ['SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'RIO.L', 'BP.L', 'GSK.L', 'DGE.L', 'BAT.L', 'GLEN.L']
}


class UKFullPipelineRunner:
    """
    Complete UK Market Pipeline combining original sophistication with new regime intelligence
    """
    
    def __init__(self, symbols=None, capital=100000, config_path='config/live_trading_config.json',
                 use_sector_scan=False, sectors_config='config/uk_sectors.json',
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
        self.gmt = pytz.timezone('Europe/London')
        
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
        logger.info("UK MARKET PIPELINE - COMPLETE EDITION v1.3.15")
        logger.info("=" * 80)
        logger.info(f"Market: London Stock Exchange (LSE)")
        logger.info(f"Trading Hours: 08:00-16:30 GMT (08:00-16:30 UTC)")
        
        if use_sector_scan:
            logger.info(f"Mode: FULL SECTOR SCAN")
            logger.info(f"Sectors Config: {sectors_config}")
            logger.info(f"Expected Stocks: ~240 (8 sectors x 30 stocks)")
        else:
            logger.info(f"Mode: PRESET/CUSTOM")
            logger.info(f"Symbols: {', '.join(symbols) if len(symbols) <= 10 else f'{len(symbols)} symbols'}")
        
        logger.info(f"Initial Capital: £{capital:,.2f} GBP")
        
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
                available_modules.append("Event Risk Guard (Basel III, FCA reporting, earnings)")
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
    
    def validate_symbols(self):
        """Validate LSE symbols format"""
        valid_symbols = []
        for symbol in self.symbols:
            if not symbol.endswith('.L'):
                logger.warning(f"[WARNING] Symbol {symbol} doesn't have .L suffix - adding it")
                symbol = f"{symbol}.L"
            valid_symbols.append(symbol)
        
        self.symbols = valid_symbols
        logger.info(f"Validated symbols: {', '.join(self.symbols) if len(self.symbols) <= 10 else f'{len(self.symbols)} symbols'}")
    
    def check_market_status(self):
        """Check if LSE market is open"""
        try:
            status = self.market_calendar.get_market_status(Exchange.LSE)
            now_gmt = datetime.now(self.gmt)
            
            logger.info(f"LSE Market Status: {status.name}")
            logger.info(f"Current Time (GMT): {now_gmt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            if status == MarketStatus.OPEN:
                logger.info("[OK] LSE is OPEN - Trading enabled")
                return True
            elif status == MarketStatus.CLOSED:
                logger.warning("[ERROR] LSE is CLOSED - No trading")
                next_open = self.market_calendar.get_next_market_open(Exchange.LSE)
                if next_open:
                    logger.info(f"Next open: {next_open.astimezone(self.gmt).strftime('%Y-%m-%d %H:%M %Z')}")
                return False
            else:
                logger.warning(f"[WARNING] LSE Status: {status.name}")
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
            
            # Handle status - it might be a dict or string
            status_value = results.get('status', 'UNKNOWN')
            if isinstance(status_value, dict):
                status_str = status_value.get('phase', 'COMPLETE').upper()
            else:
                status_str = str(status_value).upper()
            
            logger.info(f"Status: {status_str}")
            logger.info(f"Execution Time: {results.get('execution_time_minutes', 'N/A')} minutes")
            
            # Safely access statistics
            stats = results.get('statistics', {})
            logger.info(f"Stocks Scanned: {stats.get('total_stocks_scanned', 'N/A')}")
            logger.info(f"Top Opportunities: {stats.get('top_opportunities_count', 'N/A')}")
            logger.info(f"Report: {results.get('report_path', 'N/A')}")
            logger.info("="*80 + "\n")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Overnight pipeline failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def run(self, check_market_hours=True, mode='full'):
        """
        Run the UK full pipeline
        
        Args:
            check_market_hours: Check if market is open
            mode: 'full' or 'test' execution mode
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING UK MARKET COMPLETE PIPELINE")
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
                        # Safe access to fields (some may be missing)
                        symbol = opp.get('symbol', 'N/A')
                        score = opp.get('opportunity_score', opp.get('score', 0))
                        signal = opp.get('signal', opp.get('prediction', 'N/A'))
                        confidence = opp.get('confidence', 0)
                        logger.info(f"{i:2d}. {symbol:10s} | Score: {score:5.1f}/100 | "
                                  f"Signal: {signal:4s} | Conf: {confidence:5.1f}%")
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
            
            # Validate symbols
            self.validate_symbols()
            
            if len(self.symbols) == 0:
                logger.error("No symbols to trade. Exiting.")
                return False
            
            if check_market_hours and self.market_calendar:
                if not self.check_market_status():
                    logger.warning("LSE is currently closed.")
                    return False
            
            # Run sophisticated overnight pipeline (not live trading!)
            try:
                logger.info("\n" + "="*80)
                logger.info("RUNNING SOPHISTICATED UK OVERNIGHT SCREENING PIPELINE")
                logger.info("="*80)
                logger.info(f"Processing {len(self.symbols)} UK stocks")
                logger.info("="*80 + "\n")
                
                # Import the overnight pipeline (can be used for UK market)
                from models.screening.overnight_pipeline import OvernightPipeline
                
                # Initialize and run the sophisticated overnight pipeline
                overnight_pipeline = OvernightPipeline()
                
                # Run FULL sophisticated pipeline with FinBERT + LSTM + Technical analysis
                results = overnight_pipeline.run_full_pipeline(
                    sectors=None,  # All sectors
                    stocks_per_sector=30  # 240 total stocks
                )
                
                logger.info("\n" + "="*80)
                logger.info("[OK] UK OVERNIGHT PIPELINE COMPLETED SUCCESSFULLY")
                logger.info("="*80)
                logger.info(f"Stocks Analyzed: {results.get('total_stocks', 0)}")
                logger.info(f"Top Opportunities: {results.get('top_opportunities_count', 0)}")
                logger.info(f"Report: {results.get('report_path', 'N/A')}")
                logger.info("="*80)
                
                return True
                    
            except KeyboardInterrupt:
                logger.info("\n" + "="*80)
                logger.info("STOPPING UK PIPELINE")
                logger.info("="*80)
                logger.info("[OK] UK Pipeline stopped successfully")
                return True
            except Exception as e:
                logger.error(f"[ERROR] Pipeline error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='UK Market Complete Pipeline - LSE with Full Features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline with full sector scan (RECOMMENDED)
  python run_uk_full_pipeline.py --full-scan --capital 100000
  
  # Run with preset
  python run_uk_full_pipeline.py --preset "FTSE 100 Leaders" --capital 100000
  
  # Test mode (quick test with 5 stocks)
  python run_uk_full_pipeline.py --mode test
  
  # Disable regime intelligence
  python run_uk_full_pipeline.py --full-scan --no-regime
  
  # List available presets
  python run_uk_full_pipeline.py --list-presets
        """
    )
    
    parser.add_argument('--symbols', type=str,
                       help='Comma-separated list of UK symbols (with .L suffix)')
    parser.add_argument('--preset', type=str, choices=list(UK_PRESETS.keys()),
                       help='Use a predefined UK stock preset')
    parser.add_argument('--full-scan', action='store_true',
                       help='Scan all 240 stocks using sector configuration')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial trading capital in GBP (default: 100000)')
    parser.add_argument('--config', type=str, default='config/live_trading_config.json',
                       help='Path to trading configuration file')
    parser.add_argument('--sectors-config', type=str, default='config/uk_sectors.json',
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
                       help='List all available UK stock presets')
    
    args = parser.parse_args()
    
    # List presets if requested
    if args.list_presets:
        print("\nAvailable UK Stock Presets:")
        print("="*80)
        for name, symbols in UK_PRESETS.items():
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
        symbols = UK_PRESETS[args.preset]
        logger.info(f"Using preset: {args.preset}")
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    elif args.mode == 'test':
        # Test mode: use default test symbols
        symbols = ['HSBA.L', 'LLOY.L', 'BARC.L', 'NWG.L', 'STAN.L']
        logger.info("Test mode: using 5 UK bank stocks")
    else:
        logger.error("Error: Must specify --full-scan, --symbols, --preset, or --mode test")
        parser.print_help()
        sys.exit(1)
    
    # Create and run pipeline
    pipeline = UKFullPipelineRunner(
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

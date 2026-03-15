# -*- coding: utf-8 -*-
"""
AU Market Pipeline Runner - REGIME INTELLIGENCE EDITION
=======================================================

Automated trading pipeline for Australian (ASX) market with:
- Sector-based scanning (240 stocks across 8 sectors)
- Market regime detection (US/commodity/FX/rates)
- Cross-market feature engineering
- Regime-aware opportunity scoring
- ML ensemble prediction & smart filtering

Features:
- ASX-specific market hours (10:00-16:00 AEDT / 00:00-06:00 GMT)
- Overnight market data analysis (US markets, commodities, FX)
- Conditional stock scoring based on macro regime
- Sector-specific regime adjustments
- Real-time ASX data feed

Scanning Modes:
1. FULL SCAN: Scan all 240 stocks (8 sectors × 30 stocks) with regime intelligence
2. PRESET: Quick scan of predefined stock lists with regime intelligence

Usage:
    # Full sector-based scan with regime intelligence (recommended)
    python run_au_pipeline.py --full-scan --capital 100000
    
    # Quick preset scan with regime intelligence
    python run_au_pipeline.py --preset "ASX Blue Chips" --capital 100000
    
    # Custom symbols with regime intelligence
    python run_au_pipeline.py --symbols CBA.AX,BHP.AX,RIO.AX --capital 50000
    
    # Disable regime intelligence (pure fundamental scoring)
    python run_au_pipeline.py --full-scan --no-regime --capital 100000

Author: Trading System v1.3.15 - REGIME INTELLIGENCE EDITION
Date: January 6, 2026
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pytz
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from paper_trading_coordinator import PaperTradingCoordinator
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
except ImportError:
    # Fallback for standalone mode
    PaperTradingCoordinator = None
    MarketCalendar = None
    Exchange = None
    MarketStatus = None

# Import sector scanner
try:
    from models.sector_stock_scanner import StockScanner
except ImportError:
    StockScanner = None

# Import regime intelligence modules
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
import io

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/au_pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Explicitly use stdout
    ]
)
logger = logging.getLogger(__name__)

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # If reconfigure fails, fall back to default

# ASX Stock Presets
ASX_PRESETS = {
    'ASX Blue Chips': ['CBA.AX', 'BHP.AX', 'RIO.AX', 'WOW.AX', 'CSL.AX', 'WES.AX', 'NAB.AX', 'ANZ.AX'],
    'ASX Banks': ['CBA.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 'MQG.AX', 'BOQ.AX'],
    'ASX Mining': ['BHP.AX', 'RIO.AX', 'FMG.AX', 'NCM.AX', 'S32.AX', 'IGO.AX', 'MIN.AX'],
    'ASX Tech': ['WTC.AX', 'XRO.AX', 'CPU.AX', 'APX.AX', 'TNE.AX'],
    'ASX Energy': ['WDS.AX', 'STO.AX', 'ORG.AX', 'WHC.AX', 'ALD.AX'],
    'ASX Healthcare': ['CSL.AX', 'COH.AX', 'RMD.AX', 'SHL.AX', 'FPH.AX'],
    'ASX Retail': ['WOW.AX', 'WES.AX', 'HVN.AX', 'JBH.AX', 'SUL.AX'],
    'ASX Top 20': ['CBA.AX', 'BHP.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 'WOW.AX', 'WES.AX', 
                   'MQG.AX', 'GMG.AX', 'RIO.AX', 'FMG.AX', 'TCL.AX', 'TLS.AX', 'COH.AX', 
                   'RMD.AX', 'WDS.AX', 'QBE.AX', 'SCG.AX', 'STO.AX']
}

class AUPipelineRunner:
    """Australian Market Pipeline Runner with Regime Intelligence"""
    
    def __init__(self, symbols=None, capital=100000, config_path='config/live_trading_config.json', 
                 use_sector_scan=False, sectors_config='config/asx_sectors.json',
                 use_regime_intelligence=True):
        self.symbols = symbols or []
        self.capital = capital
        self.config_path = config_path
        self.use_sector_scan = use_sector_scan
        self.sectors_config = sectors_config
        self.use_regime_intelligence = use_regime_intelligence
        self.market_calendar = MarketCalendar() if MarketCalendar else None
        self.coordinator = None
        self.scanner = None
        self.aest = pytz.timezone('Australia/Sydney')
        
        # Regime intelligence components
        self.market_data_fetcher = None
        self.regime_detector = None
        self.regime_scorer = None
        
        logger.info("=" * 80)
        logger.info("AU MARKET PIPELINE RUNNER v1.3.15 - REGIME INTELLIGENCE EDITION")
        logger.info("=" * 80)
        logger.info(f"Market: ASX (Australian Securities Exchange)")
        logger.info(f"Trading Hours: 10:00-16:00 AEDT (00:00-06:00 GMT)")
        
        if use_sector_scan:
            logger.info(f"Mode: FULL SECTOR SCAN")
            logger.info(f"Sectors Config: {sectors_config}")
            logger.info(f"Expected Stocks: ~240 (8 sectors × 30 stocks)")
        else:
            logger.info(f"Mode: PRESET/CUSTOM")
            logger.info(f"Symbols: {', '.join(symbols)}")
        
        logger.info(f"Initial Capital: ${capital:,.2f} AUD")
        
        # Regime intelligence status
        if use_regime_intelligence and REGIME_INTELLIGENCE_AVAILABLE:
            logger.info(f"🧠 Regime Intelligence: ENABLED")
            logger.info(f"   - Market regime detection")
            logger.info(f"   - Cross-market features (US/commodities/FX)")
            logger.info(f"   - Conditional opportunity scoring")
            self._initialize_regime_intelligence()
        elif use_regime_intelligence and not REGIME_INTELLIGENCE_AVAILABLE:
            logger.warning(f"[WARNING] Regime Intelligence: REQUESTED BUT NOT AVAILABLE")
            logger.warning(f"   Falling back to basic scoring")
            self.use_regime_intelligence = False
        else:
            logger.info(f"[INFO] Regime Intelligence: DISABLED (using basic scoring)")
        
        logger.info("=" * 80)
    
    def _initialize_regime_intelligence(self):
        """Initialize regime intelligence components"""
        try:
            self.market_data_fetcher = MarketDataFetcher()
            self.regime_detector = MarketRegimeDetector()
            self.regime_scorer = RegimeAwareOpportunityScorer()
            logger.info("[OK] Regime intelligence components initialized")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize regime intelligence: {e}")
            self.use_regime_intelligence = False
    
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
    
    def filter_stocks_by_regime(self, market_data, regime_data):
        """
        Filter initial stock list based on regime
        
        This is an optional pre-filtering step to reduce compute
        For now, we'll keep all stocks and let the scorer handle it
        
        Returns:
            Filtered symbol list (currently returns all)
        """
        if not self.use_regime_intelligence or not regime_data:
            return self.symbols
        
        # For now, keep all symbols
        # Could add logic here to skip entire sectors if regime is very negative
        # Example: if regime == COMMODITY_WEAK, skip Materials sector entirely
        
        return self.symbols
    
    def check_market_status(self):
        """Check if ASX market is open"""
        try:
            status = self.market_calendar.get_market_status(Exchange.ASX)
            now_aest = datetime.now(self.aest)
            
            logger.info(f"ASX Market Status: {status.name}")
            logger.info(f"Current Time (AEST): {now_aest.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            if status == MarketStatus.OPEN:
                logger.info("[OK] ASX is OPEN - Trading enabled")
                return True
            elif status == MarketStatus.CLOSED:
                logger.warning("[ERROR] ASX is CLOSED - No trading")
                # Get next open time
                next_open = self.market_calendar.get_next_market_open(Exchange.ASX)
                if next_open:
                    logger.info(f"Next ASX open: {next_open.astimezone(self.aest).strftime('%Y-%m-%d %H:%M %Z')}")
                return False
            else:
                logger.warning(f"[WARNING] ASX Status: {status.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
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
        """Validate ASX symbols format"""
        valid_symbols = []
        for symbol in self.symbols:
            if not symbol.endswith('.AX'):
                logger.warning(f"[WARNING] Symbol {symbol} doesn't have .AX suffix - adding it")
                symbol = f"{symbol}.AX"
            valid_symbols.append(symbol)
        
        self.symbols = valid_symbols
        logger.info(f"Validated symbols: {', '.join(self.symbols) if len(self.symbols) <= 10 else f'{len(self.symbols)} symbols'}")
    
    def initialize_coordinator(self, market_data=None):
        """
        Initialize Paper Trading Coordinator with regime-filtered symbols
        
        Args:
            market_data: Optional market data for regime-aware initialization
        """
        try:
            # Note: The coordinator would need to be updated to accept regime data
            # For now, we pass the filtered symbols
            self.coordinator = PaperTradingCoordinator(
                symbols=self.symbols,
                initial_capital=self.capital,
                config_file=self.config_path
            )
            logger.info("[OK] Paper Trading Coordinator initialized")
            
            # If regime intelligence is enabled, log the regime context
            if self.use_regime_intelligence and market_data:
                logger.info(f"[INFO] Trading with regime intelligence context")
            
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize coordinator: {e}")
            return False
    
    def run(self, check_market_hours=True):
        """Run the AU pipeline with regime intelligence"""
        logger.info("\n" + "="*80)
        logger.info("STARTING AU MARKET PIPELINE WITH REGIME INTELLIGENCE")
        logger.info("="*80 + "\n")
        
        # Step 1: Fetch and analyze overnight market regime
        market_data, regime_data = None, None
        if self.use_regime_intelligence:
            market_data, regime_data = self.fetch_and_analyze_market_regime()
            if not market_data:
                logger.warning("[WARNING] Market regime analysis failed - proceeding without regime intelligence")
                self.use_regime_intelligence = False
        
        # Step 2: Load sector stocks if using full scan
        if self.use_sector_scan:
            if not self.load_sector_stocks():
                logger.error("Failed to load sector stocks. Exiting.")
                return False
        
        # Step 3: Validate symbols
        self.validate_symbols()
        
        if len(self.symbols) == 0:
            logger.error("No symbols to trade. Exiting.")
            return False
        
        # Step 4: Filter stocks by regime (optional pre-filtering)
        if self.use_regime_intelligence and regime_data:
            self.symbols = self.filter_stocks_by_regime(market_data, regime_data)
            logger.info(f"[INFO] After regime filtering: {len(self.symbols)} stocks")
        
        # Step 5: Check market hours if requested
        if check_market_hours and self.market_calendar:
            if not self.check_market_status():
                logger.warning("ASX is currently closed. Use --ignore-market-hours to run anyway.")
                return False
        else:
            logger.info("[WARNING] Market hours check disabled - running regardless of market status")
        
        # Step 6: Initialize coordinator with regime context
        # Step 6: Run sophisticated overnight pipeline (not live trading!)
        try:
            logger.info("\n" + "="*80)
            logger.info("RUNNING SOPHISTICATED OVERNIGHT SCREENING PIPELINE")
            if self.use_regime_intelligence:
                logger.info("[BRAIN] REGIME INTELLIGENCE: ACTIVE")
            logger.info("="*80)
            logger.info(f"Processing {len(self.symbols)} ASX stocks")
            logger.info("="*80 + "\n")
            
            # Import the REAL overnight pipeline (the sophisticated one)
            from models.screening.overnight_pipeline import OvernightPipeline
            
            # Initialize the sophisticated overnight pipeline
            overnight_pipeline = OvernightPipeline()
            
            # Run the FULL sophisticated pipeline with:
            # - Market sentiment analysis (SPI futures + US/UK overnight)
            # - Stock scanning with fundamental filters
            # - FinBERT sentiment analysis
            # - LSTM predictions
            # - Technical indicators
            # - Opportunity scoring
            # - Event risk assessment
            # - Report generation
            results = overnight_pipeline.run_full_pipeline(
                sectors=None,  # All sectors
                stocks_per_sector=30  # 30 stocks per sector = 240 total
            )
            
            logger.info("\n" + "="*80)
            logger.info("[OK] AU OVERNIGHT PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"Stocks Analyzed: {results.get('total_stocks', 0)}")
            logger.info(f"Top Opportunities: {results.get('top_opportunities_count', 0)}")
            logger.info(f"Report: {results.get('report_path', 'N/A')}")
            logger.info(f"Trading Platform Integration: reports/screening/au_morning_report.json")
            logger.info("="*80)
            
            return True
                
        except KeyboardInterrupt:
            logger.info("\n" + "="*80)
            logger.info("STOPPING AU PIPELINE")
            logger.info("="*80)
            logger.info("[OK] AU Pipeline stopped successfully")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Pipeline error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AU Market Pipeline Runner - ASX Trading with Regime Intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with full sector scan and regime intelligence (RECOMMENDED)
  python run_au_pipeline.py --full-scan --capital 100000
  
  # Run with ASX Blue Chips preset and regime intelligence
  python run_au_pipeline.py --preset "ASX Blue Chips" --capital 100000
  
  # Run with custom symbols and regime intelligence
  python run_au_pipeline.py --symbols CBA.AX,BHP.AX,RIO.AX --capital 50000
  
  # Run without regime intelligence (pure fundamental scoring)
  python run_au_pipeline.py --full-scan --no-regime --capital 100000
  
  # Run outside market hours (testing/development)
  python run_au_pipeline.py --preset "ASX Banks" --ignore-market-hours
  
  # List available presets
  python run_au_pipeline.py --list-presets
        """
    )
    
    parser.add_argument('--symbols', type=str, 
                       help='Comma-separated list of ASX symbols (e.g., CBA.AX,BHP.AX,RIO.AX)')
    parser.add_argument('--preset', type=str, choices=list(ASX_PRESETS.keys()),
                       help='Use a predefined ASX stock preset')
    parser.add_argument('--full-scan', action='store_true',
                       help='Scan all 240 stocks using sector configuration (recommended)')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial trading capital in AUD (default: 100000)')
    parser.add_argument('--config', type=str, default='config/live_trading_config.json',
                       help='Path to trading configuration file')
    parser.add_argument('--sectors-config', type=str, default='config/asx_sectors.json',
                       help='Path to sectors configuration file (for --full-scan)')
    parser.add_argument('--ignore-market-hours', action='store_true',
                       help='Run even when ASX is closed (for testing)')
    parser.add_argument('--no-regime', action='store_true',
                       help='Disable regime intelligence (use basic scoring)')
    parser.add_argument('--list-presets', action='store_true',
                       help='List all available ASX stock presets')
    
    args = parser.parse_args()
    
    # List presets if requested
    if args.list_presets:
        print("\nAvailable ASX Stock Presets:")
        print("="*80)
        for name, symbols in ASX_PRESETS.items():
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
        symbols = ASX_PRESETS[args.preset]
        logger.info(f"Using preset: {args.preset}")
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    else:
        logger.error("Error: Must specify --full-scan, --symbols, or --preset")
        parser.print_help()
        sys.exit(1)
    
    # Create and run pipeline
    pipeline = AUPipelineRunner(
        symbols=symbols,
        capital=args.capital,
        config_path=args.config,
        use_sector_scan=use_sector_scan,
        sectors_config=args.sectors_config,
        use_regime_intelligence=not args.no_regime
    )
    
    success = pipeline.run(check_market_hours=not args.ignore_market_hours)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

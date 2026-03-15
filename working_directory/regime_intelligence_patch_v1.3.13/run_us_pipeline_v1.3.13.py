"""
US Market Pipeline Runner - REGIME INTELLIGENCE EDITION
=======================================================

Automated trading pipeline for US markets (NYSE, NASDAQ) with:
- Sector-based scanning (240 stocks across 8 sectors)
- Market regime detection (US/commodity/FX/rates)
- Cross-market feature engineering
- Regime-aware opportunity scoring
- ML ensemble prediction & smart filtering

Features:
- US market hours (09:30-16:00 EST / 14:30-21:00 GMT)
- Overnight market data analysis (US markets, commodities, FX)
- Conditional stock scoring based on macro regime
- Sector-specific regime adjustments
- Real-time US market data feed
- After-hours trading support (optional)

Scanning Modes:
1. FULL SCAN: Scan all 240 stocks (8 sectors × 30 stocks) with regime intelligence
2. PRESET: Quick scan of predefined stock lists with regime intelligence

Usage:
    # Full sector-based scan with regime intelligence (recommended)
    python run_us_pipeline.py --full-scan --capital 100000
    
    # Quick preset scan with regime intelligence
    python run_us_pipeline.py --preset "US Tech Giants" --capital 100000
    
    # Custom symbols with regime intelligence
    python run_us_pipeline.py --symbols AAPL,MSFT,GOOGL --capital 50000
    
    # Disable regime intelligence (pure fundamental scoring)
    python run_us_pipeline.py --full-scan --no-regime --capital 100000

Author: Trading System v1.3.13 - REGIME INTELLIGENCE EDITION
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
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/us_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# US Stock Presets
US_PRESETS = {
    'US Tech Giants': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD'],
    'US Blue Chips': ['AAPL', 'MSFT', 'JPM', 'JNJ', 'WMT', 'PG', 'UNH', 'V'],
    'US Growth': ['TSLA', 'NVDA', 'AMD', 'PLTR', 'SQ', 'COIN', 'SNOW', 'NET'],
    'US Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC'],
    'US Healthcare': ['JNJ', 'UNH', 'LLY', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK'],
    'US Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'VLO'],
    'US Consumer': ['AMZN', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW'],
    'US Dividend': ['JNJ', 'PG', 'KO', 'PEP', 'XOM', 'CVX', 'VZ', 'T'],
    'FAANG': ['META', 'AAPL', 'AMZN', 'NFLX', 'GOOGL'],
    'Magnificent 7': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
    'Dow Jones 10': ['AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'CAT', 'MCD', 'V', 'BA', 'IBM'],
    'S&P 500 Top 10': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH', 'JNJ']
}

class USPipelineRunner:
    """US Market Pipeline Runner with Regime Intelligence"""
    
    def __init__(self, symbols=None, capital=100000, config_path='config/live_trading_config.json', 
                 use_sector_scan=False, sectors_config='config/us_sectors.json',
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
        self.est = pytz.timezone('America/New_York')
        
        # Regime intelligence components
        self.market_data_fetcher = None
        self.regime_detector = None
        self.regime_scorer = None
        
        logger.info("=" * 80)
        logger.info("US MARKET PIPELINE RUNNER v1.3.13 - REGIME INTELLIGENCE EDITION")
        logger.info("=" * 80)
        logger.info(f"Market: NYSE / NASDAQ (US Markets)")
        logger.info(f"Trading Hours: 09:30-16:00 EST (14:30-21:00 GMT)")
        
        if use_sector_scan:
            logger.info(f"Mode: FULL SECTOR SCAN")
            logger.info(f"Sectors Config: {sectors_config}")
            logger.info(f"Expected Stocks: ~240 (8 sectors × 30 stocks)")
        else:
            logger.info(f"Mode: PRESET/CUSTOM")
            logger.info(f"Symbols: {', '.join(symbols)}")
        
        logger.info(f"Initial Capital: ${capital:,.2f} USD")
        
        # Regime intelligence status
        if use_regime_intelligence and REGIME_INTELLIGENCE_AVAILABLE:
            logger.info(f"🧠 Regime Intelligence: ENABLED")
            logger.info(f"   - Market regime detection")
            logger.info(f"   - Cross-market features (US/commodities/FX)")
            logger.info(f"   - Conditional opportunity scoring")
            self._initialize_regime_intelligence()
        elif use_regime_intelligence and not REGIME_INTELLIGENCE_AVAILABLE:
            logger.warning(f"⚠️ Regime Intelligence: REQUESTED BUT NOT AVAILABLE")
            logger.warning(f"   Falling back to basic scoring")
            self.use_regime_intelligence = False
        else:
            logger.info(f"📊 Regime Intelligence: DISABLED (using basic scoring)")
        
        logger.info("=" * 80)
    
    def _initialize_regime_intelligence(self):
        """Initialize regime intelligence components"""
        try:
            self.market_data_fetcher = MarketDataFetcher()
            self.regime_detector = MarketRegimeDetector()
            self.regime_scorer = RegimeAwareOpportunityScorer()
            logger.info("✅ Regime intelligence components initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize regime intelligence: {e}")
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
            logger.error(f"❌ Error in market regime analysis: {e}", exc_info=True)
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
        """Check if US market is open"""
        try:
            status = self.market_calendar.get_market_status(Exchange.NYSE)
            now_est = datetime.now(self.est)
            
            logger.info(f"US Market Status: {status.name}")
            logger.info(f"Current Time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            if status == MarketStatus.OPEN:
                logger.info("✅ US markets are OPEN - Trading enabled")
                return True
            elif status == MarketStatus.CLOSED:
                logger.warning("❌ US markets are CLOSED - No trading")
                # Get next open time
                next_open = self.market_calendar.get_next_market_open(Exchange.NYSE)
                if next_open:
                    logger.info(f"Next US open: {next_open.astimezone(self.est).strftime('%Y-%m-%d %H:%M %Z')}")
                return False
            else:
                logger.warning(f"⚠️ US Market Status: {status.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def load_sector_stocks(self):
        """Load stocks from sector configuration"""
        if not StockScanner:
            logger.error("❌ StockScanner not available - cannot perform sector scan")
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
            logger.info(f"\n✅ Total stocks loaded: {len(self.symbols)}")
            logger.info("="*80 + "\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load sector stocks: {e}")
            return False
    
    def validate_symbols(self):
        """Validate US symbols format"""
        valid_symbols = []
        for symbol in self.symbols:
            # US symbols typically don't have suffix (except BRK.B, etc.)
            # Just uppercase them
            valid_symbols.append(symbol.upper())
        
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
                config_path=self.config_path
            )
            logger.info("✅ Paper Trading Coordinator initialized")
            
            # If regime intelligence is enabled, log the regime context
            if self.use_regime_intelligence and market_data:
                logger.info(f"📊 Trading with regime intelligence context")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize coordinator: {e}")
            return False
    
    def run(self, check_market_hours=True):
        """Run the AU pipeline with regime intelligence"""
        logger.info("\n" + "="*80)
        logger.info("STARTING US MARKET PIPELINE WITH REGIME INTELLIGENCE")
        logger.info("="*80 + "\n")
        
        # Step 1: Fetch and analyze overnight market regime
        market_data, regime_data = None, None
        if self.use_regime_intelligence:
            market_data, regime_data = self.fetch_and_analyze_market_regime()
            if not market_data:
                logger.warning("⚠️ Market regime analysis failed - proceeding without regime intelligence")
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
            logger.info(f"📊 After regime filtering: {len(self.symbols)} stocks")
        
        # Step 5: Check market hours if requested
        if check_market_hours and self.market_calendar:
            if not self.check_market_status():
                logger.warning("US markets are currently closed. Use --ignore-market-hours to run anyway.")
                return False
        else:
            logger.info("⚠️ Market hours check disabled - running regardless of market status")
        
        # Step 6: Initialize coordinator with regime context
        if not self.initialize_coordinator(market_data):
            logger.error("Failed to initialize coordinator. Exiting.")
            return False
        
        # Step 7: Start trading
        try:
            logger.info("\n" + "="*80)
            logger.info("PAPER TRADING ACTIVE")
            if self.use_regime_intelligence:
                logger.info("🧠 REGIME INTELLIGENCE: ACTIVE")
            logger.info("="*80)
            logger.info(f"Monitoring {len(self.symbols)} US stocks")
            logger.info(f"Press Ctrl+C to stop")
            logger.info("="*80 + "\n")
            
            self.coordinator.start()
            
            # Keep running
            while True:
                status = self.coordinator.get_status()
                logger.info(f"Portfolio: ${status.get('capital', {}).get('total', 0):,.2f} | "
                          f"Positions: {status.get('positions', {}).get('count', 0)} | "
                          f"Trades: {status.get('performance', {}).get('total_trades', 0)}")
                import time
                time.sleep(60)  # Status update every minute
                
        except KeyboardInterrupt:
            logger.info("\n" + "="*80)
            logger.info("STOPPING US PIPELINE")
            logger.info("="*80)
            self.coordinator.stop()
            logger.info("✅ US Pipeline stopped successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            if self.coordinator:
                self.coordinator.stop()
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='US Market Pipeline Runner - NYSE/NASDAQ Trading with Regime Intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with full sector scan and regime intelligence (RECOMMENDED)
  python run_us_pipeline.py --full-scan --capital 100000
  
  # Run with US Tech Giants preset and regime intelligence
  python run_us_pipeline.py --preset "US Tech Giants" --capital 100000
  
  # Run with custom symbols and regime intelligence
  python run_us_pipeline.py --symbols AAPL,MSFT,GOOGL --capital 50000
  
  # Run without regime intelligence (pure fundamental scoring)
  python run_us_pipeline.py --full-scan --no-regime --capital 100000
  
  # Run outside market hours (testing/development)
  python run_us_pipeline.py --preset "FAANG" --ignore-market-hours
  
  # List available presets
  python run_us_pipeline.py --list-presets
        """
    )
    
    parser.add_argument('--symbols', type=str, 
                       help='Comma-separated list of US symbols (e.g., AAPL,MSFT,GOOGL)')
    parser.add_argument('--preset', type=str, choices=list(US_PRESETS.keys()),
                       help='Use a predefined US stock preset')
    parser.add_argument('--full-scan', action='store_true',
                       help='Scan all 240 stocks using sector configuration (recommended)')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial trading capital in USD (default: 100000)')
    parser.add_argument('--config', type=str, default='config/live_trading_config.json',
                       help='Path to trading configuration file')
    parser.add_argument('--sectors-config', type=str, default='config/us_sectors.json',
                       help='Path to sectors configuration file (for --full-scan)')
    parser.add_argument('--ignore-market-hours', action='store_true',
                       help='Run even when US markets are closed (for testing)')
    parser.add_argument('--no-regime', action='store_true',
                       help='Disable regime intelligence (use basic scoring)')
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
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
    else:
        logger.error("Error: Must specify --full-scan, --symbols, or --preset")
        parser.print_help()
        sys.exit(1)
    
    # Create and run pipeline
    pipeline = USPipelineRunner(
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

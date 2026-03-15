"""
Intraday Rescan Manager for Phase 3 Auto-Rescan
================================================

This module orchestrates the complete intraday rescanning workflow,
integrating all Phase 3 components for day trading support.

Key Features:
- Integrates Incremental Scanner, Breakout Detector, Alert Dispatcher
- Manages rescan lifecycle (scan -> detect -> alert)
- Tracks opportunities across rescans
- Provides performance metrics

Author: FinBERT Enhanced Stock Screener
Version: 1.0.0 (Phase 3 Auto-Rescan)
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

# Add parent directories to path for imports
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from models.screening.incremental_scanner import IncrementalScanner
from models.screening.breakout_detector import BreakoutDetector, BreakoutSignal
from models.scheduling.alert_dispatcher import AlertDispatcher
from models.screening.market_hours_detector import MarketHoursDetector

logger = logging.getLogger(__name__)


class IntradayRescanManager:
    """
    Orchestrates the complete intraday rescanning workflow.
    
    Workflow:
    1. Check market hours
    2. Fetch current quotes for tracked stocks
    3. Filter stocks needing rescan (incremental)
    4. Detect breakouts on filtered stocks
    5. Dispatch alerts for significant breakouts
    6. Update state and tracking
    """
    
    def __init__(
        self,
        market: str = "US",
        config_file: Optional[str] = None,
        scanner: Optional[IncrementalScanner] = None,
        detector: Optional[BreakoutDetector] = None,
        dispatcher: Optional[AlertDispatcher] = None
    ):
        """
        Initialize intraday rescan manager.
        
        Args:
            market: Market identifier ('US' or 'ASX')
            config_file: Path to configuration JSON file
            scanner: Optional IncrementalScanner instance
            detector: Optional BreakoutDetector instance
            dispatcher: Optional AlertDispatcher instance
        """
        self.market = market
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.market_detector = MarketHoursDetector()
        
        # Use provided components or create new ones
        self.scanner = scanner or IncrementalScanner(
            price_change_threshold=self.config.get('price_change_threshold', 2.0),
            volume_multiplier=self.config.get('volume_multiplier', 1.5),
            min_rescan_interval=self.config.get('min_rescan_interval', 15)
        )
        
        self.detector = detector or BreakoutDetector(
            price_breakout_threshold=self.config.get('price_breakout_threshold', 2.0),
            volume_spike_multiplier=self.config.get('volume_spike_multiplier', 2.0),
            momentum_threshold=self.config.get('momentum_threshold', 3.0),
            min_signal_strength=self.config.get('min_signal_strength', 60.0)
        )
        
        self.dispatcher = dispatcher or AlertDispatcher(
            config=self.config
        )
        
        # State tracking
        self.tracked_opportunities: Dict[str, Dict] = {}
        self.rescan_count = 0
        self.start_time = datetime.now()
        
        logger.info(f"IntradayRescanManager initialized for {market} market")
        logger.info(f"  Config: {config_file or 'default'}")
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file"""
        if not config_file:
            return {}
        
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        return {}
    
    def is_market_open(self) -> bool:
        """
        Check if market is currently open.
        
        Returns:
            True if market is open for trading
        """
        if self.market == "US":
            return self.market_detector.is_us_market_open()
        elif self.market == "ASX":
            return self.market_detector.is_asx_market_open()
        else:
            logger.warning(f"Unknown market: {self.market}")
            return False
    
    def perform_rescan(
        self,
        stock_quotes: List[Dict],
        full_scan: bool = False
    ) -> Dict:
        """
        Perform a complete rescan cycle.
        
        Args:
            stock_quotes: List of current stock quote dictionaries
            full_scan: If True, force full scan (skip incremental filtering)
            
        Returns:
            Dictionary with rescan results
        """
        rescan_start = datetime.now()
        self.rescan_count += 1
        
        logger.info(f"\n{'='*80}")
        logger.info(f"INTRADAY RESCAN #{self.rescan_count} - {self.market} Market")
        logger.info(f"Time: {rescan_start.strftime('%H:%M:%S')}")
        logger.info(f"{'='*80}")
        
        # Check market hours
        if not self.is_market_open():
            logger.warning(f"{self.market} market is CLOSED - rescanning anyway for testing")
        
        # Step 1: Filter stocks for rescan (unless full scan requested)
        if full_scan:
            logger.info("FULL SCAN requested - processing all stocks")
            stocks_to_scan = stock_quotes
            skip_reasons = {}
        else:
            logger.info("Step 1: Incremental Filtering")
            stocks_to_scan, skip_reasons = self.scanner.filter_stocks_for_rescan(stock_quotes)
        
        # Step 2: Detect breakouts
        logger.info(f"\nStep 2: Breakout Detection ({len(stocks_to_scan)} stocks)")
        breakout_signals = self.detector.scan_multiple_stocks(stocks_to_scan)
        
        # Step 3: Dispatch alerts for high-strength signals
        alert_threshold = self.config.get('alert_threshold', 70.0)
        high_priority_signals = [
            s for s in breakout_signals
            if s.strength >= alert_threshold
        ]
        
        logger.info(f"\nStep 3: Alert Dispatching ({len(high_priority_signals)} high-priority)")
        alert_results = []
        for signal in high_priority_signals:
            result = self.dispatcher.dispatch_breakout_alert(signal.to_dict())
            alert_results.append({
                'symbol': signal.symbol,
                'type': signal.breakout_type.value,
                'channels': result
            })
        
        # Step 4: Update state
        logger.info("\nStep 4: State Update")
        self.scanner.update_snapshots(stocks_to_scan)
        self.scanner.save_state(self.market)
        
        # Track new opportunities
        for signal in breakout_signals:
            self._track_opportunity(signal)
        
        # Calculate performance metrics
        rescan_duration = (datetime.now() - rescan_start).total_seconds()
        
        results = {
            'rescan_number': self.rescan_count,
            'timestamp': rescan_start.isoformat(),
            'duration_seconds': rescan_duration,
            'market_open': self.is_market_open(),
            'total_stocks': len(stock_quotes),
            'scanned_stocks': len(stocks_to_scan),
            'skipped_stocks': len(skip_reasons),
            'api_savings_pct': (len(skip_reasons) / len(stock_quotes) * 100) if stock_quotes else 0,
            'breakouts_detected': len(breakout_signals),
            'alerts_sent': len(alert_results),
            'signals': [s.to_dict() for s in breakout_signals],
            'alert_results': alert_results
        }
        
        # Log summary
        logger.info(f"\n{'='*80}")
        logger.info(f"RESCAN COMPLETE")
        logger.info(f"  Duration: {rescan_duration:.1f}s")
        logger.info(f"  Scanned: {len(stocks_to_scan)}/{len(stock_quotes)} stocks")
        logger.info(f"  API Savings: {results['api_savings_pct']:.1f}%")
        logger.info(f"  Breakouts: {len(breakout_signals)}")
        logger.info(f"  Alerts: {len(alert_results)}")
        logger.info(f"{'='*80}\n")
        
        return results
    
    def _track_opportunity(self, signal: BreakoutSignal) -> None:
        """
        Track an opportunity across rescans.
        
        Args:
            signal: Breakout signal to track
        """
        symbol = signal.symbol
        
        if symbol not in self.tracked_opportunities:
            self.tracked_opportunities[symbol] = {
                'first_detected': signal.timestamp.isoformat(),
                'signals': [],
                'highest_strength': 0
            }
        
        opp = self.tracked_opportunities[symbol]
        opp['signals'].append({
            'timestamp': signal.timestamp.isoformat(),
            'type': signal.breakout_type.value,
            'strength': signal.strength,
            'price': signal.price
        })
        
        opp['highest_strength'] = max(opp['highest_strength'], signal.strength)
        opp['last_updated'] = signal.timestamp.isoformat()
    
    def get_tracked_opportunities(
        self,
        min_strength: Optional[float] = None,
        max_count: Optional[int] = None
    ) -> List[Dict]:
        """
        Get currently tracked opportunities.
        
        Args:
            min_strength: Optional minimum strength filter
            max_count: Optional maximum number to return
            
        Returns:
            List of tracked opportunities
        """
        opportunities = list(self.tracked_opportunities.items())
        
        # Filter by strength
        if min_strength:
            opportunities = [
                (symbol, data) for symbol, data in opportunities
                if data['highest_strength'] >= min_strength
            ]
        
        # Sort by highest strength
        opportunities.sort(key=lambda x: x[1]['highest_strength'], reverse=True)
        
        # Limit count
        if max_count:
            opportunities = opportunities[:max_count]
        
        return [
            {'symbol': symbol, **data}
            for symbol, data in opportunities
        ]
    
    def get_session_stats(self) -> Dict:
        """
        Get current session statistics.
        
        Returns:
            Dictionary with session stats
        """
        session_duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'market': self.market,
            'session_start': self.start_time.isoformat(),
            'session_duration_minutes': session_duration / 60,
            'rescan_count': self.rescan_count,
            'tracked_opportunities': len(self.tracked_opportunities),
            'scanner_stats': self.scanner.get_scan_stats(),
            'alert_stats': self.dispatcher.get_alert_stats(),
            'market_open': self.is_market_open()
        }
    
    def reset_session(self) -> None:
        """Reset session state (for new day)"""
        self.tracked_opportunities.clear()
        self.rescan_count = 0
        self.start_time = datetime.now()
        self.scanner.reset_state()
        self.detector.reset()
        logger.info("Session state reset")


def test_rescan_manager():
    """Test intraday rescan manager"""
    print("\n" + "="*80)
    print("TESTING INTRADAY RESCAN MANAGER")
    print("="*80)
    
    # Initialize manager
    manager = IntradayRescanManager(market="US")
    
    # Simulate first rescan
    print("\n--- RESCAN #1 ---")
    test_quotes_1 = [
        {
            'symbol': 'AAPL',
            'price': 175.50,
            'open': 175.00,
            'dayHigh': 175.50,
            'dayLow': 174.00,
            'previousClose': 175.00,
            'volume': 50_000_000,
            'avg_volume': 60_000_000
        },
        {
            'symbol': 'MSFT',
            'price': 380.25,
            'open': 380.00,
            'dayHigh': 380.25,
            'dayLow': 379.00,
            'previousClose': 380.00,
            'volume': 25_000_000,
            'avg_volume': 30_000_000
        },
    ]
    
    results_1 = manager.perform_rescan(test_quotes_1, full_scan=True)
    
    # Simulate second rescan with changes
    print("\n--- RESCAN #2 (15 min later) ---")
    import time
    time.sleep(1)
    
    test_quotes_2 = [
        {
            'symbol': 'AAPL',
            'price': 176.00,  # +0.3% - skip
            'open': 175.00,
            'dayHigh': 176.00,
            'dayLow': 174.00,
            'previousClose': 175.00,
            'volume': 51_000_000,
            'avg_volume': 60_000_000
        },
        {
            'symbol': 'MSFT',
            'price': 389.50,  # +2.4% - RESCAN!
            'open': 380.00,
            'dayHigh': 389.50,
            'dayLow': 379.00,
            'previousClose': 380.00,
            'volume': 90_000_000,  # 3x volume!
            'avg_volume': 30_000_000,
            'intraday_data': {
                'momentum_15m': 4.2,
                'momentum_60m': 3.1
            }
        },
    ]
    
    results_2 = manager.perform_rescan(test_quotes_2)
    
    # Show session stats
    print("\n--- SESSION STATISTICS ---")
    stats = manager.get_session_stats()
    print(json.dumps(stats, indent=2))
    
    # Show tracked opportunities
    print("\n--- TRACKED OPPORTUNITIES ---")
    opportunities = manager.get_tracked_opportunities()
    for opp in opportunities:
        print(f"\n{opp['symbol']}:")
        print(f"  Highest Strength: {opp['highest_strength']:.1f}")
        print(f"  Signal Count: {len(opp['signals'])}")
        print(f"  First Detected: {opp['first_detected']}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_rescan_manager()

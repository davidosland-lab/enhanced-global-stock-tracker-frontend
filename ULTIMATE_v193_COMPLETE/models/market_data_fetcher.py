#!/usr/bin/env python3
"""
Market Data Fetcher for Regime Detection
Fetches overnight US market, commodity, FX, and rates data

Author: Trading System v1.3.13 - REGIME EDITION
Date: January 6, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)

try:
    from yahooquery import Ticker
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False
    logger.warning("yahooquery not available - using mock data for testing")


class MarketDataFetcher:
    """
    Fetches market data for regime detection
    
    Data fetched:
    - US Indices: S&P 500 (^GSPC), NASDAQ (^IXIC)
    - Commodities: Iron Ore (not available on Yahoo), Oil (CL=F)
    - FX: AUD/USD (AUDUSD=X), USD Index (DX-Y.NYB)
    - Rates: US 10Y (^TNX), AU 10Y (not available on Yahoo)
    - Volatility: VIX (^VIX)
    
    Note: Some data (iron ore, AU 10Y) not available on Yahoo Finance
    Will use proxies or default values
    """
    
    def __init__(self):
        """Initialize market data fetcher"""
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_fetch = None
        logger.info("[OK] MarketDataFetcher initialized")
    
    def fetch_market_data(self, use_cache: bool = True) -> Dict:
        """
        Fetch overnight market data for regime detection
        
        Args:
            use_cache: Use cached data if available and recent
            
        Returns:
            Dictionary with market data:
                - sp500_change: S&P 500 % change
                - nasdaq_change: NASDAQ % change
                - iron_ore_change: Iron ore % change (estimated)
                - oil_change: Oil % change
                - aud_usd_change: AUD/USD % change
                - usd_index_change: USD Index % change
                - us_10y_change: US 10Y yield change (bps)
                - au_10y_change: AU 10Y yield change (bps, estimated)
                - vix_level: VIX level
                - timestamp: Data timestamp
        """
        
        # Check cache
        if use_cache and self._is_cache_valid():
            logger.info("[CACHE] Using cached market data")
            return self.cache
        
        logger.info("[GLOBE] Fetching overnight market data...")
        
        try:
            if YAHOOQUERY_AVAILABLE:
                market_data = self._fetch_from_yahoo()
            else:
                logger.warning("[!] yahooquery not available - using mock data")
                market_data = self._get_mock_data()
            
            # Cache the data
            self.cache = market_data
            self.last_fetch = datetime.now()
            
            logger.info("[OK] Market data fetched successfully")
            self._log_market_summary(market_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"[X] Error fetching market data: {e}", exc_info=True)
            return self._get_fallback_data()
    
    def _fetch_from_yahoo(self) -> Dict:
        """Fetch data from Yahoo Finance"""
        
        # Define symbols
        symbols = {
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'oil': 'CL=F',
            'aud_usd': 'AUDUSD=X',
            'usd_index': 'DX-Y.NYB',
            'us_10y': '^TNX',
            'vix': '^VIX'
        }
        
        # Fetch data
        ticker = Ticker(list(symbols.values()))
        
        # Get current and previous prices
        try:
            history = ticker.history(period='5d', interval='1d')
            quotes = ticker.quotes
            
            market_data = {}
            
            # Process each symbol
            for key, symbol in symbols.items():
                try:
                    # Get recent data
                    if symbol in history.index.get_level_values(0):
                        symbol_history = history.loc[symbol].tail(2)
                        
                        if len(symbol_history) >= 2:
                            current = symbol_history['close'].iloc[-1]
                            previous = symbol_history['close'].iloc[-2]
                            
                            if key == 'us_10y':
                                # Yield in basis points
                                change_bps = current - previous
                                market_data[f'{key}_change'] = change_bps
                                market_data[f'{key}_level'] = current
                            else:
                                # Percentage change
                                pct_change = ((current - previous) / previous) * 100
                                market_data[f'{key}_change'] = pct_change
                                market_data[f'{key}_level'] = current
                        else:
                            market_data[f'{key}_change'] = 0.0
                            market_data[f'{key}_level'] = 0.0
                    else:
                        market_data[f'{key}_change'] = 0.0
                        market_data[f'{key}_level'] = 0.0
                        
                except Exception as e:
                    logger.warning(f"[!] Error fetching {key} ({symbol}): {e}")
                    market_data[f'{key}_change'] = 0.0
                    market_data[f'{key}_level'] = 0.0
            
            # Iron ore not available on Yahoo - use proxy
            # Use materials ETF or set to 0
            market_data['iron_ore_change'] = 0.0  # Would need separate API
            
            # Australian 10Y not on Yahoo - estimate or set to 0
            market_data['au_10y_change'] = 0.0  # Would need separate API
            
            # Rename fields to match regime detector expectations
            final_data = {
                'sp500_change': market_data.get('sp500_change', 0.0),
                'nasdaq_change': market_data.get('nasdaq_change', 0.0),
                'iron_ore_change': market_data.get('iron_ore_change', 0.0),
                'oil_change': market_data.get('oil_change', 0.0),
                'aud_usd_change': market_data.get('aud_usd_change', 0.0),
                'usd_index_change': market_data.get('usd_index_change', 0.0),
                'us_10y_change': market_data.get('us_10y_change', 0.0),
                'au_10y_change': market_data.get('au_10y_change', 0.0),
                'vix_level': market_data.get('vix_level', 20.0),
                'timestamp': datetime.now().isoformat()
            }
            
            return final_data
            
        except Exception as e:
            logger.error(f"[X] Yahoo Finance fetch error: {e}", exc_info=True)
            raise
    
    def _get_mock_data(self) -> Dict:
        """
        Get mock market data for testing
        
        Returns realistic sample data
        """
        logger.info("[LIST] Using mock market data for testing")
        
        return {
            'sp500_change': 0.5,
            'nasdaq_change': 0.8,
            'iron_ore_change': -1.2,
            'oil_change': -0.8,
            'aud_usd_change': -0.3,
            'usd_index_change': 0.2,
            'us_10y_change': -2,
            'au_10y_change': -1,
            'vix_level': 18.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_data(self) -> Dict:
        """
        Get fallback data when fetch fails
        
        Returns neutral values
        """
        logger.warning("[!] Using fallback neutral market data")
        
        return {
            'sp500_change': 0.0,
            'nasdaq_change': 0.0,
            'iron_ore_change': 0.0,
            'oil_change': 0.0,
            'aud_usd_change': 0.0,
            'usd_index_change': 0.0,
            'us_10y_change': 0.0,
            'au_10y_change': 0.0,
            'vix_level': 20.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.cache or not self.last_fetch:
            return False
        
        age = (datetime.now() - self.last_fetch).total_seconds()
        return age < self.cache_duration
    
    def _log_market_summary(self, market_data: Dict):
        """Log market data summary"""
        logger.info("[#] Market Data Summary:")
        logger.info(f"  US Markets: S&P {market_data['sp500_change']:+.1f}%, NASDAQ {market_data['nasdaq_change']:+.1f}%")
        logger.info(f"  Commodities: Iron Ore {market_data['iron_ore_change']:+.1f}%, Oil {market_data['oil_change']:+.1f}%")
        logger.info(f"  FX: AUD/USD {market_data['aud_usd_change']:+.1f}%, USD Index {market_data['usd_index_change']:+.1f}%")
        logger.info(f"  Rates: US 10Y {market_data['us_10y_change']:+.1f}bps, AU 10Y {market_data['au_10y_change']:+.1f}bps")
        logger.info(f"  Volatility: VIX {market_data['vix_level']:.1f}")
    
    def get_market_summary_text(self, market_data: Optional[Dict] = None) -> str:
        """
        Get formatted text summary of market data
        
        Args:
            market_data: Market data dict (uses cached if not provided)
            
        Returns:
            Formatted text summary
        """
        if market_data is None:
            market_data = self.cache if self.cache else self.fetch_market_data()
        
        lines = []
        lines.append("=" * 80)
        lines.append("OVERNIGHT MARKET SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        lines.append("US MARKETS:")
        lines.append(f"  S&P 500:  {market_data['sp500_change']:+6.2f}%")
        lines.append(f"  NASDAQ:   {market_data['nasdaq_change']:+6.2f}%")
        lines.append(f"  VIX:      {market_data['vix_level']:7.2f}")
        lines.append("")
        lines.append("COMMODITIES:")
        lines.append(f"  Iron Ore: {market_data['iron_ore_change']:+6.2f}%")
        lines.append(f"  Oil:      {market_data['oil_change']:+6.2f}%")
        lines.append("")
        lines.append("CURRENCIES:")
        lines.append(f"  AUD/USD:  {market_data['aud_usd_change']:+6.2f}%")
        lines.append(f"  USD Index:{market_data['usd_index_change']:+6.2f}%")
        lines.append("")
        lines.append("INTEREST RATES:")
        lines.append(f"  US 10Y:   {market_data['us_10y_change']:+6.1f} bps")
        lines.append(f"  AU 10Y:   {market_data['au_10y_change']:+6.1f} bps")
        lines.append("")
        lines.append(f"Updated: {market_data['timestamp']}")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def test_market_data_fetcher():
    """Test the market data fetcher"""
    
    print("\n" + "="*80)
    print("TESTING MARKET DATA FETCHER")
    print("="*80)
    
    fetcher = MarketDataFetcher()
    
    # Fetch data
    market_data = fetcher.fetch_market_data()
    
    # Print summary
    print(fetcher.get_market_summary_text(market_data))
    
    # Test regime detection with this data
    print("\n" + "="*80)
    print("TESTING WITH REGIME DETECTOR")
    print("="*80)
    
    try:
        from market_regime_detector import MarketRegimeDetector
        
        detector = MarketRegimeDetector()
        regime_data = detector.detect_regime(market_data)
        
        print(detector.get_regime_report())
        
    except ImportError:
        print("[!] Regime detector not available for testing")
    
    # Test caching
    print("\n" + "="*80)
    print("TESTING CACHE")
    print("="*80)
    
    print("First fetch...")
    start = time.time()
    data1 = fetcher.fetch_market_data(use_cache=False)
    time1 = time.time() - start
    print(f"  Time: {time1:.3f}s")
    
    print("Second fetch (cached)...")
    start = time.time()
    data2 = fetcher.fetch_market_data(use_cache=True)
    time2 = time.time() - start
    print(f"  Time: {time2:.3f}s")
    print(f"  Speedup: {time1/time2:.1f}x faster")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_market_data_fetcher()

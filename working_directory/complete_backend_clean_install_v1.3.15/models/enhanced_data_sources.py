#!/usr/bin/env python3
"""
Enhanced Data Sources Module - Week 2 Features
Provides iron ore and AU 10Y yield data with multiple fallback sources

Author: Trading System v1.3.13 - REGIME EDITION (Week 2)
Date: January 6, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import time

logger = logging.getLogger(__name__)

# Try importing data providers
try:
    from yahooquery import Ticker
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class EnhancedDataSources:
    """
    Enhanced data sources with iron ore and AU 10Y yield
    
    Data Sources Hierarchy:
    1. Iron Ore:
       - Primary: Investing.com API (free tier)
       - Secondary: ASX proxy (FMG.AX, RIO.AX, BHP.AX average)
       - Fallback: Historical correlation estimates
    
    2. AU 10Y Yield:
       - Primary: Australian Treasury Bonds ETF (GOVT.AX)
       - Secondary: Correlation with US 10Y + AUD/USD
       - Fallback: RBA policy rate + risk premium
    
    3. Additional Data:
       - Copper (HG=F) - industrial demand indicator
       - Gold (GC=F) - safe haven indicator
       - ASX 200 Futures (^AXJO) - Australian market proxy
    """
    
    def __init__(self):
        """Initialize enhanced data sources"""
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_fetch = {}
        
        # Configuration
        self.iron_ore_proxy_stocks = ['FMG.AX', 'RIO.AX', 'BHP.AX']
        self.au_bond_proxy = 'GOVT.AX'
        
        logger.info("[OK] EnhancedDataSources initialized")
        logger.info(f"   - Iron ore proxy stocks: {', '.join(self.iron_ore_proxy_stocks)}")
        logger.info(f"   - AU bond proxy: {self.au_bond_proxy}")
    
    def fetch_iron_ore_data(self, use_cache: bool = True) -> Dict:
        """
        Fetch iron ore price data
        
        Returns:
            {
                'price': Current price (USD per tonne),
                'change_1d': 1-day % change,
                'change_1w': 1-week % change,
                'source': Data source used,
                'timestamp': Data timestamp,
                'confidence': Data confidence (0-1)
            }
        """
        
        # Check cache
        cache_key = 'iron_ore'
        if use_cache and self._is_cache_valid(cache_key):
            logger.info("📦 Using cached iron ore data")
            return self.cache[cache_key]
        
        logger.info("[GLOBE] Fetching iron ore data...")
        
        # Try multiple sources in order
        methods = [
            self._fetch_iron_ore_from_investing,
            self._fetch_iron_ore_from_asx_proxy,
            self._fetch_iron_ore_fallback
        ]
        
        for method in methods:
            try:
                data = method()
                if data and data.get('price') is not None:
                    # Cache and return
                    data['timestamp'] = datetime.now().isoformat()
                    self.cache[cache_key] = data
                    self.last_fetch[cache_key] = datetime.now()
                    
                    logger.info(f"[OK] Iron ore data fetched from {data['source']}")
                    logger.info(f"   Price: ${data['price']:.2f}/tonne, Change: {data['change_1d']:+.2f}%")
                    return data
            except Exception as e:
                logger.warning(f"[!] Failed to fetch from {method.__name__}: {e}")
                continue
        
        # All methods failed
        logger.error("[X] All iron ore data sources failed")
        return self._get_iron_ore_default()
    
    def _fetch_iron_ore_from_investing(self) -> Dict:
        """
        Fetch iron ore from Investing.com (free tier)
        Note: This is a placeholder - actual implementation would need API key
        """
        # Placeholder for Investing.com API
        # In production, you would use: https://www.investing.com/commodities/iron-ore-62-cfr-futures
        
        # For now, return None to skip to next method
        return None
    
    def _fetch_iron_ore_from_asx_proxy(self) -> Dict:
        """
        Estimate iron ore from ASX mining stocks (FMG, RIO, BHP)
        Uses correlation: mining stocks move ~0.7-0.8 with iron ore
        """
        
        if not YAHOOQUERY_AVAILABLE:
            return None
        
        logger.info("   Trying ASX mining proxy method...")
        
        # Fetch data for major miners
        ticker = Ticker(self.iron_ore_proxy_stocks)
        history = ticker.history(period='5d', interval='1d')
        
        if history.empty:
            return None
        
        # Calculate average change across miners
        changes = []
        for symbol in self.iron_ore_proxy_stocks:
            try:
                symbol_data = history.loc[symbol]
                if len(symbol_data) >= 2:
                    latest_close = symbol_data['close'].iloc[-1]
                    prev_close = symbol_data['close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100
                    changes.append(change_pct)
            except:
                continue
        
        if not changes:
            return None
        
        avg_change = sum(changes) / len(changes)
        
        # Estimate iron ore change (miners are ~0.75 correlation)
        # If miners are up 3%, iron ore likely up ~4%
        iron_ore_change = avg_change / 0.75
        
        # Estimate price (recent average ~$110-120 USD/tonne)
        base_price = 115.0
        estimated_price = base_price * (1 + iron_ore_change / 100)
        
        return {
            'price': estimated_price,
            'change_1d': iron_ore_change,
            'change_1w': iron_ore_change * 1.5,  # Rough estimate
            'source': 'ASX Mining Proxy',
            'confidence': 0.6,
            'proxy_stocks': self.iron_ore_proxy_stocks,
            'proxy_changes': changes
        }
    
    def _fetch_iron_ore_fallback(self) -> Dict:
        """
        Fallback: Use historical correlation with oil and copper
        """
        
        if not YAHOOQUERY_AVAILABLE:
            return None
        
        logger.info("   Trying commodity correlation fallback...")
        
        try:
            # Fetch oil and copper
            ticker = Ticker(['CL=F', 'HG=F'])  # Oil and Copper
            history = ticker.history(period='5d', interval='1d')
            
            if history.empty:
                return None
            
            # Calculate changes
            changes = []
            for symbol in ['CL=F', 'HG=F']:
                try:
                    symbol_data = history.loc[symbol]
                    if len(symbol_data) >= 2:
                        latest_close = symbol_data['close'].iloc[-1]
                        prev_close = symbol_data['close'].iloc[-2]
                        change_pct = ((latest_close - prev_close) / prev_close) * 100
                        changes.append(change_pct)
                except:
                    continue
            
            if not changes:
                return None
            
            # Iron ore correlates ~0.5 with oil and ~0.8 with copper
            # Weighted average
            if len(changes) >= 2:
                weighted_change = (changes[0] * 0.3 + changes[1] * 0.7)  # Oil 30%, Copper 70%
            else:
                weighted_change = changes[0] * 0.5
            
            base_price = 115.0
            estimated_price = base_price * (1 + weighted_change / 100)
            
            return {
                'price': estimated_price,
                'change_1d': weighted_change,
                'change_1w': weighted_change * 1.5,
                'source': 'Commodity Correlation',
                'confidence': 0.4
            }
            
        except Exception as e:
            logger.warning(f"   Commodity correlation failed: {e}")
            return None
    
    def _get_iron_ore_default(self) -> Dict:
        """Default iron ore data (last resort)"""
        return {
            'price': 115.0,
            'change_1d': 0.0,
            'change_1w': 0.0,
            'source': 'Default',
            'confidence': 0.0,
            'note': 'No data available - using neutral default'
        }
    
    def fetch_au_10y_yield(self, use_cache: bool = True) -> Dict:
        """
        Fetch Australian 10Y government bond yield
        
        Returns:
            {
                'yield': Current yield (%),
                'change_1d': 1-day change (bps),
                'change_1w': 1-week change (bps),
                'source': Data source used,
                'timestamp': Data timestamp,
                'confidence': Data confidence (0-1)
            }
        """
        
        # Check cache
        cache_key = 'au_10y'
        if use_cache and self._is_cache_valid(cache_key):
            logger.info("📦 Using cached AU 10Y data")
            return self.cache[cache_key]
        
        logger.info("[GLOBE] Fetching AU 10Y yield data...")
        
        # Try multiple sources
        methods = [
            self._fetch_au_10y_from_govt_etf,
            self._fetch_au_10y_from_us_correlation,
            self._fetch_au_10y_fallback
        ]
        
        for method in methods:
            try:
                data = method()
                if data and data.get('yield') is not None:
                    # Cache and return
                    data['timestamp'] = datetime.now().isoformat()
                    self.cache[cache_key] = data
                    self.last_fetch[cache_key] = datetime.now()
                    
                    logger.info(f"[OK] AU 10Y data fetched from {data['source']}")
                    logger.info(f"   Yield: {data['yield']:.2f}%, Change: {data['change_1d']:+.1f} bps")
                    return data
            except Exception as e:
                logger.warning(f"[!] Failed to fetch from {method.__name__}: {e}")
                continue
        
        # All methods failed
        logger.error("[X] All AU 10Y data sources failed")
        return self._get_au_10y_default()
    
    def _fetch_au_10y_from_govt_etf(self) -> Dict:
        """
        Estimate AU 10Y from Australian Government Bonds ETF (GOVT.AX)
        ETF price inversely correlates with yields
        """
        
        if not YAHOOQUERY_AVAILABLE:
            return None
        
        logger.info("   Trying GOVT.AX ETF method...")
        
        try:
            ticker = Ticker(self.au_bond_proxy)
            history = ticker.history(period='5d', interval='1d')
            
            if history.empty or len(history) < 2:
                return None
            
            # Calculate ETF price change
            latest_close = history['close'].iloc[-1]
            prev_close = history['close'].iloc[-2]
            etf_change_pct = ((latest_close - prev_close) / prev_close) * 100
            
            # Bond prices and yields are inversely related
            # 1% ETF price drop ≈ 10 bps yield increase (rough approximation)
            yield_change_bps = -etf_change_pct * 10
            
            # Current AU 10Y typically 3.5-4.5%
            base_yield = 4.0
            current_yield = base_yield + (yield_change_bps / 100)
            
            return {
                'yield': current_yield,
                'change_1d': yield_change_bps,
                'change_1w': yield_change_bps * 1.5,
                'source': 'GOVT.AX ETF',
                'confidence': 0.7,
                'etf_change': etf_change_pct
            }
            
        except Exception as e:
            logger.warning(f"   GOVT.AX method failed: {e}")
            return None
    
    def _fetch_au_10y_from_us_correlation(self) -> Dict:
        """
        Estimate AU 10Y from US 10Y + AUD/USD
        AU yields typically track US yields + risk premium
        """
        
        if not YAHOOQUERY_AVAILABLE:
            return None
        
        logger.info("   Trying US correlation method...")
        
        try:
            ticker = Ticker(['^TNX', 'AUDUSD=X'])  # US 10Y and AUD/USD
            history = ticker.history(period='5d', interval='1d')
            
            if history.empty:
                return None
            
            # Get US 10Y change
            us_10y_data = history.loc['^TNX']
            if len(us_10y_data) < 2:
                return None
            
            us_latest = us_10y_data['close'].iloc[-1]
            us_prev = us_10y_data['close'].iloc[-2]
            us_change_bps = (us_latest - us_prev) * 100  # TNX is in %, multiply by 100 for bps
            
            # Get AUD/USD change (stronger AUD → lower AU yields)
            try:
                aud_data = history.loc['AUDUSD=X']
                if len(aud_data) >= 2:
                    aud_latest = aud_data['close'].iloc[-1]
                    aud_prev = aud_data['close'].iloc[-2]
                    aud_change_pct = ((aud_latest - aud_prev) / aud_prev) * 100
                    # 1% AUD strength → ~5 bps AU yield decline
                    aud_effect_bps = -aud_change_pct * 5
                else:
                    aud_effect_bps = 0
            except:
                aud_effect_bps = 0
            
            # AU 10Y ≈ US 10Y + 40 bps risk premium (historical average)
            risk_premium_bps = 40
            au_yield_change_bps = us_change_bps + aud_effect_bps
            
            base_au_yield = us_latest + (risk_premium_bps / 100)
            current_au_yield = base_au_yield + (au_yield_change_bps / 100)
            
            return {
                'yield': current_au_yield,
                'change_1d': au_yield_change_bps,
                'change_1w': au_yield_change_bps * 1.5,
                'source': 'US Correlation',
                'confidence': 0.6,
                'us_10y': us_latest,
                'us_change_bps': us_change_bps,
                'aud_effect_bps': aud_effect_bps
            }
            
        except Exception as e:
            logger.warning(f"   US correlation method failed: {e}")
            return None
    
    def _fetch_au_10y_fallback(self) -> Dict:
        """
        Fallback: Use RBA cash rate + historical spread
        AU 10Y typically = RBA rate + 100-150 bps
        """
        
        logger.info("   Using RBA rate fallback...")
        
        # RBA cash rate (as of Jan 2026, assume 4.35%)
        rba_cash_rate = 4.35
        historical_spread = 1.20  # 120 bps typical spread
        
        estimated_yield = rba_cash_rate + historical_spread
        
        return {
            'yield': estimated_yield,
            'change_1d': 0.0,
            'change_1w': 0.0,
            'source': 'RBA Rate Estimate',
            'confidence': 0.3,
            'rba_rate': rba_cash_rate,
            'spread': historical_spread
        }
    
    def _get_au_10y_default(self) -> Dict:
        """Default AU 10Y data (last resort)"""
        return {
            'yield': 4.0,
            'change_1d': 0.0,
            'change_1w': 0.0,
            'source': 'Default',
            'confidence': 0.0,
            'note': 'No data available - using neutral default'
        }
    
    def fetch_additional_indicators(self) -> Dict:
        """
        Fetch additional market indicators for enhanced regime detection
        
        Returns:
            {
                'copper': Copper price data,
                'gold': Gold price data,
                'asx200': ASX 200 index data,
                'timestamp': Data timestamp
            }
        """
        
        logger.info("[GLOBE] Fetching additional indicators...")
        
        if not YAHOOQUERY_AVAILABLE:
            return {}
        
        try:
            symbols = ['HG=F', 'GC=F', '^AXJO']  # Copper, Gold, ASX 200
            ticker = Ticker(symbols)
            history = ticker.history(period='5d', interval='1d')
            
            if history.empty:
                return {}
            
            result = {}
            
            # Copper
            try:
                copper_data = history.loc['HG=F']
                if len(copper_data) >= 2:
                    copper_change = ((copper_data['close'].iloc[-1] - copper_data['close'].iloc[-2]) / 
                                    copper_data['close'].iloc[-2]) * 100
                    result['copper'] = {
                        'price': copper_data['close'].iloc[-1],
                        'change': copper_change
                    }
            except:
                pass
            
            # Gold
            try:
                gold_data = history.loc['GC=F']
                if len(gold_data) >= 2:
                    gold_change = ((gold_data['close'].iloc[-1] - gold_data['close'].iloc[-2]) / 
                                  gold_data['close'].iloc[-2]) * 100
                    result['gold'] = {
                        'price': gold_data['close'].iloc[-1],
                        'change': gold_change
                    }
            except:
                pass
            
            # ASX 200
            try:
                asx_data = history.loc['^AXJO']
                if len(asx_data) >= 2:
                    asx_change = ((asx_data['close'].iloc[-1] - asx_data['close'].iloc[-2]) / 
                                 asx_data['close'].iloc[-2]) * 100
                    result['asx200'] = {
                        'price': asx_data['close'].iloc[-1],
                        'change': asx_change
                    }
            except:
                pass
            
            result['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"[OK] Additional indicators fetched: {', '.join(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"[X] Error fetching additional indicators: {e}")
            return {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache or key not in self.last_fetch:
            return False
        
        age = (datetime.now() - self.last_fetch[key]).total_seconds()
        return age < self.cache_duration
    
    def get_all_enhanced_data(self) -> Dict:
        """
        Fetch all enhanced data sources in one call
        
        Returns:
            {
                'iron_ore': Iron ore data,
                'au_10y': AU 10Y yield data,
                'additional': Additional indicators,
                'timestamp': Overall timestamp
            }
        """
        
        logger.info("=" * 80)
        logger.info("FETCHING ENHANCED DATA SOURCES")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        result = {
            'iron_ore': self.fetch_iron_ore_data(),
            'au_10y': self.fetch_au_10y_yield(),
            'additional': self.fetch_additional_indicators(),
            'timestamp': datetime.now().isoformat()
        }
        
        elapsed = time.time() - start_time
        logger.info("=" * 80)
        logger.info(f"[OK] All enhanced data fetched in {elapsed:.3f} seconds")
        logger.info("=" * 80)
        
        return result
    
    def get_summary_text(self, data: Dict) -> str:
        """Format enhanced data as readable text"""
        
        lines = []
        lines.append("\nENHANCED DATA SOURCES SUMMARY")
        lines.append("=" * 80)
        
        # Iron Ore
        iron_ore = data.get('iron_ore', {})
        lines.append(f"\n🏗️ Iron Ore:")
        lines.append(f"   Price: ${iron_ore.get('price', 0):.2f}/tonne")
        lines.append(f"   Change: {iron_ore.get('change_1d', 0):+.2f}%")
        lines.append(f"   Source: {iron_ore.get('source', 'Unknown')}")
        lines.append(f"   Confidence: {iron_ore.get('confidence', 0):.0%}")
        
        # AU 10Y
        au_10y = data.get('au_10y', {})
        lines.append(f"\n[#] Australian 10Y Yield:")
        lines.append(f"   Yield: {au_10y.get('yield', 0):.2f}%")
        lines.append(f"   Change: {au_10y.get('change_1d', 0):+.1f} bps")
        lines.append(f"   Source: {au_10y.get('source', 'Unknown')}")
        lines.append(f"   Confidence: {au_10y.get('confidence', 0):.0%}")
        
        # Additional
        additional = data.get('additional', {})
        if additional:
            lines.append(f"\n[UP] Additional Indicators:")
            
            if 'copper' in additional:
                copper = additional['copper']
                lines.append(f"   Copper: ${copper['price']:.2f}, {copper['change']:+.2f}%")
            
            if 'gold' in additional:
                gold = additional['gold']
                lines.append(f"   Gold: ${gold['price']:.2f}, {gold['change']:+.2f}%")
            
            if 'asx200' in additional:
                asx = additional['asx200']
                lines.append(f"   ASX 200: {asx['price']:.2f}, {asx['change']:+.2f}%")
        
        lines.append("\n" + "=" * 80)
        lines.append(f"Updated: {data.get('timestamp', 'N/A')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# Test function
def test_enhanced_data_sources():
    """Test enhanced data sources"""
    
    print("\n" + "="*80)
    print("TESTING ENHANCED DATA SOURCES")
    print("="*80)
    
    fetcher = EnhancedDataSources()
    
    # Fetch all data
    data = fetcher.get_all_enhanced_data()
    
    # Print summary
    print(fetcher.get_summary_text(data))
    
    return data


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_enhanced_data_sources()

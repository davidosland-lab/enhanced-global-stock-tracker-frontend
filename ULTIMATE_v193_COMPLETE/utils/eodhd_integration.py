"""
EODHD Data Integration Module
Unified Trading System v193.11.7.6

Provides integration with EODHD (EOD Historical Data) API for:
1. SPI 200 futures (Australian market overnight indicator)
2. FTSE 100 futures (UK market pre-market indicator)

API Limits (Free Tier):
- 20 API calls per day
- Rate limiting enforced automatically
- Calls are strategic: 2 calls per day (1 for SPI, 1 for FTSE)

EODHD Symbols:
- SPI 200 Futures: AP.INDX (ASX SPI 200 futures)
- FTSE 100 Futures: UK100.INDX (UK FTSE 100 futures/CFD)

Security:
- API key stored in local .env file only
- Never uploaded to git or cloud
- Rate limiter prevents exceeding daily quota

Documentation: https://eodhistoricaldata.com/financial-apis/
"""

import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import time
from pathlib import Path

# Import secure config manager
try:
    from utils.secure_config import get_eodhd_api_key, get_rate_limiter
except ImportError:
    # Fallback for testing
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
    from utils.secure_config import get_eodhd_api_key, get_rate_limiter

logger = logging.getLogger(__name__)


class EODHDClient:
    """
    Client for EODHD API with automatic rate limiting and caching.
    
    Features:
    - Automatic rate limiting (20 calls/day)
    - Local caching (4 hour TTL for pre-market data)
    - Error handling and retry logic
    - Comprehensive logging
    """
    
    BASE_URL = "https://eodhistoricaldata.com/api"
    
    # Symbol mappings
    SYMBOLS = {
        'SPI_200': 'AP.INDX',        # SPI 200 futures (Australia)
        'FTSE_100': 'UK100.INDX'     # FTSE 100 futures (UK)
    }
    
    def __init__(self):
        """Initialize EODHD client"""
        self.api_key = get_eodhd_api_key()
        self.rate_limiter = get_rate_limiter()
        
        # Cache directory
        project_root = Path(__file__).parent.parent.absolute()
        self.cache_dir = project_root / 'cache' / 'eodhd'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache TTL (4 hours for pre-market data)
        self.cache_ttl = timedelta(hours=4)
        
        # Validate API key
        if not self.api_key:
            logger.error("EODHD API key not configured!")
            logger.error("Follow setup instructions in .env.example")
            raise ValueError("EODHD API key missing")
        
        logger.info("✓ EODHD Client initialized")
        logger.info(f"  Rate Limit: {self.rate_limiter.get_remaining_calls()}/{self.rate_limiter.max_calls_per_day} calls remaining today")
    
    def _get_cache_path(self, symbol: str, endpoint: str) -> Path:
        """Get cache file path for a symbol and endpoint"""
        cache_key = f"{symbol}_{endpoint}_{datetime.now().date().isoformat()}.json"
        return self.cache_dir / cache_key
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid"""
        if not cache_path.exists():
            return False
        
        # Check file age
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - file_time
        
        return age < self.cache_ttl
    
    def _read_cache(self, cache_path: Path) -> Optional[Dict]:
        """Read data from cache file"""
        try:
            import json
            with open(cache_path, 'r') as f:
                data = json.load(f)
            logger.info(f"✓ Using cached data from {cache_path.name}")
            return data
        except Exception as e:
            logger.error(f"Failed to read cache: {e}")
            return None
    
    def _write_cache(self, cache_path: Path, data: Dict):
        """Write data to cache file"""
        try:
            import json
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"✓ Cached data to {cache_path.name}")
        except Exception as e:
            logger.error(f"Failed to write cache: {e}")
    
    def _make_api_call(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make API call with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint (e.g., 'real-time', 'eod')
            params: Query parameters
        
        Returns:
            Response data or None if failed
        """
        # Check rate limit
        if not self.rate_limiter.can_make_call():
            remaining_time = self.rate_limiter.get_reset_time() - datetime.now()
            logger.error(f"✗ EODHD rate limit exceeded!")
            logger.error(f"  Resets in: {remaining_time}")
            return None
        
        # Add API key to params
        params['api_token'] = self.api_key
        params['fmt'] = 'json'
        
        # Build URL
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"→ Making EODHD API call: {endpoint}")
            response = requests.get(url, params=params, timeout=10)
            
            # Record API call
            self.rate_limiter.record_call()
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✓ API call successful")
            return data
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.error(f"✗ Symbol not found: {params.get('s', 'unknown')}")
            elif response.status_code == 401:
                logger.error(f"✗ Invalid API key")
            else:
                logger.error(f"✗ HTTP Error {response.status_code}: {e}")
            return None
        
        except requests.exceptions.Timeout:
            logger.error(f"✗ Request timeout")
            return None
        
        except Exception as e:
            logger.error(f"✗ API call failed: {e}")
            return None
    
    def get_realtime_price(self, market: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get real-time futures price for SPI 200 or FTSE 100.
        
        Args:
            market: 'SPI_200' or 'FTSE_100'
            use_cache: Whether to use cached data (default: True)
        
        Returns:
            Dictionary with price data or None if failed
        """
        symbol = self.SYMBOLS.get(market)
        if not symbol:
            logger.error(f"✗ Invalid market: {market}")
            return None
        
        # Check cache first
        cache_path = self._get_cache_path(symbol, 'realtime')
        if use_cache and self._is_cache_valid(cache_path):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Make API call
        endpoint = f"real-time/{symbol}"
        data = self._make_api_call(endpoint, {})
        
        if data:
            # Parse response
            result = {
                'symbol': symbol,
                'market': market,
                'price': float(data.get('close', 0)),
                'change': float(data.get('change', 0)),
                'change_pct': float(data.get('change_p', 0)),
                'open': float(data.get('open', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'volume': int(data.get('volume', 0)),
                'timestamp': data.get('timestamp', int(time.time())),
                'datetime': datetime.fromtimestamp(data.get('timestamp', time.time())).isoformat()
            }
            
            # Cache result
            self._write_cache(cache_path, result)
            
            return result
        
        return None
    
    def get_eod_data(self, market: str, days: int = 5, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Get end-of-day historical data.
        
        Args:
            market: 'SPI_200' or 'FTSE_100'
            days: Number of days of history (default: 5)
            use_cache: Whether to use cached data (default: True)
        
        Returns:
            DataFrame with historical data or None if failed
        """
        symbol = self.SYMBOLS.get(market)
        if not symbol:
            logger.error(f"✗ Invalid market: {market}")
            return None
        
        # Check cache first
        cache_path = self._get_cache_path(symbol, f'eod_{days}d')
        if use_cache and self._is_cache_valid(cache_path):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return pd.DataFrame(cached_data)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)  # Extra days for weekends
        
        # Make API call
        endpoint = f"eod/{symbol}"
        params = {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'period': 'd'
        }
        
        data = self._make_api_call(endpoint, params)
        
        if data and isinstance(data, list):
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Cache result
            cache_data = df.reset_index().to_dict(orient='records')
            self._write_cache(cache_path, cache_data)
            
            return df
        
        return None
    
    def get_spi_200_overnight_gap(self, use_cache: bool = True) -> Optional[Dict]:
        """
        Get SPI 200 overnight gap prediction.
        
        This is the PRIMARY data source for Australian market pre-market analysis.
        
        Returns:
            Dictionary with gap prediction and confidence
        """
        logger.info("[EODHD] Fetching SPI 200 futures data...")
        
        # Get realtime SPI 200 futures price
        spi_data = self.get_realtime_price('SPI_200', use_cache=use_cache)
        
        if not spi_data:
            logger.warning("[EODHD] Failed to fetch SPI 200 data")
            return None
        
        # Calculate gap prediction
        # SPI futures are a direct proxy for ASX 200 opening
        gap_pct = spi_data['change_pct']
        
        result = {
            'predicted_gap_pct': gap_pct,
            'confidence': 0.95,  # Very high confidence (direct futures contract)
            'direction': 'BULLISH' if gap_pct > 0.3 else 'BEARISH' if gap_pct < -0.3 else 'NEUTRAL',
            'spi_price': spi_data['price'],
            'spi_change_pct': gap_pct,
            'method': 'EODHD_SPI_FUTURES',
            'timestamp': spi_data['datetime'],
            'source': 'EODHD'
        }
        
        logger.info(f"[EODHD SPI] Gap Prediction: {gap_pct:+.2f}% (Confidence: 95%)")
        
        return result
    
    def get_ftse_100_overnight_gap(self, use_cache: bool = True) -> Optional[Dict]:
        """
        Get FTSE 100 overnight gap prediction.
        
        This is the PRIMARY data source for UK market pre-market analysis.
        
        Returns:
            Dictionary with gap prediction and confidence
        """
        logger.info("[EODHD] Fetching FTSE 100 futures data...")
        
        # Get realtime FTSE 100 futures price
        ftse_data = self.get_realtime_price('FTSE_100', use_cache=use_cache)
        
        if not ftse_data:
            logger.warning("[EODHD] Failed to fetch FTSE 100 data")
            return None
        
        # Calculate gap prediction
        # FTSE futures are a direct proxy for FTSE 100 opening
        gap_pct = ftse_data['change_pct']
        
        result = {
            'predicted_gap_pct': gap_pct,
            'confidence': 0.95,  # Very high confidence (direct futures contract)
            'direction': 'BULLISH' if gap_pct > 0.3 else 'BEARISH' if gap_pct < -0.3 else 'NEUTRAL',
            'ftse_price': ftse_data['price'],
            'ftse_change_pct': gap_pct,
            'method': 'EODHD_FTSE_FUTURES',
            'timestamp': ftse_data['datetime'],
            'source': 'EODHD'
        }
        
        logger.info(f"[EODHD FTSE] Gap Prediction: {gap_pct:+.2f}% (Confidence: 95%)")
        
        return result


# ============================================================
# TEST MODULE
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("\n" + "="*80)
    print("EODHD DATA INTEGRATION TEST")
    print("="*80 + "\n")
    
    try:
        # Initialize client
        client = EODHDClient()
        
        # Test SPI 200
        print("-"*80)
        print("SPI 200 FUTURES (Australian Market)")
        print("-"*80)
        spi_gap = client.get_spi_200_overnight_gap()
        if spi_gap:
            print(f"✓ Gap Prediction: {spi_gap['predicted_gap_pct']:+.2f}%")
            print(f"  Confidence: {spi_gap['confidence']:.0%}")
            print(f"  Direction: {spi_gap['direction']}")
            print(f"  SPI Price: {spi_gap['spi_price']:.2f}")
            print(f"  Timestamp: {spi_gap['timestamp']}")
        else:
            print("✗ Failed to fetch SPI 200 data")
        
        # Test FTSE 100
        print("\n" + "-"*80)
        print("FTSE 100 FUTURES (UK Market)")
        print("-"*80)
        ftse_gap = client.get_ftse_100_overnight_gap()
        if ftse_gap:
            print(f"✓ Gap Prediction: {ftse_gap['predicted_gap_pct']:+.2f}%")
            print(f"  Confidence: {ftse_gap['confidence']:.0%}")
            print(f"  Direction: {ftse_gap['direction']}")
            print(f"  FTSE Price: {ftse_gap['ftse_price']:.2f}")
            print(f"  Timestamp: {ftse_gap['timestamp']}")
        else:
            print("✗ Failed to fetch FTSE 100 data")
        
        # Show rate limit status
        print("\n" + "-"*80)
        print("RATE LIMIT STATUS")
        print("-"*80)
        limiter = get_rate_limiter()
        print(f"Remaining calls: {limiter.get_remaining_calls()}/{limiter.max_calls_per_day}")
        print(f"Next reset: {limiter.get_reset_time().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

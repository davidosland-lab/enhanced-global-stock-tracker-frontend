"""
Alpha Vantage Data Fetcher - PRIMARY DATA SOURCE
-------------------------------------------------
Uses Alpha Vantage API as primary data source with aggressive caching.
Yahoo Finance completely disabled due to IP blocking.

Features:
- Alpha Vantage TIME_SERIES_DAILY for OHLCV data
- GLOBAL_QUOTE for validation
- Aggressive caching (4 hour TTL to stay under 500 req/day limit)
- Rate limiting (12 seconds between calls = 5 calls/minute)
- Batch processing with delays

API Limits:
- 500 requests per day
- 5 requests per minute recommended

Usage:
    fetcher = AlphaVantageDataFetcher()
    data = fetcher.fetch_batch(['CBA.AX', 'WBC.AX', 'ANZ.AX'])
"""

import os
import time
import pickle
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"


class AlphaVantageDataFetcher:
    """
    Alpha Vantage-only data fetcher with aggressive caching
    to stay within 500 requests/day limit
    """
    
    def __init__(self, cache_dir: str = None, cache_ttl_minutes: int = 240):
        """
        Initialize Alpha Vantage Data Fetcher
        
        Args:
            cache_dir: Directory for cache files (default: cache/)
            cache_ttl_minutes: Cache time-to-live in minutes (240 = 4 hours)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.rate_limit_delay = 12.0  # 12 seconds = 5 calls/minute
        
        # Track API usage
        self.api_calls_today = 0
        self.api_calls_date = datetime.now().date()
        
        cache_hours = cache_ttl_minutes / 60
        logger.info(f"Alpha Vantage Data Fetcher initialized")
        logger.info(f"  Cache dir: {self.cache_dir}")
        logger.info(f"  Cache TTL: {cache_ttl_minutes} minutes ({cache_hours:.1f} hours)")
        logger.info(f"  Rate limit: {self.rate_limit_delay}s between calls (5/min)")
        logger.info(f"  Daily limit: 500 requests")
    
    def _cache_path(self, ticker: str, data_type: str = "daily") -> Path:
        """Generate cache file path for a ticker"""
        safe_ticker = ticker.replace('.', '_').replace(':', '-')
        return self.cache_dir / f"av_{safe_ticker}_{data_type}.pkl"
    
    def _load_from_cache(self, ticker: str, data_type: str = "daily") -> Optional[pd.DataFrame]:
        """Load data from cache if available and not expired"""
        cache_path = self._cache_path(ticker, data_type)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - mtime > self.cache_ttl:
                logger.debug(f"Cache expired for {ticker}")
                return None
            
            # Load cached data
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit for {ticker} ({data_type})")
            return data
            
        except Exception as e:
            logger.debug(f"Cache read error for {ticker}: {e}")
            return None
    
    def _save_to_cache(self, ticker: str, data: pd.DataFrame, data_type: str = "daily"):
        """Save data to cache"""
        try:
            cache_path = self._cache_path(ticker, data_type)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Cached {ticker} ({data_type})")
        except Exception as e:
            logger.warning(f"Cache write error for {ticker}: {e}")
    
    def _track_api_call(self):
        """Track API usage and reset daily counter"""
        today = datetime.now().date()
        if today != self.api_calls_date:
            self.api_calls_today = 0
            self.api_calls_date = today
        
        self.api_calls_today += 1
        
        if self.api_calls_today > 450:  # Warning at 90% of limit
            logger.warning(f"⚠️  High API usage: {self.api_calls_today}/500 calls today")
    
    def _convert_ticker_for_av(self, ticker: str) -> str:
        """
        Convert ticker format for Alpha Vantage
        ASX stocks: CBA.AX -> CBA (Alpha Vantage uses exchange suffix differently)
        """
        # For ASX stocks, just remove the .AX
        # Alpha Vantage doesn't always support .AX suffix
        if ticker.endswith('.AX'):
            return ticker.replace('.AX', '')
        return ticker
    
    def fetch_daily_data(self, ticker: str, outputsize: str = "compact") -> Optional[pd.DataFrame]:
        """
        Fetch daily OHLCV data from Alpha Vantage
        
        Args:
            ticker: Stock ticker symbol
            outputsize: 'compact' (100 days) or 'full' (20+ years)
            
        Returns:
            DataFrame with OHLCV data or None
        """
        # Check cache first
        cached_data = self._load_from_cache(ticker, "daily")
        if cached_data is not None:
            return cached_data
        
        # Check API limit
        if self.api_calls_today >= 500:
            logger.error(f"⛔ Daily API limit reached (500/500)")
            return None
        
        try:
            # Convert ticker
            av_symbol = self._convert_ticker_for_av(ticker)
            
            # Alpha Vantage TIME_SERIES_DAILY
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': av_symbol,
                'outputsize': outputsize,  # compact = 100 days, full = 20+ years
                'apikey': self.api_key
            }
            
            logger.info(f"Fetching {ticker} from Alpha Vantage...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Track API call
            self._track_api_call()
            
            # Check for errors
            if 'Error Message' in data:
                logger.warning(f"Alpha Vantage error for {ticker}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            if 'Time Series (Daily)' not in data:
                logger.warning(f"No data for {ticker} in Alpha Vantage response")
                return None
            
            # Convert to DataFrame
            time_series = data['Time Series (Daily)']
            
            # Parse into OHLCV format
            rows = []
            for date_str, values in time_series.items():
                rows.append({
                    'Date': pd.to_datetime(date_str),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(rows)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Cache the data
            self._save_to_cache(ticker, df, "daily")
            
            logger.info(f"✓ Fetched {ticker}: {len(df)} days of data")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {ticker} from Alpha Vantage: {str(e)[:100]}")
            return None
    
    def validate_by_quote(self, tickers: List[str]) -> List[str]:
        """
        Validate tickers using Alpha Vantage GLOBAL_QUOTE
        Much faster than fetching full daily data
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            List of valid ticker symbols
        """
        valid = []
        
        logger.info(f"Validating {len(tickers)} tickers via Alpha Vantage GLOBAL_QUOTE...")
        
        for i, ticker in enumerate(tickers):
            # Check API limit
            if self.api_calls_today >= 500:
                logger.error(f"⛔ Daily API limit reached during validation ({self.api_calls_today}/500)")
                break
            
            # Rate limiting
            if i > 0:
                time.sleep(self.rate_limit_delay)
            
            try:
                av_symbol = self._convert_ticker_for_av(ticker)
                
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': av_symbol,
                    'apikey': self.api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Track API call
                self._track_api_call()
                
                # Check if ticker is valid
                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']
                    if '05. price' in quote and float(quote['05. price']) > 0:
                        valid.append(ticker)
                        logger.debug(f"  ✓ {ticker}: Valid")
                    else:
                        logger.debug(f"  ✗ {ticker}: No price data")
                else:
                    logger.debug(f"  ✗ {ticker}: Not found")
                
            except Exception as e:
                logger.debug(f"  ✗ {ticker}: Error - {str(e)[:50]}")
                continue
        
        logger.info(f"Validation complete: {len(valid)}/{len(tickers)} passed")
        logger.info(f"API usage: {self.api_calls_today}/500 calls today")
        
        return valid
    
    def fetch_batch(self, tickers: List[str], period: Optional[str] = "compact",
                    interval: str = "1d", start: Optional[str] = None,
                    end: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch daily data for multiple tickers with rate limiting
        
        Args:
            tickers: List of ticker symbols
            period: 'compact' (100 days) or 'full' (20+ years)
            interval: Ignored (Alpha Vantage only supports daily)
            start: Ignored (use period instead)
            end: Ignored (use period instead)
            
        Returns:
            Dictionary mapping ticker -> DataFrame
        """
        results = {}
        
        if not tickers:
            return results
        
        logger.info(f"Batch fetching {len(tickers)} tickers from Alpha Vantage...")
        logger.info(f"⚠️  This will take ~{len(tickers) * self.rate_limit_delay / 60:.1f} minutes (rate limiting)")
        
        for i, ticker in enumerate(tickers):
            # Check API limit
            if self.api_calls_today >= 500:
                logger.error(f"⛔ Daily API limit reached ({self.api_calls_today}/500)")
                logger.error(f"   Fetched {len(results)}/{len(tickers)} tickers before limit")
                break
            
            # Rate limiting (except first ticker)
            if i > 0:
                time.sleep(self.rate_limit_delay)
            
            # Fetch data
            df = self.fetch_daily_data(ticker, outputsize=period)
            
            if df is not None and not df.empty:
                results[ticker] = df
                logger.info(f"  [{i+1}/{len(tickers)}] ✓ {ticker}: {len(df)} days")
            else:
                logger.warning(f"  [{i+1}/{len(tickers)}] ✗ {ticker}: No data")
        
        logger.info(f"Batch fetch complete: {len(results)}/{len(tickers)} tickers")
        logger.info(f"API usage: {self.api_calls_today}/500 calls today")
        
        return results
    
    def validate_stock_batch(self, tickers: List[str], criteria: Dict) -> List[str]:
        """
        Validate tickers with optional price/volume criteria
        
        Args:
            tickers: List of ticker symbols
            criteria: Dictionary with min_price, max_price, min_avg_volume
            
        Returns:
            List of valid tickers
        """
        logger.info(f"Validating {len(tickers)} tickers (Alpha Vantage)...")
        
        # First pass: validate tickers exist
        valid = self.validate_by_quote(tickers)
        
        if not valid:
            logger.info("Validation complete: 0 passed")
            return []
        
        # Optional price/volume filtering
        min_price = criteria.get('min_price', None)
        max_price = criteria.get('max_price', None)
        min_avg_volume = criteria.get('min_avg_volume', None)
        
        if any(v is not None for v in (min_price, max_price, min_avg_volume)):
            logger.info(f"Applying price/volume filters to {len(valid)} validated tickers...")
            
            # Need to fetch data for filtering
            # This is expensive (uses API calls), so use cached data
            filtered = []
            
            for ticker in valid:
                # Try cache first
                df = self._load_from_cache(ticker, "daily")
                
                if df is None or df.empty:
                    # Skip if no cached data (don't fetch to save API calls)
                    logger.debug(f"  ? {ticker}: No cached data for filtering")
                    filtered.append(ticker)  # Include anyway (benefit of doubt)
                    continue
                
                # Apply filters
                try:
                    last_close = float(df['Close'].iloc[-1])
                    avg_vol = float(df['Volume'].tail(20).mean())
                    
                    if min_price is not None and last_close < min_price:
                        logger.debug(f"  ✗ {ticker}: Price ${last_close:.2f} < ${min_price}")
                        continue
                    if max_price is not None and last_close > max_price:
                        logger.debug(f"  ✗ {ticker}: Price ${last_close:.2f} > ${max_price}")
                        continue
                    if min_avg_volume is not None and avg_vol < min_avg_volume:
                        logger.debug(f"  ✗ {ticker}: Volume {avg_vol:,.0f} < {min_avg_volume:,.0f}")
                        continue
                    
                    filtered.append(ticker)
                    logger.debug(f"  ✓ {ticker}: Passed filters")
                    
                except Exception as e:
                    logger.debug(f"  ? {ticker}: Filter error - {str(e)[:50]}")
                    filtered.append(ticker)  # Include anyway
            
            logger.info(f"Validation complete: {len(filtered)}/{len(tickers)} passed (with filters)")
            return filtered
        
        logger.info(f"Validation complete: {len(valid)}/{len(tickers)} passed")
        return valid
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("av_*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'ttl_hours': int(self.cache_ttl.total_seconds() / 3600),
            'api_calls_today': self.api_calls_today,
            'api_limit': 500
        }


# Convenience function
def fetch_stock_data_cached(ticker: str, period: str = "compact") -> Optional[pd.DataFrame]:
    """
    Convenience function to fetch single ticker
    
    Args:
        ticker: Stock ticker symbol
        period: 'compact' (100 days) or 'full' (20+ years)
        
    Returns:
        DataFrame with OHLCV data or None
    """
    fetcher = AlphaVantageDataFetcher()
    return fetcher.fetch_daily_data(ticker, outputsize=period)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    fetcher = AlphaVantageDataFetcher()
    
    # Test with ASX stocks
    tickers = ['CBA.AX', 'WBC.AX', 'ANZ.AX']
    print(f"\nTesting Alpha Vantage fetch for {tickers}")
    
    # Validate
    valid = fetcher.validate_by_quote(tickers)
    print(f"Valid tickers: {valid}")
    
    # Fetch data
    if valid:
        data = fetcher.fetch_batch(valid[:2])  # Limit to 2 to save API calls
        for ticker, df in data.items():
            print(f"\n{ticker}: {len(df)} days")
            print(df.tail(3))
    
    # Cache stats
    stats = fetcher.get_cache_stats()
    print(f"\nCache stats: {stats}")

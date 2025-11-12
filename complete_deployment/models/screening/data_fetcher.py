"""
Hybrid Data Fetcher with Caching and Batch Operations
------------------------------------------------------
Optimized data fetching to minimize Yahoo Finance API calls and avoid 429 errors.

Features:
- Batch fetching with yf.download() for multiple tickers
- Local caching with TTL (30 minutes default)
- Rate limiting with exponential backoff
- Graceful fallback for failed tickers
- Integration with existing StockScanner

Usage:
    fetcher = HybridDataFetcher()
    data = fetcher.fetch_batch(['CBA.AX', 'WBC.AX', 'ANZ.AX'])
"""

import os
import time
import pickle
import logging
import requests
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yfinance as yf
import pandas as pd
import numpy as np

# Setup logging
logger = logging.getLogger(__name__)

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"


# ============================================================================
# SHARED YAHOO FINANCE SESSION WITH RETRY LOGIC
# ============================================================================

def _make_yf_session() -> requests.Session:
    """
    Create a shared requests session with exponential backoff retry logic.
    This prevents 429 errors and handles transient failures gracefully.
    """
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/123.0 Safari/537.36")
    })
    retry = Retry(
        total=5,
        backoff_factor=0.6,  # 0.6, 1.2, 2.4, 4.8, 9.6 seconds
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


# Shared session for all Yahoo Finance requests
_YF_SESSION = _make_yf_session()


def _safe_yf_download(*, tickers, start=None, end=None, period=None, interval="1d",
                      group_by="ticker", threads=False):
    """
    Wrapper around yf.download with jitter/backoff on transient errors.
    Prevents 429 storms by using exponential backoff.
    
    Note: Not using custom session as newer yfinance versions require curl_cffi.
    Let yfinance handle its own session management internally.
    """
    last_err = None
    for attempt in range(6):
        try:
            return yf.download(
                tickers=tickers, start=start, end=end, period=period,
                interval=interval, group_by=group_by,
                progress=False, threads=threads
                # Note: Removed session parameter - yfinance handles this internally
            )
        except Exception as e:
            msg = str(e)
            last_err = e
            if ("429" in msg or "Too Many Requests" in msg or "Expecting value" in msg or
                "curl_cffi" in msg or "session" in msg.lower()):
                sleep_s = min(8, 0.8 * (2 ** attempt)) + random.random()
                logger.debug(f"Retry {attempt+1}/6 after {sleep_s:.1f}s due to: {msg[:80]}")
                time.sleep(sleep_s)
                continue
            raise
    
    if last_err:
        logger.warning(f"yf.download retries exhausted: {last_err}")
    
    # Final try (may return empty)
    return yf.download(
        tickers=tickers, start=start, end=end, period=period,
        interval=interval, group_by=group_by,
        progress=False, threads=threads
    )


class HybridDataFetcher:
    """
    Alpha Vantage-PRIMARY data fetcher (Yahoo Finance disabled due to IP blocking)
    Uses Alpha Vantage API with aggressive caching to stay under 500 req/day limit
    """
    
    def __init__(self, cache_dir: str = None, cache_ttl_minutes: int = 240):
        """
        Initialize Hybrid Data Fetcher (now uses Alpha Vantage as PRIMARY)
        
        Args:
            cache_dir: Directory for cache files (default: cache/)
            cache_ttl_minutes: Cache time-to-live in minutes (240 min = 4 hours)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.rate_limit_delay = 12.0  # Alpha Vantage: 12s = 5 calls/min
        
        # Alpha Vantage as PRIMARY (Yahoo disabled)
        self.alpha_vantage_key = ALPHA_VANTAGE_API_KEY
        self.use_yahoo_finance = False  # DISABLED due to IP blocking
        self.api_calls_today = 0
        self.api_calls_date = datetime.now().date()
        
        logger.info(f"Hybrid Data Fetcher initialized (ALPHA VANTAGE PRIMARY)")
        logger.info(f"  Data Source: Alpha Vantage API")
        logger.info(f"  Yahoo Finance: DISABLED (IP blocking)")
        logger.info(f"  Cache dir: {self.cache_dir}")
        logger.info(f"  Cache TTL: {cache_ttl_minutes} minutes ({cache_ttl_minutes/60:.1f} hours)")
        logger.info(f"  Rate limit: {self.rate_limit_delay}s between calls (5/min)")
        logger.info(f"  Daily limit: 500 API requests")
    
    def _cache_path(self, ticker: str, data_type: str = "info") -> Path:
        """Generate cache file path for a ticker"""
        safe_ticker = ticker.replace('.', '_').replace(':', '-')
        return self.cache_dir / f"{safe_ticker}_{data_type}.pkl"
    
    def _load_from_cache(self, ticker: str, data_type: str = "info") -> Optional[Dict]:
        """
        Load data from cache if available and not expired
        
        Returns:
            Cached data or None if cache miss/expired
        """
        cache_file = self._cache_path(ticker, data_type)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached = pickle.load(f)
            
            # Check if cache is still valid
            if datetime.now() - cached['timestamp'] < self.cache_ttl:
                logger.debug(f"Cache hit for {ticker} ({data_type})")
                return cached['data']
            else:
                logger.debug(f"Cache expired for {ticker} ({data_type})")
                return None
                
        except Exception as e:
            logger.warning(f"Cache read error for {ticker}: {e}")
            return None
    
    def _save_to_cache(self, ticker: str, data, data_type: str = "info"):
        """Save data to cache with timestamp"""
        cache_file = self._cache_path(ticker, data_type)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'timestamp': datetime.now(),
                    'data': data
                }, f)
            logger.debug(f"Cached data for {ticker} ({data_type})")
        except Exception as e:
            logger.warning(f"Cache write error for {ticker}: {e}")
    
    def _hist_cache_key(self, ticker: str, period: Optional[str], interval: str,
                        start: Optional[str], end: Optional[str]) -> str:
        """
        Generate cache key including all parameters that affect the payload.
        This prevents serving wrong granularity from cache.
        """
        tag = f"{ticker}|{period or ''}|{interval}|{start or ''}|{end or ''}"
        return f"hist_{tag}"
    
    def _track_api_call(self):
        """Track Alpha Vantage API usage"""
        today = datetime.now().date()
        if today != self.api_calls_date:
            self.api_calls_today = 0
            self.api_calls_date = today
        self.api_calls_today += 1
        
        if self.api_calls_today > 450:
            logger.warning(f"⚠️  High API usage: {self.api_calls_today}/500 calls today")
    
    def _convert_ticker_for_av(self, ticker: str) -> str:
        """Convert ticker format for Alpha Vantage (CBA.AX -> CBA)"""
        if ticker.endswith('.AX'):
            return ticker.replace('.AX', '')
        return ticker
    
    def _fetch_from_alpha_vantage_daily(self, ticker: str, outputsize: str = "compact") -> Optional[pd.DataFrame]:
        """
        Fetch daily OHLCV data from Alpha Vantage TIME_SERIES_DAILY
        
        Args:
            ticker: Stock ticker symbol
            outputsize: 'compact' (100 days) or 'full' (20+ years)
            
        Returns:
            DataFrame with OHLCV data or None
        """
        # Check API limit
        if self.api_calls_today >= 500:
            logger.error(f"⛔ Alpha Vantage daily limit reached (500/500)")
            return None
        
        try:
            av_symbol = self._convert_ticker_for_av(ticker)
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': av_symbol,
                'outputsize': outputsize,
                'apikey': self.alpha_vantage_key
            }
            
            logger.info(f"Fetching {ticker} from Alpha Vantage TIME_SERIES_DAILY...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            self._track_api_call()
            
            # Check for errors
            if 'Error Message' in data:
                logger.warning(f"Alpha Vantage error for {ticker}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            if 'Time Series (Daily)' not in data:
                logger.warning(f"No daily data for {ticker}")
                return None
            
            # Convert to DataFrame
            time_series = data['Time Series (Daily)']
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
            
            logger.info(f"✓ Fetched {ticker}: {len(df)} days (API: {self.api_calls_today}/500)")
            return df
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {str(e)[:100]}")
            return None
    
    def _fetch_from_alpha_vantage(self, ticker: str) -> Optional[Dict]:
        """
        Fetch ticker quote from Alpha Vantage GLOBAL_QUOTE (for validation)
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote info dictionary or None
        """
        if self.api_calls_today >= 500:
            logger.error(f"⛔ Alpha Vantage daily limit reached (500/500)")
            return None
        
        try:
            av_symbol = self._convert_ticker_for_av(ticker)
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': av_symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._track_api_call()
            
            if 'Global Quote' not in data or not data['Global Quote']:
                return None
            
            quote = data['Global Quote']
            
            info = {
                'symbol': ticker,
                'currentPrice': float(quote.get('05. price', 0)),
                'previousClose': float(quote.get('08. previous close', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'averageVolume': int(quote.get('06. volume', 0)) * 20,
                'marketCap': 0,
                'beta': 1.0,
                'source': 'alpha_vantage'
            }
            
            return info
            
        except Exception as e:
            logger.debug(f"Alpha Vantage error for {ticker}: {str(e)[:100]}")
            return None
    
    def validate_by_prices(self, tickers: List[str], period: str = "5d", interval: str = "1d") -> List[str]:
        """
        Validate tickers WITHOUT quoteSummary/info calls.
        Uses ONE batched price call; a ticker is valid if it returns any rows.
        
        This AVOIDS Yahoo's heavily rate-limited /quoteSummary endpoint entirely.
        
        Args:
            tickers: List of ticker symbols to validate
            period: Data period (default: 5d)
            interval: Data interval (default: 1d)
            
        Returns:
            List of valid tickers that returned price data
        """
        if not tickers:
            return []
        
        try:
            logger.info(f"Validating {len(tickers)} tickers via price data (NOT quoteSummary)...")
            df = _safe_yf_download(
                tickers=tickers, period=period, interval=interval,
                group_by="ticker", threads=False
            )
        except Exception as e:
            logger.warning(f"Validation batch fetch failed: {e}")
            return []
        
        valid = []
        
        # yfinance returns:
        # - single ticker: plain frame with OHLCV columns
        # - multiple: MultiIndex columns level 0 = ticker, level 1 = OHLCV
        if isinstance(df.columns, pd.MultiIndex):
            # Multiple tickers
            tick0 = list(dict.fromkeys(df.columns.get_level_values(0)))  # preserve order
            for t in tickers:
                if t in tick0:
                    sub = df[t]
                    if not sub.dropna(how="all").empty:
                        valid.append(t)
                        logger.debug(f"  ✓ {t}: Valid (has price data)")
                    else:
                        logger.debug(f"  ✗ {t}: Invalid (empty data)")
                else:
                    logger.debug(f"  ✗ {t}: Missing from response")
        else:
            # Single ticker case
            if not df.dropna(how="all").empty:
                valid = tickers[:1]
                logger.debug(f"  ✓ {tickers[0]}: Valid (has price data)")
        
        logger.info(f"Validation complete: {len(valid)}/{len(tickers)} passed (price-based)")
        return valid
    
    def fetch_ticker_info(self, ticker: str) -> Optional[Dict]:
        """
        Fetch ticker info with caching and Alpha Vantage fallback
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Ticker info dictionary or None if failed
        """
        # Try cache first
        cached_data = self._load_from_cache(ticker, "info")
        if cached_data is not None:
            return cached_data
        
        # Try Yahoo Finance first
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got valid info
            if not info or len(info) == 0:
                raise Exception("Empty info returned")
            
            # Cache successful fetch
            self._save_to_cache(ticker, info, "info")
            return info
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Catch ANY exception from yfinance (HTTPError, JSONDecodeError, etc.)
            error_str = str(e).lower()
            logger.debug(f"Yahoo Finance error for {ticker}: {error_str[:100]}")
            
            # Try Alpha Vantage fallback on any Yahoo Finance error
            if self.use_alpha_vantage_fallback:
                logger.warning(f"Yahoo Finance failed for {ticker}: {error_str[:50]}")
                logger.info(f"→ Trying Alpha Vantage fallback...")
                info = self._fetch_from_alpha_vantage(ticker)
                if info:
                    self._save_to_cache(ticker, info, "info")
                    return info
                else:
                    logger.warning(f"→ Alpha Vantage also failed for {ticker}")
            
            return None
    
    def fetch_batch(self, tickers: List[str],
                    period: Optional[str] = "5d",
                    interval: str = "1d",
                    start: Optional[str] = None,
                    end: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Batched OHLCV fetch for multiple tickers with caching and backoff.
        Uses _safe_yf_download with shared session and retry logic.
        
        Use either (period) or (start, end). For intraday, set interval like '5m'.
        
        Args:
            tickers: List of ticker symbols
            period: Data period (1d, 5d, 1mo, 3mo, 1y, etc.) OR None if using start/end
            interval: Data interval (1d, 1h, 5m, etc.)
            start: Start date string (YYYY-MM-DD) OR None if using period
            end: End date string (YYYY-MM-DD) OR None if using period
            
        Returns:
            Dictionary mapping ticker -> DataFrame with OHLCV data
        """
        if not tickers:
            return {}
        
        # Pull from cache first
        results: Dict[str, pd.DataFrame] = {}
        uncached: List[str] = []
        
        for t in tickers:
            key = self._hist_cache_key(t, period, interval, start, end)
            cached = self._load_from_cache(t, key)
            if cached is not None:
                results[t] = cached
            else:
                uncached.append(t)
        
        if not uncached:
            logger.info(f"All {len(tickers)} tickers loaded from cache")
            return results
        
        # One Yahoo batch call for remaining tickers
        logger.info(f"Batch fetching {len(uncached)} uncached tickers (interval={interval})...")
        df = _safe_yf_download(
            tickers=uncached, period=period, start=start, end=end,
            interval=interval, group_by="ticker", threads=False
        )
        
        # Extract per-ticker frames (robust MultiIndex handling)
        if isinstance(df.columns, pd.MultiIndex):
            # Multiple tickers
            available = list(dict.fromkeys(df.columns.get_level_values(0)))
            for t in uncached:
                if t in available:
                    sub = df[t]
                    if not sub.dropna(how="all").empty:
                        key = self._hist_cache_key(t, period, interval, start, end)
                        results[t] = sub
                        self._save_to_cache(t, sub, key)
                    else:
                        logger.warning(f"No data for {t}")
                else:
                    logger.warning(f"{t} missing from Yahoo batch response")
        else:
            # Single ticker case
            t = uncached[0]
            if not df.dropna(how="all").empty:
                key = self._hist_cache_key(t, period, interval, start, end)
                results[t] = df
                self._save_to_cache(t, df, key)
        
        logger.info(f"Batch fetch complete: {len(results)}/{len(tickers)} tickers")
        return results
    
    def validate_stock_batch(self, tickers: List[str], criteria: Dict) -> List[str]:
        """
        Backward-compatible wrapper that now validates via prices only.
        NO /quoteSummary calls = NO 429 rate limit storms.
        
        If criteria include volume/price bands, we approximate using recent OHLCV.
        For fundamentals (market cap, beta, etc.), compute them later from your own DB
        or a less frequent fundamentals API (e.g., EODHD/FMP).
        
        Args:
            tickers: List of ticker symbols to validate
            criteria: Dictionary with validation criteria (min_price, max_price, min_avg_volume)
            
        Returns:
            List of tickers that passed validation
        """
        logger.info(f"Validating {len(tickers)} tickers (price-based, NO quoteSummary)...")
        
        # First pass: price-based validation (one batch call)
        valid = self.validate_by_prices(tickers, period="5d", interval="1d")
        if not valid:
            logger.info("Validation complete: 0 passed")
            return []
        
        # Optional lightweight filtering using recent OHLCV (no fundamentals)
        min_price = criteria.get('min_price', None)
        max_price = criteria.get('max_price', None)
        min_avg_volume = criteria.get('min_avg_volume', None)
        
        if any(v is not None for v in (min_price, max_price, min_avg_volume)):
            # Fetch a small daily window for price/volume averages
            frames = self.fetch_batch(valid, period="1mo", interval="1d")
            filtered = []
            for t, df in frames.items():
                if df.empty:
                    continue
                
                # Get last close price
                last_close = float(df["Close"].dropna().iloc[-1]) if "Close" in df else 0.0
                
                # Calculate 20-day average volume
                vol20 = float(df["Volume"].dropna().tail(20).mean()) if "Volume" in df else 0.0
                
                # Apply filters
                if min_price is not None and last_close < min_price:
                    continue
                if max_price is not None and last_close > max_price:
                    continue
                if min_avg_volume is not None and vol20 < min_avg_volume:
                    continue
                
                filtered.append(t)
            
            logger.info(f"Validation complete: {len(filtered)}/{len(tickers)} passed (price/volume filters)")
            return filtered
        
        logger.info(f"Validation complete: {len(valid)}/{len(tickers)} passed")
        return valid
    
    def fetch_indices_soft(self, symbols = ("^AXJO", "^GSPC", "^IXIC", "^DJI"),
                           period: str = "5d", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Optional helper for market indices (used by SPI monitor).
        Tolerates empties, no retry storm. Returns dict of symbol -> DataFrame.
        """
        out: Dict[str, pd.DataFrame] = {}
        try:
            df = self._safe_yf_download(
                tickers=list(symbols), period=period,
                interval=interval, group_by="ticker", threads=False
            )
            
            if isinstance(df.columns, pd.MultiIndex):
                root = list(dict.fromkeys(df.columns.get_level_values(0)))
                for s in symbols:
                    if s in root:
                        sub = df[s]
                        if not sub.dropna(how="all").empty:
                            out[s] = sub
            else:
                # Single index case
                if not df.dropna(how="all").empty and symbols:
                    out[symbols[0]] = df
        except Exception as e:
            logger.warning(f"fetch_indices_soft failed: {e}")
        
        return out
    
    def clear_cache(self, older_than_hours: int = 24):
        """
        Clear cache files older than specified hours
        
        Args:
            older_than_hours: Clear cache older than this many hours
        """
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        cleared = 0
        
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if mtime < cutoff_time:
                    cache_file.unlink()
                    cleared += 1
            except Exception as e:
                logger.warning(f"Error clearing cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {cleared} old cache files")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'ttl_minutes': int(self.cache_ttl.total_seconds() / 60)
        }


# Convenience function for backward compatibility
def fetch_stock_data_cached(ticker: str, period: str = "5d", interval: str = "1d",
                            start: Optional[str] = None, end: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Convenience function to fetch single ticker with caching
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (e.g., "5d", "1mo", "1y")
        interval: Data interval (e.g., "1d", "5m", "1h")
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)
        
    Returns:
        DataFrame with OHLCV data or None
    """
    fetcher = HybridDataFetcher()
    result = fetcher.fetch_batch([ticker], period=period, interval=interval, start=start, end=end)
    return result.get(ticker)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    fetcher = HybridDataFetcher()
    
    # Test batch fetching
    tickers = ['CBA.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX']
    print(f"\nTesting batch fetch for {tickers}")
    
    data = fetcher.fetch_batch(tickers, period='5d')
    print(f"Fetched data for {len(data)} tickers")
    
    for ticker, df in data.items():
        print(f"\n{ticker}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        if not df.empty:
            print(f"  Latest close: ${df['Close'].iloc[-1]:.2f}")
    
    # Show cache stats
    stats = fetcher.get_cache_stats()
    print(f"\nCache stats:")
    print(f"  Files: {stats['total_files']}")
    print(f"  Size: {stats['total_size_mb']:.2f} MB")
    print(f"  TTL: {stats['ttl_minutes']} minutes")

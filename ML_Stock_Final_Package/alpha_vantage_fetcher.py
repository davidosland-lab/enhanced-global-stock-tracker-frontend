#!/usr/bin/env python3
"""
Alpha Vantage Data Fetcher
Alternative to Yahoo Finance using Alpha Vantage API
Can be used with MCP server or direct API calls
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import requests

logger = logging.getLogger(__name__)

class AlphaVantageDataFetcher:
    """
    Fetch stock data from Alpha Vantage API
    Supports both direct API and MCP server integration
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage fetcher
        
        Args:
            api_key: Alpha Vantage API key. If not provided, will look for:
                    1. config.py file
                    2. ALPHA_VANTAGE_API_KEY environment variable
                    3. MCP server configuration
        """
        # Try to import from config first
        if not api_key:
            try:
                from config import ALPHA_VANTAGE_API_KEY
                api_key = ALPHA_VANTAGE_API_KEY
                logger.info("API key loaded from config.py")
            except ImportError:
                pass
        
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # Free tier: 5 calls/minute = 12 seconds between calls
        self.last_call_time = 0
        
        if not self.api_key:
            logger.warning("No Alpha Vantage API key found. Set ALPHA_VANTAGE_API_KEY environment variable")
    
    def _rate_limit(self):
        """Enforce rate limiting for free tier"""
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.info(f"Rate limiting: waiting {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        self.last_call_time = time.time()
    
    def fetch_daily_data(self, symbol: str, outputsize: str = "full") -> pd.DataFrame:
        """
        Fetch daily time series data from Alpha Vantage
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'CBA.AX' -> 'CBA.AUS' for Alpha Vantage)
            outputsize: 'compact' (100 days) or 'full' (20+ years)
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.api_key:
            raise ValueError("Alpha Vantage API key required")
        
        # Convert Australian stocks format (Yahoo: CBA.AX -> Alpha Vantage: CBA.AUS)
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        self._rate_limit()
        
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': av_symbol,
            'outputsize': outputsize,
            'apikey': self.api_key,
            'datatype': 'json'
        }
        
        try:
            logger.info(f"Fetching data from Alpha Vantage for {av_symbol}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
            if 'Note' in data:
                raise ValueError(f"API limit reached: {data['Note']}")
            if 'Time Series (Daily)' not in data:
                raise ValueError(f"Unexpected response format: {list(data.keys())}")
            
            # Parse time series data
            time_series = data['Time Series (Daily)']
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match Yahoo Finance format
            column_mapping = {
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. adjusted close': 'Adj Close',
                '6. volume': 'Volume',
                '7. dividend amount': 'Dividend',
                '8. split coefficient': 'Split'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Select standard OHLCV columns
            standard_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            df = df[[col for col in standard_cols if col in df.columns]]
            
            # Add symbol column
            df['Symbol'] = symbol
            
            logger.info(f"✅ Successfully fetched {len(df)} days from Alpha Vantage")
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching Alpha Vantage data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing Alpha Vantage data: {e}")
            raise
    
    def fetch_intraday_data(self, symbol: str, interval: str = '5min') -> pd.DataFrame:
        """
        Fetch intraday data from Alpha Vantage
        
        Args:
            symbol: Stock symbol
            interval: '1min', '5min', '15min', '30min', '60min'
            
        Returns:
            DataFrame with intraday OHLCV data
        """
        if not self.api_key:
            raise ValueError("Alpha Vantage API key required")
        
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        self._rate_limit()
        
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': av_symbol,
            'interval': interval,
            'outputsize': 'full',
            'apikey': self.api_key,
            'datatype': 'json'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
            
            # Find time series key (varies by interval)
            time_series_key = f'Time Series ({interval})'
            if time_series_key not in data:
                raise ValueError(f"No intraday data found for {av_symbol}")
            
            # Parse and convert to DataFrame
            time_series = data[time_series_key]
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['Symbol'] = symbol
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}")
            raise
    
    def fetch_technical_indicators(self, symbol: str, indicator: str, **kwargs) -> pd.Series:
        """
        Fetch technical indicators from Alpha Vantage
        
        Args:
            symbol: Stock symbol
            indicator: Technical indicator function (e.g., 'RSI', 'MACD', 'SMA')
            **kwargs: Additional parameters for the indicator
            
        Returns:
            Series with indicator values
        """
        if not self.api_key:
            raise ValueError("Alpha Vantage API key required")
        
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        self._rate_limit()
        
        params = {
            'function': indicator,
            'symbol': av_symbol,
            'apikey': self.api_key,
            'datatype': 'json'
        }
        params.update(kwargs)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse technical indicator data
            # The key varies by indicator
            for key in data.keys():
                if 'Technical Analysis' in key:
                    ta_data = data[key]
                    series = pd.Series(ta_data)
                    series.index = pd.to_datetime(series.index)
                    return series.sort_index()
            
            raise ValueError(f"No technical indicator data found for {indicator}")
            
        except Exception as e:
            logger.error(f"Error fetching {indicator}: {e}")
            raise
    
    def get_quote_endpoint(self, symbol: str) -> Dict:
        """
        Get real-time quote data from Alpha Vantage
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with current price, volume, and change information
        """
        if not self.api_key:
            raise ValueError("Alpha Vantage API key required")
        
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        self._rate_limit()
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': av_symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' not in data:
                raise ValueError(f"No quote data found for {av_symbol}")
            
            quote = data['Global Quote']
            
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day'),
                'previous_close': float(quote.get('08. previous close', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%')
            }
            
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            raise


class AlphaVantageMLDataFetcher:
    """
    Drop-in replacement for Yahoo Finance data fetcher using Alpha Vantage
    Compatible with existing ML Stock Predictor interface
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.av_fetcher = AlphaVantageDataFetcher(api_key)
    
    @staticmethod
    def clear_cache():
        """Compatibility method - Alpha Vantage doesn't use local cache"""
        logger.info("Alpha Vantage doesn't use local cache")
    
    def fetch_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch stock data compatible with ML Stock Predictor
        
        Args:
            symbol: Stock symbol
            period: Time period ('1mo', '3mo', '6mo', '1y', '2y')
            interval: Data interval (only '1d' supported for Alpha Vantage daily data)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # For daily data, use full outputsize to get maximum history
            df = self.av_fetcher.fetch_daily_data(symbol, outputsize='full')
            
            # Filter by period
            period_days = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825,
                'max': 7300  # ~20 years
            }
            
            days = period_days.get(period, 180)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter data to requested period
            df = df[df.index >= cutoff_date]
            
            if len(df) < 50:
                logger.warning(f"Only {len(df)} data points available for {symbol} in {period}")
            
            logger.info(f"✅ Fetched {len(df)} days from Alpha Vantage for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch Alpha Vantage data: {e}")
            raise ValueError(f"Failed to fetch data for {symbol}: {e}")


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("Alpha Vantage Data Fetcher Test")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("\n❌ No Alpha Vantage API key found!")
        print("\nTo use Alpha Vantage, you need to:")
        print("1. Get a free API key from: https://www.alphavantage.co/support/#api-key")
        print("2. Set it as environment variable: export ALPHA_VANTAGE_API_KEY='your_key'")
        print("\nFree tier limits:")
        print("- 5 API requests per minute")
        print("- 500 requests per day")
        print("\nPremium tiers available for higher limits")
    else:
        print(f"\n✅ API key found: {api_key[:8]}...")
        
        # Test fetching data
        fetcher = AlphaVantageMLDataFetcher(api_key)
        
        print("\nTesting AAPL data fetch (1 year)...")
        try:
            df = fetcher.fetch_stock_data('AAPL', period='1y')
            print(f"✅ Got {len(df)} days of AAPL data")
            print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
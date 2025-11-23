"""
Historical Data Loader for Backtesting
=======================================

Fetches historical stock data from Yahoo Finance with intelligent caching.

Key Features:
- Yahoo Finance integration via yfinance
- Cache-first strategy (check cache before API call)
- Data validation integration
- Support for multiple time intervals (1d, 1h, 1wk)
- Batch loading for multiple symbols

Author: FinBERT v4.0
Date: October 2024
"""

import yfinance as yf
import pandas as pd
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from .cache_manager import CacheManager
from .data_validator import DataValidator

logger = logging.getLogger(__name__)


class HistoricalDataLoader:
    """Loads historical stock data with caching and validation"""
    
    def __init__(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        use_cache: bool = True,
        validate_data: bool = True
    ):
        """
        Initialize historical data loader
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_cache: Whether to use caching (default: True)
            validate_data: Whether to validate data (default: True)
        """
        self.symbol = symbol.upper()
        self.start_date = start_date
        self.end_date = end_date
        self.use_cache = use_cache
        self.validate_data = validate_data
        
        # Initialize components
        self.cache_manager = CacheManager() if use_cache else None
        self.validator = DataValidator() if validate_data else None
        
        logger.info(
            f"Data loader initialized for {self.symbol} "
            f"({self.start_date} to {self.end_date})"
        )
    
    def load_price_data(
        self,
        interval: str = '1d',
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load historical OHLCV price data
        
        Args:
            interval: Data interval ('1d', '1h', '1wk', etc.)
            force_refresh: Force refresh from API (ignore cache)
        
        Returns:
            DataFrame with OHLCV data (Date index)
        """
        logger.info(f"Loading price data for {self.symbol} (interval={interval})")
        
        # Check cache first (only for daily data)
        if self.use_cache and interval == '1d' and not force_refresh:
            cached_data = self.cache_manager.get_cached_data(
                self.symbol,
                self.start_date,
                self.end_date
            )
            
            if cached_data is not None:
                logger.info(f"Using cached data for {self.symbol}")
                return cached_data
        
        # Fetch from Yahoo Finance
        try:
            logger.info(f"Fetching data from Yahoo Finance for {self.symbol}")
            
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(
                start=self.start_date,
                end=self.end_date,
                interval=interval,
                auto_adjust=False  # Keep raw prices
            )
            
            if data.empty:
                logger.warning(f"No data returned for {self.symbol}")
                return pd.DataFrame()
            
            # Clean column names
            data.columns = data.columns.str.replace(' ', '_')
            
            # Validate data if enabled
            if self.validate_data:
                validation_results = self.validator.validate_data_quality(
                    data,
                    self.symbol
                )
                
                if not validation_results['is_valid']:
                    logger.error(
                        f"Data validation failed for {self.symbol}: "
                        f"{validation_results['issues']}"
                    )
                
                if validation_results['warnings']:
                    for warning in validation_results['warnings']:
                        logger.warning(f"{self.symbol}: {warning}")
            
            # Cache the data (only for daily data)
            if self.use_cache and interval == '1d':
                self.cache_manager.save_to_cache(self.symbol, data)
            
            logger.info(
                f"Successfully loaded {len(data)} records for {self.symbol}"
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading data for {self.symbol}: {e}")
            return pd.DataFrame()
    
    def load_with_indicators(
        self,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Load price data with technical indicators
        
        Args:
            interval: Data interval
        
        Returns:
            DataFrame with OHLCV + indicators
        """
        # Load base data
        data = self.load_price_data(interval=interval)
        
        if data.empty:
            return data
        
        # Add technical indicators
        data = self._add_technical_indicators(data)
        
        return data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add common technical indicators"""
        try:
            df = data.copy()
            
            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI (Relative Strength Index)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            
            # Volatility (ATR approximation)
            df['Daily_Return'] = df['Close'].pct_change()
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
            
            logger.info(f"Added technical indicators for {self.symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return data
    
    @staticmethod
    def load_multiple_symbols(
        symbols: List[str],
        start_date: str,
        end_date: str,
        interval: str = '1d',
        use_cache: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Load data for multiple symbols
        
        Args:
            symbols: List of stock ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            use_cache: Whether to use caching
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        logger.info(f"Loading data for {len(symbols)} symbols")
        
        results = {}
        
        for symbol in symbols:
            try:
                loader = HistoricalDataLoader(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    use_cache=use_cache
                )
                
                data = loader.load_price_data(interval=interval)
                
                if not data.empty:
                    results[symbol] = data
                else:
                    logger.warning(f"No data loaded for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error loading {symbol}: {e}")
        
        logger.info(
            f"Successfully loaded data for {len(results)}/{len(symbols)} symbols"
        )
        
        return results
    
    def get_latest_price(self) -> Optional[float]:
        """Get the most recent closing price"""
        try:
            data = self.load_price_data(interval='1d')
            
            if not data.empty:
                return float(data['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest price: {e}")
            return None
    
    def get_price_at_date(self, target_date: str) -> Optional[float]:
        """
        Get closing price at specific date
        
        Args:
            target_date: Target date (YYYY-MM-DD)
        
        Returns:
            Closing price or None if not found
        """
        try:
            data = self.load_price_data(interval='1d')
            
            if data.empty:
                return None
            
            target_dt = pd.to_datetime(target_date)
            
            if target_dt in data.index:
                return float(data.loc[target_dt, 'Close'])
            else:
                # Find nearest date
                nearest_idx = data.index.get_indexer([target_dt], method='nearest')[0]
                return float(data.iloc[nearest_idx]['Close'])
            
        except Exception as e:
            logger.error(f"Error getting price at date: {e}")
            return None

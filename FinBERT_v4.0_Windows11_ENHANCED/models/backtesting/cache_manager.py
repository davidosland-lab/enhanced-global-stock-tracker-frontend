"""
Cache Manager for Historical Stock Data
========================================

Manages SQLite cache for historical stock data to minimize API calls and improve performance.

Key Features:
- SQLite database for persistent caching
- Cache validation with 90% completeness threshold
- Automatic cache key generation
- Query optimization for date ranges

Author: FinBERT v4.0
Date: October 2024
"""

import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of historical stock data using SQLite"""
    
    def __init__(self, cache_dir: str = 'cache'):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache database
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / 'historical_data_cache.db'
        self._initialize_database()
        
        logger.info(f"Cache manager initialized at: {self.db_path}")
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create price cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    adjusted_close REAL,
                    cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol_date 
                ON price_cache(symbol, date)
            ''')
            
            conn.commit()
            logger.info("Cache database initialized successfully")
    
    def _generate_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """Generate unique cache key for data request"""
        return f"{symbol}_{start_date}_{end_date}"
    
    def get_cached_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Retrieve cached data for symbol and date range
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with cached data or None if cache miss/incomplete
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Query cached data
                query = '''
                    SELECT date, open, high, low, close, volume, adjusted_close
                    FROM price_cache
                    WHERE symbol = ? AND date >= ? AND date <= ?
                    ORDER BY date ASC
                '''
                
                df = pd.read_sql_query(
                    query, 
                    conn, 
                    params=(symbol, start_date, end_date),
                    parse_dates=['date']
                )
                
                if df.empty:
                    logger.info(f"Cache miss for {symbol}")
                    return None
                
                # Check if we have complete data (90% threshold)
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                expected_days = pd.bdate_range(start_dt, end_dt)
                actual_days = pd.to_datetime(df['date'])
                
                completeness = len(actual_days) / len(expected_days)
                
                if completeness < 0.9:
                    logger.warning(
                        f"Cache incomplete for {symbol}: {completeness:.1%} "
                        f"({len(actual_days)}/{len(expected_days)} days)"
                    )
                    return None
                
                # Set date as index
                df.set_index('date', inplace=True)
                df.index.name = 'Date'
                
                # Ensure timezone-naive index
                if df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
                
                # Rename columns to match Yahoo Finance format
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
                
                logger.info(
                    f"Cache hit for {symbol}: {len(df)} records "
                    f"({completeness:.1%} complete)"
                )
                return df
                
        except Exception as e:
            logger.error(f"Error retrieving cached data: {e}")
            return None
    
    def save_to_cache(self, symbol: str, data: pd.DataFrame):
        """
        Save data to cache
        
        Args:
            symbol: Stock ticker symbol
            data: DataFrame with OHLCV data (Date index)
        """
        try:
            if data.empty:
                logger.warning(f"No data to cache for {symbol}")
                return
            
            # Prepare data for insertion
            cache_data = data.copy()
            cache_data['symbol'] = symbol
            cache_data['date'] = cache_data.index.strftime('%Y-%m-%d')
            
            # Rename columns to match database schema
            column_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }
            
            # Handle both 'Adj Close' and 'Adj_Close' column names
            if 'Adj Close' in cache_data.columns:
                column_mapping['Adj Close'] = 'adjusted_close'
            elif 'Adj_Close' in cache_data.columns:
                column_mapping['Adj_Close'] = 'adjusted_close'
            
            cache_data.rename(columns=column_mapping, inplace=True)
            
            # Select only required columns
            cache_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']
            cache_data = cache_data[cache_columns]
            
            # Insert into database (using REPLACE to handle duplicates)
            with sqlite3.connect(self.db_path) as conn:
                cache_data.to_sql(
                    'price_cache', 
                    conn, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                
                logger.info(f"Cached {len(cache_data)} records for {symbol}")
                
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def invalidate_cache(self, symbol: Optional[str] = None):
        """
        Invalidate cache entries
        
        Args:
            symbol: Specific symbol to invalidate (or None for all)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if symbol:
                    cursor.execute('DELETE FROM price_cache WHERE symbol = ?', (symbol,))
                    logger.info(f"Invalidated cache for {symbol}")
                else:
                    cursor.execute('DELETE FROM price_cache')
                    logger.info("Invalidated entire cache")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute('SELECT COUNT(*) FROM price_cache')
                total_records = cursor.fetchone()[0]
                
                # Unique symbols
                cursor.execute('SELECT COUNT(DISTINCT symbol) FROM price_cache')
                unique_symbols = cursor.fetchone()[0]
                
                # Date range
                cursor.execute('SELECT MIN(date), MAX(date) FROM price_cache')
                date_range = cursor.fetchone()
                
                # Database size
                db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
                
                return {
                    'total_records': total_records,
                    'unique_symbols': unique_symbols,
                    'date_range': {
                        'start': date_range[0] if date_range[0] else 'N/A',
                        'end': date_range[1] if date_range[1] else 'N/A'
                    },
                    'database_size_mb': round(db_size, 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

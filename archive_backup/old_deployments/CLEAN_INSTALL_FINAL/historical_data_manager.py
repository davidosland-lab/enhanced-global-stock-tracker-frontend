"""
Historical Data Manager for Local Storage and Fast Backtesting
===============================================================
This module provides comprehensive local storage for historical market data
to significantly speed up backtesting and reduce Yahoo Finance API calls.
"""

import os
import json
import pickle
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import yfinance as yf
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalDataManager:
    """
    Manages local storage of historical market data for fast backtesting.
    Features:
    - SQLite database for structured storage
    - Automatic data updates
    - Compression for space efficiency
    - Multi-symbol batch downloads
    - Intelligent caching strategies
    """
    
    def __init__(self, data_dir: str = "historical_data"):
        """Initialize the data manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database paths
        self.db_path = self.data_dir / "market_data.db"
        self.metadata_path = self.data_dir / "metadata.json"
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load metadata
        self.metadata = self._load_metadata()
        
        # Thread pool for parallel downloads
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        logger.info(f"📦 Historical Data Manager initialized at {self.data_dir}")
    
    def _init_database(self):
        """Initialize SQLite database with optimized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main price data table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                interval TEXT,
                PRIMARY KEY (symbol, timestamp, interval)
            )
        ''')
        
        # Create indexes for fast queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
            ON price_data(symbol, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON price_data(timestamp)
        ''')
        
        # Create technical indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators (
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL,
                parameters TEXT,
                PRIMARY KEY (symbol, timestamp, indicator_name)
            )
        ''')
        
        # Create predictions history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                model_name TEXT,
                predicted_price REAL,
                predicted_direction INTEGER,
                confidence REAL,
                actual_price REAL,
                actual_direction INTEGER,
                error REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create backtest results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                model_name TEXT,
                accuracy REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                total_return REAL,
                win_rate REAL,
                parameters TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_metadata(self) -> Dict:
        """Load metadata about stored data"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            "last_update": {},
            "symbols": {},
            "intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"],
            "data_ranges": {}
        }
    
    def _save_metadata(self):
        """Save metadata"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    async def download_historical_data(self, 
                                      symbols: List[str], 
                                      period: str = "2y",
                                      intervals: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Download historical data for multiple symbols in parallel
        
        Args:
            symbols: List of stock symbols
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            intervals: List of intervals to download
        
        Returns:
            Dictionary of DataFrames with historical data
        """
        if intervals is None:
            intervals = ["1d", "1h", "30m"]  # Default intervals
        
        logger.info(f"📥 Downloading historical data for {len(symbols)} symbols")
        logger.info(f"   Period: {period}, Intervals: {intervals}")
        
        results = {}
        tasks = []
        
        # Create download tasks
        for symbol in symbols:
            for interval in intervals:
                task = self.executor.submit(self._download_single, symbol, period, interval)
                tasks.append((symbol, interval, task))
        
        # Collect results
        for symbol, interval, task in tasks:
            try:
                df = task.result(timeout=30)
                if df is not None and not df.empty:
                    # Store in database
                    self._store_price_data(symbol, df, interval)
                    
                    # Update results
                    if symbol not in results:
                        results[symbol] = {}
                    results[symbol][interval] = df
                    
                    logger.info(f"✅ Downloaded {symbol} ({interval}): {len(df)} records")
            except Exception as e:
                logger.error(f"❌ Failed to download {symbol} ({interval}): {e}")
        
        # Update metadata
        for symbol in symbols:
            self.metadata["last_update"][symbol] = datetime.now().isoformat()
            if symbol not in self.metadata["symbols"]:
                self.metadata["symbols"][symbol] = {
                    "intervals": intervals,
                    "first_date": None,
                    "last_date": None,
                    "record_count": 0
                }
        
        self._save_metadata()
        return results
    
    def _download_single(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Download data for a single symbol and interval"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
            
            # Reset index to get timestamp as column
            df = df.reset_index()
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {symbol} ({interval}): {e}")
            return None
    
    def _store_price_data(self, symbol: str, df: pd.DataFrame, interval: str):
        """Store price data in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Prepare data for insertion
            df['symbol'] = symbol
            df['interval'] = interval
            
            # Rename columns to match database schema
            df = df.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Select relevant columns
            columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'interval']
            df_to_store = df[columns]
            
            # Store in database (replace existing data)
            df_to_store.to_sql('price_data', conn, if_exists='replace', index=False)
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing data for {symbol}: {e}")
        finally:
            conn.close()
    
    def get_historical_data(self, 
                          symbol: str, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          interval: str = "1d") -> pd.DataFrame:
        """
        Retrieve historical data from local storage
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
        
        Returns:
            DataFrame with historical data
        """
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Build query
            query = """
                SELECT timestamp, open, high, low, close, volume
                FROM price_data
                WHERE symbol = ? AND interval = ?
            """
            params = [symbol, interval]
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp"
            
            # Execute query
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                logger.info(f"📊 Retrieved {len(df)} records for {symbol} from local storage")
            else:
                logger.warning(f"⚠️ No local data found for {symbol}, consider downloading first")
            
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol}: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def update_symbol_data(self, symbol: str, force: bool = False) -> bool:
        """
        Update data for a symbol if needed
        
        Args:
            symbol: Stock symbol
            force: Force update even if recent data exists
        
        Returns:
            True if updated, False otherwise
        """
        try:
            # Check last update time
            last_update = self.metadata["last_update"].get(symbol)
            
            if not force and last_update:
                last_update_dt = datetime.fromisoformat(last_update)
                if datetime.now() - last_update_dt < timedelta(hours=1):
                    logger.info(f"⏭️ Skipping {symbol} - recently updated")
                    return False
            
            # Download latest data
            logger.info(f"🔄 Updating {symbol} data...")
            ticker = yf.Ticker(symbol)
            
            # Download different intervals
            intervals = ["1d", "1h", "30m", "5m"]
            for interval in intervals:
                df = ticker.history(period="1mo", interval=interval)
                if not df.empty:
                    self._store_price_data(symbol, df.reset_index(), interval)
            
            # Update metadata
            self.metadata["last_update"][symbol] = datetime.now().isoformat()
            self._save_metadata()
            
            logger.info(f"✅ Updated {symbol} successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update {symbol}: {e}")
            return False
    
    def get_batch_data(self, 
                      symbols: List[str], 
                      start_date: str,
                      end_date: str,
                      interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Get historical data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            interval: Data interval
        
        Returns:
            Dictionary of DataFrames
        """
        results = {}
        
        for symbol in symbols:
            df = self.get_historical_data(symbol, start_date, end_date, interval)
            if not df.empty:
                results[symbol] = df
        
        logger.info(f"📦 Retrieved data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def store_backtest_results(self, results: Dict[str, Any]):
        """Store backtest results for future reference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO backtest_results 
                (symbol, start_date, end_date, model_name, accuracy, 
                 sharpe_ratio, max_drawdown, total_return, win_rate, parameters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                results.get('symbol'),
                results.get('start_date'),
                results.get('end_date'),
                results.get('model_name'),
                results.get('accuracy'),
                results.get('sharpe_ratio'),
                results.get('max_drawdown'),
                results.get('total_return'),
                results.get('win_rate'),
                json.dumps(results.get('parameters', {}))
            ))
            
            conn.commit()
            logger.info(f"💾 Stored backtest results for {results.get('symbol')}")
            
        except Exception as e:
            logger.error(f"Error storing backtest results: {e}")
        finally:
            conn.close()
    
    def get_best_models(self, symbol: str, metric: str = "accuracy") -> pd.DataFrame:
        """Get best performing models for a symbol based on backtest history"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            query = f"""
                SELECT model_name, AVG({metric}) as avg_metric, 
                       COUNT(*) as test_count, MAX(created_at) as last_test
                FROM backtest_results
                WHERE symbol = ?
                GROUP BY model_name
                ORDER BY avg_metric DESC
                LIMIT 10
            """
            
            df = pd.read_sql_query(query, conn, params=[symbol])
            return df
            
        except Exception as e:
            logger.error(f"Error getting best models: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Remove data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean price data
            cursor.execute('''
                DELETE FROM price_data 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            # Clean predictions
            cursor.execute('''
                DELETE FROM predictions 
                WHERE created_at < ?
            ''', (cutoff_date,))
            
            conn.commit()
            logger.info(f"🧹 Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
        finally:
            conn.close()
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM price_data")
            stats['total_price_records'] = cursor.fetchone()[0]
            
            # Count unique symbols
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM price_data")
            stats['unique_symbols'] = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_data")
            min_date, max_date = cursor.fetchone()
            stats['date_range'] = {
                'start': min_date,
                'end': max_date
            }
            
            # Get storage size
            stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
            
            # Count backtest results
            cursor.execute("SELECT COUNT(*) FROM backtest_results")
            stats['total_backtests'] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()


# Example usage and integration
async def demo_usage():
    """Demonstrate how to use the Historical Data Manager"""
    
    # Initialize manager
    manager = HistoricalDataManager("historical_data")
    
    # Download historical data for multiple symbols
    symbols = ["CBA.AX", "^AORD", "^GSPC", "AAPL", "MSFT"]
    data = await manager.download_historical_data(
        symbols=symbols,
        period="1y",
        intervals=["1d", "1h", "30m"]
    )
    
    # Get data for backtesting
    cba_data = manager.get_historical_data(
        symbol="CBA.AX",
        start_date="2024-01-01",
        end_date="2024-12-31",
        interval="1d"
    )
    
    print(f"Retrieved {len(cba_data)} days of CBA.AX data")
    print(f"Latest price: ${cba_data['close'].iloc[-1]:.2f}")
    
    # Get batch data for multiple symbols
    batch_data = manager.get_batch_data(
        symbols=["CBA.AX", "^AORD"],
        start_date="2024-06-01",
        end_date="2024-12-31",
        interval="1d"
    )
    
    # Store backtest results
    manager.store_backtest_results({
        'symbol': 'CBA.AX',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'model_name': 'LSTM',
        'accuracy': 0.65,
        'sharpe_ratio': 1.2,
        'max_drawdown': -0.15,
        'total_return': 0.25,
        'win_rate': 0.58,
        'parameters': {'layers': 3, 'neurons': 128}
    })
    
    # Get statistics
    stats = manager.get_data_statistics()
    print(f"Database statistics: {stats}")
    
    # Get best performing models
    best_models = manager.get_best_models("CBA.AX", metric="accuracy")
    print(f"Best models for CBA.AX:\n{best_models}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_usage())
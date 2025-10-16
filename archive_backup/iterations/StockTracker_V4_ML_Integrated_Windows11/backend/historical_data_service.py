#!/usr/bin/env python3
"""
Enhanced Historical Data Service with Local Database Storage
Provides caching, batch downloads, and fast data retrieval for ML modules
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
import logging
from pathlib import Path
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalDataService:
    """
    Centralized service for managing historical market data
    Features:
    - SQLite local storage for fast retrieval
    - Automatic updates for stale data
    - Batch download capabilities
    - Integration with ML modules
    """
    
    def __init__(self, db_path: str = "historical_data/market_data.db"):
        """Initialize the historical data service"""
        self.db_dir = Path("historical_data")
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "market_data.db"
        self.cache_dir = self.db_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Thread pool for parallel downloads
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        logger.info(f"📊 Historical Data Service initialized with database at {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main price data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                interval TEXT DEFAULT '1d',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date, interval)
            )
        ''')
        
        # Create indexes for performance (only if they don't exist)
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_date ON price_data(symbol, date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON price_data(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_updated ON price_data(last_updated)')
        except sqlite3.OperationalError:
            # Indexes might already exist or columns might have different names
            pass
        
        # Metadata table for tracking updates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                symbol TEXT PRIMARY KEY,
                first_date DATE,
                last_date DATE,
                total_records INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_quality REAL DEFAULT 1.0
            )
        ''')
        
        # Technical indicators cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators_cache (
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL,
                parameters TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date, indicator_name, parameters)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def download_historical_data(self, symbol: str, period: str = "2y", interval: str = "1d") -> Dict:
        """Download and store historical data for a symbol"""
        try:
            logger.info(f"📥 Downloading {symbol} data: period={period}, interval={interval}")
            
            # Download from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data available for {symbol}")
                return {"success": False, "message": f"No data available for {symbol}"}
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            records_added = 0
            for date, row in df.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO price_data 
                    (symbol, date, open, high, low, close, volume, interval, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    date.date(),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume']),
                    interval,
                    datetime.now()
                ))
                records_added += 1
            
            # Update metadata
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (symbol, first_date, last_date, total_records, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                symbol,
                df.index[0].date(),
                df.index[-1].date(),
                records_added,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored {records_added} records for {symbol}")
            
            return {
                "success": True,
                "symbol": symbol,
                "records_added": records_added,
                "date_range": {
                    "start": str(df.index[0].date()),
                    "end": str(df.index[-1].date())
                }
            }
            
        except Exception as e:
            logger.error(f"Error downloading {symbol}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def batch_download(self, symbols: List[str], period: str = "2y") -> Dict:
        """Download data for multiple symbols in parallel"""
        results = []
        futures = []
        
        logger.info(f"🚀 Starting batch download for {len(symbols)} symbols")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            for symbol in symbols:
                future = executor.submit(self.download_historical_data, symbol, period)
                futures.append((symbol, future))
            
            for symbol, future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to download {symbol}: {str(e)}")
                    results.append({"success": False, "symbol": symbol, "error": str(e)})
        
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "total": len(symbols),
            "successful": successful,
            "failed": len(symbols) - successful,
            "results": results
        }
    
    def get_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                 auto_download: bool = True) -> Optional[pd.DataFrame]:
        """
        Get historical data from local database
        Auto-downloads if data is missing or stale
        """
        conn = sqlite3.connect(self.db_path)
        
        # Build query
        query = "SELECT * FROM price_data WHERE symbol = ?"
        params = [symbol]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        # Try to get data from database
        df = pd.read_sql_query(query, conn, parse_dates=['date'])
        conn.close()
        
        # Check if we need to download
        if df.empty and auto_download:
            logger.info(f"No local data for {symbol}, downloading...")
            self.download_historical_data(symbol)
            # Try again
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'])
            conn.close()
        elif not df.empty:
            # Check if data is stale (more than 1 day old)
            last_update = pd.to_datetime(df['last_updated'].iloc[-1])
            if (datetime.now() - last_update).days > 1 and auto_download:
                logger.info(f"Data for {symbol} is stale, updating...")
                self.download_historical_data(symbol, period="5d")
                # Get updated data
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'])
                conn.close()
        
        if not df.empty:
            # Set date as index
            df.set_index('date', inplace=True)
            # Remove metadata columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total symbols
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM price_data")
        total_symbols = cursor.fetchone()[0]
        
        # Get total records
        cursor.execute("SELECT COUNT(*) FROM price_data")
        total_records = cursor.fetchone()[0]
        
        # Get date range
        cursor.execute("SELECT MIN(date), MAX(date) FROM price_data")
        date_range = cursor.fetchone()
        
        # Get symbols with data
        cursor.execute("SELECT symbol, COUNT(*) as count FROM price_data GROUP BY symbol")
        symbols_data = cursor.fetchall()
        
        # Get recent updates
        cursor.execute("""
            SELECT symbol, last_updated 
            FROM metadata 
            ORDER BY last_updated DESC 
            LIMIT 10
        """)
        recent_updates = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_symbols": total_symbols,
            "total_records": total_records,
            "date_range": {
                "start": str(date_range[0]) if date_range[0] else None,
                "end": str(date_range[1]) if date_range[1] else None
            },
            "symbols": [{"symbol": s[0], "records": s[1]} for s in symbols_data],
            "recent_updates": [{"symbol": s[0], "updated": str(s[1])} for s in recent_updates],
            "database_size": os.path.getsize(self.db_path) / (1024 * 1024)  # Size in MB
        }
    
    def clear_old_data(self, days_to_keep: int = 730) -> int:
        """Clear data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        cursor.execute("DELETE FROM price_data WHERE date < ?", (cutoff_date.date(),))
        deleted_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"🗑️ Cleared {deleted_rows} old records")
        return deleted_rows
    
    def get_data_for_ml(self, symbol: str, lookback_days: int = 365) -> Dict:
        """Get data formatted for ML models"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)
        
        df = self.get_data(symbol, str(start_date), str(end_date))
        
        if df is None or df.empty:
            return None
        
        # Calculate additional features for ML
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # Moving averages
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()
        
        # Volatility
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return {
            "symbol": symbol,
            "data": df.dropna().to_dict('records'),
            "features": list(df.columns),
            "records": len(df),
            "date_range": {
                "start": str(df.index[0].date()) if len(df) > 0 else None,
                "end": str(df.index[-1].date()) if len(df) > 0 else None
            }
        }

# Singleton instance
_service_instance = None

def get_service() -> HistoricalDataService:
    """Get or create the historical data service singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = HistoricalDataService()
    return _service_instance

if __name__ == "__main__":
    # Test the service
    service = get_service()
    
    # Download some test data
    print("Testing Historical Data Service...")
    
    # Single download
    result = service.download_historical_data("AAPL", "1mo")
    print(f"AAPL download: {result}")
    
    # Get statistics
    stats = service.get_statistics()
    print(f"Database statistics: {json.dumps(stats, indent=2)}")
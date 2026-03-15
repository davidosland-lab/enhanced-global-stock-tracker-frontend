"""
Pipeline Integration Module

Integrates Parquet storage and DuckDB analytics with existing trading pipelines.
Automatically captures and stores prediction results, trade data, and market metadata.

Usage:
    from pipelines.data_storage.pipeline_integration import PipelineStorageManager
    
    storage = PipelineStorageManager()
    storage.store_prediction_results(predictions_df, symbols)
    storage.store_market_snapshot(markets_df)
    analytics = storage.get_analytics_report()
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import pandas as pd
import numpy as np

from .parquet_store import ParquetTradeStore, ParquetMarketStore
from .duckdb_analytics import DuckDBAnalyticsEngine

logger = logging.getLogger(__name__)


class PipelineStorageManager:
    """
    Integration layer between trading pipelines and Parquet storage
    
    Features:
    - Automatic conversion of pipeline results to Parquet format
    - Trade execution logging
    - Market snapshot storage
    - Analytics dashboard integration
    """
    
    def __init__(
        self,
        base_path: Union[str, Path] = 'data',
        enable_analytics: bool = True
    ):
        """
        Initialize Pipeline Storage Manager
        
        Args:
            base_path: Base directory for data storage
            enable_analytics: Enable DuckDB analytics engine
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage engines
        self.trade_store = ParquetTradeStore(self.base_path / 'trades')
        self.market_store = ParquetMarketStore(self.base_path / 'markets')
        
        # Initialize analytics engine
        self.analytics_engine = None
        if enable_analytics:
            try:
                self.analytics_engine = DuckDBAnalyticsEngine(
                    trade_data_path=self.base_path / 'trades',
                    market_data_path=self.base_path / 'markets',
                    database_path=self.base_path / 'analytics.duckdb'
                )
                logger.info("[OK] Analytics engine enabled")
            except Exception as e:
                logger.warning(f"[WARNING] Analytics engine initialization failed: {e}")
        
        logger.info(f"[OK] Pipeline Storage Manager initialized at: {self.base_path}")
    
    def store_prediction_results(
        self,
        predictions: List[Dict],
        trade_date: Optional[Union[date, str]] = None
    ) -> Dict[str, any]:
        """
        Store prediction results from overnight screening pipelines
        
        Args:
            predictions: List of prediction dictionaries from batch_predictor
            trade_date: Date of predictions (defaults to today)
        
        Returns:
            Dict with storage statistics
        """
        if not predictions:
            logger.warning("[WARNING] No predictions to store")
            return {'stored': 0, 'errors': 0}
        
        # Convert predictions to trades DataFrame
        trades_df = self._predictions_to_trades_df(predictions)
        
        if trades_df.empty:
            logger.warning("[WARNING] No valid trades to store")
            return {'stored': 0, 'errors': 0}
        
        # Group by symbol and store
        trades_by_symbol = {}
        for symbol in trades_df['symbol'].unique():
            symbol_trades = trades_df[trades_df['symbol'] == symbol].copy()
            trades_by_symbol[symbol] = symbol_trades
        
        # Batch store
        stored_paths = self.trade_store.store_trades_batch(trades_by_symbol, trade_date)
        
        stats = {
            'stored': len(stored_paths),
            'errors': len(trades_by_symbol) - len(stored_paths),
            'total_trades': len(trades_df),
            'symbols': list(trades_by_symbol.keys()),
            'date': str(trade_date or datetime.now().date())
        }
        
        logger.info(f"[OK] Stored {stats['stored']}/{len(trades_by_symbol)} symbols ({stats['total_trades']} trades)")
        return stats
    
    def store_market_snapshot(
        self,
        markets_df: pd.DataFrame,
        snapshot_date: Optional[Union[date, str]] = None
    ) -> Path:
        """
        Store market metadata snapshot
        
        Args:
            markets_df: DataFrame with market data (symbol, sector, price, etc.)
            snapshot_date: Date of snapshot (defaults to today)
        
        Returns:
            Path to stored Parquet file
        """
        if markets_df.empty:
            logger.warning("[WARNING] No market data to store")
            return None
        
        # Ensure required columns
        markets_df = self._normalize_market_data(markets_df)
        
        # Store
        path = self.market_store.store_markets(markets_df, snapshot_date)
        
        logger.info(f"[OK] Stored market snapshot: {len(markets_df)} symbols")
        return path
    
    def store_execution_trade(
        self,
        symbol: str,
        price: float,
        volume: int,
        side: str,
        order_type: str = 'market',
        role: str = 'taker',
        executed_price: Optional[float] = None,
        fees: float = 0.0,
        trade_id: Optional[str] = None
    ) -> Path:
        """
        Store a single executed trade
        
        Args:
            symbol: Stock symbol
            price: Order price
            volume: Share quantity
            side: 'buy' or 'sell'
            order_type: 'market' or 'limit'
            role: 'maker' or 'taker'
            executed_price: Actual execution price
            fees: Transaction fees
            trade_id: Unique trade identifier
        
        Returns:
            Path to stored Parquet file
        """
        if executed_price is None:
            executed_price = price
        
        if trade_id is None:
            trade_id = f"{symbol}_{int(datetime.now().timestamp() * 1000)}"
        
        # Create trade DataFrame
        trade_df = pd.DataFrame([{
            'timestamp': pd.Timestamp.now(tz='UTC'),
            'symbol': symbol,
            'price': price,
            'volume': volume,
            'side': side,
            'order_type': order_type,
            'trade_id': trade_id,
            'executed_price': executed_price,
            'bid': executed_price * 0.999,  # Approximate
            'ask': executed_price * 1.001,  # Approximate
            'spread': executed_price * 0.002,
            'role': role,
            'cost_basis': executed_price * volume,
            'fees': fees,
            'pnl': 0.0,  # Will be calculated on position close
            'cumulative_pnl': 0.0,
            'portfolio_value': 0.0
        }])
        
        # Store
        path = self.trade_store.store_trades(trade_df, symbol)
        
        logger.info(f"[OK] Stored execution: {symbol} {side.upper()} {volume}@{executed_price:.2f}")
        return path
    
    def get_analytics_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive analytics report
        
        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            Dict with analytics data
        """
        if not self.analytics_engine:
            logger.warning("[WARNING] Analytics engine not available")
            return {}
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
        
        try:
            # Portfolio performance
            report['portfolio'] = self.analytics_engine.get_portfolio_performance(
                start_date=start_date,
                end_date=end_date
            )
            
            # Top performers
            report['top_performers'] = self.analytics_engine.get_top_performers(
                metric='total_pnl',
                limit=10,
                start_date=start_date,
                end_date=end_date
            ).to_dict('records')
            
            # Maker/Taker analysis
            maker_taker_df = self.analytics_engine.analyze_maker_taker_returns(
                start_date=start_date,
                end_date=end_date
            )
            report['maker_taker'] = {
                'data': maker_taker_df.to_dict('records') if not maker_taker_df.empty else [],
                'summary': {
                    'maker_avg': maker_taker_df[maker_taker_df['role'] == 'maker']['avg_return'].mean() if not maker_taker_df.empty else 0.0,
                    'taker_avg': maker_taker_df[maker_taker_df['role'] == 'taker']['avg_return'].mean() if not maker_taker_df.empty else 0.0
                }
            }
            
            # Category efficiency
            category_df = self.analytics_engine.analyze_category_efficiency()
            report['category_efficiency'] = category_df.to_dict('records') if not category_df.empty else []
            
            logger.info("[OK] Analytics report generated")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to generate analytics: {e}")
            report['error'] = str(e)
        
        return report
    
    def get_storage_stats(self) -> Dict:
        """
        Get comprehensive storage statistics
        
        Returns:
            Dict with storage metrics
        """
        trade_stats = self.trade_store.get_storage_stats()
        
        stats = {
            'base_path': str(self.base_path),
            'trades': trade_stats,
            'analytics_enabled': self.analytics_engine is not None
        }
        
        if self.analytics_engine:
            try:
                stats['total_trades'] = self.analytics_engine.get_trade_count()
            except:
                stats['total_trades'] = 0
        
        return stats
    
    def _predictions_to_trades_df(self, predictions: List[Dict]) -> pd.DataFrame:
        """
        Convert prediction results to trades DataFrame
        
        Args:
            predictions: List of prediction dictionaries
        
        Returns:
            DataFrame in trade format
        """
        trades = []
        
        for pred in predictions:
            try:
                # Extract prediction data
                symbol = pred.get('symbol', 'UNKNOWN')
                signal = pred.get('signal', 'HOLD')
                confidence = pred.get('confidence', 0.0)
                current_price = pred.get('current_price', pred.get('price', 0.0))
                
                # Skip if no price
                if current_price <= 0:
                    continue
                
                # Convert prediction to simulated trade
                side = 'buy' if signal == 'BUY' else ('sell' if signal == 'SELL' else 'hold')
                
                if side == 'hold':
                    continue  # Don't store HOLD signals as trades
                
                # Create trade record
                trade = {
                    'timestamp': pd.Timestamp.now(tz='UTC'),
                    'symbol': symbol,
                    'price': current_price,
                    'volume': int(confidence * 100),  # Volume proportional to confidence
                    'side': side,
                    'order_type': 'limit',
                    'trade_id': f"PRED_{symbol}_{int(datetime.now().timestamp())}",
                    'executed_price': current_price,
                    'bid': current_price * 0.999,
                    'ask': current_price * 1.001,
                    'spread': current_price * 0.002,
                    'role': 'taker',
                    'cost_basis': current_price * (confidence * 100),
                    'fees': 0.0,
                    'pnl': 0.0,
                    'cumulative_pnl': 0.0,
                    'portfolio_value': 0.0
                }
                
                trades.append(trade)
                
            except Exception as e:
                logger.warning(f"Failed to convert prediction to trade: {e}")
                continue
        
        return pd.DataFrame(trades)
    
    def _normalize_market_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize market data to match schema
        
        Args:
            df: Input DataFrame
        
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        # Required columns with defaults
        defaults = {
            'symbol': 'UNKNOWN',
            'name': '',
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 0.0,
            'price': 0.0,
            'volume': 0,
            'avg_volume': 0,
            'open': 0.0,
            'high': 0.0,
            'low': 0.0,
            'close': 0.0,
            'previous_close': 0.0,
            'change_percent': 0.0,
            'status': 'open',
            'category': 'Unknown',
            'efficiency_score': 0.5
        }
        
        for col, default_val in defaults.items():
            if col not in df.columns:
                df[col] = default_val
        
        return df


class PipelineDataLogger:
    """
    Convenience logger for pipeline integration
    
    Usage in existing pipelines:
        from pipelines.data_storage.pipeline_integration import PipelineDataLogger
        
        logger = PipelineDataLogger()
        logger.log_predictions(predictions)
        logger.log_market_data(stocks_df)
    """
    
    def __init__(self, base_path: str = 'data'):
        self.storage = PipelineStorageManager(base_path)
        logger.info("[OK] Pipeline Data Logger initialized")
    
    def log_predictions(self, predictions: List[Dict]) -> Dict:
        """Log prediction results"""
        return self.storage.store_prediction_results(predictions)
    
    def log_market_data(self, markets_df: pd.DataFrame) -> Path:
        """Log market snapshot"""
        return self.storage.store_market_snapshot(markets_df)
    
    def log_trade(self, **kwargs) -> Path:
        """Log single trade execution"""
        return self.storage.store_execution_trade(**kwargs)
    
    def get_report(self) -> Dict:
        """Get analytics report"""
        return self.storage.get_analytics_report()
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        return self.storage.get_storage_stats()


# Example integration code for existing pipelines
def integrate_with_us_pipeline(predictions: List[Dict], stocks_df: pd.DataFrame):
    """
    Example: How to integrate with run_us_full_pipeline.py
    
    Add this at the end of the pipeline after predictions are generated:
    
        from pipelines.data_storage.pipeline_integration import integrate_with_us_pipeline
        integrate_with_us_pipeline(predictions, stocks_df)
    """
    logger = PipelineDataLogger(base_path='data/us')
    
    # Store predictions as trade signals
    pred_stats = logger.log_predictions(predictions)
    logger.info(f"[US PIPELINE] Stored {pred_stats['stored']} prediction signals")
    
    # Store market snapshot
    if not stocks_df.empty:
        market_path = logger.log_market_data(stocks_df)
        logger.info(f"[US PIPELINE] Stored market snapshot: {market_path}")
    
    # Get analytics
    report = logger.get_report()
    if 'portfolio' in report:
        logger.info(f"[US PIPELINE] Portfolio PnL: ${report['portfolio'].get('total_pnl', 0):.2f}")
    
    return report


# Testing and validation
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test storage manager
    storage = PipelineStorageManager(base_path='data/test')
    
    # Test prediction storage
    test_predictions = [
        {
            'symbol': 'AAPL',
            'signal': 'BUY',
            'confidence': 0.85,
            'current_price': 175.50,
            'target_price': 185.00
        },
        {
            'symbol': 'MSFT',
            'signal': 'HOLD',
            'confidence': 0.60,
            'current_price': 380.00
        },
        {
            'symbol': 'GOOGL',
            'signal': 'SELL',
            'confidence': 0.70,
            'current_price': 140.00
        }
    ]
    
    stats = storage.store_prediction_results(test_predictions)
    print(f"\n[TEST] Stored {stats['stored']} predictions")
    
    # Test market snapshot
    test_markets = pd.DataFrame([
        {
            'symbol': 'AAPL',
            'sector': 'Technology',
            'price': 175.50,
            'volume': 50000000,
            'market_cap': 2800000000000
        },
        {
            'symbol': 'MSFT',
            'sector': 'Technology',
            'price': 380.00,
            'volume': 30000000,
            'market_cap': 2900000000000
        }
    ])
    
    market_path = storage.store_market_snapshot(test_markets)
    print(f"[TEST] Stored market snapshot: {market_path}")
    
    # Test analytics
    report = storage.get_analytics_report()
    print(f"\n[TEST] Analytics Report:")
    print(f"  Portfolio trades: {report.get('portfolio', {}).get('total_trades', 0)}")
    
    # Get storage stats
    storage_stats = storage.get_storage_stats()
    print(f"\n[TEST] Storage Stats:")
    print(f"  Base path: {storage_stats['base_path']}")
    print(f"  Total symbols: {storage_stats['trades']['total_symbols']}")
    print(f"  Total size: {storage_stats['trades']['total_size_mb']} MB")

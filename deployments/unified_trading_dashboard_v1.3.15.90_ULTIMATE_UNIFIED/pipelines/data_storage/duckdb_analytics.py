"""
DuckDB Analytics Engine

Blazing-fast SQL analytics on Parquet files
- 10-50x faster than pandas for large datasets
- SQL interface for complex queries
- Seamless Parquet integration
- In-memory or persistent database

Inspired by Jon Becker's prediction market analysis framework
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import date, datetime
import pandas as pd
import duckdb

logger = logging.getLogger(__name__)


class DuckDBAnalyticsEngine:
    """
    High-performance SQL analytics engine for trade data
    
    Features:
    - Query Parquet files directly (no loading required)
    - 100x faster than pandas for aggregations
    - Full SQL support (joins, window functions, CTEs)
    - Parallel query execution
    - Memory-efficient streaming
    """
    
    def __init__(
        self,
        trade_data_path: Union[str, Path] = 'data/trades',
        market_data_path: Union[str, Path] = 'data/markets',
        database_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize DuckDB analytics engine
        
        Args:
            trade_data_path: Path to Parquet trade data
            market_data_path: Path to Parquet market data
            database_path: Path for persistent database (None for in-memory)
        """
        self.trade_data_path = Path(trade_data_path)
        self.market_data_path = Path(market_data_path)
        
        # Create DuckDB connection (in-memory or persistent)
        if database_path:
            self.con = duckdb.connect(str(database_path))
            logger.info(f"[OK] DuckDB connected to database: {database_path}")
        else:
            self.con = duckdb.connect(':memory:')
            logger.info(f"[OK] DuckDB in-memory database created")
        
        # Configure DuckDB for optimal performance
        self.con.execute("SET threads TO 4")  # Use 4 threads for parallel queries
        self.con.execute("SET memory_limit = '4GB'")  # Set memory limit
        
        logger.info(f"[OK] DuckDB Analytics Engine initialized")
        logger.info(f"     Trade data: {self.trade_data_path}")
        logger.info(f"     Market data: {self.market_data_path}")
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            sql: SQL query string
        
        Returns:
            DataFrame with query results
        """
        try:
            result = self.con.execute(sql).df()
            logger.debug(f"[OK] Query executed: {len(result)} rows returned")
            return result
        except Exception as e:
            logger.error(f"[ERROR] Query failed: {e}")
            logger.error(f"SQL: {sql}")
            raise
    
    def execute(self, sql: str) -> None:
        """
        Execute SQL statement without returning results
        
        Args:
            sql: SQL statement
        """
        try:
            self.con.execute(sql)
            logger.debug(f"[OK] SQL executed successfully")
        except Exception as e:
            logger.error(f"[ERROR] SQL execution failed: {e}")
            raise
    
    # ========================================================================
    # MAKER/TAKER ANALYSIS (Jon Becker Research Replication)
    # ========================================================================
    
    def analyze_maker_taker_returns(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Analyze maker vs taker returns (replicates Kalshi research)
        
        Returns average excess returns by role and price level
        Like Figure 3 in the research paper
        
        Args:
            symbol: Filter by symbol (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            DataFrame with maker/taker returns by price level
        """
        symbol_filter = f"AND symbol = '{symbol}'" if symbol else ""
        date_filter = ""
        if start_date:
            date_filter += f"AND timestamp >= '{start_date}' "
        if end_date:
            date_filter += f"AND timestamp <= '{end_date}' "
        
        query = f"""
        WITH price_buckets AS (
            SELECT 
                CAST(FLOOR(cost_basis / 10) * 10 AS INTEGER) AS price_bucket,
                role,
                pnl,
                cost_basis,
                CASE 
                    WHEN pnl > 0 THEN 1.0 
                    ELSE 0.0 
                END AS won,
                (pnl / cost_basis) * 100 AS return_pct
            FROM read_parquet('{self.trade_data_path}/**/*.parquet')
            WHERE cost_basis BETWEEN 1 AND 99
              AND role IN ('maker', 'taker')
              {symbol_filter}
              {date_filter}
        )
        SELECT 
            price_bucket,
            role,
            COUNT(*) AS trade_count,
            AVG(return_pct) AS avg_return,
            AVG(won) AS win_rate,
            STDDEV(return_pct) AS return_std,
            MIN(return_pct) AS min_return,
            MAX(return_pct) AS max_return
        FROM price_buckets
        GROUP BY price_bucket, role
        ORDER BY price_bucket, role
        """
        
        return self.query(query)
    
    def analyze_longshot_bias(
        self,
        symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Analyze longshot bias (replicates Kalshi research finding)
        
        Compares actual win rate to implied probability by price level
        Research finding: 1-cent contracts win only 0.43% vs 1% implied
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            DataFrame with actual vs implied probabilities
        """
        symbol_filter = f"WHERE symbol = '{symbol}'" if symbol else ""
        
        query = f"""
        WITH price_analysis AS (
            SELECT 
                CAST(cost_basis AS INTEGER) AS price,
                CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END AS won,
                cost_basis / 100.0 AS implied_prob
            FROM read_parquet('{self.trade_data_path}/**/*.parquet')
            {symbol_filter}
            {'AND' if symbol else 'WHERE'} cost_basis BETWEEN 1 AND 99
        )
        SELECT 
            price,
            COUNT(*) AS trade_count,
            AVG(won) AS actual_win_rate,
            AVG(implied_prob) AS implied_prob,
            AVG(won) - AVG(implied_prob) AS mispricing,
            (AVG(won) - AVG(implied_prob)) / AVG(implied_prob) * 100 AS mispricing_pct
        FROM price_analysis
        GROUP BY price
        HAVING COUNT(*) >= 10
        ORDER BY price
        """
        
        return self.query(query)
    
    def analyze_category_efficiency(self) -> pd.DataFrame:
        """
        Calculate maker-taker gap by category (replicates research Table 1)
        
        Research finding:
        - Finance: 0.17 pp gap (highly efficient)
        - Sports: 2.23 pp gap
        - Entertainment: 4.79 pp gap (highly inefficient)
        
        Returns:
            DataFrame with efficiency metrics by category
        """
        query = f"""
        WITH category_returns AS (
            SELECT 
                m.sector AS category,
                t.role,
                (t.pnl / t.cost_basis) * 100 AS return_pct,
                t.cost_basis
            FROM read_parquet('{self.trade_data_path}/**/*.parquet') t
            LEFT JOIN read_parquet('{self.market_data_path}/**/*.parquet') m
                ON t.symbol = m.symbol
            WHERE t.role IN ('maker', 'taker')
              AND t.cost_basis BETWEEN 1 AND 99
              AND m.sector IS NOT NULL
        )
        SELECT 
            category,
            COUNT(*) AS trade_count,
            AVG(CASE WHEN role = 'taker' THEN return_pct END) AS taker_return,
            AVG(CASE WHEN role = 'maker' THEN return_pct END) AS maker_return,
            AVG(CASE WHEN role = 'maker' THEN return_pct END) - 
            AVG(CASE WHEN role = 'taker' THEN return_pct END) AS gap,
            STDDEV(CASE WHEN role = 'taker' THEN return_pct END) AS taker_std,
            STDDEV(CASE WHEN role = 'maker' THEN return_pct END) AS maker_std
        FROM category_returns
        GROUP BY category
        HAVING COUNT(*) >= 100
        ORDER BY gap DESC
        """
        
        return self.query(query)
    
    def analyze_yes_no_asymmetry(self) -> pd.DataFrame:
        """
        Analyze YES/NO asymmetry (bullish vs bearish bias)
        
        Research finding: YES contracts underperform NO contracts by 1.85 pp
        "Optimism Tax" - retail traders overpay for bullish outcomes
        
        Returns:
            DataFrame comparing YES (buy) vs NO (sell) performance
        """
        query = f"""
        WITH side_returns AS (
            SELECT 
                side,
                cost_basis,
                CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END AS won,
                (pnl / cost_basis) * 100 AS return_pct
            FROM read_parquet('{self.trade_data_path}/**/*.parquet')
            WHERE cost_basis BETWEEN 1 AND 99
              AND side IN ('buy', 'sell')
        )
        SELECT 
            side,
            CAST(FLOOR(cost_basis / 10) * 10 AS INTEGER) AS price_bucket,
            COUNT(*) AS trade_count,
            AVG(return_pct) AS avg_return,
            AVG(won) AS win_rate,
            STDDEV(return_pct) AS return_std
        FROM side_returns
        GROUP BY side, price_bucket
        ORDER BY price_bucket, side
        """
        
        return self.query(query)
    
    # ========================================================================
    # TEMPORAL ANALYSIS
    # ========================================================================
    
    def analyze_temporal_evolution(
        self,
        symbol: str,
        window_days: int = 30
    ) -> pd.DataFrame:
        """
        Analyze how market efficiency changes over time
        
        Replicates research finding: Markets become more efficient as volume grows
        Like Kalshi's evolution from taker-favorable to maker-favorable
        
        Args:
            symbol: Stock symbol
            window_days: Rolling window in days
        
        Returns:
            DataFrame with temporal efficiency metrics
        """
        query = f"""
        WITH daily_stats AS (
            SELECT 
                DATE_TRUNC('day', timestamp) AS date,
                role,
                COUNT(*) AS trade_count,
                SUM(volume) AS total_volume,
                AVG(spread) AS avg_spread,
                AVG((pnl / cost_basis) * 100) AS avg_return
            FROM read_parquet('{self.trade_data_path}/symbol={symbol}/**/*.parquet')
            WHERE role IN ('maker', 'taker')
            GROUP BY date, role
        )
        SELECT 
            date,
            role,
            trade_count,
            total_volume,
            avg_spread,
            avg_return,
            AVG(avg_return) OVER (
                PARTITION BY role 
                ORDER BY date 
                ROWS BETWEEN {window_days} PRECEDING AND CURRENT ROW
            ) AS rolling_avg_return,
            AVG(avg_spread) OVER (
                PARTITION BY role 
                ORDER BY date 
                ROWS BETWEEN {window_days} PRECEDING AND CURRENT ROW
            ) AS rolling_avg_spread
        FROM daily_stats
        ORDER BY date, role
        """
        
        return self.query(query)
    
    # ========================================================================
    # PERFORMANCE METRICS
    # ========================================================================
    
    def get_portfolio_performance(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            symbol: Filter by symbol (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            Dict with performance metrics
        """
        symbol_filter = f"AND symbol = '{symbol}'" if symbol else ""
        date_filter = ""
        if start_date:
            date_filter += f"AND timestamp >= '{start_date}' "
        if end_date:
            date_filter += f"AND timestamp <= '{end_date}' "
        
        query = f"""
        SELECT 
            COUNT(*) AS total_trades,
            SUM(volume) AS total_volume,
            SUM(pnl) AS total_pnl,
            AVG(pnl) AS avg_pnl_per_trade,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS win_rate,
            MAX(pnl) AS best_trade,
            MIN(pnl) AS worst_trade,
            STDDEV(pnl) AS pnl_std,
            AVG(fees) AS avg_fees,
            SUM(fees) AS total_fees
        FROM read_parquet('{self.trade_data_path}/**/*.parquet')
        WHERE 1=1
          {symbol_filter}
          {date_filter}
        """
        
        result = self.query(query)
        return result.iloc[0].to_dict() if len(result) > 0 else {}
    
    def get_top_performers(
        self,
        metric: str = 'total_pnl',
        limit: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get top performing symbols
        
        Args:
            metric: Metric to rank by ('total_pnl', 'win_rate', 'avg_return')
            limit: Number of top symbols to return
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            DataFrame with top performers
        """
        date_filter = ""
        if start_date:
            date_filter += f"AND timestamp >= '{start_date}' "
        if end_date:
            date_filter += f"AND timestamp <= '{end_date}' "
        
        query = f"""
        SELECT 
            symbol,
            COUNT(*) AS trade_count,
            SUM(pnl) AS total_pnl,
            AVG(pnl) AS avg_pnl,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS win_rate,
            AVG((pnl / cost_basis) * 100) AS avg_return
        FROM read_parquet('{self.trade_data_path}/**/*.parquet')
        WHERE 1=1
          {date_filter}
        GROUP BY symbol
        HAVING COUNT(*) >= 5
        ORDER BY {metric} DESC
        LIMIT {limit}
        """
        
        return self.query(query)
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def get_trade_count(self, symbol: Optional[str] = None) -> int:
        """Get total number of trades"""
        symbol_filter = f"WHERE symbol = '{symbol}'" if symbol else ""
        query = f"""
        SELECT COUNT(*) AS count
        FROM read_parquet('{self.trade_data_path}/**/*.parquet')
        {symbol_filter}
        """
        result = self.query(query)
        return int(result.iloc[0]['count']) if len(result) > 0 else 0
    
    def get_available_dates(self, symbol: str) -> List[str]:
        """Get list of dates with trade data for a symbol"""
        query = f"""
        SELECT DISTINCT DATE_TRUNC('day', timestamp) AS date
        FROM read_parquet('{self.trade_data_path}/symbol={symbol}/**/*.parquet')
        ORDER BY date DESC
        """
        result = self.query(query)
        return [str(d.date()) for d in result['date'].tolist()]
    
    def close(self):
        """Close DuckDB connection"""
        self.con.close()
        logger.info("[OK] DuckDB connection closed")


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Initialize analytics engine
    engine = DuckDBAnalyticsEngine(
        trade_data_path='data/test_trades',
        market_data_path='data/test_markets'
    )
    
    print("\n=== TRADE COUNT ===")
    count = engine.get_trade_count()
    print(f"Total trades: {count:,}")
    
    print("\n=== MAKER/TAKER ANALYSIS ===")
    maker_taker = engine.analyze_maker_taker_returns()
    print(maker_taker.head(20))
    
    print("\n=== PORTFOLIO PERFORMANCE ===")
    perf = engine.get_portfolio_performance()
    for key, value in perf.items():
        print(f"{key}: {value}")
    
    engine.close()

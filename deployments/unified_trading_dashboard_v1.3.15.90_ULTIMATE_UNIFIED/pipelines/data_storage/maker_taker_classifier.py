"""
Maker/Taker Classifier

Classify every trade as maker (passive liquidity) or taker (aggressive)
Critical for understanding market microstructure and identifying edge

Based on Jon Becker's research:
- Makers earn +1.12% average excess return
- Takers lose -1.12% average excess return
- The gap varies by category (Finance: 0.17 pp, Entertainment: 4.79 pp)
"""

import logging
from typing import Dict, Literal
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MakerTakerClassifier:
    """
    Classify trades into maker (passive) vs taker (aggressive) categories
    
    Classification Rules:
    1. Market orders → TAKER
    2. Limit orders that cross the spread → TAKER
    3. Limit orders that rest on the book → MAKER
    4. Midpoint fills → Ambiguous (rare, default to MAKER)
    
    Research findings (Kalshi):
    - Makers win 80 of 99 price levels
    - Takers systematically overpay for "YES" (bullish) outcomes
    - Gap largest in emotional categories (Sports, Entertainment)
    """
    
    Role = Literal['maker', 'taker', 'unknown']
    
    def __init__(self):
        """Initialize classifier"""
        self.classification_count = {'maker': 0, 'taker': 0, 'unknown': 0}
        logger.info("[OK] Maker/Taker Classifier initialized")
    
    def classify_trade(
        self,
        order_type: str,
        price: float,
        bid: float,
        ask: float,
        was_on_book: bool = False
    ) -> Role:
        """
        Classify a single trade
        
        Args:
            order_type: 'market' or 'limit'
            price: Executed price
            bid: Best bid at execution
            ask: Best ask at execution
            was_on_book: Whether order was resting on book
        
        Returns:
            'maker', 'taker', or 'unknown'
        """
        # Market orders are always takers
        if order_type.lower() == 'market':
            self.classification_count['taker'] += 1
            return 'taker'
        
        # If we know it was resting on the book
        if was_on_book:
            self.classification_count['maker'] += 1
            return 'maker'
        
        # Classify limit orders by price position
        if order_type.lower() == 'limit':
            # Crossed the spread (aggressive) → TAKER
            if price >= ask:  # Bought at or above ask
                self.classification_count['taker'] += 1
                return 'taker'
            elif price <= bid:  # Sold at or below bid
                self.classification_count['taker'] += 1
                return 'taker'
            
            # Between bid and ask (provided liquidity) → MAKER
            elif bid < price < ask:
                self.classification_count['maker'] += 1
                return 'maker'
            
            # At bid or ask (ambiguous, default to maker)
            elif price == bid or price == ask:
                self.classification_count['maker'] += 1
                return 'maker'
        
        # Unknown
        self.classification_count['unknown'] += 1
        return 'unknown'
    
    def classify_trades_df(
        self,
        trades_df: pd.DataFrame,
        order_type_col: str = 'order_type',
        price_col: str = 'price',
        bid_col: str = 'bid',
        ask_col: str = 'ask'
    ) -> pd.DataFrame:
        """
        Classify all trades in a DataFrame
        
        Args:
            trades_df: DataFrame with trade data
            order_type_col: Name of order type column
            price_col: Name of price column
            bid_col: Name of bid column
            ask_col: Name of ask column
        
        Returns:
            DataFrame with 'role' column added
        """
        trades_df = trades_df.copy()
        
        # Vectorized classification for speed
        trades_df['role'] = 'unknown'
        
        # Market orders → taker
        market_mask = trades_df[order_type_col].str.lower() == 'market'
        trades_df.loc[market_mask, 'role'] = 'taker'
        
        # Limit orders
        limit_mask = trades_df[order_type_col].str.lower() == 'limit'
        
        # Crossed spread → taker
        crossed_buy = (trades_df[price_col] >= trades_df[ask_col]) & limit_mask
        crossed_sell = (trades_df[price_col] <= trades_df[bid_col]) & limit_mask
        trades_df.loc[crossed_buy | crossed_sell, 'role'] = 'taker'
        
        # Between bid/ask → maker
        inside_spread = (
            (trades_df[price_col] > trades_df[bid_col]) &
            (trades_df[price_col] < trades_df[ask_col]) &
            limit_mask
        )
        trades_df.loc[inside_spread, 'role'] = 'maker'
        
        # At bid or ask → maker (default)
        at_quote = (
            ((trades_df[price_col] == trades_df[bid_col]) |
             (trades_df[price_col] == trades_df[ask_col])) &
            limit_mask
        )
        trades_df.loc[at_quote, 'role'] = 'maker'
        
        # Update counts
        role_counts = trades_df['role'].value_counts().to_dict()
        for role, count in role_counts.items():
            if role in self.classification_count:
                self.classification_count[role] += count
        
        logger.info(f"[OK] Classified {len(trades_df)} trades")
        logger.info(f"     Makers: {(trades_df['role'] == 'maker').sum()} ({(trades_df['role'] == 'maker').sum() / len(trades_df) * 100:.1f}%)")
        logger.info(f"     Takers: {(trades_df['role'] == 'taker').sum()} ({(trades_df['role'] == 'taker').sum() / len(trades_df) * 100:.1f}%)")
        
        return trades_df
    
    def get_statistics(self) -> Dict:
        """
        Get classification statistics
        
        Returns:
            Dict with classification counts and percentages
        """
        total = sum(self.classification_count.values())
        
        if total == 0:
            return self.classification_count
        
        return {
            'maker_count': self.classification_count['maker'],
            'taker_count': self.classification_count['taker'],
            'unknown_count': self.classification_count['unknown'],
            'total': total,
            'maker_pct': self.classification_count['maker'] / total * 100,
            'taker_pct': self.classification_count['taker'] / total * 100,
            'unknown_pct': self.classification_count['unknown'] / total * 100
        }
    
    def calculate_maker_taker_performance(
        self,
        trades_df: pd.DataFrame,
        pnl_col: str = 'pnl',
        cost_basis_col: str = 'cost_basis'
    ) -> Dict:
        """
        Calculate performance metrics by role
        
        Replicates research findings:
        - Maker avg return: +1.12%
        - Taker avg return: -1.12%
        - Gap: 2.24 percentage points
        
        Args:
            trades_df: DataFrame with classified trades
            pnl_col: Name of P&L column
            cost_basis_col: Name of cost basis column
        
        Returns:
            Dict with performance metrics by role
        """
        # Ensure trades are classified
        if 'role' not in trades_df.columns:
            logger.warning("[WARNING] Trades not classified, classifying now...")
            trades_df = self.classify_trades_df(trades_df)
        
        # Calculate returns
        trades_df['return_pct'] = (trades_df[pnl_col] / trades_df[cost_basis_col]) * 100
        trades_df['won'] = trades_df[pnl_col] > 0
        
        # Aggregate by role
        maker_trades = trades_df[trades_df['role'] == 'maker']
        taker_trades = trades_df[trades_df['role'] == 'taker']
        
        def calc_metrics(df):
            if len(df) == 0:
                return {
                    'count': 0,
                    'avg_return': 0.0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0,
                    'avg_pnl': 0.0,
                    'return_std': 0.0
                }
            
            return {
                'count': len(df),
                'avg_return': df['return_pct'].mean(),
                'win_rate': df['won'].mean() * 100,
                'total_pnl': df[pnl_col].sum(),
                'avg_pnl': df[pnl_col].mean(),
                'return_std': df['return_pct'].std()
            }
        
        maker_metrics = calc_metrics(maker_trades)
        taker_metrics = calc_metrics(taker_trades)
        
        # Calculate gap
        return_gap = maker_metrics['avg_return'] - taker_metrics['avg_return']
        
        results = {
            'maker': maker_metrics,
            'taker': taker_metrics,
            'gap': {
                'return_gap': return_gap,
                'win_rate_gap': maker_metrics['win_rate'] - taker_metrics['win_rate'],
                'pnl_gap': maker_metrics['total_pnl'] - taker_metrics['total_pnl']
            }
        }
        
        logger.info(f"[OK] Maker/Taker Performance Analysis:")
        logger.info(f"     Maker return: {maker_metrics['avg_return']:+.2f}% (n={maker_metrics['count']})")
        logger.info(f"     Taker return: {taker_metrics['avg_return']:+.2f}% (n={taker_metrics['count']})")
        logger.info(f"     Gap: {return_gap:+.2f} pp")
        
        return results


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create sample trade data
    np.random.seed(42)
    n_trades = 10000
    
    sample_trades = pd.DataFrame({
        'timestamp': pd.date_range('2026-02-12', periods=n_trades, freq='1min'),
        'symbol': np.random.choice(['AAPL', 'MSFT', 'GOOGL'], n_trades),
        'price': np.random.uniform(100, 200, n_trades),
        'volume': np.random.randint(100, 10000, n_trades),
        'order_type': np.random.choice(['market', 'limit'], n_trades, p=[0.3, 0.7]),
        'bid': np.random.uniform(99, 199, n_trades),
        'ask': np.random.uniform(101, 201, n_trades),
    })
    
    # Ensure bid < ask
    sample_trades['bid'] = sample_trades[['bid', 'price']].min(axis=1) - 0.5
    sample_trades['ask'] = sample_trades[['ask', 'price']].max(axis=1) + 0.5
    
    # Add P&L (makers slightly positive, takers slightly negative)
    sample_trades['pnl'] = np.random.normal(0, 10, n_trades)
    sample_trades['cost_basis'] = sample_trades['price']
    
    # Initialize classifier
    classifier = MakerTakerClassifier()
    
    # Classify trades
    classified = classifier.classify_trades_df(sample_trades)
    
    # Calculate performance
    performance = classifier.calculate_maker_taker_performance(classified)
    
    print("\n=== CLASSIFICATION STATISTICS ===")
    stats = classifier.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== PERFORMANCE METRICS ===")
    print(f"Maker: {performance['maker']}")
    print(f"Taker: {performance['taker']}")
    print(f"Gap: {performance['gap']}")

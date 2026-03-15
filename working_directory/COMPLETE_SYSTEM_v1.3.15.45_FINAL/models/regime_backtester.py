#!/usr/bin/env python3
"""
Regime-Aware Backtesting Framework - Week 2 Features
Historical regime reconstruction and performance analysis

⚠️  WARNING: THIS IS A BACKTESTING/SIMULATION TOOL ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This tool uses simulated/random data for Monte Carlo analysis and testing.
DO NOT use this for live trading decisions.
Use REAL market data from yahoo finance/yfinance for production trading.

This is for STRATEGY TESTING and ANALYSIS ONLY.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Author: Trading System v1.3.13 - REGIME EDITION (Week 2)
Date: January 6, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from yahooquery import Ticker
    import pandas as pd
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logger.warning("Required packages not available")


class RegimeBacktester:
    """
    Backtesting framework for regime-aware trading strategies
    
    Features:
    - Historical regime reconstruction
    - Performance comparison (with vs. without regime)
    - Metrics by regime type
    - Regime transition analysis
    - Walk-forward validation
    """
    
    def __init__(self, start_date: str = "2023-01-01", end_date: str = "2025-12-31"):
        """
        Initialize backtester
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        self.start_date = start_date
        self.end_date = end_date
        self.results = {}
        
        logger.info("[OK] RegimeBacktester initialized")
        logger.info(f"   Period: {start_date} to {end_date}")
    
    def reconstruct_historical_regimes(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Reconstruct historical market regimes from price data
        
        Args:
            data: DataFrame with market data (sp500, nasdaq, oil, etc.)
            
        Returns:
            DataFrame with regime classifications added
        """
        logger.info("[~] Reconstructing historical regimes...")
        
        if data.empty:
            logger.warning("[!] No data provided")
            return data
        
        # Calculate returns
        data['sp500_return'] = data['sp500'].pct_change() * 100
        data['nasdaq_return'] = data['nasdaq'].pct_change() * 100
        data['oil_return'] = data['oil'].pct_change() * 100
        data['iron_ore_return'] = data.get('iron_ore', data['oil']).pct_change() * 100
        data['audusd_return'] = data.get('audusd', 1.0) if 'audusd' in data.columns else 0
        
        # Simple regime classification rules
        regimes = []
        for idx, row in data.iterrows():
            regime = self._classify_regime(row)
            regimes.append(regime)
        
        data['regime'] = regimes
        
        logger.info(f"[OK] Reconstructed {len(data)} days of regimes")
        logger.info(f"   Unique regimes: {data['regime'].nunique()}")
        
        return data
    
    def _classify_regime(self, row: pd.Series) -> str:
        """
        Classify market regime based on market conditions
        
        Args:
            row: Series with market returns
            
        Returns:
            Regime classification string
        """
        sp500_ret = row.get('sp500_return', 0)
        nasdaq_ret = row.get('nasdaq_return', 0)
        oil_ret = row.get('oil_return', 0)
        iron_ore_ret = row.get('iron_ore_return', 0)
        
        # Tech rally: NASDAQ > S&P and both positive
        if nasdaq_ret > sp500_ret and nasdaq_ret > 1.0 and sp500_ret > 0.5:
            return 'US_TECH_RISK_ON'
        
        # Commodity weakness: Oil and iron ore both down
        if oil_ret < -1.0 and iron_ore_ret < -1.0:
            return 'COMMODITY_WEAK'
        
        # Commodity strength: Oil and iron ore both up
        if oil_ret > 1.0 and iron_ore_ret > 1.0:
            return 'COMMODITY_STRONG'
        
        # Risk off: S&P and NASDAQ both down significantly
        if sp500_ret < -1.0 and nasdaq_ret < -1.0:
            return 'US_RISK_OFF'
        
        # Default: neutral
        return 'NEUTRAL'
    
    def backtest_strategy(
        self,
        stocks_data: Dict[str, pd.DataFrame],
        regime_data: pd.DataFrame,
        use_regime: bool = True,
        regime_weight: float = 0.4
    ) -> Dict:
        """
        Backtest trading strategy with or without regime intelligence
        
        Args:
            stocks_data: Dict of {symbol: DataFrame with OHLCV}
            regime_data: DataFrame with regime classifications
            use_regime: Whether to use regime-aware scoring
            regime_weight: Weight for regime component (0-1)
            
        Returns:
            Dict with backtest results
        """
        logger.info(f"[#] Backtesting strategy (regime={use_regime})...")
        
        trades = []
        portfolio_value = []
        initial_capital = 100000
        current_capital = initial_capital
        positions = {}
        
        # Merge regime data with stock data
        for date in regime_data.index:
            regime = regime_data.loc[date, 'regime'] if use_regime else 'NEUTRAL'
            
            # Score each stock
            stock_scores = {}
            for symbol, df in stocks_data.items():
                if date not in df.index:
                    continue
                
                # Base score (simplified momentum)
                price = df.loc[date, 'close']
                ma20 = df.loc[:date, 'close'].tail(20).mean()
                base_score = ((price - ma20) / ma20) * 100 if ma20 > 0 else 0
                
                # Regime adjustment
                if use_regime:
                    regime_adjustment = self._get_regime_adjustment(symbol, regime)
                    final_score = (base_score * (1 - regime_weight)) + (regime_adjustment * regime_weight * 100)
                else:
                    final_score = base_score
                
                stock_scores[symbol] = final_score
            
            # Select top stocks
            sorted_stocks = sorted(stock_scores.items(), key=lambda x: x[1], reverse=True)
            top_stocks = [s[0] for s in sorted_stocks[:3]]  # Top 3 stocks
            
            # Execute trades (simplified)
            for symbol in top_stocks:
                if symbol not in positions and current_capital > 10000:
                    # Buy
                    position_size = 10000
                    price = stocks_data[symbol].loc[date, 'close']
                    shares = position_size / price
                    positions[symbol] = {'shares': shares, 'entry_price': price, 'entry_date': date}
                    current_capital -= position_size
                    
                    trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares,
                        'regime': regime
                    })
            
            # Calculate portfolio value
            portfolio_val = current_capital
            for symbol, pos in positions.items():
                if date in stocks_data[symbol].index:
                    current_price = stocks_data[symbol].loc[date, 'close']
                    portfolio_val += pos['shares'] * current_price
            
            portfolio_value.append({
                'date': date,
                'value': portfolio_val,
                'regime': regime
            })
        
        # Calculate metrics
        final_value = portfolio_value[-1]['value'] if portfolio_value else initial_capital
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        # Calculate by regime
        regime_performance = self._calculate_regime_performance(portfolio_value)
        
        results = {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'num_trades': len(trades),
            'trades': trades,
            'portfolio_value': portfolio_value,
            'regime_performance': regime_performance,
            'use_regime': use_regime,
            'regime_weight': regime_weight if use_regime else 0.0
        }
        
        logger.info(f"[OK] Backtest complete: {total_return:+.2f}% return, {len(trades)} trades")
        
        return results
    
    def _get_regime_adjustment(self, symbol: str, regime: str) -> float:
        """
        Get regime adjustment for a stock based on its sector
        
        Args:
            symbol: Stock symbol
            regime: Current regime
            
        Returns:
            Adjustment factor (-1 to +1)
        """
        # Simplified sector mapping
        sector_map = {
            'BHP.AX': 'Materials',
            'RIO.AX': 'Materials',
            'FMG.AX': 'Materials',
            'CBA.AX': 'Financials',
            'NAB.AX': 'Financials',
            'CSL.AX': 'Healthcare',
            'WOW.AX': 'Consumer',
        }
        
        sector = sector_map.get(symbol, 'Unknown')
        
        # Regime impact by sector
        regime_impacts = {
            'US_TECH_RISK_ON': {
                'Materials': -0.5,
                'Financials': -0.3,
                'Healthcare': 0.2,
                'Consumer': 0.0
            },
            'COMMODITY_WEAK': {
                'Materials': -1.0,
                'Financials': -0.3,
                'Healthcare': 0.1,
                'Consumer': 0.0
            },
            'COMMODITY_STRONG': {
                'Materials': 1.0,
                'Financials': 0.3,
                'Healthcare': -0.1,
                'Consumer': 0.0
            },
            'US_RISK_OFF': {
                'Materials': -0.7,
                'Financials': -0.8,
                'Healthcare': 0.3,
                'Consumer': -0.2
            },
            'NEUTRAL': {
                'Materials': 0.0,
                'Financials': 0.0,
                'Healthcare': 0.0,
                'Consumer': 0.0
            }
        }
        
        return regime_impacts.get(regime, {}).get(sector, 0.0)
    
    def _calculate_regime_performance(self, portfolio_value: List[Dict]) -> Dict:
        """
        Calculate performance metrics by regime
        
        Args:
            portfolio_value: List of {date, value, regime}
            
        Returns:
            Dict with performance by regime
        """
        if not portfolio_value:
            return {}
        
        df = pd.DataFrame(portfolio_value)
        df['return'] = df['value'].pct_change() * 100
        
        regime_stats = {}
        for regime in df['regime'].unique():
            regime_data = df[df['regime'] == regime]
            
            if len(regime_data) > 1:
                regime_stats[regime] = {
                    'days': len(regime_data),
                    'avg_return': regime_data['return'].mean(),
                    'total_return': regime_data['return'].sum(),
                    'win_rate': (regime_data['return'] > 0).sum() / len(regime_data) * 100,
                    'best_day': regime_data['return'].max(),
                    'worst_day': regime_data['return'].min()
                }
        
        return regime_stats
    
    def compare_strategies(
        self,
        stocks_data: Dict[str, pd.DataFrame],
        regime_data: pd.DataFrame
    ) -> Dict:
        """
        Compare regime-aware vs. basic strategy
        
        Args:
            stocks_data: Dict of {symbol: DataFrame with OHLCV}
            regime_data: DataFrame with regime classifications
            
        Returns:
            Dict with comparison results
        """
        logger.info("[#] Comparing strategies...")
        
        # Backtest without regime
        basic_results = self.backtest_strategy(
            stocks_data,
            regime_data,
            use_regime=False
        )
        
        # Backtest with regime
        regime_results = self.backtest_strategy(
            stocks_data,
            regime_data,
            use_regime=True,
            regime_weight=0.4
        )
        
        # Calculate improvements
        comparison = {
            'basic': {
                'total_return': basic_results['total_return'],
                'num_trades': basic_results['num_trades'],
                'final_value': basic_results['final_value']
            },
            'regime_aware': {
                'total_return': regime_results['total_return'],
                'num_trades': regime_results['num_trades'],
                'final_value': regime_results['final_value']
            },
            'improvement': {
                'return_diff': regime_results['total_return'] - basic_results['total_return'],
                'return_pct_improvement': ((regime_results['total_return'] - basic_results['total_return']) / 
                                          abs(basic_results['total_return']) * 100) if basic_results['total_return'] != 0 else 0
            },
            'regime_performance': regime_results['regime_performance']
        }
        
        logger.info(f"[OK] Comparison complete:")
        logger.info(f"   Basic: {basic_results['total_return']:+.2f}%")
        logger.info(f"   Regime-Aware: {regime_results['total_return']:+.2f}%")
        logger.info(f"   Improvement: {comparison['improvement']['return_diff']:+.2f}%")
        
        return comparison
    
    def generate_report(self, comparison: Dict) -> str:
        """
        Generate human-readable backtest report
        
        Args:
            comparison: Comparison results from compare_strategies()
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("\n" + "="*80)
        lines.append("BACKTESTING REPORT - REGIME-AWARE STRATEGY")
        lines.append("="*80)
        
        # Basic strategy
        basic = comparison['basic']
        lines.append(f"\n[#] BASIC STRATEGY (No Regime Intelligence):")
        lines.append(f"   Total Return: {basic['total_return']:+.2f}%")
        lines.append(f"   Final Value: ${basic['final_value']:,.2f}")
        lines.append(f"   Number of Trades: {basic['num_trades']}")
        
        # Regime-aware strategy
        regime = comparison['regime_aware']
        lines.append(f"\n🧠 REGIME-AWARE STRATEGY (40% Regime Weight):")
        lines.append(f"   Total Return: {regime['total_return']:+.2f}%")
        lines.append(f"   Final Value: ${regime['final_value']:,.2f}")
        lines.append(f"   Number of Trades: {regime['num_trades']}")
        
        # Improvement
        improvement = comparison['improvement']
        lines.append(f"\n✨ IMPROVEMENT:")
        lines.append(f"   Return Difference: {improvement['return_diff']:+.2f}%")
        lines.append(f"   Percentage Improvement: {improvement['return_pct_improvement']:+.2f}%")
        
        # Performance by regime
        if 'regime_performance' in comparison and comparison['regime_performance']:
            lines.append(f"\n[UP] PERFORMANCE BY REGIME:")
            for regime_name, stats in comparison['regime_performance'].items():
                lines.append(f"\n   {regime_name}:")
                lines.append(f"      Days: {stats['days']}")
                lines.append(f"      Avg Return: {stats['avg_return']:+.2f}%")
                lines.append(f"      Total Return: {stats['total_return']:+.2f}%")
                lines.append(f"      Win Rate: {stats['win_rate']:.1f}%")
                lines.append(f"      Best Day: {stats['best_day']:+.2f}%")
                lines.append(f"      Worst Day: {stats['worst_day']:+.2f}%")
        
        lines.append("\n" + "="*80)
        lines.append(f"Backtest Period: {self.start_date} to {self.end_date}")
        lines.append("="*80 + "\n")
        
        return "\n".join(lines)


def test_backtester():
    """Test backtesting framework"""
    
    print("\n" + "="*80)
    print("TESTING REGIME-AWARE BACKTESTING FRAMEWORK")
    print("="*80)
    
    if not DEPENDENCIES_AVAILABLE:
        print("[X] Required packages not available")
        return
    
    # Create backtester
    backtester = RegimeBacktester(
        start_date="2024-01-01",
        end_date="2025-12-31"
    )
    
    # Generate sample data (simplified for testing)
    dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='D')
    
    # Sample market data
    np.random.seed(42)
    market_data = pd.DataFrame({
        'sp500': 4500 + np.cumsum(np.random.randn(len(dates)) * 20),
        'nasdaq': 14000 + np.cumsum(np.random.randn(len(dates)) * 50),
        'oil': 80 + np.cumsum(np.random.randn(len(dates)) * 2),
        'iron_ore': 100 + np.cumsum(np.random.randn(len(dates)) * 3)
    }, index=dates)
    
    # Reconstruct regimes
    regime_data = backtester.reconstruct_historical_regimes(market_data)
    
    # Sample stock data
    stocks_data = {}
    for symbol in ['BHP.AX', 'CBA.AX', 'CSL.AX', 'RIO.AX']:
        stocks_data[symbol] = pd.DataFrame({
            'close': 30 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'volume': 1000000 + np.random.randint(-100000, 100000, len(dates))
        }, index=dates)
    
    # Compare strategies
    comparison = backtester.compare_strategies(stocks_data, regime_data)
    
    # Generate report
    report = backtester.generate_report(comparison)
    print(report)
    
    return comparison


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_backtester()

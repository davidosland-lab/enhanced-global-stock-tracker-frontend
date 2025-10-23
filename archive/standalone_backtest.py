#!/usr/bin/env python3
"""
Standalone Backtesting Script - Run completely on your local computer
No API needed - this runs everything locally
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

class LocalBacktester:
    """Standalone backtester that runs entirely on your local machine"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.results = []
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        print(f"📥 Fetching data for {symbol}...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        print(f"✅ Fetched {len(data)} days of data")
        return data
    
    def calculate_signals(self, data: pd.DataFrame, strategy: str = "sma_crossover") -> pd.DataFrame:
        """Generate trading signals based on strategy"""
        df = data.copy()
        
        if strategy == "sma_crossover":
            # Simple Moving Average Crossover
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            
            # Generate signals
            df['Signal'] = 0
            df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1
            df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1
            
        elif strategy == "rsi_oversold":
            # RSI Oversold/Overbought
            df['RSI'] = self.calculate_rsi(df['Close'])
            
            df['Signal'] = 0
            df.loc[df['RSI'] < 30, 'Signal'] = 1  # Buy when oversold
            df.loc[df['RSI'] > 70, 'Signal'] = -1  # Sell when overbought
            
        elif strategy == "momentum":
            # Momentum strategy
            df['Returns'] = df['Close'].pct_change()
            df['Momentum'] = df['Returns'].rolling(10).mean()
            
            df['Signal'] = 0
            df.loc[df['Momentum'] > 0.01, 'Signal'] = 1
            df.loc[df['Momentum'] < -0.01, 'Signal'] = -1
        
        return df
    
    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy: str = "sma_crossover"
    ) -> Dict[str, Any]:
        """
        Run a complete backtest
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy: Trading strategy to use
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 RUNNING BACKTEST FOR {symbol}")
        print(f"Strategy: {strategy}")
        print(f"Period: {start_date} to {end_date}")
        print('='*60)
        
        # Fetch data
        data = self.fetch_data(symbol, start_date, end_date)
        
        if data.empty:
            print("❌ No data available")
            return {}
        
        # Generate signals
        data = self.calculate_signals(data, strategy)
        
        # Initialize variables
        position = 0
        cash = self.initial_capital
        portfolio_value = []
        trades = []
        
        # Simulate trading
        for i in range(len(data)):
            current_price = data['Close'].iloc[i]
            signal = data['Signal'].iloc[i] if 'Signal' in data.columns else 0
            
            # Execute trades
            if signal == 1 and position == 0:  # Buy signal
                shares = cash / current_price
                position = shares
                cash = 0
                trades.append({
                    'Date': data.index[i],
                    'Type': 'BUY',
                    'Price': current_price,
                    'Shares': shares
                })
                
            elif signal == -1 and position > 0:  # Sell signal
                cash = position * current_price
                trades.append({
                    'Date': data.index[i],
                    'Type': 'SELL',
                    'Price': current_price,
                    'Shares': position
                })
                position = 0
            
            # Calculate portfolio value
            total_value = cash + (position * current_price)
            portfolio_value.append(total_value)
        
        # Calculate metrics
        final_value = portfolio_value[-1] if portfolio_value else self.initial_capital
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns for Sharpe ratio
        portfolio_series = pd.Series(portfolio_value, index=data.index)
        daily_returns = portfolio_series.pct_change().dropna()
        
        sharpe_ratio = 0
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
        
        # Maximum drawdown
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        
        # Win rate
        winning_trades = [t for t in trades if t['Type'] == 'SELL']
        win_count = 0
        
        for i, trade in enumerate(winning_trades):
            if i > 0:
                buy_price = trades[i*2-1]['Price']  # Previous buy
                sell_price = trade['Price']
                if sell_price > buy_price:
                    win_count += 1
        
        win_rate = win_count / len(winning_trades) if winning_trades else 0
        
        results = {
            'Symbol': symbol,
            'Strategy': strategy,
            'Start Date': start_date,
            'End Date': end_date,
            'Initial Capital': self.initial_capital,
            'Final Value': final_value,
            'Total Return': total_return,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Number of Trades': len(trades),
            'Win Rate': win_rate,
            'Portfolio Values': portfolio_series,
            'Trade History': trades
        }
        
        self.print_results(results)
        self.results.append(results)
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Pretty print backtest results"""
        print("\n📊 BACKTEST RESULTS")
        print("-"*40)
        print(f"Total Return: {results['Total Return']:.2%}")
        print(f"Final Value: ${results['Final Value']:,.2f}")
        print(f"Sharpe Ratio: {results['Sharpe Ratio']:.2f}")
        print(f"Max Drawdown: {results['Max Drawdown']:.2%}")
        print(f"Number of Trades: {results['Number of Trades']}")
        print(f"Win Rate: {results['Win Rate']:.2%}")
        
        # Risk assessment
        sharpe = results['Sharpe Ratio']
        if sharpe < 0.5:
            risk = "HIGH RISK"
        elif sharpe < 1.0:
            risk = "MEDIUM RISK"
        else:
            risk = "LOW RISK"
        
        print(f"\n⚠️ Risk Assessment: {risk}")
    
    def plot_results(self, results: Dict[str, Any]):
        """Plot backtest results"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Portfolio value over time
        portfolio = results['Portfolio Values']
        axes[0].plot(portfolio.index, portfolio.values, label='Portfolio Value', color='blue')
        axes[0].axhline(y=self.initial_capital, color='red', linestyle='--', label='Initial Capital')
        axes[0].set_title(f"Portfolio Performance - {results['Symbol']}")
        axes[0].set_ylabel('Portfolio Value ($)')
        axes[0].legend()
        axes[0].grid(True)
        
        # Drawdown
        returns = portfolio.pct_change()
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        axes[1].fill_between(drawdown.index, 0, drawdown.values * 100, color='red', alpha=0.3)
        axes[1].set_title('Drawdown')
        axes[1].set_ylabel('Drawdown (%)')
        axes[1].set_xlabel('Date')
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def compare_strategies(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategies: List[str] = None
    ):
        """Compare multiple strategies"""
        
        if strategies is None:
            strategies = ["sma_crossover", "rsi_oversold", "momentum"]
        
        comparison = []
        
        for strategy in strategies:
            result = self.run_backtest(symbol, start_date, end_date, strategy)
            comparison.append({
                'Strategy': strategy,
                'Return': result['Total Return'],
                'Sharpe': result['Sharpe Ratio'],
                'Max DD': result['Max Drawdown'],
                'Trades': result['Number of Trades']
            })
        
        # Print comparison table
        print("\n📊 STRATEGY COMPARISON")
        print("="*60)
        
        df = pd.DataFrame(comparison)
        print(df.to_string(index=False))
        
        # Find best strategy
        best = df.loc[df['Return'].idxmax()]
        print(f"\n🏆 Best Strategy: {best['Strategy']} with {best['Return']:.2%} return")


def main():
    """Example usage"""
    
    # Create backtester
    backtester = LocalBacktester(initial_capital=100000)
    
    # Example 1: Single backtest
    print("\n" + "="*60)
    print("EXAMPLE 1: SINGLE BACKTEST")
    print("="*60)
    
    result = backtester.run_backtest(
        symbol="AAPL",
        start_date="2023-01-01",
        end_date="2024-01-01",
        strategy="sma_crossover"
    )
    
    # Example 2: Compare strategies
    print("\n" + "="*60)
    print("EXAMPLE 2: STRATEGY COMPARISON")
    print("="*60)
    
    backtester.compare_strategies(
        symbol="MSFT",
        start_date="2023-01-01",
        end_date="2024-01-01"
    )
    
    # Example 3: Plot results (uncomment if you have matplotlib)
    # backtester.plot_results(result)
    
    print("\n✅ Backtesting complete!")


if __name__ == "__main__":
    main()
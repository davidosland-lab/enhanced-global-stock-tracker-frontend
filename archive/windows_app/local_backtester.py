"""
Local Backtesting Engine
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class LocalBacktester:
    """Run backtests locally on user's computer"""
    
    def __init__(self):
        self.results = []
        
    def run(self, symbol: str, start_date: str, end_date: str, 
            strategy: str, initial_capital: float) -> Dict[str, Any]:
        """Run a backtest"""
        
        logger.info(f"Running backtest for {symbol} from {start_date} to {end_date}")
        
        # Fetch historical data
        data = self.fetch_data(symbol, start_date, end_date)
        
        if data.empty:
            return {"error": "No data available"}
        
        # Generate trading signals based on strategy
        signals = self.generate_signals(data, strategy)
        
        # Run backtest simulation
        result = self.simulate_trading(data, signals, initial_capital)
        
        # Calculate metrics
        metrics = self.calculate_metrics(result, initial_capital)
        
        # Format trades for display
        trades = self.format_trades(result['trades'])
        
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "final_value": metrics['final_value'],
            "total_return": metrics['total_return'],
            "sharpe_ratio": metrics['sharpe_ratio'],
            "max_drawdown": metrics['max_drawdown'],
            "win_rate": metrics['win_rate'],
            "total_trades": metrics['total_trades'],
            "trades": trades,
            "portfolio_values": result['portfolio_values'],
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data"""
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        return data
    
    def generate_signals(self, data: pd.DataFrame, strategy: str) -> pd.Series:
        """Generate trading signals based on strategy"""
        
        if strategy == "Long Only" or strategy == "long_only":
            return self.long_only_signals(data)
        elif strategy == "Long/Short" or strategy == "long_short":
            return self.long_short_signals(data)
        elif strategy == "Mean Reversion":
            return self.mean_reversion_signals(data)
        elif strategy == "Momentum":
            return self.momentum_signals(data)
        elif strategy == "ML Signals":
            return self.ml_signals(data)
        else:
            return pd.Series(0, index=data.index)
    
    def long_only_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate long-only signals (SMA crossover)"""
        sma_20 = data['Close'].rolling(20).mean()
        sma_50 = data['Close'].rolling(50).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[sma_20 > sma_50] = 1
        
        return signals
    
    def long_short_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate long/short signals"""
        sma_20 = data['Close'].rolling(20).mean()
        sma_50 = data['Close'].rolling(50).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[sma_20 > sma_50] = 1
        signals[sma_20 < sma_50] = -1
        
        return signals
    
    def mean_reversion_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate mean reversion signals"""
        # Calculate z-score
        mean = data['Close'].rolling(20).mean()
        std = data['Close'].rolling(20).std()
        z_score = (data['Close'] - mean) / std
        
        signals = pd.Series(0, index=data.index)
        signals[z_score < -2] = 1  # Buy when oversold
        signals[z_score > 2] = -1  # Sell when overbought
        
        return signals
    
    def momentum_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate momentum signals"""
        returns = data['Close'].pct_change()
        momentum = returns.rolling(10).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[momentum > 0.001] = 1
        signals[momentum < -0.001] = -1
        
        return signals
    
    def ml_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate ML-based signals (simplified)"""
        # This would use trained models in practice
        # For now, use a combination of indicators
        
        rsi = self.calculate_rsi(data['Close'])
        macd = self.calculate_macd(data['Close'])
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when RSI < 30 and MACD positive
        signals[(rsi < 30) & (macd > 0)] = 1
        
        # Sell when RSI > 70 and MACD negative
        signals[(rsi > 70) & (macd < 0)] = -1
        
        return signals
    
    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, series: pd.Series) -> pd.Series:
        """Calculate MACD"""
        ema_12 = series.ewm(span=12).mean()
        ema_26 = series.ewm(span=26).mean()
        return ema_12 - ema_26
    
    def simulate_trading(self, data: pd.DataFrame, signals: pd.Series, 
                        initial_capital: float) -> Dict[str, Any]:
        """Simulate trading based on signals"""
        
        position = 0
        cash = initial_capital
        portfolio_values = []
        trades = []
        
        for i in range(len(data)):
            date = data.index[i]
            price = data['Close'].iloc[i]
            signal = signals.iloc[i] if i < len(signals) else 0
            
            # Execute trades based on signal
            if signal == 1 and position == 0:
                # Buy
                shares = cash / price
                position = shares
                cash = 0
                trades.append({
                    'date': date,
                    'type': 'BUY',
                    'price': price,
                    'shares': shares,
                    'value': shares * price
                })
                
            elif signal == -1 and position > 0:
                # Sell
                cash = position * price
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'shares': position,
                    'value': position * price
                })
                position = 0
            
            # Calculate portfolio value
            total_value = cash + (position * price if position > 0 else 0)
            portfolio_values.append(total_value)
        
        return {
            'portfolio_values': portfolio_values,
            'trades': trades,
            'final_position': position,
            'final_cash': cash
        }
    
    def calculate_metrics(self, result: Dict[str, Any], 
                         initial_capital: float) -> Dict[str, Any]:
        """Calculate backtest metrics"""
        
        portfolio_values = result['portfolio_values']
        trades = result['trades']
        
        # Calculate returns
        final_value = portfolio_values[-1] if portfolio_values else initial_capital
        total_return = (final_value - initial_capital) / initial_capital
        
        # Calculate daily returns
        returns = pd.Series(portfolio_values).pct_change().dropna()
        
        # Sharpe ratio
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        cumulative = pd.Series(portfolio_values) / initial_capital
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        
        # Win rate
        winning_trades = 0
        total_trades = 0
        
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_price = trades[i]['price']
                sell_price = trades[i + 1]['price']
                if sell_price > buy_price:
                    winning_trades += 1
                total_trades += 1
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(trades)
        }
    
    def format_trades(self, trades: List[Dict]) -> List[tuple]:
        """Format trades for display"""
        formatted = []
        
        for trade in trades:
            formatted.append((
                trade['date'].strftime('%Y-%m-%d'),
                trade['type'],
                "Stock",
                f"{trade['shares']:.2f}",
                f"${trade['price']:.2f}",
                ""  # P&L calculated later
            ))
        
        return formatted
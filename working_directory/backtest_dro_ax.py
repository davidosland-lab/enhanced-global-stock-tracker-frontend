"""
DRO.AX (Droneshield Limited) - 2 Year Backtest
==============================================
Testing the latest ML model decision-making on Australian defense stock
"""

import sys
import os
from datetime import datetime, timedelta
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest_dro_ax.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import yfinance for data
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YFINANCE_AVAILABLE = True
except ImportError:
    logger.warning("yfinance not available - install with: pip install yfinance")
    YFINANCE_AVAILABLE = False

# Try to import ML components
try:
    from ml_pipeline.swing_signal_generator import SwingSignalGenerator
    ML_AVAILABLE = True
    logger.info("✓ ML pipeline available")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"ML pipeline not available: {e}")

try:
    from phase3_intraday_deployment.paper_trading_coordinator import (
        PaperTradingCoordinator,
        Position,
        PositionType
    )
    COORDINATOR_AVAILABLE = True
    logger.info("✓ Paper trading coordinator available")
except ImportError as e:
    COORDINATOR_AVAILABLE = False
    logger.warning(f"Paper trading coordinator not available: {e}")


class DROBacktestEngine:
    """Backtest engine for DRO.AX using latest model"""
    
    def __init__(self, symbol='DRO.AX', initial_capital=100000.0):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.closed_positions = []
        self.trades = []
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.max_drawdown = 0.0
        self.peak_capital = initial_capital
        
        # ML Signal Generator (if available)
        if ML_AVAILABLE:
            try:
                self.signal_generator = SwingSignalGenerator()
                logger.info("✓ ML Signal Generator initialized")
            except Exception as e:
                logger.warning(f"Could not initialize signal generator: {e}")
                self.signal_generator = None
        else:
            self.signal_generator = None
    
    def fetch_historical_data(self, start_date, end_date):
        """Fetch historical price data for DRO.AX"""
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance not available - cannot fetch data")
            return None
        
        try:
            logger.info(f"Fetching {self.symbol} data from {start_date} to {end_date}...")
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty:
                logger.error(f"No data retrieved for {self.symbol}")
                return None
            
            logger.info(f"✓ Retrieved {len(df)} days of data")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def generate_signal(self, current_price, historical_data, current_date):
        """Generate trading signal using ML model or fallback logic"""
        
        if self.signal_generator and len(historical_data) >= 50:
            try:
                # Use ML signal generator
                signal = self.signal_generator.generate_signal(
                    symbol=self.symbol,
                    current_price=current_price,
                    historical_data=historical_data
                )
                return signal
            except Exception as e:
                logger.warning(f"ML signal generation failed: {e}, using fallback")
        
        # Fallback: Simple momentum + volume strategy
        return self._generate_fallback_signal(current_price, historical_data)
    
    def _generate_fallback_signal(self, current_price, historical_data):
        """Fallback signal generation using technical indicators"""
        
        if len(historical_data) < 50:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Calculate indicators
        df = historical_data.copy()
        
        # SMA crossover
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Volume trend
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Generate signal
        signal = {
            'action': 'HOLD',
            'confidence': 50,
            'reason': 'Neutral market conditions',
            'indicators': {
                'sma_20': float(latest['SMA_20']),
                'sma_50': float(latest['SMA_50']),
                'rsi': float(latest['RSI']),
                'volume_ratio': float(latest['Volume'] / latest['Volume_MA']) if latest['Volume_MA'] > 0 else 1.0
            }
        }
        
        # Buy signals
        buy_score = 0
        if latest['SMA_20'] > latest['SMA_50'] and prev['SMA_20'] <= prev['SMA_50']:
            buy_score += 30  # Golden cross
        if latest['RSI'] < 30:
            buy_score += 20  # Oversold
        if latest['Volume'] > latest['Volume_MA'] * 1.5:
            buy_score += 15  # High volume
        if current_price > latest['SMA_20']:
            buy_score += 10  # Above short-term MA
        
        # Sell signals
        sell_score = 0
        if latest['SMA_20'] < latest['SMA_50'] and prev['SMA_20'] >= prev['SMA_50']:
            sell_score += 30  # Death cross
        if latest['RSI'] > 70:
            sell_score += 20  # Overbought
        if current_price < latest['SMA_20']:
            sell_score += 15  # Below short-term MA
        
        if buy_score >= 40:
            signal['action'] = 'BUY'
            signal['confidence'] = min(buy_score, 85)
            signal['reason'] = f'Buy signals: score={buy_score}'
        elif sell_score >= 30:
            signal['action'] = 'SELL'
            signal['confidence'] = min(sell_score, 85)
            signal['reason'] = f'Sell signals: score={sell_score}'
        
        return signal
    
    def enter_position(self, date, price, signal):
        """Enter a trading position"""
        
        if self.symbol in self.positions:
            return False  # Already in position
        
        # Position sizing: 10% of capital (reduced for high volatility)
        position_size = 0.10
        position_value = self.current_capital * position_size
        shares = int(position_value / price)
        
        if shares < 1:
            return False
        
        cost = shares * price
        
        # Stop loss: 8% below entry (wider for volatile stock)
        stop_loss = price * 0.92
        
        # Take profit: 15% above entry (adjusted for high potential)
        take_profit = price * 1.15
        
        position = {
            'symbol': self.symbol,
            'entry_date': date,
            'entry_price': price,
            'shares': shares,
            'cost': cost,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signal': signal,
            'current_price': price,
            'unrealized_pnl': 0.0
        }
        
        self.positions[self.symbol] = position
        self.current_capital -= cost
        self.total_trades += 1
        
        logger.info(f"✓ POSITION OPENED: {date.strftime('%Y-%m-%d')} | {shares} shares @ ${price:.2f} | Stop: ${stop_loss:.2f} | Target: ${take_profit:.2f}")
        
        return True
    
    def update_position(self, date, current_price):
        """Update position with current price"""
        
        if self.symbol not in self.positions:
            return
        
        position = self.positions[self.symbol]
        position['current_price'] = current_price
        position['unrealized_pnl'] = (current_price - position['entry_price']) * position['shares']
    
    def check_exit(self, date, current_price):
        """Check if position should be exited"""
        
        if self.symbol not in self.positions:
            return False
        
        position = self.positions[self.symbol]
        
        # Check stop loss
        if current_price <= position['stop_loss']:
            self.exit_position(date, current_price, 'STOP_LOSS')
            return True
        
        # Check take profit
        if current_price >= position['take_profit']:
            self.exit_position(date, current_price, 'TAKE_PROFIT')
            return True
        
        # Check holding period (max 20 days for swing trades)
        days_held = (date - position['entry_date']).days
        if days_held >= 20:
            self.exit_position(date, current_price, 'TIME_EXIT')
            return True
        
        return False
    
    def exit_position(self, date, exit_price, reason):
        """Exit trading position"""
        
        if self.symbol not in self.positions:
            return
        
        position = self.positions[self.symbol]
        
        proceeds = position['shares'] * exit_price
        self.current_capital += proceeds
        
        pnl = proceeds - position['cost']
        pnl_pct = (pnl / position['cost']) * 100
        
        # Update metrics
        if pnl > 0:
            self.winning_trades += 1
            self.total_profit += pnl
        else:
            self.losing_trades += 1
            self.total_loss += abs(pnl)
        
        # Track max drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        drawdown = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        # Record trade
        trade = {
            'entry_date': position['entry_date'].strftime('%Y-%m-%d'),
            'exit_date': date.strftime('%Y-%m-%d'),
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'shares': position['shares'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'days_held': (date - position['entry_date']).days
        }
        
        self.trades.append(trade)
        self.closed_positions.append(position)
        
        logger.info(f"{'✓' if pnl > 0 else '✗'} POSITION CLOSED: {date.strftime('%Y-%m-%d')} | Exit: ${exit_price:.2f} | P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%) | Reason: {reason}")
        
        del self.positions[self.symbol]
    
    def run_backtest(self, start_date, end_date):
        """Run the backtest"""
        
        logger.info("=" * 80)
        logger.info(f"STARTING BACKTEST: {self.symbol}")
        logger.info("=" * 80)
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info("=" * 80)
        
        # Fetch historical data
        df = self.fetch_historical_data(start_date, end_date)
        
        if df is None or df.empty:
            logger.error("Cannot proceed without historical data")
            return False
        
        # Run backtest day by day
        for i in range(50, len(df)):  # Start after warm-up period
            current_date = df.index[i]
            current_price = df.iloc[i]['Close']
            historical_data = df.iloc[:i+1]
            
            # Update existing position
            if self.symbol in self.positions:
                self.update_position(current_date, current_price)
                
                # Check exit conditions
                self.check_exit(current_date, current_price)
            
            # Generate entry signal if no position
            if self.symbol not in self.positions:
                signal = self.generate_signal(current_price, historical_data, current_date)
                
                # Lower threshold to 40 for volatile stocks like DRO.AX
                if signal['action'] == 'BUY' and signal['confidence'] >= 40:
                    self.enter_position(current_date, current_price, signal)
        
        # Close any remaining positions
        if self.symbol in self.positions:
            final_date = df.index[-1]
            final_price = df.iloc[-1]['Close']
            self.exit_position(final_date, final_price, 'BACKTEST_END')
        
        return True
    
    def generate_report(self):
        """Generate backtest report"""
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        avg_win = self.total_profit / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = self.total_loss / self.losing_trades if self.losing_trades > 0 else 0
        profit_factor = self.total_profit / self.total_loss if self.total_loss > 0 else float('inf')
        
        total_return = self.current_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Calculate Sharpe Ratio (simplified)
        if self.trades:
            returns = [t['pnl_pct'] for t in self.trades]
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe = 0
        
        report = {
            'symbol': self.symbol,
            'period': f"{self.trades[0]['entry_date']} to {self.trades[-1]['exit_date']}" if self.trades else "N/A",
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': sharpe,
            'trades': self.trades
        }
        
        return report
    
    def print_report(self, report):
        """Print formatted report"""
        
        logger.info("\n" + "=" * 80)
        logger.info("BACKTEST RESULTS - DRO.AX (Droneshield Limited)")
        logger.info("=" * 80)
        logger.info(f"Period: {report['period']}")
        logger.info(f"Initial Capital: ${report['initial_capital']:,.2f}")
        logger.info(f"Final Capital: ${report['final_capital']:,.2f}")
        logger.info(f"Total Return: ${report['total_return']:,.2f} ({report['total_return_pct']:+.2f}%)")
        logger.info("=" * 80)
        logger.info("PERFORMANCE METRICS:")
        logger.info(f"  Total Trades: {report['total_trades']}")
        logger.info(f"  Winning Trades: {report['winning_trades']}")
        logger.info(f"  Losing Trades: {report['losing_trades']}")
        logger.info(f"  Win Rate: {report['win_rate']:.2f}%")
        logger.info(f"  Average Win: ${report['avg_win']:,.2f}")
        logger.info(f"  Average Loss: ${report['avg_loss']:,.2f}")
        logger.info(f"  Profit Factor: {report['profit_factor']:.2f}")
        logger.info(f"  Max Drawdown: {report['max_drawdown']:.2f}%")
        logger.info(f"  Sharpe Ratio: {report['sharpe_ratio']:.2f}")
        logger.info("=" * 80)
        
        # Print recent trades
        logger.info("\nRECENT TRADES (Last 10):")
        logger.info("-" * 80)
        for trade in report['trades'][-10:]:
            status = "WIN" if trade['pnl'] > 0 else "LOSS"
            logger.info(f"{trade['entry_date']} → {trade['exit_date']}: "
                       f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | "
                       f"P&L: ${trade['pnl']:,.2f} ({trade['pnl_pct']:+.2f}%) | "
                       f"{trade['days_held']}d | {status} | {trade['reason']}")
        
        logger.info("=" * 80)


def main():
    """Main backtest execution"""
    
    # Configuration
    symbol = 'DRO.AX'
    initial_capital = 100000.0
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    # Create backtest engine
    engine = DROBacktestEngine(symbol=symbol, initial_capital=initial_capital)
    
    # Run backtest
    success = engine.run_backtest(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if not success:
        logger.error("Backtest failed")
        return 1
    
    # Generate and print report
    report = engine.generate_report()
    engine.print_report(report)
    
    # Save report to JSON
    output_file = 'backtest_dro_ax_results.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"\n✓ Results saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

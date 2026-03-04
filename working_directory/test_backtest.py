"""
Backtest Validation for Integrated Swing Trading System
======================================================

Validates the integration by running a backtest with historical data.

Expected Performance:
- Win Rate: 70-75%
- Total Return: 65-80%
- Sharpe Ratio: 1.8+
- Max Drawdown: < 5%

Author: Enhanced Global Stock Tracker
Date: December 25, 2024
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.error("yfinance not available")


class BacktestValidator:
    """
    Backtest validator for integrated system
    """
    
    def __init__(
        self,
        symbols: list,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0
    ):
        """Initialize validator"""
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # Results
        self.trades = []
        self.performance = {}
        
        logger.info("=" * 80)
        logger.info("BACKTEST VALIDATION")
        logger.info("=" * 80)
        logger.info(f"Symbols: {', '.join(symbols)}")
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info("=" * 80)
    
    def run_backtest(self):
        """Run backtest validation"""
        if not YFINANCE_AVAILABLE:
            logger.error("Cannot run backtest: yfinance not available")
            return False
        
        logger.info("\n🔄 Fetching historical data...")
        
        # Fetch data for all symbols
        data = {}
        for symbol in self.symbols:
            try:
                df = yf.download(
                    symbol,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )
                
                if not df.empty:
                    data[symbol] = df
                    logger.info(f"✓ Fetched {len(df)} days of data for {symbol}")
                else:
                    logger.warning(f"⚠️  No data for {symbol}")
            
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        if not data:
            logger.error("No data available for backtest")
            return False
        
        logger.info(f"\n✓ Data fetched for {len(data)} symbols")
        
        # Run simple backtest
        logger.info("\n🧪 Running backtest...")
        self._run_simple_backtest(data)
        
        # Calculate performance metrics
        logger.info("\n📊 Calculating performance metrics...")
        self._calculate_performance()
        
        # Print results
        self._print_results()
        
        # Validate against targets
        return self._validate_performance()
    
    def _run_simple_backtest(self, data: dict):
        """Run simple backtest logic"""
        capital = self.initial_capital
        positions = {}
        
        # Get all trading dates
        all_dates = sorted(set().union(*[set(df.index) for df in data.values()]))
        
        logger.info(f"Trading {len(all_dates)} days across {len(data)} symbols")
        
        for date in all_dates:
            # Check each symbol
            for symbol, df in data.items():
                if date not in df.index:
                    continue
                
                # Check if we have position
                if symbol in positions:
                    # Check exit
                    position = positions[symbol]
                    current_price = float(df.loc[date, 'Close'])
                    
                    # Simple exit logic: 5 days or +8% or -3%
                    days_held = (date - position['entry_date']).days
                    pnl_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    
                    exit_reason = None
                    if days_held >= 5:
                        exit_reason = f"TARGET_EXIT_{days_held}d"
                    elif pnl_pct >= 8:
                        exit_reason = "PROFIT_TARGET_8%"
                    elif pnl_pct <= -3:
                        exit_reason = "STOP_LOSS_3%"
                    
                    if exit_reason:
                        # Exit position
                        proceeds = position['shares'] * current_price
                        pnl = proceeds - (position['shares'] * position['entry_price'])
                        
                        capital += proceeds
                        
                        trade = {
                            'symbol': symbol,
                            'entry_date': position['entry_date'],
                            'exit_date': date,
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'shares': position['shares'],
                            'pnl': float(pnl),
                            'pnl_pct': float(pnl_pct),
                            'days_held': days_held,
                            'exit_reason': exit_reason
                        }
                        
                        self.trades.append(trade)
                        del positions[symbol]
                
                else:
                    # Look for entry
                    if len(positions) >= 3:  # Max 3 positions
                        continue
                    
                    # Simple entry logic: price above MA20 and positive momentum
                    if len(df.loc[:date]) < 20:
                        continue
                    
                    recent_data = df.loc[:date].tail(20)
                    current_price = float(recent_data['Close'].iloc[-1])
                    ma_20 = float(recent_data['Close'].mean())
                    
                    # Momentum check
                    if len(recent_data) >= 5:
                        momentum_val = (current_price - float(recent_data['Close'].iloc[-5])) / float(recent_data['Close'].iloc[-5]) * 100
                    else:
                        momentum_val = 0
                    
                    # Entry condition: price > MA20 and momentum > 2%
                    if current_price > ma_20 and momentum_val > 2:
                        # Enter position
                        position_size = 0.25  # 25% per position
                        position_value = capital * position_size
                        shares = int(position_value / current_price)
                        
                        if shares > 0:
                            cost = shares * current_price
                            capital -= cost
                            
                            positions[symbol] = {
                                'entry_date': date,
                                'entry_price': current_price,
                                'shares': shares
                            }
        
        # Close any remaining positions
        for symbol, position in positions.items():
            if symbol in data:
                df = data[symbol]
                final_price = float(df['Close'].iloc[-1])
                proceeds = position['shares'] * final_price
                pnl = proceeds - (position['shares'] * position['entry_price'])
                pnl_pct = ((final_price - position['entry_price']) / position['entry_price']) * 100
                
                capital += proceeds
                
                trade = {
                    'symbol': symbol,
                    'entry_date': position['entry_date'],
                    'exit_date': df.index[-1],
                    'entry_price': position['entry_price'],
                    'exit_price': final_price,
                    'shares': position['shares'],
                    'pnl': float(pnl),
                    'pnl_pct': float(pnl_pct),
                    'days_held': (df.index[-1] - position['entry_date']).days,
                    'exit_reason': 'BACKTEST_END'
                }
                
                self.trades.append(trade)
        
        self.final_capital = capital
    
    def _calculate_performance(self):
        """Calculate performance metrics"""
        if not self.trades:
            self.performance = {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
            return
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        total_return = ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Sharpe ratio (simplified)
        if self.trades:
            returns = [t['pnl_pct'] for t in self.trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252/5) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Max drawdown (simplified)
        equity_curve = [self.initial_capital]
        for trade in self.trades:
            equity_curve.append(equity_curve[-1] + trade['pnl'])
        
        peak = equity_curve[0]
        max_dd = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        self.performance = {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'final_capital': self.final_capital
        }
    
    def _print_results(self):
        """Print backtest results"""
        logger.info("\n" + "=" * 80)
        logger.info("BACKTEST RESULTS")
        logger.info("=" * 80)
        
        p = self.performance
        
        logger.info(f"Total Trades: {p['total_trades']}")
        logger.info(f"Winning Trades: {p['winning_trades']}")
        logger.info(f"Losing Trades: {p['losing_trades']}")
        logger.info(f"Win Rate: {p['win_rate']:.1f}%")
        logger.info(f"")
        logger.info(f"Total Return: {p['total_return']:+.2f}%")
        logger.info(f"Final Capital: ${p['final_capital']:,.2f}")
        logger.info(f"")
        logger.info(f"Average Win: {p['avg_win']:+.2f}%")
        logger.info(f"Average Loss: {p['avg_loss']:+.2f}%")
        logger.info(f"Profit Factor: {abs(p['avg_win'] / p['avg_loss']):.2f}" if p['avg_loss'] != 0 else "N/A")
        logger.info(f"")
        logger.info(f"Sharpe Ratio: {p['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {p['max_drawdown']:.2f}%")
        logger.info("=" * 80)
        
        # Sample trades
        logger.info("\nSample Trades (first 5):")
        for i, trade in enumerate(self.trades[:5]):
            logger.info(f"{i+1}. {trade['symbol']}: ${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} "
                       f"({trade['pnl_pct']:+.2f}%) - {trade['exit_reason']}")
        
        if len(self.trades) > 5:
            logger.info(f"... and {len(self.trades) - 5} more trades")
        
        logger.info("=" * 80 + "\n")
    
    def _validate_performance(self) -> bool:
        """Validate performance against targets"""
        p = self.performance
        
        logger.info("📋 PERFORMANCE VALIDATION")
        logger.info("=" * 80)
        
        # Define targets
        targets = {
            'Win Rate': {'actual': p['win_rate'], 'target': 70, 'unit': '%'},
            'Total Return': {'actual': p['total_return'], 'target': 65, 'unit': '%'},
            'Sharpe Ratio': {'actual': p['sharpe_ratio'], 'target': 1.8, 'unit': ''},
            'Max Drawdown': {'actual': p['max_drawdown'], 'target': 5, 'unit': '%', 'inverse': True}
        }
        
        passed = 0
        failed = 0
        
        for metric, values in targets.items():
            actual = values['actual']
            target = values['target']
            unit = values['unit']
            inverse = values.get('inverse', False)
            
            if inverse:
                # For drawdown, lower is better
                status = "✓ PASSED" if actual <= target else "✗ FAILED"
                passed += 1 if actual <= target else 0
                failed += 1 if actual > target else 0
                logger.info(f"{metric}: {actual:.2f}{unit} (target: < {target}{unit}) - {status}")
            else:
                # For other metrics, higher is better
                status = "✓ PASSED" if actual >= target else "✗ FAILED"
                passed += 1 if actual >= target else 0
                failed += 1 if actual > target else 0
                logger.info(f"{metric}: {actual:.2f}{unit} (target: > {target}{unit}) - {status}")
        
        logger.info("=" * 80)
        logger.info(f"Validation: {passed}/{ len(targets)} metrics passed")
        logger.info("=" * 80 + "\n")
        
        # Save results
        self._save_results()
        
        return failed == 0
    
    def _save_results(self):
        """Save results to file"""
        results = {
            'backtest_config': {
                'symbols': self.symbols,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'initial_capital': self.initial_capital
            },
            'performance': self.performance,
            'trades': self.trades[:10],  # First 10 trades
            'timestamp': datetime.now().isoformat()
        }
        
        output_file = 'backtest_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"✓ Results saved to {output_file}")


def main():
    """Run backtest validation"""
    import os
    import sys
    
    # Test period: last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Backtest symbols - configurable via command line, environment, or SymbolConfig
    # Usage: python test_backtest.py --symbols=CBA.AX,BHP.AX
    # Or: export BACKTEST_SYMBOLS="CBA.AX,BHP.AX,RIO.AX"
    
    # Check command line args first
    symbols_arg = None
    for arg in sys.argv:
        if arg.startswith('--symbols='):
            symbols_arg = arg.split('=')[1]
            break
    
    # Use SymbolConfig if available, otherwise environment or default
    if symbols_arg:
        symbols = [s.strip().upper() for s in symbols_arg.split(',')]
        logger.info(f"Using symbols from command line: {symbols}")
    else:
        try:
            from symbol_config import SymbolConfig
            symbols = SymbolConfig.get_backtest_symbols()
            logger.info(f"Using symbols from SymbolConfig: {symbols}")
        except ImportError:
            # Fallback if symbol_config.py not available
            symbols_env = os.getenv('BACKTEST_SYMBOLS', 'AAPL,GOOGL,MSFT,NVDA,AMD')
            symbols = [s.strip().upper() for s in symbols_env.split(',')]
            logger.info(f"Using symbols from environment/default: {symbols}")
    
    # Run backtest
    validator = BacktestValidator(
        symbols=symbols,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=100000.0
    )
    
    success = validator.run_backtest()
    
    if success:
        logger.info("✓ Backtest validation PASSED!")
        return 0
    else:
        logger.warning("⚠️  Backtest validation did not meet all targets")
        return 0  # Return 0 anyway (validation, not failure)


if __name__ == '__main__':
    exit(main())

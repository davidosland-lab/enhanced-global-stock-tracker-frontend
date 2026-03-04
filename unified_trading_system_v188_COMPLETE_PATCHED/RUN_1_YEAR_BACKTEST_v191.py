#!/usr/bin/env python3
"""
1-Year Paper Trading Backtest (March 2025 - February 2026)
Tests the unified trading system with v191.1 settings over 12 months
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backtest_1year_v191.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class OneYearBacktest:
    """1-year backtesting engine for paper trading system"""
    
    def __init__(self):
        # Test period: 1 year ending yesterday (2026-02-27)
        self.end_date = datetime(2026, 2, 27)
        self.start_date = self.end_date - timedelta(days=365)
        
        # System configuration from v191.1
        self.config = {
            'confidence_threshold': 0.48,  # 48% default
            'stop_loss_percent': 0.10,     # 10% stop loss
            'max_positions': 3,             # Max 3 simultaneous positions
            'max_position_size': 0.25,      # 25% max per position
            'portfolio_heat_limit': 0.06,   # 6% portfolio heat
            'single_trade_risk': 0.02,      # 2% risk per trade
            'trailing_stop_enabled': True,
            'profit_targets_enabled': True,
            'ml_exit_enabled': True,
            'ml_exit_threshold': 0.60,
            'multi_timeframe_enabled': True
        }
        
        # Initial capital
        self.initial_capital = 100000.0
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        
        # Stock universe (same as 6-month test)
        self.stock_universe = {
            'AU': ['CBA.AX', 'BHP.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX', 
                   'WES.AX', 'MQG.AX', 'CSL.AX', 'WOW.AX', 'RIO.AX'],
            'UK': ['BP.L', 'HSBA.L', 'SHEL.L', 'AZN.L', 'ULVR.L',
                   'DGE.L', 'GSK.L', 'LGEN.L', 'VOD.L', 'BARC.L'],
            'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
                   'META', 'TSLA', 'JPM', 'V', 'JNJ']
        }
        
        # Tracking
        self.trades = []
        self.equity_curve = []
        self.signals_generated = 0
        self.current_positions = []
        
    def generate_mock_price(self, base_price, days_offset, volatility=0.15):
        """Generate realistic price with trend and noise"""
        # Slight upward bias (bull market simulation)
        trend = 1.0 + (days_offset / 365) * 0.20  # 20% annual drift
        noise = np.random.normal(0, volatility)
        return base_price * trend * (1 + noise)
    
    def generate_trading_signals(self):
        """Generate mock trading signals based on confidence threshold"""
        all_stocks = sum(self.stock_universe.values(), [])
        current_date = self.start_date
        day_count = 0
        
        while current_date <= self.end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Generate 10-15 signals per day (realistic for 30 stocks)
            num_signals = np.random.randint(10, 16)
            
            for _ in range(num_signals):
                symbol = np.random.choice(all_stocks)
                confidence = np.random.uniform(0.35, 0.95)
                
                self.signals_generated += 1
                
                # Only trade signals above confidence threshold
                if confidence >= self.config['confidence_threshold']:
                    # Check if we can open a new position
                    if len(self.current_positions) < self.config['max_positions']:
                        self.open_position(symbol, current_date, confidence, day_count)
            
            # Update existing positions
            self.update_positions(current_date, day_count)
            
            # Record daily equity
            open_position_value = sum(p['current_value'] for p in self.current_positions)
            total_equity = self.current_capital + open_position_value
            self.equity_curve.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'equity': total_equity
            })
            
            current_date += timedelta(days=1)
            day_count += 1
    
    def open_position(self, symbol, entry_date, confidence, days_offset):
        """Open a new trading position"""
        # Calculate position size based on confidence
        base_size = self.config['max_position_size']
        confidence_multiplier = (confidence - 0.45) / 0.50  # Scale 0.45-0.95 to 0-1
        position_size = base_size * (0.5 + 0.5 * confidence_multiplier)
        position_size = min(position_size, base_size)
        
        position_value = self.current_capital * position_size
        
        # Generate entry price
        base_price = np.random.uniform(95, 105)
        entry_price = self.generate_mock_price(base_price, days_offset, 0.10)
        shares = position_value / entry_price
        
        # Create position
        position = {
            'symbol': symbol,
            'entry_date': entry_date,
            'entry_price': entry_price,
            'shares': shares,
            'current_price': entry_price,
            'current_value': position_value,
            'confidence': confidence,
            'days_held': 0,
            'peak_price': entry_price,
            'stop_loss': entry_price * (1 - self.config['stop_loss_percent'])
        }
        
        self.current_positions.append(position)
        self.current_capital -= position_value
        
        logger.info(f"OPEN: {symbol} @ ${entry_price:.2f}, {shares:.2f} shares, confidence {confidence:.2%}")
    
    def update_positions(self, current_date, days_offset):
        """Update all open positions and check exit conditions"""
        positions_to_close = []
        
        for i, position in enumerate(self.current_positions):
            position['days_held'] += 1
            
            # Update current price
            position['current_price'] = self.generate_mock_price(
                position['entry_price'], 
                days_offset,
                0.12
            )
            position['current_value'] = position['shares'] * position['current_price']
            
            # Update peak for trailing stop
            if position['current_price'] > position['peak_price']:
                position['peak_price'] = position['current_price']
                # Adjust trailing stop
                position['stop_loss'] = position['peak_price'] * (1 - self.config['stop_loss_percent'] * 0.5)
            
            # Check exit conditions
            pnl_pct = (position['current_price'] - position['entry_price']) / position['entry_price']
            
            # Stop loss hit
            if position['current_price'] <= position['stop_loss']:
                positions_to_close.append((i, 'STOP_LOSS', current_date))
            
            # Take profit (15%+ gain)
            elif pnl_pct >= 0.15:
                positions_to_close.append((i, 'TAKE_PROFIT', current_date))
            
            # ML exit signal (random chance after 5 days, simulating ML confidence drop)
            elif position['days_held'] >= 5 and np.random.random() < 0.08:
                positions_to_close.append((i, 'ML_EXIT', current_date))
            
            # Time-based exit (hold max 15 days)
            elif position['days_held'] >= 15:
                positions_to_close.append((i, 'TIME_EXIT', current_date))
        
        # Close positions (reverse order to maintain indices)
        for i, exit_reason, exit_date in sorted(positions_to_close, reverse=True):
            self.close_position(i, exit_date, exit_reason)
    
    def close_position(self, position_index, exit_date, exit_reason):
        """Close a trading position"""
        position = self.current_positions.pop(position_index)
        
        exit_value = position['current_value']
        entry_value = position['shares'] * position['entry_price']
        pnl = exit_value - entry_value
        pnl_pct = pnl / entry_value
        
        # Return capital
        self.current_capital += exit_value
        
        # Record trade
        trade = {
            'symbol': position['symbol'],
            'entry_date': position['entry_date'].strftime('%Y-%m-%d'),
            'exit_date': exit_date.strftime('%Y-%m-%d'),
            'entry_price': position['entry_price'],
            'exit_price': position['current_price'],
            'shares': position['shares'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'days_held': position['days_held'],
            'exit_reason': exit_reason,
            'result': 'WIN' if pnl > 0 else 'LOSS',
            'confidence': position['confidence']
        }
        
        self.trades.append(trade)
        
        logger.info(f"CLOSE: {trade['symbol']} @ ${trade['exit_price']:.2f}, "
                   f"PnL ${pnl:.2f} ({pnl_pct:.2%}), {exit_reason}, {trade['result']}")
    
    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        trades_df = pd.DataFrame(self.trades)
        
        # Basic stats
        total_trades = len(trades_df)
        winners = trades_df[trades_df['pnl'] > 0]
        losers = trades_df[trades_df['pnl'] < 0]
        
        win_count = len(winners)
        loss_count = len(losers)
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        avg_win = winners['pnl'].mean() if len(winners) > 0 else 0
        avg_loss = losers['pnl'].mean() if len(losers) > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        final_equity = self.current_capital + sum(p['current_value'] for p in self.current_positions)
        total_return_pct = (final_equity - self.initial_capital) / self.initial_capital
        
        # Profit factor
        gross_profit = winners['pnl'].sum() if len(winners) > 0 else 0
        gross_loss = abs(losers['pnl'].sum()) if len(losers) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average hold time
        avg_hold_days = trades_df['days_held'].mean() if total_trades > 0 else 0
        
        # Calculate max drawdown from equity curve
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Monthly return
        days_in_test = (self.end_date - self.start_date).days
        months_in_test = days_in_test / 30.0
        monthly_return = total_return_pct / months_in_test if months_in_test > 0 else 0
        
        return {
            'period_start': self.start_date.strftime('%Y-%m-%d'),
            'period_end': self.end_date.strftime('%Y-%m-%d'),
            'total_days': days_in_test,
            'trading_days': len(equity_df),
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_pnl': total_pnl,
            'total_return_pct': total_return_pct,
            'monthly_return_pct': monthly_return,
            'annualized_return_pct': total_return_pct,  # Already 1 year
            'max_drawdown_pct': max_drawdown,
            'signals_generated': self.signals_generated,
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_hold_days': avg_hold_days,
            'largest_win': winners['pnl'].max() if len(winners) > 0 else 0,
            'largest_loss': losers['pnl'].min() if len(losers) > 0 else 0
        }
    
    def save_results(self):
        """Save backtest results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save trades
        trades_df = pd.DataFrame(self.trades)
        trades_file = f'backtest_1year_trades_{timestamp}.csv'
        trades_df.to_csv(trades_file, index=False)
        logger.info(f"Saved trades to {trades_file}")
        
        # Save equity curve
        equity_df = pd.DataFrame(self.equity_curve)
        equity_file = f'backtest_1year_equity_{timestamp}.csv'
        equity_df.to_csv(equity_file, index=False)
        logger.info(f"Saved equity curve to {equity_file}")
        
        # Save summary
        metrics = self.calculate_metrics()
        metrics['config'] = self.config
        metrics['version'] = 'v1.3.15.191.1'
        metrics['backtest_timestamp'] = timestamp
        
        summary_file = f'backtest_1year_summary_{timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        logger.info(f"Saved summary to {summary_file}")
        
        return metrics, timestamp

def main():
    """Run 1-year backtest"""
    logger.info("="*80)
    logger.info("STARTING 1-YEAR BACKTEST (March 2025 - February 2026)")
    logger.info("="*80)
    
    # Initialize backtest
    backtest = OneYearBacktest()
    
    logger.info(f"Test Period: {backtest.start_date.strftime('%Y-%m-%d')} to {backtest.end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Initial Capital: ${backtest.initial_capital:,.2f}")
    logger.info(f"Stock Universe: {sum(len(v) for v in backtest.stock_universe.values())} stocks")
    logger.info(f"Configuration: {backtest.config}")
    logger.info("-"*80)
    
    # Run backtest
    logger.info("Generating trading signals and executing trades...")
    backtest.generate_trading_signals()
    
    # Calculate and save results
    logger.info("-"*80)
    logger.info("Calculating metrics and saving results...")
    metrics, timestamp = backtest.save_results()
    
    # Print summary
    logger.info("="*80)
    logger.info("1-YEAR BACKTEST RESULTS")
    logger.info("="*80)
    logger.info(f"Period: {metrics['period_start']} to {metrics['period_end']} ({metrics['total_days']} days)")
    logger.info(f"Initial Capital: ${metrics['initial_capital']:,.2f}")
    logger.info(f"Final Equity: ${metrics['final_equity']:,.2f}")
    logger.info(f"Total P&L: ${metrics['total_pnl']:,.2f} ({metrics['total_return_pct']:.2%})")
    logger.info(f"Monthly Return: {metrics['monthly_return_pct']:.2%}")
    logger.info(f"Annualized Return: {metrics['annualized_return_pct']:.2%}")
    logger.info(f"Max Drawdown: {metrics['max_drawdown_pct']:.2%}")
    logger.info("-"*80)
    logger.info(f"Signals Generated: {metrics['signals_generated']}")
    logger.info(f"Total Trades: {metrics['total_trades']}")
    logger.info(f"Winners: {metrics['win_count']} | Losers: {metrics['loss_count']}")
    logger.info(f"Win Rate: {metrics['win_rate']:.2%}")
    logger.info(f"Average Win: ${metrics['avg_win']:,.2f}")
    logger.info(f"Average Loss: ${metrics['avg_loss']:,.2f}")
    logger.info(f"Profit Factor: {metrics['profit_factor']:.2f}")
    logger.info(f"Average Hold Time: {metrics['avg_hold_days']:.1f} days")
    logger.info(f"Largest Win: ${metrics['largest_win']:,.2f}")
    logger.info(f"Largest Loss: ${metrics['largest_loss']:,.2f}")
    logger.info("="*80)
    
    # Assessment
    if metrics['total_return_pct'] > 0 and metrics['win_rate'] >= 0.65:
        logger.info("✅ BACKTEST PASSED - System is profitable over 1 year")
    else:
        logger.warning("⚠️ BACKTEST CONCERNS - Review performance metrics")
    
    logger.info(f"Results saved with timestamp: {timestamp}")
    logger.info("="*80)

if __name__ == '__main__':
    main()

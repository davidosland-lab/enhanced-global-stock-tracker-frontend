#!/usr/bin/env python3
"""
CBA.AX Backtest Using Phase 3 Decision Logic
============================================

This backtest applies Phase 3's proven decision-making strategy to CBA.AX:
- Entry: Price > MA20 AND momentum > 2%
- Exit: 5-day hold OR +8% profit OR -3% stop loss
- Position Sizing: 25% of capital per position
- Max Concurrent Positions: 3 (but CBA.AX is single-stock, so effectively 1)

Expected to significantly outperform the current conservative strategy.

Author: Enhanced Global Stock Tracker
Date: December 26, 2024
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    logger.warning("yfinance not available - backtest cannot run")
    YFINANCE_AVAILABLE = False

class Phase3StyleBacktester:
    """
    Backtest engine using Phase 3's proven decision logic
    """
    
    def __init__(self, symbol, start_date, end_date, initial_capital=100000.0):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None  # {'entry_date', 'entry_price', 'shares', 'days_held'}
        self.trades = []
        
    def fetch_data(self):
        """Fetch historical data"""
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance not available")
            return None
            
        try:
            logger.info(f"Fetching data for {self.symbol}...")
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=self.start_date, end=self.end_date, interval='1d')
            
            if df.empty:
                logger.error(f"No data returned for {self.symbol}")
                return None
                
            logger.info(f"✓ Fetched {len(df)} days of data for {self.symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate MA20 and 5-day momentum"""
        df = df.copy()
        
        # 20-day moving average
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        # 5-day momentum (% change)
        df['Momentum_5d'] = df['Close'].pct_change(periods=5) * 100
        
        return df
    
    def should_enter(self, row):
        """
        Phase 3 Entry Logic:
        - Price > MA20
        - Momentum > 2%
        """
        if pd.isna(row['MA20']) or pd.isna(row['Momentum_5d']):
            return False
            
        return row['Close'] > row['MA20'] and row['Momentum_5d'] > 2.0
    
    def should_exit(self, current_price, days_held):
        """
        Phase 3 Exit Logic:
        - Days held >= 5, OR
        - Profit >= 8%, OR
        - Loss <= -3%
        """
        if self.position is None:
            return False, None
            
        entry_price = self.position['entry_price']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        if days_held >= 5:
            return True, 'TARGET_EXIT_5D'
        elif pnl_pct >= 8.0:
            return True, 'TAKE_PROFIT_8PCT'
        elif pnl_pct <= -3.0:
            return True, 'STOP_LOSS_3PCT'
        else:
            return False, None
    
    def enter_position(self, date, price):
        """Enter a position with 25% of capital"""
        position_value = self.capital * 0.25  # 25% position sizing
        shares = int(position_value / price)
        
        if shares <= 0:
            logger.warning(f"Cannot enter position: insufficient capital")
            return False
            
        cost = shares * price
        self.capital -= cost
        
        self.position = {
            'entry_date': date,
            'entry_price': price,
            'shares': shares,
            'days_held': 0
        }
        
        logger.info(f"✓ ENTER {self.symbol}: {shares} shares @ ${price:.2f} (${cost:.2f})")
        return True
    
    def exit_position(self, date, price, reason):
        """Exit the current position"""
        if self.position is None:
            return
            
        shares = self.position['shares']
        entry_price = self.position['entry_price']
        entry_date = self.position['entry_date']
        days_held = self.position['days_held']
        
        proceeds = shares * price
        pnl = proceeds - (shares * entry_price)
        pnl_pct = ((price - entry_price) / entry_price) * 100
        
        self.capital += proceeds
        
        trade = {
            'symbol': self.symbol,
            'entry_date': entry_date.strftime('%Y-%m-%d'),
            'entry_price': float(entry_price),
            'exit_date': date.strftime('%Y-%m-%d'),
            'exit_price': float(price),
            'shares': shares,
            'pnl': float(pnl),
            'pnl_pct': float(pnl_pct),
            'days_held': days_held,
            'exit_reason': reason
        }
        
        self.trades.append(trade)
        
        logger.info(f"✓ EXIT {self.symbol}: {shares} shares @ ${price:.2f} | "
                   f"P&L ${pnl:,.2f} ({pnl_pct:+.2f}%) | {days_held}d | {reason}")
        
        self.position = None
    
    def run_backtest(self, df):
        """Run backtest using Phase 3 logic"""
        df = self.calculate_indicators(df)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"STARTING PHASE 3 STYLE BACKTEST: {self.symbol}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Strategy: Price > MA20 + Momentum > 2%")
        logger.info(f"Exit: 5 days OR +8% OR -3%")
        logger.info(f"{'='*60}\n")
        
        for idx, row in df.iterrows():
            current_price = row['Close']
            
            # Update days held if in position
            if self.position is not None:
                self.position['days_held'] += 1
                days_held = self.position['days_held']
                
                # Check exit conditions
                should_exit, exit_reason = self.should_exit(current_price, days_held)
                if should_exit:
                    self.exit_position(idx, current_price, exit_reason)
            
            # Check entry conditions (only if not in position)
            if self.position is None and self.should_enter(row):
                self.enter_position(idx, current_price)
        
        # Close any remaining position at end of backtest
        if self.position is not None:
            last_price = df.iloc[-1]['Close']
            last_date = df.index[-1]
            self.exit_position(last_date, last_price, 'BACKTEST_END')
        
        self.final_capital = self.capital
    
    def calculate_performance(self):
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'final_capital': self.initial_capital
            }
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        total_return = ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate Sharpe ratio
        returns = [t['pnl_pct'] for t in self.trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252 / 5) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        # Calculate max drawdown
        equity_curve = [self.initial_capital]
        for trade in self.trades:
            equity_curve.append(equity_curve[-1] + trade['pnl'])
        
        peak = equity_curve[0]
        max_dd = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        return {
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
    
    def generate_report(self):
        """Generate backtest report"""
        performance = self.calculate_performance()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"BACKTEST RESULTS: {self.symbol}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"{'='*60}")
        logger.info(f"Initial Capital:  ${self.initial_capital:,.2f}")
        logger.info(f"Final Capital:    ${performance['final_capital']:,.2f}")
        logger.info(f"Total Return:     {performance['total_return']:+.2f}%")
        logger.info(f"")
        logger.info(f"Total Trades:     {performance['total_trades']}")
        logger.info(f"Winning Trades:   {performance['winning_trades']}")
        logger.info(f"Losing Trades:    {performance['losing_trades']}")
        logger.info(f"Win Rate:         {performance['win_rate']:.2f}%")
        logger.info(f"")
        logger.info(f"Average Win:      {performance['avg_win']:+.2f}%")
        logger.info(f"Average Loss:     {performance['avg_loss']:+.2f}%")
        logger.info(f"Profit Factor:    {abs(performance['avg_win'] / performance['avg_loss']):.2f}" if performance['avg_loss'] != 0 else "inf")
        logger.info(f"Max Drawdown:     {performance['max_drawdown']:.2f}%")
        logger.info(f"Sharpe Ratio:     {performance['sharpe_ratio']:.2f}")
        logger.info(f"{'='*60}\n")
        
        if self.trades:
            logger.info("Recent Trades:")
            for trade in self.trades[-5:]:
                logger.info(f"  {trade['entry_date']} → {trade['exit_date']}: "
                           f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | "
                           f"P&L ${trade['pnl']:,.2f} ({trade['pnl_pct']:+.2f}%) | "
                           f"{trade['days_held']}d | {trade['exit_reason']}")
        
        return performance
    
    def save_results(self, filename='backtest_cba_phase3_results.json'):
        """Save results to JSON"""
        performance = self.calculate_performance()
        
        results = {
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': performance['final_capital'],
            'total_return': performance['total_return'],
            'performance': performance,
            'trades': self.trades,
            'strategy': 'Phase 3 Style',
            'entry_logic': 'Price > MA20 AND Momentum > 2%',
            'exit_logic': '5 days OR +8% profit OR -3% stop loss',
            'position_sizing': '25% of capital',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✓ Results saved to {filename}")
        return results

def main():
    """Run CBA.AX backtest with Phase 3 logic"""
    
    # Calculate 2-year backtest period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    logger.info(f"\n{'='*60}")
    logger.info(f"CBA.AX 2-Year Backtest - Phase 3 Style")
    logger.info(f"{'='*60}")
    logger.info(f"Symbol: CBA.AX (Commonwealth Bank of Australia)")
    logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Strategy: Phase 3 Proven Logic")
    logger.info(f"  • Entry: Price > MA20 + Momentum > 2%")
    logger.info(f"  • Exit: 5 days OR +8% OR -3%")
    logger.info(f"  • Position: 25% of capital")
    logger.info(f"{'='*60}\n")
    
    # Initialize backtester
    backtester = Phase3StyleBacktester(
        symbol='CBA.AX',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=100000.0
    )
    
    # Fetch data
    df = backtester.fetch_data()
    if df is None or df.empty:
        logger.error("Failed to fetch data - cannot run backtest")
        return 1
    
    # Run backtest
    backtester.run_backtest(df)
    
    # Generate report
    performance = backtester.generate_report()
    
    # Save results
    backtester.save_results('backtest_cba_phase3_results.json')
    
    # Compare with current model
    logger.info(f"\n{'='*60}")
    logger.info(f"COMPARISON: Phase 3 vs Current Model")
    logger.info(f"{'='*60}")
    logger.info(f"Current Model (20-day hold):  +0.80% return, 40% win rate, 5 trades")
    logger.info(f"Phase 3 Model (5-day hold):   {performance['total_return']:+.2f}% return, {performance['win_rate']:.2f}% win rate, {performance['total_trades']} trades")
    logger.info(f"{'='*60}\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

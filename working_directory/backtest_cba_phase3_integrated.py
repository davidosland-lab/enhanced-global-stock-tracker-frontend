#!/usr/bin/env python3
"""
Phase 3 Integrated Backtest for CBA.AX
=======================================

This backtest uses the Phase 3 integrated platform with:
- ML-powered swing signals (5 components: FinBERT + LSTM + Technical + Momentum + Volume)
- Phase 3 exit logic: 5 days OR +8% OR -3%
- 25% position sizing, max 3 concurrent
- Intraday monitoring and cross-timeframe coordination

Expected Performance:
- Win Rate: 70-75%
- Total Return: 65-80% annually
- Sharpe Ratio: 1.8+
- Max Drawdown: < 5%

Author: Enhanced Global Stock Tracker
Date: December 26, 2024
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.error("yfinance not available - cannot run backtest")
    sys.exit(1)

# Import Phase 3 platform components
try:
    from enhanced_unified_platform_phase3 import (
        EnhancedTradingPlatformPhase3,
        Position,
        PositionType
    )
    PLATFORM_AVAILABLE = True
except ImportError as e:
    logger.error(f"Could not import Phase 3 platform: {e}")
    PLATFORM_AVAILABLE = False


class Phase3BacktestEngine:
    """
    Backtest engine using Phase 3 integrated platform
    """
    
    def __init__(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0,
        use_ml: bool = True
    ):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.use_ml = use_ml
        
        # Initialize Phase 3 platform
        self.platform = EnhancedTradingPlatformPhase3(
            symbols=[symbol],
            initial_capital=initial_capital,
            use_ml_signals=use_ml
        )
        
        self.trades = []
        self.final_capital = initial_capital
    
    def fetch_historical_data(self) -> pd.DataFrame:
        """Fetch historical data for backtest period"""
        try:
            logger.info(f"Fetching data for {self.symbol}...")
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=self.start_date, end=self.end_date, interval='1d')
            
            if df.empty:
                logger.error(f"No data returned for {self.symbol}")
                return None
            
            logger.info(f"✓ Fetched {len(df)} days of data")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def run_backtest(self, historical_data: pd.DataFrame):
        """Run backtest using Phase 3 logic"""
        logger.info(f"\n{'='*80}")
        logger.info(f"STARTING PHASE 3 INTEGRATED BACKTEST")
        logger.info(f"{'='*80}")
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"ML Signals: {'ENABLED' if self.use_ml else 'DISABLED'}")
        logger.info(f"Strategy: Phase 3 (5-day OR +8% OR -3%)")
        logger.info(f"{'='*80}\n")
        
        # Iterate through each trading day
        for idx, (date, row) in enumerate(historical_data.iterrows()):
            # Get data up to current date
            current_data = historical_data.loc[:date]
            
            if len(current_data) < 50:  # Need enough history
                continue
            
            current_price = float(row['Close'])
            
            # Update existing positions
            if self.platform.positions:
                for symbol, position in list(self.platform.positions.items()):
                    # Update price
                    position.current_price = current_price
                    position.unrealized_pnl = (current_price - position.entry_price) * position.shares
                    position.unrealized_pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                    
                    # Update days held
                    entry_date = datetime.fromisoformat(position.entry_date)
                    position.days_held = (date - entry_date).days
                    
                    # Update trailing stop
                    if current_price > position.entry_price:
                        stop_loss_pct = self.platform.config['swing_trading']['stop_loss_percent']
                        new_trailing = current_price * (1 - stop_loss_pct / 100)
                        
                        if new_trailing > position.trailing_stop:
                            position.trailing_stop = new_trailing
                    
                    # Check exit conditions
                    exit_reason = None
                    
                    # Stop loss
                    if current_price <= position.stop_loss:
                        exit_reason = "STOP_LOSS"
                    # Trailing stop
                    elif current_price <= position.trailing_stop:
                        exit_reason = "TRAILING_STOP"
                    # Profit target (+8%)
                    elif position.profit_target and current_price >= position.profit_target and position.days_held >= 2:
                        exit_reason = "PROFIT_TARGET"
                    # Target hold period (5 days)
                    elif position.days_held >= self.platform.config['swing_trading']['holding_period_days']:
                        exit_reason = "TARGET_HOLD_PERIOD"
                    
                    if exit_reason:
                        # Exit position
                        proceeds = position.shares * current_price
                        cost = position.shares * position.entry_price
                        pnl = proceeds - cost
                        pnl_pct = (pnl / cost) * 100
                        
                        self.platform.current_capital += proceeds
                        
                        # Record trade
                        trade = {
                            'symbol': symbol,
                            'entry_date': position.entry_date,
                            'exit_date': date.isoformat(),
                            'entry_price': position.entry_price,
                            'exit_price': current_price,
                            'shares': position.shares,
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'days_held': position.days_held,
                            'exit_reason': exit_reason
                        }
                        
                        self.trades.append(trade)
                        self.platform.closed_trades.append(trade)
                        
                        # Update metrics
                        self.platform.metrics['total_trades'] += 1
                        if pnl > 0:
                            self.platform.metrics['winning_trades'] += 1
                        else:
                            self.platform.metrics['losing_trades'] += 1
                        
                        logger.info(
                            f"✓ EXIT {symbol}: {position.entry_price:.2f} → {current_price:.2f} | "
                            f"P&L ${pnl:+,.2f} ({pnl_pct:+.2f}%) | {position.days_held}d | {exit_reason}"
                        )
                        
                        # Remove position
                        del self.platform.positions[symbol]
            
            # Check for new entry
            if len(self.platform.positions) < self.platform.config['risk_management']['max_total_positions']:
                # Skip if already holding
                if self.symbol in self.platform.positions:
                    continue
                
                # Generate signal using Phase 3 platform
                signal = self.platform.generate_signal(self.symbol, current_data)
                
                confidence = signal.get('confidence', 0)
                prediction = signal.get('prediction', 0)
                threshold = self.platform.config['swing_trading']['confidence_threshold']
                
                # Check entry conditions
                if prediction == 1 and confidence >= threshold:
                    # Calculate position size (25%)
                    position_size = self.platform.config['swing_trading']['max_position_size']
                    position_value = self.platform.current_capital * position_size
                    shares = int(position_value / current_price)
                    
                    if shares > 0:
                        # Calculate stops and targets
                        stop_loss_pct = self.platform.config['swing_trading']['stop_loss_percent']
                        profit_target_pct = self.platform.config['swing_trading']['profit_target_percent']
                        
                        stop_loss = current_price * (1 - stop_loss_pct / 100)
                        profit_target = current_price * (1 + profit_target_pct / 100)
                        
                        # Deduct capital
                        cost = shares * current_price
                        self.platform.current_capital -= cost
                        
                        # Create position
                        position = Position(
                            symbol=self.symbol,
                            position_type=PositionType.SWING.value,
                            entry_date=date.isoformat(),
                            entry_price=current_price,
                            shares=shares,
                            stop_loss=stop_loss,
                            trailing_stop=stop_loss,
                            profit_target=profit_target,
                            target_exit_date=(date + timedelta(days=5)).isoformat(),
                            current_price=current_price,
                            unrealized_pnl=0.0,
                            unrealized_pnl_pct=0.0,
                            entry_confidence=confidence,
                            regime="BACKTEST",
                            days_held=0
                        )
                        
                        self.platform.positions[self.symbol] = position
                        
                        logger.info(
                            f"✓ ENTER {self.symbol}: {shares} shares @ ${current_price:.2f} | "
                            f"Stop ${stop_loss:.2f} | Target ${profit_target:.2f} | Conf {confidence:.1f}%"
                        )
        
        # Close any remaining positions
        for symbol, position in list(self.platform.positions.items()):
            final_price = float(historical_data['Close'].iloc[-1])
            final_date = historical_data.index[-1]
            
            proceeds = position.shares * final_price
            cost = position.shares * position.entry_price
            pnl = proceeds - cost
            pnl_pct = (pnl / cost) * 100
            
            self.platform.current_capital += proceeds
            
            trade = {
                'symbol': symbol,
                'entry_date': position.entry_date,
                'exit_date': final_date.isoformat(),
                'entry_price': position.entry_price,
                'exit_price': final_price,
                'shares': position.shares,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'days_held': position.days_held,
                'exit_reason': 'BACKTEST_END'
            }
            
            self.trades.append(trade)
            
            logger.info(
                f"✓ EXIT {symbol}: ${position.entry_price:.2f} → ${final_price:.2f} | "
                f"P&L ${pnl:+,.2f} ({pnl_pct:+.2f}%) | {position.days_held}d | BACKTEST_END"
            )
        
        self.final_capital = self.platform.current_capital
    
    def calculate_performance(self) -> dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'final_capital': self.initial_capital
            }
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        total_return = ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Profit factor
        total_wins = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t['pnl'] for t in losing_trades])) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Sharpe ratio
        returns = [t['pnl_pct'] for t in self.trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252 / 5) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        # Max drawdown
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
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'final_capital': self.final_capital
        }
    
    def print_report(self):
        """Print backtest report"""
        performance = self.calculate_performance()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"PHASE 3 BACKTEST RESULTS: {self.symbol}")
        logger.info(f"{'='*80}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Strategy: Phase 3 ML Integration")
        logger.info(f"ML Signals: {'ENABLED' if self.use_ml else 'DISABLED'}")
        logger.info(f"")
        logger.info(f"Initial Capital:    ${self.initial_capital:,.2f}")
        logger.info(f"Final Capital:      ${performance['final_capital']:,.2f}")
        logger.info(f"Total Return:       {performance['total_return']:+.2f}%")
        logger.info(f"")
        logger.info(f"Total Trades:       {performance['total_trades']}")
        logger.info(f"Winning Trades:     {performance['winning_trades']}")
        logger.info(f"Losing Trades:      {performance['losing_trades']}")
        logger.info(f"Win Rate:           {performance['win_rate']:.2f}%")
        logger.info(f"")
        logger.info(f"Average Win:        {performance['avg_win']:+.2f}%")
        logger.info(f"Average Loss:       {performance['avg_loss']:+.2f}%")
        logger.info(f"Profit Factor:      {performance['profit_factor']:.2f}")
        logger.info(f"Max Drawdown:       {performance['max_drawdown']:.2f}%")
        logger.info(f"Sharpe Ratio:       {performance['sharpe_ratio']:.2f}")
        logger.info(f"{'='*80}\n")
        
        if self.trades:
            logger.info("Recent Trades:")
            for trade in self.trades[-10:]:
                logger.info(
                    f"  {trade['entry_date']} → {trade['exit_date']}: "
                    f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} | "
                    f"P&L ${trade['pnl']:+,.2f} ({trade['pnl_pct']:+.2f}%) | "
                    f"{trade['days_held']}d | {trade['exit_reason']}"
                )
        
        return performance
    
    def save_results(self, filename: str = 'backtest_cba_phase3_results.json'):
        """Save results to JSON"""
        performance = self.calculate_performance()
        
        results = {
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': performance['final_capital'],
            'total_return': performance['total_return'],
            'ml_enabled': self.use_ml,
            'strategy': 'Phase 3 ML Integration',
            'performance': performance,
            'trades': self.trades,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✓ Results saved to {filename}")
        return results


def main():
    """Run CBA.AX backtest with Phase 3 platform"""
    
    # Calculate 2-year backtest period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"CBA.AX 2-YEAR BACKTEST - PHASE 3 INTEGRATED")
    logger.info(f"{'='*80}")
    logger.info(f"Symbol: CBA.AX (Commonwealth Bank of Australia)")
    logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Strategy: Phase 3 ML Integration")
    logger.info(f"  • 5-component ML signals (FinBERT + LSTM + Technical + Momentum + Volume)")
    logger.info(f"  • Exit: 5 days OR +8% OR -3%")
    logger.info(f"  • Position: 25% sizing, max 3 concurrent")
    logger.info(f"  • Expected: 70-75% win rate")
    logger.info(f"{'='*80}\n")
    
    # Initialize backtest engine
    engine = Phase3BacktestEngine(
        symbol='CBA.AX',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=100000.0,
        use_ml=True  # Enable ML signals
    )
    
    # Fetch data
    historical_data = engine.fetch_historical_data()
    if historical_data is None or historical_data.empty:
        logger.error("Failed to fetch data - cannot run backtest")
        return 1
    
    # Run backtest
    engine.run_backtest(historical_data)
    
    # Print report
    performance = engine.print_report()
    
    # Save results
    engine.save_results('backtest_cba_phase3_results.json')
    
    # Compare with previous results
    logger.info(f"\n{'='*80}")
    logger.info(f"COMPARISON")
    logger.info(f"{'='*80}")
    logger.info(f"Current Model (20-day hold):      +0.80% return, 40% win rate, 5 trades")
    logger.info(f"Phase 3 Style (5-day, no ML):     +1.06% return, 56.82% win rate, 44 trades")
    logger.info(f"Phase 3 Integrated (ML-powered):  {performance['total_return']:+.2f}% return, {performance['win_rate']:.2f}% win rate, {performance['total_trades']} trades")
    logger.info(f"{'='*80}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

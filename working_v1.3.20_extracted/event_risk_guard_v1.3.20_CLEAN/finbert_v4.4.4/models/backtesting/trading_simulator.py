"""
Trading Simulator with Realistic Costs
=======================================

Simulates realistic trading with commission, slippage, and position management.

Key Features:
- Commission modeling (default 0.1%)
- Slippage modeling (default 0.05%)
- Confidence-based position sizing (5-20% of capital)
- Complete trade history tracking
- Comprehensive performance metrics (Sharpe, Sortino, max drawdown, win rate, profit factor)

Author: FinBERT v4.0
Date: October 2024
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade"""
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    shares: float
    position_type: str  # 'LONG' or 'SHORT'
    entry_confidence: float
    entry_commission: float
    exit_commission: Optional[float]
    pnl: Optional[float]
    return_pct: Optional[float]
    status: str  # 'OPEN' or 'CLOSED'


class TradingSimulator:
    """
    Simulates trading with realistic costs and position management
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,  # 0.1%
        slippage_rate: float = 0.0005,   # 0.05%
        max_position_size: float = 0.20,   # 20% of capital
        stop_loss_pct: float = 0.03,  # 3% stop loss
        take_profit_pct: float = 0.10  # 10% take profit
    ):
        """
        Initialize trading simulator
        
        Args:
            initial_capital: Starting capital
            commission_rate: Commission as fraction (e.g., 0.001 = 0.1%)
            slippage_rate: Slippage as fraction (e.g., 0.0005 = 0.05%)
            max_position_size: Maximum position size as fraction of capital
            stop_loss_pct: Stop loss threshold as fraction (e.g., 0.03 = 3%)
            take_profit_pct: Take profit threshold as fraction (e.g., 0.10 = 10%)
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        
        # Trading state
        self.positions = []  # Currently open positions
        self.closed_trades = []  # Completed trades
        self.equity_curve = []  # Daily equity values
        self.daily_returns = []  # Daily return percentages
        self.equity_history = []  # Detailed equity tracking for charts
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_commission_paid = 0.0
        
        logger.info(
            f"Trading simulator initialized (capital=${initial_capital:,.2f}, "
            f"commission={commission_rate*100:.2f}%, slippage={slippage_rate*100:.3f}%)"
        )
    
    def _check_stop_loss_take_profit(self, timestamp: datetime, current_price: float) -> List[Dict]:
        """
        Check all open positions for stop-loss and take-profit triggers
        
        Args:
            timestamp: Current timestamp
            current_price: Current market price
            
        Returns:
            List of closed positions
        """
        closed_positions = []
        
        for position in list(self.positions):  # Use list() to allow modification during iteration
            entry_price = position.entry_price
            
            # Calculate P&L percentage
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Check stop-loss
            if pnl_pct <= -self.stop_loss_pct:
                logger.info(
                    f"Stop-loss triggered at {timestamp}: "
                    f"Entry ${entry_price:.2f}, Current ${current_price:.2f}, "
                    f"Loss {pnl_pct:.2%}"
                )
                result = self._close_single_position(position, timestamp, current_price, reason='STOP_LOSS')
                closed_positions.append(result)
            
            # Check take-profit
            elif pnl_pct >= self.take_profit_pct:
                logger.info(
                    f"Take-profit triggered at {timestamp}: "
                    f"Entry ${entry_price:.2f}, Current ${current_price:.2f}, "
                    f"Profit {pnl_pct:.2%}"
                )
                result = self._close_single_position(position, timestamp, current_price, reason='TAKE_PROFIT')
                closed_positions.append(result)
        
        return closed_positions
    
    def execute_signal(
        self,
        timestamp: datetime,
        signal: str,
        price: float,
        confidence: float,
        actual_price: Optional[float] = None
    ) -> Dict:
        """
        Execute trading signal
        
        Args:
            timestamp: Signal timestamp
            signal: 'BUY', 'SELL', or 'HOLD'
            price: Predicted/target price
            confidence: Signal confidence (0-1)
            actual_price: Actual market price (if different from price)
        
        Returns:
            Dictionary with execution details
        """
        # Use actual price if provided, otherwise use predicted price
        execution_price = actual_price if actual_price is not None else price
        
        # Check stop-loss and take-profit BEFORE executing new signal
        stopped_positions = self._check_stop_loss_take_profit(timestamp, execution_price)
        
        # Apply slippage (simulates market impact and timing)
        if signal == 'BUY':
            execution_price *= (1 + self.slippage_rate)
        elif signal == 'SELL':
            execution_price *= (1 - self.slippage_rate)
        
        # Execute based on signal
        if signal == 'BUY':
            result = self._open_long_position(timestamp, execution_price, confidence)
        elif signal == 'SELL':
            result = self._close_positions(timestamp, execution_price)
        else:  # HOLD
            result = {
                'action': 'HOLD',
                'reason': 'No signal',
                'timestamp': timestamp
            }
        
        # Add stopped positions to result
        if stopped_positions:
            result['stopped_positions'] = stopped_positions
        
        # Track equity after each signal
        self._track_equity(timestamp, execution_price)
        
        return result
    
    def _track_equity(self, timestamp: datetime, current_price: float):
        """Track equity value at each timestamp for charts"""
        # Calculate current equity (cash + position values)
        positions_value = sum([pos.shares * current_price for pos in self.positions])
        total_equity = self.current_capital + positions_value
        
        # Store equity history
        self.equity_history.append({
            'timestamp': timestamp.strftime('%Y-%m-%d') if isinstance(timestamp, datetime) else str(timestamp),
            'equity': round(total_equity, 2),
            'cash': round(self.current_capital, 2),
            'positions_value': round(positions_value, 2)
        })
    
    def _open_long_position(
        self,
        timestamp: datetime,
        price: float,
        confidence: float
    ) -> Dict:
        """
        Open a long position
        
        Args:
            timestamp: Entry timestamp
            price: Entry price
            confidence: Signal confidence
        
        Returns:
            Execution details
        """
        try:
            # Calculate position size based on confidence
            position_value = self._calculate_position_size(confidence)
            
            # Check if we have enough capital
            if position_value > self.current_capital:
                return {
                    'action': 'REJECTED',
                    'reason': 'Insufficient capital',
                    'timestamp': timestamp
                }
            
            # Calculate shares and commission
            shares = position_value / price
            commission = position_value * self.commission_rate
            
            # Deduct from capital
            self.current_capital -= (position_value + commission)
            self.total_commission_paid += commission
            
            # Create position
            trade = Trade(
                entry_date=timestamp,
                exit_date=None,
                entry_price=price,
                exit_price=None,
                shares=shares,
                position_type='LONG',
                entry_confidence=confidence,
                entry_commission=commission,
                exit_commission=None,
                pnl=None,
                return_pct=None,
                status='OPEN'
            )
            
            self.positions.append(trade)
            self.total_trades += 1
            
            logger.info(
                f"Opened LONG position: {shares:.2f} shares @ ${price:.2f} "
                f"(confidence={confidence:.2f}, commission=${commission:.2f})"
            )
            
            return {
                'action': 'BUY',
                'timestamp': timestamp,
                'price': price,
                'shares': shares,
                'value': position_value,
                'commission': commission,
                'remaining_capital': self.current_capital
            }
            
        except Exception as e:
            logger.error(f"Error opening long position: {e}")
            return {
                'action': 'ERROR',
                'reason': str(e),
                'timestamp': timestamp
            }
    
    def _close_single_position(
        self,
        position,
        timestamp: datetime,
        price: float,
        reason: str = 'SIGNAL'
    ) -> Dict:
        """
        Close a single position
        
        Args:
            position: Position object to close
            timestamp: Exit timestamp
            price: Exit price
            reason: Reason for closing ('SIGNAL', 'STOP_LOSS', 'TAKE_PROFIT')
        
        Returns:
            Execution details
        """
        try:
            # Calculate exit value
            exit_value = position.shares * price
            exit_commission = exit_value * self.commission_rate
            
            # Calculate P&L
            exit_proceeds = exit_value - exit_commission
            pnl = exit_proceeds - (position.shares * position.entry_price)
            return_pct = pnl / (position.shares * position.entry_price)
            
            # Update capital
            self.current_capital += exit_proceeds
            self.total_commission_paid += exit_commission
            
            # Update position
            position.exit_date = timestamp
            position.exit_price = price
            position.exit_commission = exit_commission
            position.pnl = pnl
            position.return_pct = return_pct
            position.status = 'CLOSED'
            
            # Track win/loss
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            # Move to closed trades
            self.closed_trades.append(position)
            
            # Remove from open positions
            self.positions.remove(position)
            
            logger.info(
                f"Closed position ({reason}): {position.shares:.2f} shares @ ${price:.2f} "
                f"(Entry ${position.entry_price:.2f}, P&L=${pnl:.2f}, return={return_pct*100:.2f}%)"
            )
            
            return {
                'action': 'CLOSE',
                'reason': reason,
                'timestamp': timestamp,
                'price': price,
                'pnl': pnl,
                'return_pct': return_pct
            }
            
        except Exception as e:
            logger.error(f"Error closing single position: {e}")
            return {'action': 'ERROR', 'error': str(e)}
    
    def _close_positions(
        self,
        timestamp: datetime,
        price: float
    ) -> Dict:
        """
        Close all open positions
        
        Args:
            timestamp: Exit timestamp
            price: Exit price
        
        Returns:
            Execution details
        """
        if not self.positions:
            return {
                'action': 'NO_POSITION',
                'reason': 'No open positions to close',
                'timestamp': timestamp
            }
        
        total_pnl = 0.0
        closed_count = 0
        
        for position in self.positions:
            try:
                # Calculate exit value
                exit_value = position.shares * price
                exit_commission = exit_value * self.commission_rate
                
                # Calculate P&L
                entry_cost = position.shares * position.entry_price + position.entry_commission
                exit_proceeds = exit_value - exit_commission
                pnl = exit_proceeds - (position.shares * position.entry_price)
                return_pct = pnl / (position.shares * position.entry_price)
                
                # Update capital
                self.current_capital += exit_proceeds
                self.total_commission_paid += exit_commission
                
                # Update position
                position.exit_date = timestamp
                position.exit_price = price
                position.exit_commission = exit_commission
                position.pnl = pnl
                position.return_pct = return_pct
                position.status = 'CLOSED'
                
                # Track win/loss
                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                
                # Move to closed trades
                self.closed_trades.append(position)
                
                total_pnl += pnl
                closed_count += 1
                
                logger.info(
                    f"Closed LONG position: {position.shares:.2f} shares @ ${price:.2f} "
                    f"(P&L=${pnl:.2f}, return={return_pct*100:.2f}%)"
                )
                
            except Exception as e:
                logger.error(f"Error closing position: {e}")
        
        # Clear positions
        self.positions = []
        
        return {
            'action': 'SELL',
            'timestamp': timestamp,
            'price': price,
            'positions_closed': closed_count,
            'total_pnl': total_pnl,
            'remaining_capital': self.current_capital
        }
    
    def _calculate_position_size(self, confidence: float) -> float:
        """
        Calculate position size based on confidence
        
        Position sizing rules:
        - Low confidence (50-60%): 5% of capital
        - Medium confidence (60-80%): 5-15% of capital
        - High confidence (80-100%): 15-20% of capital
        
        Args:
            confidence: Signal confidence (0-1)
        
        Returns:
            Position value in dollars
        """
        # Base position size (5% of capital)
        base_size = self.current_capital * 0.05
        
        # Scale based on confidence
        if confidence > 0.5:
            # Scale from 1x to 4x base size (5% to 20%)
            confidence_factor = (confidence - 0.5) / 0.5  # 0 to 1
            max_multiplier = 4.0  # Up to 4x base size
            multiplier = 1 + (max_multiplier - 1) * confidence_factor
            position_size = base_size * multiplier
        else:
            # Very low confidence, use minimal position
            position_size = base_size * 0.5
        
        # Cap at maximum position size
        max_size = self.current_capital * self.max_position_size
        position_size = min(position_size, max_size)
        
        return position_size
    
    def update_equity(self, timestamp: datetime, current_prices: Dict[str, float]):
        """
        Update equity curve based on current market prices
        
        Args:
            timestamp: Current timestamp
            current_prices: Dictionary mapping symbols to prices
        """
        # Calculate current equity (capital + open position values)
        open_position_value = 0.0
        
        for position in self.positions:
            # Assuming we're tracking symbol in position (would need to add)
            # For now, use the entry price as approximation
            open_position_value += position.shares * position.entry_price
        
        total_equity = self.current_capital + open_position_value
        
        # Track equity
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': total_equity,
            'cash': self.current_capital,
            'position_value': open_position_value
        })
        
        # Calculate daily return
        if len(self.equity_curve) > 1:
            prev_equity = self.equity_curve[-2]['equity']
            daily_return = (total_equity - prev_equity) / prev_equity
            self.daily_returns.append(daily_return)
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            if not self.closed_trades:
                return {'error': 'No closed trades to analyze'}
            
            # Basic metrics
            final_equity = self.current_capital + sum(
                pos.shares * pos.entry_price for pos in self.positions
            )
            
            total_return = (final_equity - self.initial_capital) / self.initial_capital
            
            # Trade statistics
            total_trades = len(self.closed_trades)
            win_rate = self.winning_trades / total_trades if total_trades > 0 else 0
            
            # Calculate average win/loss
            winning_trades = [t for t in self.closed_trades if t.pnl > 0]
            losing_trades = [t for t in self.closed_trades if t.pnl <= 0]
            
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            
            # Profit factor
            total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
            total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Returns-based metrics
            if self.daily_returns:
                returns_array = np.array(self.daily_returns)
                
                # Sharpe Ratio (annualized, assuming 252 trading days)
                avg_return = np.mean(returns_array)
                std_return = np.std(returns_array)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
                
                # Sortino Ratio (downside risk only)
                downside_returns = returns_array[returns_array < 0]
                downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
                sortino_ratio = (avg_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0
                
            else:
                sharpe_ratio = 0
                sortino_ratio = 0
            
            # Max Drawdown
            if self.equity_curve:
                equity_series = pd.Series([e['equity'] for e in self.equity_curve])
                running_max = equity_series.expanding().max()
                drawdown = (equity_series - running_max) / running_max
                max_drawdown = drawdown.min()
            else:
                max_drawdown = 0
            
            # Average hold time
            hold_times = [
                (t.exit_date - t.entry_date).days
                for t in self.closed_trades
                if t.exit_date
            ]
            avg_hold_time = np.mean(hold_times) if hold_times else 0
            
            return {
                'initial_capital': self.initial_capital,
                'final_equity': final_equity,
                'total_return': total_return,
                'total_return_pct': total_return * 100,
                'total_trades': total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown * 100,
                'total_commission_paid': self.total_commission_paid,
                'avg_hold_time_days': avg_hold_time,
                'current_cash': self.current_capital,
                'open_positions': len(self.positions),
                'charts': self.get_chart_data()  # Add chart data
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {'error': str(e)}
    
    def get_equity_curve_df(self) -> pd.DataFrame:
        """Get equity curve as DataFrame"""
        if not self.equity_curve:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)
        return df
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get all trades as DataFrame"""
        if not self.closed_trades:
            return pd.DataFrame()
        
        trades_data = [asdict(trade) for trade in self.closed_trades]
        df = pd.DataFrame(trades_data)
        return df
    
    def get_chart_data(self) -> Dict:
        """
        Generate all chart data for visualization
        
        Returns:
            Dictionary with data for all charts
        """
        return {
            'equity_curve': self.get_equity_curve_data(),
            'drawdown_curve': self.get_drawdown_data(),
            'trade_distribution': self.get_trade_distribution(),
            'monthly_returns': self.get_monthly_returns()
        }
    
    def get_equity_curve_data(self) -> List[Dict]:
        """Get equity curve data for chart"""
        return self.equity_history if self.equity_history else []
    
    def get_drawdown_data(self) -> List[Dict]:
        """Calculate drawdown at each point"""
        if not self.equity_history:
            return []
        
        drawdowns = []
        peak = self.equity_history[0]['equity']
        
        for point in self.equity_history:
            equity = point['equity']
            if equity > peak:
                peak = equity
            drawdown = (equity - peak) / peak * 100 if peak > 0 else 0
            drawdowns.append({
                'timestamp': point['timestamp'],
                'drawdown': round(drawdown, 2),
                'peak': round(peak, 2),
                'equity': round(equity, 2)
            })
        
        return drawdowns
    
    def get_trade_distribution(self) -> Dict:
        """Get P&L distribution by buckets"""
        buckets = {
            'large_loss': 0,     # < -5%
            'medium_loss': 0,    # -5% to -2%
            'small_loss': 0,     # -2% to 0%
            'small_win': 0,      # 0% to +2%
            'medium_win': 0,     # +2% to +5%
            'large_win': 0       # > +5%
        }
        
        bucket_details = {
            'large_loss': [],
            'medium_loss': [],
            'small_loss': [],
            'small_win': [],
            'medium_win': [],
            'large_win': []
        }
        
        for trade in self.closed_trades:
            if trade.return_pct is None:
                continue
            
            ret = trade.return_pct * 100
            trade_info = {
                'return': round(ret, 2),
                'pnl': round(trade.pnl, 2),
                'entry_date': trade.entry_date.strftime('%Y-%m-%d') if isinstance(trade.entry_date, datetime) else str(trade.entry_date),
                'exit_date': trade.exit_date.strftime('%Y-%m-%d') if isinstance(trade.exit_date, datetime) else str(trade.exit_date)
            }
            
            if ret < -5:
                buckets['large_loss'] += 1
                bucket_details['large_loss'].append(trade_info)
            elif ret < -2:
                buckets['medium_loss'] += 1
                bucket_details['medium_loss'].append(trade_info)
            elif ret < 0:
                buckets['small_loss'] += 1
                bucket_details['small_loss'].append(trade_info)
            elif ret < 2:
                buckets['small_win'] += 1
                bucket_details['small_win'].append(trade_info)
            elif ret < 5:
                buckets['medium_win'] += 1
                bucket_details['medium_win'].append(trade_info)
            else:
                buckets['large_win'] += 1
                bucket_details['large_win'].append(trade_info)
        
        return {
            'buckets': buckets,
            'details': bucket_details,
            'labels': ['<-5%', '-5 to -2%', '-2 to 0%', '0 to +2%', '+2 to +5%', '>+5%']
        }
    
    def get_monthly_returns(self) -> Dict:
        """Calculate monthly returns"""
        if not self.equity_history or len(self.equity_history) < 2:
            return {'months': [], 'returns': [], 'years': []}
        
        monthly_data = {}
        prev_month_equity = self.equity_history[0]['equity']
        prev_month_key = None
        
        for point in self.equity_history:
            date_str = point['timestamp']
            try:
                if isinstance(date_str, str):
                    date = pd.to_datetime(date_str)
                else:
                    date = date_str
                
                month_key = date.strftime('%Y-%m')
                
                # If month changed, calculate return
                if prev_month_key and month_key != prev_month_key:
                    ret = (point['equity'] - prev_month_equity) / prev_month_equity * 100 if prev_month_equity > 0 else 0
                    monthly_data[prev_month_key] = round(ret, 2)
                    prev_month_equity = point['equity']
                
                prev_month_key = month_key
                
            except Exception as e:
                logger.error(f"Error processing date {date_str}: {e}")
                continue
        
        # Add last month
        if prev_month_key and self.equity_history[-1]['equity'] != prev_month_equity:
            ret = (self.equity_history[-1]['equity'] - prev_month_equity) / prev_month_equity * 100 if prev_month_equity > 0 else 0
            monthly_data[prev_month_key] = round(ret, 2)
        
        # Format for frontend
        months = list(monthly_data.keys())
        returns = list(monthly_data.values())
        years = list(set([m.split('-')[0] for m in months]))
        
        return {
            'months': months,
            'returns': returns,
            'years': sorted(years),
            'data': monthly_data
        }
    
    def reset(self):
        """Reset simulator to initial state"""
        self.current_capital = self.initial_capital
        self.positions = []
        self.closed_trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.equity_history = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_commission_paid = 0.0
        
        logger.info("Trading simulator reset to initial state")

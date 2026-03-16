"""
Realistic Backtest Engine with Stop-Loss and Risk Management
=============================================================

Enhanced backtesting engine that simulates real-world trading with:
- Stop-loss orders (fixed and trailing)
- Take-profit orders
- Position sizing based on risk percentage
- Maximum portfolio heat (total risk exposure)
- Maximum position limits
- Realistic order execution
- Risk-adjusted performance metrics

Author: FinBERT v4.4.4 Enhanced
Date: December 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order types"""
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"


class StopLossType(Enum):
    """Stop-loss types"""
    FIXED_PERCENT = "FIXED_PERCENT"  # Fixed percentage from entry
    FIXED_PRICE = "FIXED_PRICE"      # Fixed price level
    TRAILING_PERCENT = "TRAILING_PERCENT"  # Trailing % from peak
    ATR_BASED = "ATR_BASED"          # ATR multiple from entry


@dataclass
class RealisticPosition:
    """Enhanced position with risk management"""
    symbol: str
    shares: float
    entry_price: float
    entry_date: datetime
    current_price: float
    
    # Stop-loss parameters
    stop_loss_price: float
    stop_loss_type: StopLossType
    trailing_stop_percent: Optional[float] = None
    highest_price_since_entry: Optional[float] = None
    
    # Take-profit parameters
    take_profit_price: Optional[float] = None
    take_profit_enabled: bool = False
    
    # Risk parameters
    risk_amount: float = 0.0  # Dollar amount at risk
    risk_percent: float = 0.0  # Percent of portfolio at risk
    position_size_percent: float = 0.0  # Percent of portfolio
    
    # Performance tracking
    current_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    max_favorable_excursion: float = 0.0  # Best unrealized profit
    max_adverse_excursion: float = 0.0    # Worst unrealized loss
    
    # Trade metadata
    signal_confidence: float = 0.0
    allocation_pct: float = 0.0
    hold_days: int = 0


class RealisticBacktestEngine:
    """
    Realistic backtesting engine with comprehensive risk management
    
    Simulates real-world trading with stop-losses, take-profits,
    position sizing, and portfolio risk limits.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        
        # Risk Management Parameters
        risk_per_trade_percent: float = 1.0,  # Max 1% of capital per trade
        max_portfolio_heat: float = 6.0,      # Max 6% total portfolio at risk
        max_position_size_percent: float = 20.0,  # Max 20% per position
        max_positions: int = 10,              # Max 10 simultaneous positions
        
        # Stop-Loss Parameters
        stop_loss_percent: float = 2.0,       # Default 2% stop-loss
        stop_loss_type: StopLossType = StopLossType.FIXED_PERCENT,
        trailing_stop_percent: Optional[float] = None,  # None = disabled
        atr_multiplier: float = 2.0,          # For ATR-based stops
        
        # Take-Profit Parameters
        use_take_profit: bool = True,
        risk_reward_ratio: float = 2.0,       # 2:1 reward:risk ratio
        
        # Execution Parameters
        commission_rate: float = 0.001,       # 0.1% commission
        slippage_rate: float = 0.0005,        # 0.05% slippage
        
        # Allocation Strategy
        allocation_strategy: str = 'risk_based',  # 'risk_based', 'equal', 'custom'
        custom_allocations: Optional[Dict[str, float]] = None
    ):
        """
        Initialize realistic backtest engine
        
        Args:
            initial_capital: Starting capital
            risk_per_trade_percent: Maximum risk per trade (% of capital)
            max_portfolio_heat: Maximum total portfolio risk (% of capital)
            max_position_size_percent: Maximum size per position (% of capital)
            max_positions: Maximum number of simultaneous positions
            stop_loss_percent: Default stop-loss percentage
            stop_loss_type: Type of stop-loss to use
            trailing_stop_percent: Trailing stop percentage (if enabled)
            atr_multiplier: ATR multiplier for ATR-based stops
            use_take_profit: Enable take-profit orders
            risk_reward_ratio: Target risk:reward ratio for take-profits
            commission_rate: Commission as fraction
            slippage_rate: Slippage as fraction
            allocation_strategy: How to size positions
            custom_allocations: Custom allocation weights
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Risk management
        self.risk_per_trade_percent = risk_per_trade_percent
        self.max_portfolio_heat = max_portfolio_heat
        self.max_position_size_percent = max_position_size_percent
        self.max_positions = max_positions
        
        # Stop-loss configuration
        self.default_stop_loss_percent = stop_loss_percent
        self.stop_loss_type = stop_loss_type
        self.trailing_stop_percent = trailing_stop_percent
        self.atr_multiplier = atr_multiplier
        
        # Take-profit configuration
        self.use_take_profit = use_take_profit
        self.risk_reward_ratio = risk_reward_ratio
        
        # Execution
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # Allocation
        self.allocation_strategy = allocation_strategy
        self.custom_allocations = custom_allocations or {}
        
        # Portfolio state
        self.positions: Dict[str, RealisticPosition] = {}
        self.cash = initial_capital
        self.portfolio_history = []
        
        # Trade tracking
        self.all_trades = []
        self.trades_by_symbol = {}
        self.stopped_out_trades = []  # Trades closed by stop-loss
        self.take_profit_trades = []  # Trades closed by take-profit
        
        # Performance tracking
        self.total_commission_paid = 0.0
        self.daily_returns = []
        self.current_portfolio_heat = 0.0  # Current total risk
        
        # Statistics
        self.stop_loss_count = 0
        self.take_profit_count = 0
        self.manual_exit_count = 0
        
        logger.info(
            f"Realistic backtest engine initialized:\n"
            f"  Capital: ${initial_capital:,.2f}\n"
            f"  Risk per trade: {risk_per_trade_percent}%\n"
            f"  Max portfolio heat: {max_portfolio_heat}%\n"
            f"  Stop-loss: {stop_loss_type.value} ({stop_loss_percent}%)\n"
            f"  Take-profit: {'Enabled' if use_take_profit else 'Disabled'} "
            f"({risk_reward_ratio}:1 R:R)"
        )
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: float,
        signal_confidence: float,
        target_allocation: float = None
    ) -> Tuple[float, float, float]:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            stop_loss_price: Stop-loss price
            signal_confidence: Signal confidence (0-1)
            target_allocation: Target allocation weight (optional)
        
        Returns:
            Tuple of (shares, position_value, risk_amount)
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            logger.warning(f"{symbol}: Zero risk per share, using default 2%")
            risk_per_share = entry_price * 0.02
        
        # Calculate maximum risk amount for this trade
        portfolio_value = self.get_portfolio_value({})
        max_risk_amount = portfolio_value * (self.risk_per_trade_percent / 100.0)
        
        # Adjust risk based on confidence (higher confidence = more risk)
        confidence_multiplier = 0.5 + (signal_confidence * 0.5)  # 0.5 to 1.0
        risk_amount = max_risk_amount * confidence_multiplier
        
        # Calculate shares based on risk
        shares_by_risk = risk_amount / risk_per_share
        position_value_by_risk = shares_by_risk * entry_price
        
        # Apply maximum position size limit
        max_position_value = portfolio_value * (self.max_position_size_percent / 100.0)
        
        if position_value_by_risk > max_position_value:
            logger.info(
                f"{symbol}: Position capped at {self.max_position_size_percent}% "
                f"(was ${position_value_by_risk:,.0f}, now ${max_position_value:,.0f})"
            )
            position_value = max_position_value
            shares = position_value / entry_price
            actual_risk = shares * risk_per_share
        else:
            position_value = position_value_by_risk
            shares = shares_by_risk
            actual_risk = risk_amount
        
        # Ensure we have enough cash
        required_cash = position_value * (1 + self.commission_rate)
        if required_cash > self.cash:
            # Scale down position to available cash
            affordable_value = self.cash / (1 + self.commission_rate)
            shares = affordable_value / entry_price
            position_value = shares * entry_price
            actual_risk = shares * risk_per_share
            logger.info(
                f"{symbol}: Position scaled down to available cash "
                f"(${position_value:,.2f})"
            )
        
        return shares, position_value, actual_risk
    
    def check_portfolio_heat_limit(self, additional_risk: float) -> bool:
        """
        Check if adding a new position would exceed portfolio heat limit
        
        Args:
            additional_risk: Additional risk from new position
        
        Returns:
            True if position can be opened, False otherwise
        """
        portfolio_value = self.get_portfolio_value({})
        new_total_risk = self.current_portfolio_heat + additional_risk
        new_heat_percent = (new_total_risk / portfolio_value) * 100
        
        if new_heat_percent > self.max_portfolio_heat:
            logger.warning(
                f"Portfolio heat limit exceeded: {new_heat_percent:.1f}% > "
                f"{self.max_portfolio_heat}% (risk=${new_total_risk:,.0f})"
            )
            return False
        
        return True
    
    def calculate_stop_loss_price(
        self,
        symbol: str,
        entry_price: float,
        direction: str,
        atr_value: Optional[float] = None
    ) -> float:
        """
        Calculate stop-loss price based on configured strategy
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            atr_value: ATR value (for ATR-based stops)
        
        Returns:
            Stop-loss price
        """
        if self.stop_loss_type == StopLossType.FIXED_PERCENT:
            # Fixed percentage from entry
            if direction == 'LONG':
                return entry_price * (1 - self.default_stop_loss_percent / 100.0)
            else:
                return entry_price * (1 + self.default_stop_loss_percent / 100.0)
        
        elif self.stop_loss_type == StopLossType.ATR_BASED:
            # ATR-based stop
            if atr_value is None:
                logger.warning(f"{symbol}: No ATR provided, using fixed stop")
                return self.calculate_stop_loss_price(symbol, entry_price, direction, None)
            
            if direction == 'LONG':
                return entry_price - (atr_value * self.atr_multiplier)
            else:
                return entry_price + (atr_value * self.atr_multiplier)
        
        elif self.stop_loss_type == StopLossType.TRAILING_PERCENT:
            # Initial trailing stop (will be updated dynamically)
            if self.trailing_stop_percent is None:
                logger.warning(f"{symbol}: Trailing stop not configured, using fixed")
                return self.calculate_stop_loss_price(symbol, entry_price, direction, None)
            
            if direction == 'LONG':
                return entry_price * (1 - self.trailing_stop_percent / 100.0)
            else:
                return entry_price * (1 + self.trailing_stop_percent / 100.0)
        
        else:
            # Default to fixed percent
            if direction == 'LONG':
                return entry_price * (1 - self.default_stop_loss_percent / 100.0)
            else:
                return entry_price * (1 + self.default_stop_loss_percent / 100.0)
    
    def calculate_take_profit_price(
        self,
        entry_price: float,
        stop_loss_price: float,
        direction: str
    ) -> Optional[float]:
        """
        Calculate take-profit price based on risk:reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop-loss price
            direction: 'LONG' or 'SHORT'
        
        Returns:
            Take-profit price or None if disabled
        """
        if not self.use_take_profit:
            return None
        
        risk_per_share = abs(entry_price - stop_loss_price)
        reward_per_share = risk_per_share * self.risk_reward_ratio
        
        if direction == 'LONG':
            return entry_price + reward_per_share
        else:
            return entry_price - reward_per_share
    
    def update_trailing_stops(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ):
        """
        Update trailing stop-loss levels for all positions
        
        Args:
            timestamp: Current timestamp
            current_prices: Current prices for all symbols
        """
        for symbol, pos in self.positions.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Track highest price since entry (for trailing stops)
            if pos.highest_price_since_entry is None:
                pos.highest_price_since_entry = current_price
            elif current_price > pos.highest_price_since_entry:
                pos.highest_price_since_entry = current_price
                
                # Update trailing stop if enabled
                if pos.stop_loss_type == StopLossType.TRAILING_PERCENT and pos.trailing_stop_percent:
                    new_stop = pos.highest_price_since_entry * (
                        1 - pos.trailing_stop_percent / 100.0
                    )
                    
                    # Only move stop up, never down
                    if new_stop > pos.stop_loss_price:
                        old_stop = pos.stop_loss_price
                        pos.stop_loss_price = new_stop
                        logger.debug(
                            f"{symbol}: Trailing stop updated ${old_stop:.2f} → "
                            f"${new_stop:.2f} (peak=${pos.highest_price_since_entry:.2f})"
                        )
            
            # Track max favorable/adverse excursion
            unrealized_pnl = (current_price - pos.entry_price) * pos.shares
            if unrealized_pnl > pos.max_favorable_excursion:
                pos.max_favorable_excursion = unrealized_pnl
            if unrealized_pnl < pos.max_adverse_excursion:
                pos.max_adverse_excursion = unrealized_pnl
    
    def check_stop_losses(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Check if any positions hit stop-loss levels
        
        Args:
            timestamp: Current timestamp
            current_prices: Current prices
        
        Returns:
            List of stop-loss executions
        """
        stop_loss_executions = []
        positions_to_close = []
        
        for symbol, pos in self.positions.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Check stop-loss (for LONG positions)
            if current_price <= pos.stop_loss_price:
                logger.info(
                    f"🛑 STOP-LOSS HIT: {symbol} @ ${current_price:.2f} "
                    f"(stop=${pos.stop_loss_price:.2f}, entry=${pos.entry_price:.2f})"
                )
                
                execution = self._close_position_at_stop_loss(
                    timestamp, symbol, pos, current_price
                )
                stop_loss_executions.append(execution)
                positions_to_close.append(symbol)
                self.stop_loss_count += 1
        
        # Remove closed positions
        for symbol in positions_to_close:
            del self.positions[symbol]
        
        return stop_loss_executions
    
    def check_take_profits(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Check if any positions hit take-profit levels
        
        Args:
            timestamp: Current timestamp
            current_prices: Current prices
        
        Returns:
            List of take-profit executions
        """
        take_profit_executions = []
        positions_to_close = []
        
        for symbol, pos in self.positions.items():
            if not pos.take_profit_enabled or pos.take_profit_price is None:
                continue
            
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Check take-profit (for LONG positions)
            if current_price >= pos.take_profit_price:
                logger.info(
                    f"🎯 TAKE-PROFIT HIT: {symbol} @ ${current_price:.2f} "
                    f"(target=${pos.take_profit_price:.2f}, entry=${pos.entry_price:.2f})"
                )
                
                execution = self._close_position_at_take_profit(
                    timestamp, symbol, pos, current_price
                )
                take_profit_executions.append(execution)
                positions_to_close.append(symbol)
                self.take_profit_count += 1
        
        # Remove closed positions
        for symbol in positions_to_close:
            del self.positions[symbol]
        
        return take_profit_executions
    
    def _close_position_at_stop_loss(
        self,
        timestamp: datetime,
        symbol: str,
        position: RealisticPosition,
        execution_price: float
    ) -> Dict:
        """Close position at stop-loss level"""
        # Apply slippage (worse execution at stop-loss)
        execution_price = execution_price * (1 - self.slippage_rate)
        
        # Calculate proceeds
        sell_value = position.shares * execution_price
        commission = sell_value * self.commission_rate
        proceeds = sell_value - commission
        
        # Calculate P&L
        cost_basis = position.shares * position.entry_price
        pnl = proceeds - cost_basis
        return_pct = pnl / cost_basis if cost_basis > 0 else 0
        
        # Update cash and portfolio heat
        self.cash += proceeds
        self.total_commission_paid += commission
        self.current_portfolio_heat -= position.risk_amount
        
        # Track trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'exit_type': 'STOP_LOSS',
            'shares': position.shares,
            'entry_price': position.entry_price,
            'exit_price': execution_price,
            'stop_loss_price': position.stop_loss_price,
            'value': sell_value,
            'commission': commission,
            'pnl': pnl,
            'return_pct': return_pct,
            'entry_date': position.entry_date,
            'exit_date': timestamp,
            'hold_days': (timestamp - position.entry_date).days,
            'signal_confidence': position.signal_confidence,
            'risk_amount': position.risk_amount,
            'risk_percent': position.risk_percent,
            'max_favorable_excursion': position.max_favorable_excursion,
            'max_adverse_excursion': position.max_adverse_excursion
        }
        
        self.all_trades.append(trade)
        self.stopped_out_trades.append(trade)
        
        if symbol not in self.trades_by_symbol:
            self.trades_by_symbol[symbol] = []
        self.trades_by_symbol[symbol].append(trade)
        
        return trade
    
    def _close_position_at_take_profit(
        self,
        timestamp: datetime,
        symbol: str,
        position: RealisticPosition,
        execution_price: float
    ) -> Dict:
        """Close position at take-profit level"""
        # Apply slippage (slightly better execution at take-profit)
        execution_price = execution_price * (1 - self.slippage_rate * 0.5)
        
        # Calculate proceeds
        sell_value = position.shares * execution_price
        commission = sell_value * self.commission_rate
        proceeds = sell_value - commission
        
        # Calculate P&L
        cost_basis = position.shares * position.entry_price
        pnl = proceeds - cost_basis
        return_pct = pnl / cost_basis if cost_basis > 0 else 0
        
        # Update cash and portfolio heat
        self.cash += proceeds
        self.total_commission_paid += commission
        self.current_portfolio_heat -= position.risk_amount
        
        # Track trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'exit_type': 'TAKE_PROFIT',
            'shares': position.shares,
            'entry_price': position.entry_price,
            'exit_price': execution_price,
            'take_profit_price': position.take_profit_price,
            'value': sell_value,
            'commission': commission,
            'pnl': pnl,
            'return_pct': return_pct,
            'entry_date': position.entry_date,
            'exit_date': timestamp,
            'hold_days': (timestamp - position.entry_date).days,
            'signal_confidence': position.signal_confidence,
            'risk_amount': position.risk_amount,
            'risk_percent': position.risk_percent,
            'max_favorable_excursion': position.max_favorable_excursion,
            'max_adverse_excursion': position.max_adverse_excursion
        }
        
        self.all_trades.append(trade)
        self.take_profit_trades.append(trade)
        
        if symbol not in self.trades_by_symbol:
            self.trades_by_symbol[symbol] = []
        self.trades_by_symbol[symbol].append(trade)
        
        return trade
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate current portfolio value"""
        positions_value = sum(
            pos.shares * current_prices.get(pos.symbol, pos.current_price)
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def get_risk_metrics(self) -> Dict:
        """
        Calculate comprehensive risk metrics
        
        Returns:
            Dictionary of risk metrics
        """
        if not self.all_trades:
            return {'error': 'No trades to analyze'}
        
        closed_trades = [t for t in self.all_trades if 'pnl' in t]
        
        # Stop-loss analysis
        stop_loss_trades = [t for t in closed_trades if t.get('exit_type') == 'STOP_LOSS']
        take_profit_trades = [t for t in closed_trades if t.get('exit_type') == 'TAKE_PROFIT']
        
        # Calculate metrics
        metrics = {
            'total_trades': len(closed_trades),
            'stop_loss_exits': len(stop_loss_trades),
            'take_profit_exits': len(take_profit_trades),
            'stop_loss_rate': len(stop_loss_trades) / len(closed_trades) * 100 if closed_trades else 0,
            'take_profit_rate': len(take_profit_trades) / len(closed_trades) * 100 if closed_trades else 0,
            
            'avg_risk_per_trade': np.mean([t.get('risk_amount', 0) for t in closed_trades]),
            'max_risk_taken': max([t.get('risk_amount', 0) for t in closed_trades]) if closed_trades else 0,
            'avg_risk_percent': np.mean([t.get('risk_percent', 0) for t in closed_trades]),
            
            'avg_stop_loss_hit': np.mean([t['pnl'] for t in stop_loss_trades]) if stop_loss_trades else 0,
            'avg_take_profit_hit': np.mean([t['pnl'] for t in take_profit_trades]) if take_profit_trades else 0,
            
            'realized_risk_reward': self._calculate_realized_risk_reward(closed_trades),
            'expectancy': self._calculate_expectancy(closed_trades),
            
            'max_portfolio_heat_reached': max([abs(t.get('risk_percent', 0)) for t in closed_trades]) if closed_trades else 0,
        }
        
        return metrics
    
    def _calculate_realized_risk_reward(self, trades: List[Dict]) -> float:
        """Calculate actual realized risk:reward ratio"""
        if not trades:
            return 0
        
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] < 0]
        
        if not losses:
            return 999.0  # All winners
        
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losses]))
        
        return avg_win / avg_loss if avg_loss > 0 else 0
    
    def _calculate_expectancy(self, trades: List[Dict]) -> float:
        """Calculate system expectancy ($ per trade)"""
        if not trades:
            return 0
        
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] < 0]
        
        win_rate = len(wins) / len(trades)
        loss_rate = 1 - win_rate
        
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losses])) if losses else 0
        
        return (win_rate * avg_win) - (loss_rate * avg_loss)
    
    def reset(self):
        """Reset engine to initial state"""
        self.current_capital = self.initial_capital
        self.cash = self.initial_capital
        self.positions = {}
        self.portfolio_history = []
        self.all_trades = []
        self.trades_by_symbol = {}
        self.stopped_out_trades = []
        self.take_profit_trades = []
        self.total_commission_paid = 0.0
        self.daily_returns = []
        self.current_portfolio_heat = 0.0
        self.stop_loss_count = 0
        self.take_profit_count = 0
        self.manual_exit_count = 0
        
        logger.info("Realistic backtest engine reset")

"""
Portfolio Backtesting Engine
=============================

Manages multi-stock portfolio backtesting with capital allocation, correlation analysis,
and portfolio-level performance metrics.

Key Features:
- Multi-stock portfolio management
- Capital allocation strategies (equal-weight, risk-parity, custom)
- Correlation analysis and diversification metrics
- Portfolio rebalancing
- Aggregated performance metrics
- Portfolio-level risk management

Author: FinBERT v4.0
Date: November 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class PortfolioPosition:
    """Represents a position in the portfolio"""
    symbol: str
    shares: float
    entry_price: float
    entry_date: datetime
    current_price: float
    current_value: float
    unrealized_pnl: float
    allocation_pct: float
    
    # Phase 1 & 2: Risk management fields
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
    risk_amount: float = 0.0
    position_value: float = 0.0


class PortfolioBacktestEngine:
    """
    Portfolio backtesting engine for multi-stock strategies
    
    Manages capital allocation across multiple stocks and tracks
    portfolio-level performance metrics.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        allocation_strategy: str = 'equal',  # 'equal', 'risk_parity', 'custom', 'risk_based'
        custom_allocations: Optional[Dict[str, float]] = None,
        rebalance_frequency: str = 'monthly',  # 'never', 'weekly', 'monthly', 'quarterly'
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
        
        # Phase 1 & 2: Risk management parameters
        enable_stop_loss: bool = True,
        stop_loss_percent: float = 2.0,
        enable_take_profit: bool = True,
        risk_reward_ratio: float = 2.0,
        risk_per_trade_percent: float = 1.0,
        max_portfolio_heat: float = 6.0,
        max_position_size_percent: float = 20.0
    ):
        """
        Initialize portfolio backtesting engine
        
        Args:
            initial_capital: Starting capital
            allocation_strategy: How to allocate capital across stocks
            custom_allocations: Custom allocations (symbol -> weight), must sum to 1.0
            rebalance_frequency: How often to rebalance portfolio
            commission_rate: Commission as fraction (0.001 = 0.1%)
            slippage_rate: Slippage as fraction (0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.allocation_strategy = allocation_strategy
        self.custom_allocations = custom_allocations or {}
        self.rebalance_frequency = rebalance_frequency
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # Phase 1 & 2: Risk management parameters
        self.enable_stop_loss = enable_stop_loss
        self.stop_loss_percent = stop_loss_percent
        self.enable_take_profit = enable_take_profit
        self.risk_reward_ratio = risk_reward_ratio
        self.risk_per_trade_percent = risk_per_trade_percent
        self.max_portfolio_heat = max_portfolio_heat
        self.max_position_size_percent = max_position_size_percent
        
        # Portfolio state
        self.positions: Dict[str, PortfolioPosition] = {}
        self.cash = initial_capital
        self.portfolio_history = []  # Track portfolio value over time
        self.rebalance_dates = []  # Track when rebalances occurred
        
        # Trade tracking
        self.all_trades = []  # All trades across all symbols
        self.trades_by_symbol = {}  # Trades organized by symbol
        
        # Performance tracking
        self.total_commission_paid = 0.0
        self.daily_returns = []
        
        # Phase 1 & 2: Risk tracking
        self.current_portfolio_heat = 0.0
        self.stop_loss_exits = 0
        self.take_profit_exits = 0
        self.stopped_out_trades = []
        self.take_profit_trades = []
        
        logger.info(
            f"Portfolio engine initialized (capital=${initial_capital:,.2f}, "
            f"strategy={allocation_strategy}, rebalance={rebalance_frequency})"
        )
        
        # Phase 1 & 2: Log risk management settings
        if enable_stop_loss or enable_take_profit:
            logger.info(
                f"Risk Management Enabled: "
                f"stop_loss={stop_loss_percent}%, "
                f"take_profit={enable_take_profit} ({risk_reward_ratio}:1 R:R), "
                f"risk_per_trade={risk_per_trade_percent}%, "
                f"max_heat={max_portfolio_heat}%"
            )
    
    def calculate_target_allocations(
        self,
        symbols: List[str],
        historical_returns: Optional[Dict[str, pd.Series]] = None
    ) -> Dict[str, float]:
        """
        Calculate target allocation weights for each symbol
        
        Args:
            symbols: List of stock symbols
            historical_returns: Optional historical returns for risk-parity
        
        Returns:
            Dictionary mapping symbol to allocation weight (0-1)
        """
        if self.allocation_strategy == 'equal':
            # Equal weight across all symbols
            weight = 1.0 / len(symbols)
            return {symbol: weight for symbol in symbols}
        
        elif self.allocation_strategy == 'custom':
            # Use custom allocations
            if not self.custom_allocations:
                logger.warning("Custom allocations not provided, using equal weight")
                weight = 1.0 / len(symbols)
                return {symbol: weight for symbol in symbols}
            
            # Validate custom allocations
            total_weight = sum(self.custom_allocations.get(s, 0) for s in symbols)
            if abs(total_weight - 1.0) > 0.01:
                logger.warning(
                    f"Custom allocations sum to {total_weight}, normalizing to 1.0"
                )
                return {
                    s: self.custom_allocations.get(s, 0) / total_weight 
                    for s in symbols
                }
            
            return {s: self.custom_allocations.get(s, 0) for s in symbols}
        
        elif self.allocation_strategy == 'risk_parity':
            # Risk parity: allocate inversely to volatility
            if not historical_returns:
                logger.warning(
                    "Historical returns not provided for risk parity, using equal weight"
                )
                weight = 1.0 / len(symbols)
                return {symbol: weight for symbol in symbols}
            
            # Calculate volatilities
            volatilities = {}
            for symbol in symbols:
                if symbol in historical_returns:
                    vol = historical_returns[symbol].std()
                    volatilities[symbol] = vol if vol > 0 else 1.0
                else:
                    volatilities[symbol] = 1.0
            
            # Inverse volatility weighting
            inv_vols = {s: 1.0 / volatilities[s] for s in symbols}
            total_inv_vol = sum(inv_vols.values())
            
            return {s: inv_vols[s] / total_inv_vol for s in symbols}
        
        else:
            logger.error(f"Unknown allocation strategy: {self.allocation_strategy}")
            weight = 1.0 / len(symbols)
            return {symbol: weight for symbol in symbols}
    
    def execute_portfolio_signals(
        self,
        timestamp: datetime,
        signals: Dict[str, Dict],
        current_prices: Dict[str, float],
        target_allocations: Dict[str, float]
    ) -> Dict:
        """
        Execute trading signals for all symbols in portfolio
        
        Args:
            timestamp: Current timestamp
            signals: Dictionary mapping symbol to signal dict (prediction, confidence)
            current_prices: Dictionary mapping symbol to current price
            target_allocations: Target allocation weights
        
        Returns:
            Execution summary
        """
        executions = {}
        
        # Phase 1: Check stop-losses and take-profits FIRST
        if self.enable_stop_loss:
            stop_loss_exits = self._check_stop_losses(timestamp, current_prices)
            for exit_execution in stop_loss_exits:
                executions[exit_execution['symbol']] = exit_execution
        
        if self.enable_take_profit:
            take_profit_exits = self._check_take_profits(timestamp, current_prices)
            for exit_execution in take_profit_exits:
                executions[exit_execution['symbol']] = exit_execution
        
        for symbol in signals.keys():
            if symbol not in current_prices:
                logger.warning(f"No price data for {symbol}, skipping")
                continue
            
            signal = signals[symbol]
            price = current_prices[symbol]
            
            # Execute signal for this symbol
            execution = self._execute_symbol_signal(
                timestamp=timestamp,
                symbol=symbol,
                signal=signal['prediction'],
                confidence=signal['confidence'],
                price=price,
                target_allocation=target_allocations.get(symbol, 0)
            )
            
            executions[symbol] = execution
        
        # Update portfolio value
        self._update_portfolio_value(timestamp, current_prices)
        
        return {
            'timestamp': timestamp,
            'executions': executions,
            'portfolio_value': self.get_portfolio_value(current_prices),
            'cash': self.cash,
            'positions': len(self.positions)
        }
    
    def _execute_symbol_signal(
        self,
        timestamp: datetime,
        symbol: str,
        signal: str,
        confidence: float,
        price: float,
        target_allocation: float
    ) -> Dict:
        """
        Execute signal for a single symbol
        
        Args:
            timestamp: Current timestamp
            symbol: Stock symbol
            signal: 'BUY', 'SELL', or 'HOLD'
            confidence: Signal confidence
            price: Current price
            target_allocation: Target allocation weight for this symbol
        
        Returns:
            Execution details
        """
        # Apply slippage
        if signal == 'BUY':
            execution_price = price * (1 + self.slippage_rate)
        elif signal == 'SELL':
            execution_price = price * (1 - self.slippage_rate)
        else:
            return {'action': 'HOLD', 'symbol': symbol, 'timestamp': timestamp}
        
        # Handle BUY signals
        if signal == 'BUY':
            # Phase 2: Calculate stop-loss price first
            stop_loss_price = execution_price * (1 - self.stop_loss_percent / 100.0)
            
            # Calculate position size based on strategy
            portfolio_value = self.get_portfolio_value({symbol: price for symbol in self.positions})
            total_value = portfolio_value + self.cash
            
            if self.allocation_strategy == 'risk_based':
                # Phase 2: Risk-based position sizing
                risk_per_share = execution_price - stop_loss_price
                max_risk_dollars = total_value * (self.risk_per_trade_percent / 100.0)
                
                # Adjust risk based on confidence
                confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
                risk_dollars = max_risk_dollars * confidence_multiplier
                
                # Calculate shares based on risk
                shares = risk_dollars / risk_per_share if risk_per_share > 0 else 0
                invest_amount = shares * execution_price
                
                # Apply max position size limit
                max_position_value = total_value * (self.max_position_size_percent / 100.0)
                if invest_amount > max_position_value:
                    logger.info(
                        f"{symbol}: Position capped at {self.max_position_size_percent}% "
                        f"(${invest_amount:,.0f} -> ${max_position_value:,.0f})"
                    )
                    invest_amount = max_position_value
                    shares = invest_amount / execution_price
                    risk_dollars = shares * risk_per_share
                
                # Check portfolio heat limit
                new_heat = self.current_portfolio_heat + risk_dollars
                max_heat = total_value * (self.max_portfolio_heat / 100.0)
                if new_heat > max_heat:
                    logger.warning(
                        f"{symbol}: Portfolio heat limit exceeded: "
                        f"${new_heat:,.0f} > ${max_heat:,.0f} (skipping trade)"
                    )
                    return {'action': 'REJECTED', 'reason': 'PORTFOLIO_HEAT_LIMIT', 'symbol': symbol, 'timestamp': timestamp}
            else:
                # Traditional allocation-based sizing
                target_value = total_value * target_allocation
                current_value = 0
                if symbol in self.positions:
                    current_value = self.positions[symbol].shares * price
                
                invest_amount = target_value - current_value
                shares = invest_amount / execution_price if invest_amount > 0 else 0
                risk_per_share = execution_price - stop_loss_price
                risk_dollars = shares * risk_per_share
            
            # Only invest if positive and we have cash
            if invest_amount > 0 and invest_amount <= self.cash:
                commission = invest_amount * self.commission_rate
                total_cost = invest_amount + commission
                
                if total_cost <= self.cash:
                    # Execute buy
                    self.cash -= total_cost
                    self.total_commission_paid += commission
                    
                    # Phase 2: Calculate take-profit price
                    take_profit_price = 0.0
                    if self.enable_take_profit:
                        risk_per_share = execution_price - stop_loss_price
                        reward_per_share = risk_per_share * self.risk_reward_ratio
                        take_profit_price = execution_price + reward_per_share
                    
                    # Update or create position
                    if symbol in self.positions:
                        pos = self.positions[symbol]
                        old_shares = pos.shares
                        old_value = pos.shares * pos.entry_price
                        new_shares = old_shares + shares
                        new_value = old_value + invest_amount
                        pos.shares = new_shares
                        pos.entry_price = new_value / new_shares  # Average price
                        pos.current_price = price
                        pos.current_value = new_shares * price
                        pos.unrealized_pnl = pos.current_value - new_value
                        # Phase 1 & 2: Update risk management fields
                        pos.stop_loss_price = pos.entry_price * (1 - self.stop_loss_percent / 100.0)
                        pos.take_profit_price = take_profit_price
                        pos.risk_amount = pos.risk_amount + risk_dollars
                        pos.position_value = new_value
                    else:
                        self.positions[symbol] = PortfolioPosition(
                            symbol=symbol,
                            shares=shares,
                            entry_price=execution_price,
                            entry_date=timestamp,
                            current_price=price,
                            current_value=shares * price,
                            unrealized_pnl=0,
                            allocation_pct=target_allocation * 100,
                            # Phase 1 & 2: Set risk management fields
                            stop_loss_price=stop_loss_price,
                            take_profit_price=take_profit_price,
                            risk_amount=risk_dollars,
                            position_value=invest_amount
                        )
                    
                    # Phase 2: Update portfolio heat
                    self.current_portfolio_heat += risk_dollars
                    
                    # Track trade
                    trade = {
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'action': 'BUY',
                        'shares': shares,
                        'price': execution_price,
                        'value': invest_amount,
                        'commission': commission
                    }
                    self.all_trades.append(trade)
                    
                    if symbol not in self.trades_by_symbol:
                        self.trades_by_symbol[symbol] = []
                    self.trades_by_symbol[symbol].append(trade)
                    
                    # Phase 1 & 2: Enhanced logging
                    logger.info(
                        f"BUY {symbol}: {shares:.2f} shares @ ${execution_price:.2f} "
                        f"(commission=${commission:.2f}, stop=${stop_loss_price:.2f}, "
                        f"target=${take_profit_price:.2f}, risk=${risk_dollars:.2f})"
                    )
                    
                    return {
                        'action': 'BUY',
                        'symbol': symbol,
                        'shares': shares,
                        'price': execution_price,
                        'commission': commission,
                        'timestamp': timestamp
                    }
        
        # Handle SELL signals
        elif signal == 'SELL' and symbol in self.positions:
            pos = self.positions[symbol]
            
            # Sell entire position
            sell_value = pos.shares * execution_price
            commission = sell_value * self.commission_rate
            proceeds = sell_value - commission
            
            # Calculate P&L
            cost_basis = pos.shares * pos.entry_price
            pnl = proceeds - cost_basis
            return_pct = pnl / cost_basis if cost_basis > 0 else 0
            
            # Execute sell
            self.cash += proceeds
            self.total_commission_paid += commission
            
            # Phase 2: Update portfolio heat
            if hasattr(pos, 'risk_amount'):
                self.current_portfolio_heat -= pos.risk_amount
            
            # Track trade
            trade = {
                'timestamp': timestamp,
                'symbol': symbol,
                'action': 'SELL',
                'shares': pos.shares,
                'price': execution_price,
                'value': sell_value,
                'commission': commission,
                'pnl': pnl,
                'return_pct': return_pct,
                'entry_date': pos.entry_date,
                'exit_date': timestamp,
                'hold_days': (timestamp - pos.entry_date).days
            }
            self.all_trades.append(trade)
            
            if symbol not in self.trades_by_symbol:
                self.trades_by_symbol[symbol] = []
            self.trades_by_symbol[symbol].append(trade)
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(
                f"SELL {symbol}: {pos.shares:.2f} shares @ ${execution_price:.2f} "
                f"(P&L=${pnl:.2f}, return={return_pct*100:.1f}%)"
            )
            
            return {
                'action': 'SELL',
                'symbol': symbol,
                'shares': pos.shares,
                'price': execution_price,
                'commission': commission,
                'pnl': pnl,
                'return_pct': return_pct,
                'timestamp': timestamp
            }
        
        return {'action': 'HOLD', 'symbol': symbol, 'timestamp': timestamp}
    
    def _update_portfolio_value(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ):
        """Update portfolio value and tracking"""
        # Update position values
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                pos.current_price = current_prices[symbol]
                pos.current_value = pos.shares * pos.current_price
                cost_basis = pos.shares * pos.entry_price
                pos.unrealized_pnl = pos.current_value - cost_basis
        
        # Calculate total portfolio value
        total_value = self.get_portfolio_value(current_prices)
        
        # Calculate return
        daily_return = 0
        if len(self.portfolio_history) > 0:
            prev_value = self.portfolio_history[-1]['total_value']
            daily_return = (total_value - prev_value) / prev_value if prev_value > 0 else 0
            self.daily_returns.append(daily_return)
        
        # Store portfolio snapshot
        self.portfolio_history.append({
            'timestamp': timestamp.strftime('%Y-%m-%d') if isinstance(timestamp, datetime) else str(timestamp),
            'total_value': round(total_value, 2),
            'cash': round(self.cash, 2),
            'positions_value': round(sum(p.current_value for p in self.positions.values()), 2),
            'num_positions': len(self.positions),
            'daily_return': round(daily_return * 100, 4) if daily_return else 0
        })
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate current portfolio value"""
        positions_value = sum(
            pos.shares * current_prices.get(pos.symbol, pos.current_price)
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def calculate_correlation_matrix(
        self,
        returns_data: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for portfolio stocks
        
        Args:
            returns_data: Dictionary mapping symbol to returns series
        
        Returns:
            Correlation matrix DataFrame
        """
        if not returns_data:
            return pd.DataFrame()
        
        # Combine returns into DataFrame
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate correlation
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix
    
    def calculate_diversification_metrics(
        self,
        correlation_matrix: pd.DataFrame,
        allocations: Dict[str, float]
    ) -> Dict:
        """
        Calculate portfolio diversification metrics
        
        Args:
            correlation_matrix: Correlation matrix
            allocations: Current allocations
        
        Returns:
            Diversification metrics
        """
        if correlation_matrix.empty:
            return {'error': 'No correlation data'}
        
        # Average correlation
        avg_correlation = correlation_matrix.values[
            np.triu_indices_from(correlation_matrix.values, k=1)
        ].mean()
        
        # Diversification ratio
        # Perfect diversification = 1/N, no diversification = 1
        n_stocks = len(allocations)
        diversification_ratio = 1 / (1 + (n_stocks - 1) * avg_correlation)
        
        # Effective number of stocks (inverse Herfindahl index)
        weights = np.array(list(allocations.values()))
        effective_stocks = 1 / np.sum(weights ** 2)
        
        return {
            'avg_correlation': round(avg_correlation, 4),
            'diversification_ratio': round(diversification_ratio, 4),
            'effective_num_stocks': round(effective_stocks, 2),
            'max_correlation': round(correlation_matrix.values.max(), 4),
            'min_correlation': round(correlation_matrix.values[
                correlation_matrix.values < 1
            ].min(), 4)
        }
    
    def calculate_portfolio_metrics(self) -> Dict:
        """
        Calculate comprehensive portfolio performance metrics
        
        Returns:
            Portfolio metrics dictionary
        """
        if not self.portfolio_history:
            return {'error': 'No portfolio history'}
        
        # Basic metrics
        initial_value = self.initial_capital
        final_value = self.portfolio_history[-1]['total_value']
        total_return = (final_value - initial_value) / initial_value
        
        # Extract equity curve
        equity_values = [p['total_value'] for p in self.portfolio_history]
        
        # Sharpe Ratio
        if len(self.daily_returns) > 0:
            returns_array = np.array(self.daily_returns)
            avg_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            
            # Sortino Ratio
            downside_returns = returns_array[returns_array < 0]
            downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
            sortino_ratio = (avg_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        else:
            sharpe_ratio = 0
            sortino_ratio = 0
        
        # Max Drawdown
        equity_series = pd.Series(equity_values)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Trade statistics
        closed_trades = [t for t in self.all_trades if 'pnl' in t]
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Per-symbol breakdown
        symbols_performance = {}
        for symbol in self.trades_by_symbol.keys():
            symbol_trades = [t for t in self.trades_by_symbol[symbol] if 'pnl' in t]
            if symbol_trades:
                symbol_pnl = sum(t['pnl'] for t in symbol_trades)
                symbol_return = sum(t['return_pct'] for t in symbol_trades) / len(symbol_trades)
                symbols_performance[symbol] = {
                    'total_pnl': round(symbol_pnl, 2),
                    'avg_return': round(symbol_return * 100, 2),
                    'num_trades': len(symbol_trades),
                    'wins': len([t for t in symbol_trades if t['pnl'] > 0]),
                    'losses': len([t for t in symbol_trades if t['pnl'] <= 0])
                }
        
        # Phase 1 & 2: Calculate risk management metrics
        stop_loss_rate = (self.stop_loss_exits / len(closed_trades) * 100) if closed_trades else 0
        take_profit_rate = (self.take_profit_exits / len(closed_trades) * 100) if closed_trades else 0
        
        # Calculate realized risk:reward ratio
        wins = [t for t in closed_trades if t['pnl'] > 0]
        losses = [t for t in closed_trades if t['pnl'] < 0]
        avg_win_amt = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss_amt = abs(np.mean([t['pnl'] for t in losses])) if losses else 0
        realized_rr = avg_win_amt / avg_loss_amt if avg_loss_amt > 0 else 0
        
        # Calculate expectancy
        expectancy = (win_rate * avg_win_amt) - ((1 - win_rate) * avg_loss_amt) if closed_trades else 0
        
        return {
            'initial_capital': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(self.all_trades),
            'closed_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_commission_paid': self.total_commission_paid,
            'symbols_performance': symbols_performance,
            'num_symbols': len(set(t['symbol'] for t in self.all_trades)),
            'avg_positions': np.mean([p['num_positions'] for p in self.portfolio_history]),
            'charts': self.get_portfolio_charts(),
            # Phase 1 & 2: Risk management metrics
            'stop_loss_exits': self.stop_loss_exits,
            'take_profit_exits': self.take_profit_exits,
            'stop_loss_rate': stop_loss_rate,
            'take_profit_rate': take_profit_rate,
            'realized_risk_reward': realized_rr,
            'expectancy': expectancy,
            'risk_management_enabled': self.enable_stop_loss or self.enable_take_profit
        }
    
    def get_portfolio_charts(self) -> Dict:
        """Generate chart data for portfolio visualization"""
        return {
            'equity_curve': self.portfolio_history,
            'drawdown_curve': self._calculate_drawdown_series(),
            'allocation_pie': self._get_allocation_breakdown(),
            'contribution_analysis': self._get_contribution_analysis(),
            'monthly_returns': self._calculate_monthly_returns()
        }
    
    def _calculate_drawdown_series(self) -> List[Dict]:
        """Calculate drawdown at each point in time"""
        if not self.portfolio_history:
            return []
        
        drawdowns = []
        peak = self.portfolio_history[0]['total_value']
        
        for point in self.portfolio_history:
            value = point['total_value']
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak * 100 if peak > 0 else 0
            drawdowns.append({
                'timestamp': point['timestamp'],
                'drawdown': round(drawdown, 2),
                'peak': round(peak, 2),
                'value': round(value, 2)
            })
        
        return drawdowns
    
    def _get_allocation_breakdown(self) -> Dict:
        """Get current allocation breakdown by symbol"""
        if not self.positions:
            return {'symbols': [], 'allocations': [], 'values': []}
        
        total_positions_value = sum(p.current_value for p in self.positions.values())
        
        symbols = []
        allocations = []
        values = []
        
        for symbol, pos in self.positions.items():
            symbols.append(symbol)
            alloc_pct = (pos.current_value / total_positions_value * 100) if total_positions_value > 0 else 0
            allocations.append(round(alloc_pct, 2))
            values.append(round(pos.current_value, 2))
        
        return {
            'symbols': symbols,
            'allocations': allocations,
            'values': values,
            'total_value': round(total_positions_value, 2)
        }
    
    def _get_contribution_analysis(self) -> Dict:
        """Analyze each symbol's contribution to portfolio returns (realized + unrealized)"""
        contributions = {}
        
        # Calculate realized P&L from closed trades
        for symbol in self.trades_by_symbol.keys():
            symbol_trades = [t for t in self.trades_by_symbol[symbol] if 'pnl' in t]
            realized_pnl = sum(t['pnl'] for t in symbol_trades) if symbol_trades else 0
            contributions[symbol] = realized_pnl
        
        # Add unrealized P&L from open positions
        for symbol, position in self.positions.items():
            if symbol not in contributions:
                contributions[symbol] = 0
            contributions[symbol] += position.unrealized_pnl
        
        # Round final contributions
        contributions = {k: round(v, 2) for k, v in contributions.items()}
        
        return {
            'symbols': list(contributions.keys()),
            'contributions': list(contributions.values())
        }
    
    def _calculate_monthly_returns(self) -> Dict:
        """Calculate monthly returns for heatmap"""
        if not self.portfolio_history or len(self.portfolio_history) < 2:
            return {'months': [], 'returns': [], 'years': []}
        
        monthly_data = {}
        prev_month_value = self.portfolio_history[0]['total_value']
        prev_month_key = None
        
        for point in self.portfolio_history:
            date_str = point['timestamp']
            try:
                date = pd.to_datetime(date_str)
                month_key = date.strftime('%Y-%m')
                
                if prev_month_key and month_key != prev_month_key:
                    ret = (point['total_value'] - prev_month_value) / prev_month_value * 100 if prev_month_value > 0 else 0
                    monthly_data[prev_month_key] = round(ret, 2)
                    prev_month_value = point['total_value']
                
                prev_month_key = month_key
            except:
                continue
        
        # Add last month
        if prev_month_key and self.portfolio_history[-1]['total_value'] != prev_month_value:
            ret = (self.portfolio_history[-1]['total_value'] - prev_month_value) / prev_month_value * 100 if prev_month_value > 0 else 0
            monthly_data[prev_month_key] = round(ret, 2)
        
        return {
            'months': list(monthly_data.keys()),
            'returns': list(monthly_data.values()),
            'years': sorted(list(set(m.split('-')[0] for m in monthly_data.keys()))),
            'data': monthly_data
        }
    
    def _check_stop_losses(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Phase 1: Check if any positions hit stop-loss levels
        
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
            
            # Check stop-loss
            if hasattr(pos, 'stop_loss_price') and pos.stop_loss_price > 0:
                if current_price <= pos.stop_loss_price:
                    logger.info(
                        f"🛑 STOP-LOSS HIT: {symbol} @ ${current_price:.2f} "
                        f"(stop=${pos.stop_loss_price:.2f}, entry=${pos.entry_price:.2f})"
                    )
                    
                    # Execute stop-loss exit
                    execution_price = current_price * (1 - self.slippage_rate)  # Worse execution
                    sell_value = pos.shares * execution_price
                    commission = sell_value * self.commission_rate
                    proceeds = sell_value - commission
                    
                    # Calculate P&L
                    cost_basis = pos.shares * pos.entry_price
                    pnl = proceeds - cost_basis
                    return_pct = pnl / cost_basis if cost_basis > 0 else 0
                    
                    # Update cash
                    self.cash += proceeds
                    self.total_commission_paid += commission
                    
                    # Track trade
                    trade = {
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'action': 'SELL',
                        'exit_type': 'STOP_LOSS',
                        'shares': pos.shares,
                        'entry_price': pos.entry_price,
                        'exit_price': execution_price,
                        'stop_loss_price': pos.stop_loss_price,
                        'value': sell_value,
                        'commission': commission,
                        'pnl': pnl,
                        'return_pct': return_pct,
                        'entry_date': pos.entry_date,
                        'exit_date': timestamp,
                        'hold_days': (timestamp - pos.entry_date).days,
                        'risk_amount': getattr(pos, 'risk_amount', 0)
                    }
                    
                    self.all_trades.append(trade)
                    self.stopped_out_trades.append(trade)
                    self.stop_loss_exits += 1
                    
                    if symbol not in self.trades_by_symbol:
                        self.trades_by_symbol[symbol] = []
                    self.trades_by_symbol[symbol].append(trade)
                    
                    stop_loss_executions.append(trade)
                    positions_to_close.append(symbol)
        
        # Remove closed positions
        for symbol in positions_to_close:
            if hasattr(self.positions[symbol], 'risk_amount'):
                self.current_portfolio_heat -= self.positions[symbol].risk_amount
            del self.positions[symbol]
        
        return stop_loss_executions
    
    def _check_take_profits(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Phase 2: Check if any positions hit take-profit levels
        
        Args:
            timestamp: Current timestamp
            current_prices: Current prices
        
        Returns:
            List of take-profit executions
        """
        take_profit_executions = []
        positions_to_close = []
        
        for symbol, pos in self.positions.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Check take-profit
            if hasattr(pos, 'take_profit_price') and pos.take_profit_price > 0:
                if current_price >= pos.take_profit_price:
                    logger.info(
                        f"🎯 TAKE-PROFIT HIT: {symbol} @ ${current_price:.2f} "
                        f"(target=${pos.take_profit_price:.2f}, entry=${pos.entry_price:.2f})"
                    )
                    
                    # Execute take-profit exit
                    execution_price = current_price * (1 - self.slippage_rate * 0.5)  # Better execution
                    sell_value = pos.shares * execution_price
                    commission = sell_value * self.commission_rate
                    proceeds = sell_value - commission
                    
                    # Calculate P&L
                    cost_basis = pos.shares * pos.entry_price
                    pnl = proceeds - cost_basis
                    return_pct = pnl / cost_basis if cost_basis > 0 else 0
                    
                    # Update cash
                    self.cash += proceeds
                    self.total_commission_paid += commission
                    
                    # Track trade
                    trade = {
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'action': 'SELL',
                        'exit_type': 'TAKE_PROFIT',
                        'shares': pos.shares,
                        'entry_price': pos.entry_price,
                        'exit_price': execution_price,
                        'take_profit_price': pos.take_profit_price,
                        'value': sell_value,
                        'commission': commission,
                        'pnl': pnl,
                        'return_pct': return_pct,
                        'entry_date': pos.entry_date,
                        'exit_date': timestamp,
                        'hold_days': (timestamp - pos.entry_date).days,
                        'risk_amount': getattr(pos, 'risk_amount', 0)
                    }
                    
                    self.all_trades.append(trade)
                    self.take_profit_trades.append(trade)
                    self.take_profit_exits += 1
                    
                    if symbol not in self.trades_by_symbol:
                        self.trades_by_symbol[symbol] = []
                    self.trades_by_symbol[symbol].append(trade)
                    
                    take_profit_executions.append(trade)
                    positions_to_close.append(symbol)
        
        # Remove closed positions
        for symbol in positions_to_close:
            if hasattr(self.positions[symbol], 'risk_amount'):
                self.current_portfolio_heat -= self.positions[symbol].risk_amount
            del self.positions[symbol]
        
        return take_profit_executions
    
    def reset(self):
        """Reset portfolio to initial state"""
        self.current_capital = self.initial_capital
        self.cash = self.initial_capital
        self.positions = {}
        self.portfolio_history = []
        self.rebalance_dates = []
        self.all_trades = []
        self.trades_by_symbol = {}
        self.total_commission_paid = 0.0
        self.daily_returns = []
        
        # Phase 1 & 2: Reset risk tracking
        self.current_portfolio_heat = 0.0
        self.stop_loss_exits = 0
        self.take_profit_exits = 0
        self.stopped_out_trades = []
        self.take_profit_trades = []
        
        logger.info("Portfolio engine reset to initial state")

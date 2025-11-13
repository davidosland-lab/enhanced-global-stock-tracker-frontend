"""
Paper Trading Engine
Simulates real trading with virtual money
"""

import logging
import yfinance as yf
from datetime import datetime
from typing import Dict, Optional, Tuple
from .trade_database import TradingDatabase

logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """
    Paper trading engine for simulated trading
    Uses real market data but virtual money
    """
    
    def __init__(self, db_path: str = "trading.db", 
                 commission_rate: float = 0.001,
                 slippage_rate: float = 0.0005):
        """
        Initialize paper trading engine
        
        Args:
            db_path: Path to trading database
            commission_rate: Commission as decimal (0.001 = 0.1%)
            slippage_rate: Slippage as decimal (0.0005 = 0.05%)
        """
        self.db = TradingDatabase(db_path)
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        logger.info(f"Paper trading engine initialized (commission: {commission_rate*100}%, slippage: {slippage_rate*100}%)")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current market price from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                logger.info(f"Fetched {symbol} price: ${current_price:.2f}")
                return current_price
            else:
                logger.warning(f"No price data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return None
    
    def calculate_costs(self, price: float, quantity: int, side: str) -> Tuple[float, float, float]:
        """
        Calculate total costs including commission and slippage
        
        Args:
            price: Current market price
            quantity: Number of shares
            side: 'BUY' or 'SELL'
            
        Returns:
            (total_cost, commission, slippage)
        """
        base_cost = price * quantity
        commission = base_cost * self.commission_rate
        
        # Slippage: BUY slightly higher, SELL slightly lower
        if side == 'BUY':
            slippage = base_cost * self.slippage_rate
            total_cost = base_cost + commission + slippage
        else:  # SELL
            slippage = base_cost * self.slippage_rate
            total_cost = base_cost - commission - slippage
        
        return total_cost, commission, slippage
    
    def place_market_order(self, symbol: str, side: str, quantity: int,
                          strategy: str = None, notes: str = None) -> Dict:
        """
        Place a market order (instant execution at current price)
        
        Args:
            symbol: Stock symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            strategy: Strategy name (optional)
            notes: Additional notes (optional)
            
        Returns:
            Order result dictionary
        """
        try:
            # Validate inputs
            if quantity <= 0:
                return {'success': False, 'error': 'Quantity must be positive'}
            
            if side not in ['BUY', 'SELL']:
                return {'success': False, 'error': 'Side must be BUY or SELL'}
            
            # Get current price
            current_price = self.get_current_price(symbol)
            if current_price is None:
                return {'success': False, 'error': f'Failed to fetch price for {symbol}'}
            
            # Calculate costs
            total_cost, commission, slippage = self.calculate_costs(current_price, quantity, side)
            
            # Get account info
            account = self.db.get_account()
            
            # Check sufficient funds for BUY
            if side == 'BUY':
                if total_cost > account['cash_balance']:
                    return {
                        'success': False,
                        'error': f'Insufficient funds. Need ${total_cost:.2f}, have ${account["cash_balance"]:.2f}'
                    }
            
            # Check if position exists for SELL
            if side == 'SELL':
                position = self.db.get_position(symbol)
                if position is None:
                    return {'success': False, 'error': f'No position in {symbol} to sell'}
                if position['quantity'] < quantity:
                    return {
                        'success': False,
                        'error': f'Insufficient shares. Have {position["quantity"]}, trying to sell {quantity}'
                    }
            
            # Execute trade
            if side == 'BUY':
                # Create trade record
                trade_id = self.db.create_trade(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    entry_price=current_price,
                    commission=commission,
                    slippage=slippage,
                    strategy=strategy,
                    notes=notes
                )
                
                # Update position
                self.db.upsert_position(symbol, quantity, current_price)
                
                # Update account cash
                new_cash = account['cash_balance'] - total_cost
                self.db.update_account(cash_balance=new_cash)
                
                logger.info(f"✅ BUY ORDER FILLED: {quantity} {symbol} @ ${current_price:.2f}")
                
                return {
                    'success': True,
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': quantity,
                    'price': current_price,
                    'total_cost': total_cost,
                    'commission': commission,
                    'slippage': slippage,
                    'timestamp': datetime.now().isoformat()
                }
            
            else:  # SELL
                # Get existing position
                position = self.db.get_position(symbol)
                
                # Find matching open trade(s) to close
                open_trades = self.db.get_trades(status='OPEN', symbol=symbol)
                
                # Close trade (simplified: close oldest first)
                if open_trades:
                    trade = open_trades[-1]  # Get oldest
                    pnl, pnl_percent = self.db.close_trade(
                        trade['trade_id'],
                        current_price,
                        commission,
                        slippage
                    )
                
                # Update position
                new_quantity = position['quantity'] - quantity
                if new_quantity == 0:
                    self.db.remove_position(symbol)
                else:
                    self.db.upsert_position(symbol, -quantity, position['avg_cost'])
                
                # Update account cash
                new_cash = account['cash_balance'] + total_cost
                self.db.update_account(cash_balance=new_cash)
                
                logger.info(f"✅ SELL ORDER FILLED: {quantity} {symbol} @ ${current_price:.2f}")
                
                return {
                    'success': True,
                    'trade_id': trade['trade_id'] if open_trades else None,
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': quantity,
                    'price': current_price,
                    'total_proceeds': total_cost,
                    'commission': commission,
                    'slippage': slippage,
                    'pnl': pnl if open_trades else None,
                    'pnl_percent': pnl_percent if open_trades else None,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_position(self, symbol: str) -> Dict:
        """
        Close entire position for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Result dictionary
        """
        position = self.db.get_position(symbol)
        
        if position is None:
            return {'success': False, 'error': f'No position in {symbol}'}
        
        quantity = position['quantity']
        return self.place_market_order(symbol, 'SELL', quantity, 
                                      strategy='Position Close',
                                      notes='Closed entire position')
    
    def update_all_positions(self) -> Dict:
        """
        Update current prices for all positions
        
        Returns:
            Summary of updates
        """
        positions = self.db.get_positions()
        updated = 0
        failed = []
        
        total_portfolio_value = 0
        
        for position in positions:
            symbol = position['symbol']
            current_price = self.get_current_price(symbol)
            
            if current_price:
                self.db.update_position_prices(symbol, current_price)
                total_portfolio_value += current_price * position['quantity']
                updated += 1
            else:
                failed.append(symbol)
        
        # Update account portfolio value
        account = self.db.get_account()
        total_value = account['cash_balance'] + total_portfolio_value
        total_pnl = total_value - account['initial_capital']
        total_pnl_percent = (total_pnl / account['initial_capital']) * 100 if account['initial_capital'] > 0 else 0
        
        self.db.update_account(
            portfolio_value=total_portfolio_value,
            total_value=total_value,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent
        )
        
        logger.info(f"Updated {updated} positions (Portfolio value: ${total_portfolio_value:.2f})")
        
        return {
            'success': True,
            'updated': updated,
            'failed': failed,
            'portfolio_value': total_portfolio_value,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent
        }
    
    def get_account_summary(self) -> Dict:
        """
        Get complete account summary with updated values
        
        Returns:
            Account summary dictionary
        """
        # Update all positions first
        self.update_all_positions()
        
        # Get updated account
        account = self.db.get_account()
        
        # Get positions
        positions = self.db.get_positions()
        
        # Get statistics
        stats = self.db.get_trade_statistics()
        
        return {
            'account': account,
            'positions': positions,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_account(self, initial_capital: float = 10000) -> Dict:
        """
        Reset account to initial state
        
        Args:
            initial_capital: Starting capital amount
            
        Returns:
            Confirmation dictionary
        """
        self.db.reset_account(initial_capital)
        logger.info(f"Account reset with ${initial_capital} capital")
        
        return {
            'success': True,
            'message': f'Account reset with ${initial_capital} capital',
            'initial_capital': initial_capital
        }

"""
Position Manager
Handles position tracking and management
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from .trade_database import TradingDatabase
from .paper_trading_engine import PaperTradingEngine

logger = logging.getLogger(__name__)


class PositionManager:
    """Manages open positions"""
    
    def __init__(self, paper_engine: PaperTradingEngine):
        """Initialize position manager"""
        self.engine = paper_engine
        self.db = paper_engine.db
        logger.info("Position manager initialized")
    
    def get_all_positions(self) -> Dict:
        """
        Get all current positions with updated prices
        
        Returns:
            Dictionary with positions
        """
        # Update prices first
        self.engine.update_all_positions()
        
        positions = self.db.get_positions()
        
        return {
            'success': True,
            'positions': positions,
            'count': len(positions),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_position(self, symbol: str) -> Dict:
        """
        Get specific position
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Position details
        """
        # Update price for this symbol
        current_price = self.engine.get_current_price(symbol)
        if current_price:
            self.db.update_position_prices(symbol, current_price)
        
        position = self.db.get_position(symbol)
        
        if position:
            return {
                'success': True,
                'position': position,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': f'No position in {symbol}'
            }
    
    def close_position(self, symbol: str) -> Dict:
        """
        Close entire position
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Close result
        """
        return self.engine.close_position(symbol)
    
    def adjust_position(self, symbol: str, quantity_change: int) -> Dict:
        """
        Adjust position size
        
        Args:
            symbol: Stock symbol
            quantity_change: Positive to add, negative to reduce
            
        Returns:
            Adjustment result
        """
        position = self.db.get_position(symbol)
        
        if position is None:
            return {'success': False, 'error': f'No position in {symbol}'}
        
        if quantity_change > 0:
            # Add to position
            return self.engine.place_market_order(
                symbol, 'BUY', quantity_change,
                strategy='Position Adjustment',
                notes=f'Increased position by {quantity_change} shares'
            )
        elif quantity_change < 0:
            # Reduce position
            quantity = abs(quantity_change)
            if quantity > position['quantity']:
                return {
                    'success': False,
                    'error': f'Cannot reduce by {quantity}, only have {position["quantity"]} shares'
                }
            
            return self.engine.place_market_order(
                symbol, 'SELL', quantity,
                strategy='Position Adjustment',
                notes=f'Reduced position by {quantity} shares'
            )
        else:
            return {'success': False, 'error': 'Quantity change cannot be zero'}
    
    def set_stop_loss(self, symbol: str, stop_price: float = None,
                      stop_percent: float = None) -> Dict:
        """
        Set stop-loss for position
        
        Args:
            symbol: Stock symbol
            stop_price: Absolute stop price
            stop_percent: Stop-loss as percentage below current (e.g., 0.03 for 3%)
            
        Returns:
            Confirmation
        """
        position = self.db.get_position(symbol)
        
        if position is None:
            return {'success': False, 'error': f'No position in {symbol}'}
        
        current_price = self.engine.get_current_price(symbol)
        if current_price is None:
            return {'success': False, 'error': f'Failed to fetch price for {symbol}'}
        
        # Calculate stop price
        if stop_price:
            final_stop_price = stop_price
        elif stop_percent:
            final_stop_price = current_price * (1 - stop_percent)
        else:
            return {'success': False, 'error': 'Must provide stop_price or stop_percent'}
        
        # Validate
        if final_stop_price >= current_price:
            return {
                'success': False,
                'error': f'Stop-loss price (${final_stop_price:.2f}) must be below current price (${current_price:.2f})'
            }
        
        # Update position with stop-loss
        conn = self.db.db.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE portfolio SET stop_loss_price = ?, updated_at = ?
            WHERE symbol = ?
        ''', (final_stop_price, datetime.now().isoformat(), symbol))
        conn.commit()
        conn.close()
        
        logger.info(f"Stop-loss set for {symbol}: ${final_stop_price:.2f} ({((current_price - final_stop_price)/current_price)*100:.1f}% below current)")
        
        return {
            'success': True,
            'symbol': symbol,
            'stop_loss_price': final_stop_price,
            'current_price': current_price,
            'stop_loss_percent': ((current_price - final_stop_price) / current_price) * 100
        }
    
    def set_take_profit(self, symbol: str, take_profit_price: float = None,
                       take_profit_percent: float = None) -> Dict:
        """
        Set take-profit for position
        
        Args:
            symbol: Stock symbol
            take_profit_price: Absolute take-profit price
            take_profit_percent: Take-profit as percentage above current (e.g., 0.10 for 10%)
            
        Returns:
            Confirmation
        """
        position = self.db.get_position(symbol)
        
        if position is None:
            return {'success': False, 'error': f'No position in {symbol}'}
        
        current_price = self.engine.get_current_price(symbol)
        if current_price is None:
            return {'success': False, 'error': f'Failed to fetch price for {symbol}'}
        
        # Calculate take-profit price
        if take_profit_price:
            final_tp_price = take_profit_price
        elif take_profit_percent:
            final_tp_price = current_price * (1 + take_profit_percent)
        else:
            return {'success': False, 'error': 'Must provide take_profit_price or take_profit_percent'}
        
        # Validate
        if final_tp_price <= current_price:
            return {
                'success': False,
                'error': f'Take-profit price (${final_tp_price:.2f}) must be above current price (${current_price:.2f})'
            }
        
        # Update position with take-profit
        conn = self.db.db.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE portfolio SET take_profit_price = ?, updated_at = ?
            WHERE symbol = ?
        ''', (final_tp_price, datetime.now().isoformat(), symbol))
        conn.commit()
        conn.close()
        
        logger.info(f"Take-profit set for {symbol}: ${final_tp_price:.2f} ({((final_tp_price - current_price)/current_price)*100:.1f}% above current)")
        
        return {
            'success': True,
            'symbol': symbol,
            'take_profit_price': final_tp_price,
            'current_price': current_price,
            'take_profit_percent': ((final_tp_price - current_price) / current_price) * 100
        }
    
    def check_stop_loss_take_profit(self) -> Dict:
        """
        Check all positions for stop-loss and take-profit triggers
        
        Returns:
            Summary of triggered orders
        """
        positions = self.db.get_positions()
        triggered = []
        
        for position in positions:
            symbol = position['symbol']
            current_price = self.engine.get_current_price(symbol)
            
            if current_price is None:
                continue
            
            # Check stop-loss
            if position['stop_loss_price'] and current_price <= position['stop_loss_price']:
                result = self.engine.close_position(symbol)
                if result['success']:
                    triggered.append({
                        'symbol': symbol,
                        'type': 'STOP_LOSS',
                        'trigger_price': position['stop_loss_price'],
                        'exit_price': current_price,
                        'result': result
                    })
                    logger.warning(f"🛑 STOP-LOSS TRIGGERED: {symbol} @ ${current_price:.2f}")
            
            # Check take-profit
            elif position['take_profit_price'] and current_price >= position['take_profit_price']:
                result = self.engine.close_position(symbol)
                if result['success']:
                    triggered.append({
                        'symbol': symbol,
                        'type': 'TAKE_PROFIT',
                        'trigger_price': position['take_profit_price'],
                        'exit_price': current_price,
                        'result': result
                    })
                    logger.info(f"🎯 TAKE-PROFIT HIT: {symbol} @ ${current_price:.2f}")
        
        return {
            'success': True,
            'triggered': triggered,
            'count': len(triggered)
        }

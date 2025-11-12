"""
Order Manager
Handles order creation, execution, and monitoring
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional
from .trade_database import TradingDatabase
from .paper_trading_engine import PaperTradingEngine

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Manages orders including limit orders and stop-loss/take-profit
    """
    
    def __init__(self, paper_engine: PaperTradingEngine):
        """
        Initialize order manager
        
        Args:
            paper_engine: PaperTradingEngine instance
        """
        self.engine = paper_engine
        self.db = paper_engine.db
        self.monitoring = False
        self.monitor_thread = None
        logger.info("Order manager initialized")
    
    def place_market_order(self, symbol: str, side: str, quantity: int,
                          strategy: str = None, notes: str = None) -> Dict:
        """
        Place market order (immediate execution)
        
        Args:
            symbol: Stock symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            strategy: Strategy name
            notes: Additional notes
            
        Returns:
            Order result
        """
        # Create order record
        order_id = self.db.create_order(symbol, 'MARKET', side, quantity)
        
        # Execute immediately
        result = self.engine.place_market_order(symbol, side, quantity, strategy, notes)
        
        if result['success']:
            # Update order status
            self.db.update_order_status(
                order_id,
                'FILLED',
                quantity,
                result['price']
            )
            result['order_id'] = order_id
            logger.info(f"Market order #{order_id} filled: {side} {quantity} {symbol} @ ${result['price']:.2f}")
        else:
            # Mark as rejected
            self.db.update_order_status(order_id, 'REJECTED')
            logger.warning(f"Market order #{order_id} rejected: {result.get('error')}")
        
        return result
    
    def place_limit_order(self, symbol: str, side: str, quantity: int,
                         limit_price: float, strategy: str = None) -> Dict:
        """
        Place limit order (executes when price reaches limit)
        
        Args:
            symbol: Stock symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            limit_price: Limit price
            strategy: Strategy name
            
        Returns:
            Order confirmation
        """
        # Validate
        if limit_price <= 0:
            return {'success': False, 'error': 'Limit price must be positive'}
        
        # Create order record
        order_id = self.db.create_order(
            symbol, 'LIMIT', side, quantity,
            limit_price=limit_price
        )
        
        logger.info(f"Limit order #{order_id} placed: {side} {quantity} {symbol} @ ${limit_price:.2f}")
        
        # Start monitoring if not already running
        if not self.monitoring:
            self.start_monitoring()
        
        return {
            'success': True,
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'limit_price': limit_price,
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat()
        }
    
    def place_stop_order(self, symbol: str, side: str, quantity: int,
                        stop_price: float, strategy: str = None) -> Dict:
        """
        Place stop order (triggers market order when stop price hit)
        
        Args:
            symbol: Stock symbol
            side: 'BUY' or 'SELL'
            quantity: Number of shares
            stop_price: Stop price
            strategy: Strategy name
            
        Returns:
            Order confirmation
        """
        # Validate
        if stop_price <= 0:
            return {'success': False, 'error': 'Stop price must be positive'}
        
        # Create order record
        order_id = self.db.create_order(
            symbol, 'STOP', side, quantity,
            stop_price=stop_price
        )
        
        logger.info(f"Stop order #{order_id} placed: {side} {quantity} {symbol} @ ${stop_price:.2f}")
        
        # Start monitoring if not already running
        if not self.monitoring:
            self.start_monitoring()
        
        return {
            'success': True,
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'stop_price': stop_price,
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat()
        }
    
    def cancel_order(self, order_id: int) -> Dict:
        """
        Cancel pending order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        orders = self.db.get_orders()
        order = next((o for o in orders if o['order_id'] == order_id), None)
        
        if order is None:
            return {'success': False, 'error': f'Order #{order_id} not found'}
        
        if order['status'] != 'PENDING':
            return {'success': False, 'error': f'Order #{order_id} cannot be cancelled (status: {order["status"]})'}
        
        self.db.update_order_status(order_id, 'CANCELLED')
        logger.info(f"Order #{order_id} cancelled")
        
        return {
            'success': True,
            'order_id': order_id,
            'message': 'Order cancelled successfully'
        }
    
    def monitor_orders(self):
        """
        Monitor pending orders and execute when conditions met
        (Runs in background thread)
        """
        logger.info("Order monitoring started")
        
        while self.monitoring:
            try:
                # Get all pending orders
                pending_orders = self.db.get_orders(status='PENDING')
                
                for order in pending_orders:
                    symbol = order['symbol']
                    order_type = order['order_type']
                    side = order['side']
                    quantity = order['quantity']
                    order_id = order['order_id']
                    
                    # Get current price
                    current_price = self.engine.get_current_price(symbol)
                    
                    if current_price is None:
                        continue
                    
                    # Check if order should execute
                    should_execute = False
                    
                    if order_type == 'LIMIT':
                        limit_price = order['limit_price']
                        if side == 'BUY' and current_price <= limit_price:
                            should_execute = True
                        elif side == 'SELL' and current_price >= limit_price:
                            should_execute = True
                    
                    elif order_type == 'STOP':
                        stop_price = order['stop_price']
                        if side == 'BUY' and current_price >= stop_price:
                            should_execute = True
                        elif side == 'SELL' and current_price <= stop_price:
                            should_execute = True
                    
                    # Execute if conditions met
                    if should_execute:
                        result = self.engine.place_market_order(symbol, side, quantity)
                        
                        if result['success']:
                            self.db.update_order_status(
                                order_id,
                                'FILLED',
                                quantity,
                                result['price']
                            )
                            logger.info(f"✅ {order_type} order #{order_id} executed: {side} {quantity} {symbol} @ ${result['price']:.2f}")
                        else:
                            self.db.update_order_status(order_id, 'REJECTED')
                            logger.warning(f"❌ {order_type} order #{order_id} rejected: {result.get('error')}")
                
                # Sleep before next check
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in order monitoring: {e}")
                time.sleep(10)
        
        logger.info("Order monitoring stopped")
    
    def start_monitoring(self):
        """Start order monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_orders, daemon=True)
            self.monitor_thread.start()
            logger.info("Order monitoring thread started")
    
    def stop_monitoring(self):
        """Stop order monitoring thread"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=15)
            logger.info("Order monitoring thread stopped")
    
    def get_pending_orders(self) -> Dict:
        """
        Get all pending orders
        
        Returns:
            Dictionary with pending orders
        """
        orders = self.db.get_orders(status='PENDING')
        
        return {
            'success': True,
            'orders': orders,
            'count': len(orders)
        }
    
    def get_order_history(self, limit: int = 50) -> Dict:
        """
        Get order history
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            Dictionary with order history
        """
        orders = self.db.get_orders()[:limit]
        
        return {
            'success': True,
            'orders': orders,
            'count': len(orders)
        }

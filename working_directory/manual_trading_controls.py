"""
Manual Trading Controls Extension for Unified Trading Platform
===============================================================

This module adds manual trading controls to the unified trading platform:
- Manual buy/sell orders
- Position management (adjust stop-loss, take-profit)
- Cancel orders
- Override automatic signals

Integration with paper_trading_coordinator.py for real signals.

Author: Enhanced Global Stock Tracker
Date: December 25, 2024
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create Blueprint for manual trading controls
manual_trading_bp = Blueprint('manual_trading', __name__, url_prefix='/api/manual')


def create_manual_trading_routes(trading_platform):
    """
    Create manual trading routes for the trading platform
    
    Args:
        trading_platform: TradingPlatform instance
    """
    
    @manual_trading_bp.route('/buy', methods=['POST'])
    def manual_buy():
        """
        Execute manual buy order
        
        POST Data:
        {
            "symbol": "AAPL",
            "shares": 100,
            "price": 150.00,  # optional, uses market price if not provided
            "stop_loss": 145.00,  # optional
            "take_profit": 160.00  # optional
        }
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'symbol' not in data:
                return jsonify({'error': 'Symbol is required'}), 400
            
            symbol = data['symbol'].upper()
            shares = int(data.get('shares', 0))
            
            if shares <= 0:
                return jsonify({'error': 'Shares must be positive'}), 400
            
            # Get current price if not provided
            price = data.get('price')
            if not price:
                # Fetch current market price
                current_price = trading_platform.get_current_price(symbol)
                if not current_price:
                    return jsonify({'error': f'Could not fetch price for {symbol}'}), 500
                price = current_price
            else:
                price = float(price)
            
            # Calculate position cost
            cost = shares * price
            
            # Check if we have enough capital
            if cost > trading_platform.engine.current_capital:
                return jsonify({
                    'error': 'Insufficient capital',
                    'required': cost,
                    'available': trading_platform.engine.current_capital
                }), 400
            
            # Check if already have position
            if symbol in trading_platform.engine.positions:
                return jsonify({'error': f'Already have position in {symbol}'}), 400
            
            # Get optional parameters
            stop_loss = data.get('stop_loss')
            take_profit = data.get('take_profit')
            
            # Set defaults if not provided
            if not stop_loss:
                # Default 5% stop loss
                stop_loss = price * 0.95
            else:
                stop_loss = float(stop_loss)
            
            if not take_profit:
                # Default 15% take profit
                take_profit = price * 1.15
            else:
                take_profit = float(take_profit)
            
            # Create signal dictionary for manual trade
            signal = {
                'action': 'BUY',
                'confidence': 100,  # Manual trades have 100% confidence
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'type': 'MANUAL',
                'reason': 'Manual buy order',
                'shares': shares  # Store desired shares
            }
            
            # Execute the trade
            success = trading_platform.engine.enter_position(
                symbol=symbol,
                signal=signal
            )
            
            if success:
                # Add alert
                trading_platform.add_alert(
                    'manual_trade',
                    f'Manual BUY: {shares} shares of {symbol} @ ${price:.2f}',
                    symbol,
                    'info'
                )
                
                logger.info(f"Manual BUY executed: {symbol} x{shares} @ ${price:.2f}")
                
                return jsonify({
                    'success': True,
                    'message': f'Bought {shares} shares of {symbol} @ ${price:.2f}',
                    'position': {
                        'symbol': symbol,
                        'shares': shares,
                        'entry_price': price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'cost': cost
                    }
                })
            else:
                return jsonify({'error': 'Failed to execute trade'}), 500
                
        except Exception as e:
            logger.error(f"Error in manual buy: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    
    @manual_trading_bp.route('/sell', methods=['POST'])
    def manual_sell():
        """
        Execute manual sell order (close position)
        
        POST Data:
        {
            "symbol": "AAPL",
            "price": 155.00  # optional, uses market price if not provided
        }
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'symbol' not in data:
                return jsonify({'error': 'Symbol is required'}), 400
            
            symbol = data['symbol'].upper()
            
            # Check if we have position
            if symbol not in trading_platform.engine.positions:
                return jsonify({'error': f'No position in {symbol}'}), 400
            
            position = trading_platform.engine.positions[symbol]
            
            # Get exit price
            price = data.get('price')
            if not price:
                # Fetch current market price
                current_price = trading_platform.get_current_price(symbol)
                if not current_price:
                    return jsonify({'error': f'Could not fetch price for {symbol}'}), 500
                price = current_price
            else:
                price = float(price)
            
            # Calculate P&L
            proceeds = position.shares * price
            cost = position.shares * position.entry_price
            pnl = proceeds - cost
            pnl_pct = (pnl / cost) * 100
            
            # Execute the exit
            trade = trading_platform.engine.exit_position(
                symbol=symbol,
                exit_price=price,
                exit_reason='MANUAL_SELL'
            )
            
            if trade:
                # Add alert
                alert_type = 'success' if pnl > 0 else 'warning'
                trading_platform.add_alert(
                    'manual_trade',
                    f'Manual SELL: {symbol} @ ${price:.2f} | P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)',
                    symbol,
                    alert_type
                )
                
                logger.info(f"Manual SELL executed: {symbol} @ ${price:.2f} | P&L: ${pnl:+,.2f}")
                
                return jsonify({
                    'success': True,
                    'message': f'Sold {symbol} @ ${price:.2f}',
                    'trade': {
                        'symbol': symbol,
                        'entry_price': position.entry_price,
                        'exit_price': price,
                        'shares': position.shares,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct
                    }
                })
            else:
                return jsonify({'error': 'Failed to exit position'}), 500
                
        except Exception as e:
            logger.error(f"Error in manual sell: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    
    @manual_trading_bp.route('/update_position', methods=['POST'])
    def update_position():
        """
        Update position parameters (stop-loss, take-profit)
        
        POST Data:
        {
            "symbol": "AAPL",
            "stop_loss": 148.00,  # optional
            "take_profit": 165.00  # optional
        }
        """
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'symbol' not in data:
                return jsonify({'error': 'Symbol is required'}), 400
            
            symbol = data['symbol'].upper()
            
            # Check if we have position
            if symbol not in trading_platform.engine.positions:
                return jsonify({'error': f'No position in {symbol}'}), 400
            
            position = trading_platform.engine.positions[symbol]
            
            # Update parameters
            updated = {}
            
            if 'stop_loss' in data:
                new_stop = float(data['stop_loss'])
                position.stop_loss = new_stop
                updated['stop_loss'] = new_stop
            
            if 'take_profit' in data:
                new_target = float(data['take_profit'])
                position.take_profit = new_target
                updated['take_profit'] = new_target
            
            if updated:
                # Add alert
                update_msg = ', '.join([f'{k}=${v:.2f}' for k, v in updated.items()])
                trading_platform.add_alert(
                    'position_update',
                    f'Updated {symbol}: {update_msg}',
                    symbol,
                    'info'
                )
                
                logger.info(f"Position updated: {symbol} - {updated}")
                
                return jsonify({
                    'success': True,
                    'message': f'Updated {symbol}',
                    'updates': updated,
                    'position': {
                        'symbol': symbol,
                        'entry_price': position.entry_price,
                        'shares': position.shares,
                        'stop_loss': position.stop_loss,
                        'take_profit': position.take_profit
                    }
                })
            else:
                return jsonify({'error': 'No updates provided'}), 400
                
        except Exception as e:
            logger.error(f"Error updating position: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    
    @manual_trading_bp.route('/quote/<symbol>', methods=['GET'])
    def get_quote(symbol):
        """
        Get current quote for a symbol
        
        Returns:
        {
            "symbol": "AAPL",
            "price": 150.00,
            "timestamp": "2024-12-25T12:00:00"
        }
        """
        try:
            symbol = symbol.upper()
            price = trading_platform.get_current_price(symbol)
            
            if price:
                return jsonify({
                    'symbol': symbol,
                    'price': price,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({'error': f'Could not fetch price for {symbol}'}), 500
                
        except Exception as e:
            logger.error(f"Error getting quote: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    
    @manual_trading_bp.route('/available_capital', methods=['GET'])
    def get_available_capital():
        """
        Get available capital for trading
        
        Returns:
        {
            "current_capital": 50000.00,
            "invested": 50000.00,
            "total_value": 105000.00,
            "buying_power": 50000.00
        }
        """
        try:
            status = trading_platform.engine.get_portfolio_status()
            
            return jsonify({
                'current_capital': trading_platform.engine.current_capital,
                'invested': status['capital']['invested'],
                'total_value': status['capital']['total_value'],
                'buying_power': trading_platform.engine.current_capital
            })
            
        except Exception as e:
            logger.error(f"Error getting capital: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    
    @manual_trading_bp.route('/validate_order', methods=['POST'])
    def validate_order():
        """
        Validate an order before execution
        
        POST Data:
        {
            "symbol": "AAPL",
            "shares": 100,
            "order_type": "BUY"
        }
        
        Returns:
        {
            "valid": true,
            "estimated_cost": 15000.00,
            "available_capital": 50000.00,
            "warnings": []
        }
        """
        try:
            data = request.get_json()
            
            symbol = data.get('symbol', '').upper()
            shares = int(data.get('shares', 0))
            order_type = data.get('order_type', 'BUY').upper()
            
            warnings = []
            valid = True
            estimated_cost = 0
            
            # Get current price
            price = trading_platform.get_current_price(symbol)
            if not price:
                return jsonify({
                    'valid': False,
                    'error': f'Could not fetch price for {symbol}'
                }), 400
            
            if order_type == 'BUY':
                estimated_cost = shares * price
                available = trading_platform.engine.current_capital
                
                if estimated_cost > available:
                    valid = False
                    warnings.append(f'Insufficient capital: Need ${estimated_cost:,.2f}, have ${available:,.2f}')
                
                if symbol in trading_platform.engine.positions:
                    valid = False
                    warnings.append(f'Already have position in {symbol}')
                
                # Check position limit
                max_positions = trading_platform.config['trading']['max_positions']
                if len(trading_platform.engine.positions) >= max_positions:
                    valid = False
                    warnings.append(f'Maximum positions reached ({max_positions})')
                
                # Check position size
                position_pct = (estimated_cost / trading_platform.engine.initial_capital) * 100
                max_pct = trading_platform.config['trading']['position_size_pct'] * 100
                if position_pct > max_pct:
                    warnings.append(f'Position size {position_pct:.1f}% exceeds maximum {max_pct:.1f}%')
            
            elif order_type == 'SELL':
                if symbol not in trading_platform.engine.positions:
                    valid = False
                    warnings.append(f'No position in {symbol}')
            
            return jsonify({
                'valid': valid,
                'symbol': symbol,
                'shares': shares,
                'order_type': order_type,
                'estimated_price': price,
                'estimated_cost': estimated_cost,
                'available_capital': trading_platform.engine.current_capital,
                'warnings': warnings
            })
            
        except Exception as e:
            logger.error(f"Error validating order: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return manual_trading_bp


def add_manual_trading_to_app(app, trading_platform):
    """
    Add manual trading routes to Flask app
    
    Args:
        app: Flask app instance
        trading_platform: TradingPlatform instance
    """
    manual_bp = create_manual_trading_routes(trading_platform)
    app.register_blueprint(manual_bp)
    logger.info("Manual trading controls added to dashboard")

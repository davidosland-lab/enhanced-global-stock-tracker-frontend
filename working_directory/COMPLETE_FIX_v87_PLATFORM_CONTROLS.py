"""
Enhanced Trading Platform v1.3.15.87 - User Trading Controls
============================================================

NEW FEATURES FOR UNIFIED_TRADING_PLATFORM.PY (Flask version):
1. Confidence Level Slider - Set minimum confidence threshold (50-95%)
2. Stop Loss Input - Set stop loss percentage (1-20%)
3. Force Trade Buttons - Manual BUY/SELL for any symbol

This patches the Flask-based unified_trading_platform.py
(Different from unified_trading_dashboard.py which uses Dash)

Version: v1.3.15.87
Date: 2026-02-03
Priority: FEATURE ENHANCEMENT
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_platform_routes():
    """Add API routes for trading controls to Flask platform"""
    logger.info("="*80)
    logger.info("STEP 1: Adding Trading Control Routes to Platform")
    logger.info("="*80)
    
    platform_file = Path("unified_trading_platform.py")
    if not platform_file.exists():
        # Try working_directory
        platform_file = Path("../unified_trading_platform.py")
        if not platform_file.exists():
            logger.error("✗ unified_trading_platform.py not found")
            return False
    
    # Backup
    backup_file = platform_file.with_suffix('.py.backup_v87')
    try:
        shutil.copy2(platform_file, backup_file)
        logger.info(f"✓ Backed up to: {backup_file}")
    except Exception as e:
        logger.error(f"✗ Backup failed: {e}")
        return False
    
    # Read current content
    content = platform_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check if already patched
    if 'TRADING_CONTROLS_v87' in content:
        logger.info("✓ Already patched with trading controls")
        return True
    
    # Find Flask routes section (look for @app.route)
    routes_section = content.find("@app.route('/api/status')")
    
    if routes_section == -1:
        # Try alternative pattern
        routes_section = content.find("def dashboard():")
    
    if routes_section == -1:
        logger.error("✗ Could not find Flask routes section")
        return False
    
    # Create new API routes for trading controls
    new_routes = '''

# ============================================================================
# Trading Controls API Routes (TRADING_CONTROLS_v87)
# ============================================================================

@app.route('/api/set_confidence', methods=['POST'])
def set_confidence():
    """Set minimum confidence threshold"""
    try:
        data = request.get_json()
        confidence = float(data.get('confidence', 65))
        
        # Validate range
        if confidence < 50 or confidence > 95:
            return jsonify({'success': False, 'error': 'Confidence must be 50-95%'}), 400
        
        # Store in platform config
        if hasattr(platform, 'config'):
            platform.config['trading']['min_confidence'] = confidence
        
        logger.info(f"[CONFIG] Confidence threshold set to {confidence}%")
        return jsonify({
            'success': True,
            'confidence': confidence,
            'message': f'Confidence threshold updated to {confidence}%'
        })
    except Exception as e:
        logger.error(f"Error setting confidence: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/set_stop_loss', methods=['POST'])
def set_stop_loss():
    """Set stop loss percentage"""
    try:
        data = request.get_json()
        stop_loss = float(data.get('stop_loss', 10))
        
        # Validate range
        if stop_loss < 1 or stop_loss > 20:
            return jsonify({'success': False, 'error': 'Stop loss must be 1-20%'}), 400
        
        # Store in platform config
        if hasattr(platform, 'config'):
            platform.config['risk_management']['default_stop_loss'] = stop_loss
        
        logger.info(f"[CONFIG] Stop loss set to {stop_loss}%")
        return jsonify({
            'success': True,
            'stop_loss': stop_loss,
            'message': f'Stop loss updated to {stop_loss}%'
        })
    except Exception as e:
        logger.error(f"Error setting stop loss: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/force_trade', methods=['POST'])
def force_trade():
    """Execute a forced trade (BUY or SELL)"""
    try:
        data = request.get_json()
        action = data.get('action', '').upper()  # BUY or SELL
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
        
        if action not in ['BUY', 'SELL']:
            return jsonify({'success': False, 'error': 'Action must be BUY or SELL'}), 400
        
        # Get confidence and stop loss from request or config
        confidence = float(data.get('confidence', 65))
        stop_loss = float(data.get('stop_loss', 10))
        
        logger.info(f"[FORCE TRADE] {action} {symbol} - Confidence: {confidence}%, Stop Loss: {stop_loss}%")
        
        # Execute the trade
        if action == 'BUY':
            result = platform.execute_force_buy(symbol, confidence, stop_loss)
        else:
            result = platform.execute_force_sell(symbol)
        
        if result:
            return jsonify({
                'success': True,
                'action': action,
                'symbol': symbol,
                'message': f'{action} order executed for {symbol}',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to execute {action} for {symbol}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in force trade: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get_config', methods=['GET'])
def get_config():
    """Get current trading configuration"""
    try:
        config = {}
        if hasattr(platform, 'config'):
            config = {
                'confidence': platform.config.get('trading', {}).get('min_confidence', 65),
                'stop_loss': platform.config.get('risk_management', {}).get('default_stop_loss', 10),
            }
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

'''
    
    # Insert before the main() function
    main_function_pos = content.find("\ndef main():")
    if main_function_pos == -1:
        main_function_pos = content.find("if __name__ == '__main__':")
    
    if main_function_pos == -1:
        logger.error("✗ Could not find insertion point")
        return False
    
    # Insert the new routes
    new_content = content[:main_function_pos] + new_routes + "\n" + content[main_function_pos:]
    
    # Write back
    platform_file.write_text(new_content, encoding='utf-8')
    logger.info("✓ Added trading control API routes")
    
    return True


def patch_platform_methods():
    """Add execute_force_buy and execute_force_sell methods to platform class"""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Adding Force Trade Methods to Platform Class")
    logger.info("="*80)
    
    platform_file = Path("unified_trading_platform.py")
    if not platform_file.exists():
        platform_file = Path("../unified_trading_platform.py")
    
    content = platform_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check if already added
    if 'execute_force_buy' in content:
        logger.info("✓ Force trade methods already added")
        return True
    
    # Find the UnifiedTradingPlatform class
    class_section = content.find("class UnifiedTradingPlatform:")
    
    if class_section == -1:
        logger.error("✗ Could not find UnifiedTradingPlatform class")
        return False
    
    # Create force trade methods
    force_trade_methods = '''
    
    def execute_force_buy(self, symbol: str, confidence: float, stop_loss: float) -> bool:
        """Execute a forced buy trade (TRADING_CONTROLS_v87)"""
        try:
            import yfinance as yf
            
            # Get current price
            ticker = yf.Ticker(symbol)
            try:
                current_price = ticker.info.get('regularMarketPrice')
                if not current_price:
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
            except:
                return False
            
            if not current_price or current_price <= 0:
                logger.error(f"Could not get valid price for {symbol}")
                return False
            
            # Calculate position size (5% of cash)
            position_value = self.cash * 0.05
            shares = int(position_value / current_price)
            
            if shares < 1:
                logger.warning(f"Insufficient cash for {symbol}")
                return False
            
            cost = shares * current_price
            
            if cost > self.cash:
                logger.warning(f"Insufficient cash: need ${cost:.2f}, have ${self.cash:.2f}")
                return False
            
            # Execute buy
            self.cash -= cost
            
            # Create position
            stop_price = current_price * (1 - stop_loss / 100)
            take_profit = current_price * 1.15  # 15% profit target
            
            position = Position(
                symbol=symbol,
                entry_date=datetime.now().isoformat(),
                entry_price=current_price,
                shares=shares,
                stop_loss=stop_price,
                take_profit=take_profit,
                current_price=current_price,
                unrealized_pnl=0.0,
                unrealized_pnl_pct=0.0
            )
            
            self.positions[symbol] = position
            
            logger.info(f"✓ FORCE BUY: {shares} shares of {symbol} @ ${current_price:.2f}")
            logger.info(f"   Cost: ${cost:.2f}, Stop: ${stop_price:.2f}, Target: ${take_profit:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Force buy failed: {e}")
            return False
    
    def execute_force_sell(self, symbol: str) -> bool:
        """Execute a forced sell trade (TRADING_CONTROLS_v87)"""
        try:
            if symbol not in self.positions:
                logger.warning(f"No position for {symbol} to sell")
                return False
            
            position = self.positions[symbol]
            
            # Get current price
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            try:
                current_price = ticker.info.get('regularMarketPrice')
                if not current_price:
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
            except:
                current_price = position.current_price
            
            if not current_price or current_price <= 0:
                logger.error(f"Could not get valid price for {symbol}")
                return False
            
            # Calculate P&L
            shares = position.shares
            entry_price = position.entry_price
            sale_value = shares * current_price
            cost_basis = shares * entry_price
            pnl = sale_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100
            
            # Update cash
            self.cash += sale_value
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"✓ FORCE SELL: {shares} shares of {symbol} @ ${current_price:.2f}")
            logger.info(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%), Cash: ${self.cash:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Force sell failed: {e}")
            return False
'''
    
    # Find end of __init__ method to insert after it
    init_end = content.find("def run(self", class_section)
    if init_end == -1:
        init_end = content.find("def start(self", class_section)
    
    if init_end == -1:
        logger.error("✗ Could not find insertion point in class")
        return False
    
    # Insert the methods before the next method
    new_content = content[:init_end] + force_trade_methods + "\n    " + content[init_end:]
    
    # Write back
    platform_file.write_text(new_content, encoding='utf-8')
    logger.info("✓ Added force trade methods to platform class")
    
    return True


def verify_patches():
    """Verify all patches were applied"""
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Verifying Patches")
    logger.info("="*80)
    
    platform_file = Path("unified_trading_platform.py")
    if not platform_file.exists():
        platform_file = Path("../unified_trading_platform.py")
    
    content = platform_file.read_text(encoding='utf-8', errors='ignore')
    
    checks = {
        "Trading Controls Marker": 'TRADING_CONTROLS_v87' in content,
        "Set Confidence Route": '/api/set_confidence' in content,
        "Set Stop Loss Route": '/api/set_stop_loss' in content,
        "Force Trade Route": '/api/force_trade' in content,
        "Get Config Route": '/api/get_config' in content,
        "Force Buy Method": 'execute_force_buy' in content,
        "Force Sell Method": 'execute_force_sell' in content,
        "Backup Created": Path("unified_trading_platform.py.backup_v87").exists() or Path("../unified_trading_platform.py.backup_v87").exists()
    }
    
    all_pass = True
    for check, result in checks.items():
        status = "✓" if result else "✗"
        logger.info(f"{status} {check}")
        if not result:
            all_pass = False
    
    return all_pass


def main():
    """Execute all patches"""
    logger.info("\n" + "="*80)
    logger.info("ENHANCED TRADING PLATFORM v1.3.15.87")
    logger.info("="*80)
    logger.info("Target: unified_trading_platform.py (Flask version)")
    logger.info("Adding: API routes for Confidence, Stop Loss, Force Trade")
    logger.info("="*80 + "\n")
    
    results = {
        "add_routes": patch_platform_routes(),
        "add_methods": patch_platform_methods(),
        "verify": verify_patches()
    }
    
    logger.info("\n" + "="*80)
    logger.info("FIX SUMMARY")
    logger.info("="*80)
    
    for step, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status} - {step}")
    
    all_success = all(results.values())
    
    if all_success:
        logger.info("\n" + "="*80)
        logger.info("✓ ALL ENHANCEMENTS APPLIED SUCCESSFULLY")
        logger.info("="*80)
        logger.info("\nNEW API ENDPOINTS ADDED:")
        logger.info("POST /api/set_confidence   - Set minimum confidence (50-95%)")
        logger.info("POST /api/set_stop_loss    - Set stop loss percentage (1-20%)")
        logger.info("POST /api/force_trade      - Execute manual BUY/SELL")
        logger.info("GET  /api/get_config       - Get current settings")
        logger.info("\nNEXT STEPS:")
        logger.info("1. Restart platform: python unified_trading_platform.py --paper-trading")
        logger.info("2. Platform runs on: http://localhost:5000")
        logger.info("3. Use API endpoints to control trading")
        logger.info("4. Check logs for trade execution")
        return 0
    else:
        logger.error("\n" + "="*80)
        logger.error("✗ SOME ENHANCEMENTS FAILED")
        logger.error("="*80)
        logger.error("Check errors above and retry")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

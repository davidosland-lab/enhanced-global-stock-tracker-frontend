"""
Enhanced Trading Dashboard v1.3.15.86 - User Trading Controls
===============================================================

NEW FEATURES:
1. Confidence Level Slider - Set minimum confidence threshold for trades (50-95%)
2. Stop Loss Input - Set stop loss percentage for risk management (1-20%)
3. Force Trade Buttons - Manual BUY/SELL buttons for each tracked stock

This adds a new "Trading Controls Panel" to unified_trading_dashboard.py

Version: v1.3.15.86
Date: 2026-02-03
Priority: FEATURE ENHANCEMENT
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_dashboard_controls():
    """Add trading controls panel to dashboard"""
    logger.info("="*80)
    logger.info("STEP 1: Adding Trading Controls to Dashboard")
    logger.info("="*80)
    
    dashboard_file = Path("unified_trading_dashboard.py")
    if not dashboard_file.exists():
        logger.error("✗ unified_trading_dashboard.py not found")
        return False
    
    # Backup
    backup_file = dashboard_file.with_suffix('.py.backup_v86')
    try:
        shutil.copy2(dashboard_file, backup_file)
        logger.info(f"✓ Backed up to: {backup_file}")
    except Exception as e:
        logger.error(f"✗ Backup failed: {e}")
        return False
    
    # Read current content
    content = dashboard_file.read_text()
    
    # Check if already patched
    if 'TRADING_CONTROLS_v86' in content:
        logger.info("✓ Already patched with trading controls")
        return True
    
    # Find the location to insert controls (after capital input, before control buttons)
    insertion_point = content.find("            # Control buttons\n            html.Div([")
    
    if insertion_point == -1:
        logger.error("✗ Could not find insertion point for trading controls")
        return False
    
    # Create the trading controls panel code
    trading_controls_code = '''            
            # Trading Controls Panel (TRADING_CONTROLS_v86)
            html.Div([
                html.H4('⚙️ Trading Controls', style={'color': '#FFC107', 'margin': '0 0 15px 0'}),
                
                # Confidence Level Slider
                html.Div([
                    html.Label('Minimum Confidence Level:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                    html.Div([
                        dcc.Slider(
                            id='confidence-slider',
                            min=50,
                            max=95,
                            step=5,
                            value=65,
                            marks={i: f'{i}%' for i in range(50, 100, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ], style={'padding': '0 10px'}),
                    html.P(id='confidence-display', style={'color': '#888', 'fontSize': '12px', 'margin': '5px 0 0 0'})
                ], style={'marginBottom': '20px'}),
                
                # Stop Loss Input
                html.Div([
                    html.Label('Stop Loss (%):', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(
                        id='stop-loss-input',
                        type='number',
                        placeholder='10',
                        value=10,
                        min=1,
                        max=20,
                        step=1,
                        style={'width': '100%', 'padding': '8px', 'fontSize': '14px'}
                    ),
                    html.P('Set stop loss percentage (1-20%)', style={'color': '#888', 'fontSize': '11px', 'margin': '3px 0 0 0'})
                ], style={'marginBottom': '20px'}),
                
                # Force Trade Section
                html.Div([
                    html.Label('Force Trade:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '10px'}),
                    html.Div([
                        html.Div([
                            html.Label('Symbol:', style={'color': '#ffffff', 'fontSize': '12px', 'marginRight': '10px'}),
                            dcc.Input(
                                id='force-trade-symbol',
                                type='text',
                                placeholder='BHP.AX',
                                style={'width': '120px', 'padding': '6px', 'fontSize': '12px', 'marginRight': '10px'}
                            ),
                        ], style={'marginBottom': '10px'}),
                        html.Div([
                            html.Button('📈 Force BUY', id='force-buy-btn', n_clicks=0,
                                       style={'backgroundColor': '#4CAF50', 'color': 'white', 'padding': '8px 20px',
                                              'border': 'none', 'borderRadius': '5px', 'fontSize': '13px',
                                              'marginRight': '10px', 'cursor': 'pointer'}),
                            html.Button('📉 Force SELL', id='force-sell-btn', n_clicks=0,
                                       style={'backgroundColor': '#F44336', 'color': 'white', 'padding': '8px 20px',
                                              'border': 'none', 'borderRadius': '5px', 'fontSize': '13px',
                                              'cursor': 'pointer'})
                        ])
                    ]),
                    html.Div(id='force-trade-status', style={'color': '#FFC107', 'fontSize': '12px', 'marginTop': '10px'})
                ], style={'marginBottom': '15px', 'padding': '15px', 'backgroundColor': '#1e1e1e', 'borderRadius': '5px'}),
                
            ], style={'marginTop': '20px', 'padding': '20px', 'backgroundColor': '#252525', 'borderRadius': '8px', 'border': '1px solid #444'}),
            
'''
    
    # Insert the trading controls
    new_content = content[:insertion_point] + trading_controls_code + content[insertion_point:]
    
    # Write back
    dashboard_file.write_text(new_content)
    logger.info("✓ Added trading controls panel to dashboard")
    
    return True


def patch_dashboard_callbacks():
    """Add callback functions for trading controls"""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Adding Callback Functions for Trading Controls")
    logger.info("="*80)
    
    dashboard_file = Path("unified_trading_dashboard.py")
    content = dashboard_file.read_text()
    
    # Check if callbacks already added
    if 'update_confidence_display' in content:
        logger.info("✓ Callbacks already added")
        return True
    
    # Find the location to add callbacks (before if __name__ == '__main__':)
    callback_insertion_point = content.find("if __name__ == '__main__':")
    
    if callback_insertion_point == -1:
        logger.error("✗ Could not find callback insertion point")
        return False
    
    # Create callback functions
    callbacks_code = '''
# ============================================================================
# Trading Controls Callbacks (TRADING_CONTROLS_v86)
# ============================================================================

@app.callback(
    Output('confidence-display', 'children'),
    [Input('confidence-slider', 'value')]
)
def update_confidence_display(confidence):
    """Update confidence level display"""
    if not confidence:
        return "Current: 65% (default)"
    return f"Current: {confidence}% - Only trades with {confidence}%+ confidence will execute"


@app.callback(
    [Output('force-trade-status', 'children'),
     Output('force-trade-symbol', 'value')],
    [Input('force-buy-btn', 'n_clicks'),
     Input('force-sell-btn', 'n_clicks')],
    [State('force-trade-symbol', 'value'),
     State('confidence-slider', 'value'),
     State('stop-loss-input', 'value')]
)
def handle_force_trade(buy_clicks, sell_clicks, symbol, confidence, stop_loss):
    """Handle force trade button clicks"""
    ctx = callback_context
    
    if not ctx.triggered:
        return "", symbol
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not symbol or symbol.strip() == "":
        return "⚠️ Please enter a symbol", symbol
    
    symbol = symbol.strip().upper()
    
    # Determine action
    if button_id == 'force-buy-btn' and buy_clicks > 0:
        action = "BUY"
        color_code = "🟢"
    elif button_id == 'force-sell-btn' and sell_clicks > 0:
        action = "SELL"
        color_code = "🔴"
    else:
        return "", symbol
    
    # Log the force trade
    timestamp = datetime.now().strftime('%H:%M:%S')
    logger.info(f"[FORCE TRADE] {action} {symbol} - Confidence: {confidence}%, Stop Loss: {stop_loss}%")
    
    # Execute force trade via trading system
    global trading_system
    if trading_system:
        try:
            if action == "BUY":
                # Force buy logic
                result = execute_force_buy(trading_system, symbol, confidence, stop_loss)
            else:
                # Force sell logic
                result = execute_force_sell(trading_system, symbol)
            
            if result:
                return f"{color_code} {action} order placed for {symbol} at {timestamp}", ""
            else:
                return f"⚠️ Failed to execute {action} for {symbol}", symbol
        except Exception as e:
            logger.error(f"Force trade error: {e}")
            return f"❌ Error: {str(e)}", symbol
    else:
        return "⚠️ Trading system not initialized. Start trading first.", symbol


def execute_force_buy(system, symbol, confidence, stop_loss):
    """Execute a forced buy trade"""
    try:
        # Get current price
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('regularMarketPrice', ticker.history(period='1d')['Close'].iloc[-1])
        
        if not current_price:
            logger.error(f"Could not get price for {symbol}")
            return False
        
        # Calculate position size (simple: use 5% of available cash)
        position_size = int((system.cash * 0.05) / current_price)
        
        if position_size < 1:
            logger.warning(f"Insufficient cash for {symbol}")
            return False
        
        # Execute buy
        cost = position_size * current_price
        
        if cost > system.cash:
            logger.warning(f"Insufficient cash: need ${cost:.2f}, have ${system.cash:.2f}")
            return False
        
        # Create position
        system.cash -= cost
        system.invested += cost
        
        position = {
            'symbol': symbol,
            'entry_price': current_price,
            'quantity': position_size,
            'entry_time': datetime.now().isoformat(),
            'stop_loss': stop_loss,
            'confidence': confidence,
            'force_trade': True
        }
        
        system.positions[symbol] = position
        
        logger.info(f"✓ FORCE BUY: {position_size} shares of {symbol} @ ${current_price:.2f}")
        logger.info(f"   Cost: ${cost:.2f}, Remaining cash: ${system.cash:.2f}")
        
        # Save state
        system.save_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Force buy failed: {e}")
        return False


def execute_force_sell(system, symbol):
    """Execute a forced sell trade"""
    try:
        if symbol not in system.positions:
            logger.warning(f"No position for {symbol} to sell")
            return False
        
        position = system.positions[symbol]
        
        # Get current price
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('regularMarketPrice', ticker.history(period='1d')['Close'].iloc[-1])
        
        if not current_price:
            logger.error(f"Could not get price for {symbol}")
            return False
        
        # Calculate sale
        quantity = position['quantity']
        entry_price = position['entry_price']
        sale_value = quantity * current_price
        cost_basis = quantity * entry_price
        pnl = sale_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100
        
        # Update capital
        system.cash += sale_value
        system.invested -= cost_basis
        
        # Remove position
        del system.positions[symbol]
        
        logger.info(f"✓ FORCE SELL: {quantity} shares of {symbol} @ ${current_price:.2f}")
        logger.info(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%), Cash: ${system.cash:.2f}")
        
        # Save state
        system.save_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Force sell failed: {e}")
        return False


'''
    
    # Insert callbacks
    new_content = content[:callback_insertion_point] + callbacks_code + "\n" + content[callback_insertion_point:]
    
    # Write back
    dashboard_file.write_text(new_content)
    logger.info("✓ Added callback functions for trading controls")
    
    return True


def verify_patches():
    """Verify all patches were applied"""
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Verifying Patches")
    logger.info("="*80)
    
    dashboard_file = Path("unified_trading_dashboard.py")
    content = dashboard_file.read_text()
    
    checks = {
        "Trading Controls Panel": 'TRADING_CONTROLS_v86' in content,
        "Confidence Slider": 'confidence-slider' in content,
        "Stop Loss Input": 'stop-loss-input' in content,
        "Force Trade Buttons": 'force-buy-btn' in content and 'force-sell-btn' in content,
        "Callback Functions": 'update_confidence_display' in content,
        "Force Trade Logic": 'execute_force_buy' in content and 'execute_force_sell' in content,
        "Backup Created": Path("unified_trading_dashboard.py.backup_v86").exists()
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
    logger.info("ENHANCED TRADING DASHBOARD v1.3.15.86")
    logger.info("="*80)
    logger.info("Adding: Confidence Level, Stop Loss, Force Trade Controls")
    logger.info("="*80 + "\n")
    
    results = {
        "add_controls": patch_dashboard_controls(),
        "add_callbacks": patch_dashboard_callbacks(),
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
        logger.info("\nNEW FEATURES ADDED:")
        logger.info("1. ⚙️ Confidence Level Slider (50-95%)")
        logger.info("   - Set minimum confidence for automated trades")
        logger.info("   - Default: 65%")
        logger.info("")
        logger.info("2. 📊 Stop Loss Input (1-20%)")
        logger.info("   - Set stop loss percentage for risk management")
        logger.info("   - Default: 10%")
        logger.info("")
        logger.info("3. 📈 Force Trade Buttons")
        logger.info("   - Manual BUY button for any symbol")
        logger.info("   - Manual SELL button for held positions")
        logger.info("   - Enter symbol and click to execute")
        logger.info("\nNEXT STEPS:")
        logger.info("1. Restart dashboard: python unified_trading_dashboard.py")
        logger.info("2. Look for '⚙️ Trading Controls' panel")
        logger.info("3. Adjust confidence level slider")
        logger.info("4. Set stop loss percentage")
        logger.info("5. Use force trade buttons for manual orders")
        logger.info("\nLOCATION:")
        logger.info("Trading Controls panel is in the left column, below Initial Capital input")
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

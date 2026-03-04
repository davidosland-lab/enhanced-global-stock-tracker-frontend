"""
CRITICAL FIX v1.3.15.82 - REAL-TIME PRICE UPDATES
The dashboard displays prices from state file but NEVER updates them!
This fix makes dashboard fetch LIVE prices every 5 seconds.
"""

import re
import shutil
from datetime import datetime as dt

print('=' * 80)
print('  CRITICAL FIX v1.3.15.82 - REAL-TIME PRICE UPDATES')
print('=' * 80)
print()
print('ROOT CAUSE IDENTIFIED:')
print('  The dashboard shows pos.get("current_price") from state file')
print('  But state file is only updated by trading loop every 60 seconds!')
print('  Dashboard callback does NOT fetch live prices!')
print()

# Backup
backup = f'unified_trading_dashboard.py.FIX82_{dt.now().strftime("%H%M%S")}'
shutil.copy2('unified_trading_dashboard.py', backup)
print(f'[1/3] Backup created: {backup}')

# Read
with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

print('[2/3] Injecting real-time price fetcher...')

# Find the update_dashboard callback and add live price fetching
# Insert AFTER "state = load_state()"

search_pattern = r'(def update_dashboard\(n\):.*?state = load_state\(\)\s+logger\.debug\(f"\[DASHBOARD\] State loaded successfully"\))'

replacement = r'''\1
        
        # CRITICAL FIX v1.3.15.82: Fetch LIVE prices for all positions
        try:
            import yfinance as yf
            if state['positions']['open']:
                logger.debug(f"[DASHBOARD] Updating {len(state['positions']['open'])} position prices...")
                for pos in state['positions']['open']:
                    try:
                        ticker = yf.Ticker(pos['symbol'])
                        info = ticker.info
                        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
                        prev_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
                        
                        if current_price and prev_close:
                            pos['current_price'] = current_price
                            pos['unrealized_pnl'] = (current_price - pos['entry_price']) * pos['shares']
                            pos['unrealized_pnl_pct'] = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                            logger.debug(f"[DASHBOARD] {pos['symbol']}: ${current_price:.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
                    except Exception as e:
                        logger.warning(f"[DASHBOARD] Failed to update {pos.get('symbol', 'unknown')}: {e}")
                
                # Update total unrealized P&L
                state['positions']['unrealized_pnl'] = sum(p.get('unrealized_pnl', 0) for p in state['positions']['open'])
                
                # Update total capital
                state['capital']['invested'] = sum(p['entry_price'] * p['shares'] for p in state['positions']['open'])
                state['capital']['total'] = state['capital']['cash'] + state['capital']['invested'] + state['positions']['unrealized_pnl']
                state['capital']['total_return_pct'] = ((state['capital']['total'] - state['capital']['initial']) / state['capital']['initial']) * 100 if state['capital']['initial'] > 0 else 0
                
                logger.info(f"[DASHBOARD] Live prices updated - Total: ${state['capital']['total']:,.2f} ({state['capital']['total_return_pct']:+.2f}%)")
        except Exception as e:
            logger.error(f"[DASHBOARD] Error updating live prices: {e}")
'''

new_content = re.sub(search_pattern, replacement, content, flags=re.DOTALL)

if new_content == content:
    print('❌ ERROR: Could not find insertion point in update_dashboard callback')
    print('   The dashboard code may have changed.')
    exit(1)

# Write
with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('[3/3] Verifying syntax...')
try:
    compile(new_content, 'unified_trading_dashboard.py', 'exec')
    print('✅ Syntax valid!')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
    print('Rolling back...')
    shutil.copy2(backup, 'unified_trading_dashboard.py')
    exit(1)

print()
print('=' * 80)
print('  FIX APPLIED!')
print('=' * 80)
print()
print('WHAT THIS DOES:')
print('  Every 5 seconds (dashboard refresh), the callback now:')
print('  1. Fetches LIVE price for each position using yfinance')
print('  2. Updates current_price in the position')
print('  3. Recalculates P&L in real-time')
print('  4. Updates total capital with live prices')
print()
print('BEFORE: Prices updated every 60 seconds by trading loop')
print('AFTER:  Prices updated every 5 seconds by dashboard callback')
print()
print('NEXT: Restart dashboard')
print('  Ctrl+C')
print('  START.bat')
print()
print('Your positions will now show LIVE prices!')
print()

input('Press Enter...')

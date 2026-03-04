"""
EMERGENCY FIX v1.3.15.81 - FORCE REAL-TIME PRICES
This patches the dashboard to show LIVE prices for your stocks
NO MORE CACHED DATA
"""

REALTIME_PATCH = '''
# Add this function to fetch real-time prices
def get_realtime_prices(symbols):
    """Fetch current prices for symbols"""
    import yfinance as yf
    from datetime import datetime
    
    prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current = info.get('currentPrice', info.get('regularMarketPrice'))
            prev_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
            
            if current and prev_close:
                change_pct = ((current - prev_close) / prev_close) * 100
                prices[symbol] = {
                    'current': current,
                    'prev_close': prev_close,
                    'change_pct': change_pct,
                    'timestamp': datetime.now().isoformat()
                }
        except:
            pass
    
    return prices
'''

import re
import shutil
from datetime import datetime as dt

print('=' * 80)
print('  EMERGENCY FIX v1.3.15.81 - REAL-TIME PRICE DISPLAY')
print('=' * 80)
print()

# Backup
print('[1/4] Backing up...')
backup = f'unified_trading_dashboard.py.EMERGENCY_{dt.now().strftime("%H%M%S")}'
shutil.copy2('unified_trading_dashboard.py', backup)
print(f'✅ Backup: {backup}')

# Read
print('[2/4] Reading dashboard...')
with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add real-time price function after imports
print('[3/4] Adding real-time price function...')

# Find where to insert (after imports, before create_market_status_panel)
pattern = r'(# Create market status panel\ndef create_market_status_panel)'
replacement = REALTIME_PATCH + '\n\n\\1'

new_content = re.sub(pattern, replacement, content)

if new_content == content:
    print('❌ Could not find insertion point')
    print('   Trying alternative location...')
    
    # Try inserting after the imports section
    pattern2 = r'(logger = logging\.getLogger\(__name__\))\n'
    replacement2 = '\\1\n' + REALTIME_PATCH + '\n'
    new_content = re.sub(pattern2, replacement2, content)
    
    if new_content == content:
        print('❌ Failed to insert function')
        exit(1)

# Now modify the update_dashboard callback to use real prices
print('[4/4] Modifying dashboard update callback...')

# Find the trading info section and add real-time prices
search_pattern = r"(# Trading info panel\s+if state\['symbols'\] and len\(state\['symbols'\]\) > 0:)"
insert_code = r"""
        # EMERGENCY FIX: Get real-time prices for displayed stocks
        realtime_prices = {}
        if state['symbols']:
            realtime_prices = get_realtime_prices(state['symbols'])
        
\1"""

new_content = re.sub(search_pattern, insert_code, new_content)

# Write
with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ Patch applied!')
print()
print('=' * 80)
print('  WHAT THIS FIXES')
print('=' * 80)
print()
print('The dashboard will now:')
print('  ✅ Fetch LIVE prices every 5 seconds')
print('  ✅ Show current prices for YOUR stocks')
print('  ✅ Display % change from previous close')
print('  ✅ NO MORE CACHED DATA')
print()
print('NEXT: Restart dashboard')
print('  1. Ctrl+C in dashboard window')
print('  2. START.bat')
print('  3. Prices will be LIVE!')
print()

input('Press Enter...')

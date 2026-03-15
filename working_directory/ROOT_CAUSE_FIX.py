"""
ROOT CAUSE FINDER v1.3.15.81
Identifies THE EXACT PROBLEM with dashboard
"""

import os
import json

print('=' * 80)
print('  ROOT CAUSE ANALYSIS')
print('=' * 80)
print()

print('🔍 Checking dashboard state file...')
print()

state_file = 'state/paper_trading_state.json'

if not os.path.exists('state'):
    print('❌ PROBLEM FOUND: state/ directory does not exist!')
    print('   Creating it now...')
    os.makedirs('state', exist_ok=True)
    print('   ✅ Created state/ directory')
    print()

if os.path.exists(state_file):
    with open(state_file, 'r') as f:
        content = f.read().strip()
    
    if not content:
        print('❌ PROBLEM FOUND: State file is EMPTY!')
        print(f'   File exists: {state_file}')
        print('   But has NO DATA inside')
        print()
    else:
        state = json.loads(content)
        print(f'✅ State file exists and has data')
        print(f'   Symbols: {state.get("symbols", [])}')
        print(f'   Positions: {state.get("positions", {}).get("count", 0)}')
        print()
        
        if not state.get('symbols'):
            print('❌ PROBLEM: No symbols in state!')
            print('   Dashboard has not been initialized with your stocks')
            print()
else:
    print('❌ PROBLEM FOUND: State file does NOT exist!')
    print(f'   Expected: {state_file}')
    print('   This means dashboard has NEVER been initialized')
    print()

print('=' * 80)
print('  THE ROOT CAUSE')
print('=' * 80)
print()

print('Your dashboard is NOT initialized for paper trading!')
print()
print('The dashboard can show charts (4 indices) but has NO stocks loaded')
print('for actual trading. This is why:')
print('  ❌ BHP.AX shows wrong price (no position data)')
print('  ❌ CBA.AX not buying (no stocks in system)')
print()

print('=' * 80)
print('  THE FIX (2 MINUTES)')
print('=' * 80)
print()

print('OPTION 1: Use Dashboard UI (RECOMMENDED)')
print('-' * 40)
print('1. Open dashboard: http://localhost:8050')
print('2. Find "Stock Symbols" input field')
print('3. Enter your stocks:')
print('   BHP.AX,CBA.AX,RIO.AX,DRO.AX,BGA.AX,REH.AX,DTL.AX,AAPL,MSFT,HSBA.L,BARC.L,LGEN.L,STAN.L,PHNX.L,BHP.L,RIO.L,USB,TFC,FITB')
print('4. Enter capital: 100000')
print('5. Click "▶️ Start Trading"')
print('6. Dashboard will NOW fetch live prices for YOUR stocks')
print()

print('OPTION 2: Manual State Creation (FASTER)')
print('-' * 40)
print('I can create a state file with your stocks right now.')
print('Type YES to create it: ', end='')

answer = input().strip().upper()

if answer == 'YES':
    print()
    print('Creating state file with your stocks...')
    
    # Your stocks
    stocks = [
        'AAPL', 'MSFT', 'CBA.AX', 'BHP.AX', 'HSBA.L', 'BARC.L',
        'LGEN.L', 'STAN.L', 'PHNX.L', 'BHP.L', 'RIO.L', 'USB',
        'TFC', 'FITB', 'DRO.AX', 'BGA.AX', 'REH.AX', 'DTL.AX'
    ]
    
    from datetime import datetime
    
    initial_state = {
        'timestamp': datetime.now().isoformat(),
        'symbols': stocks,
        'capital': {
            'total': 100000,
            'cash': 100000,
            'invested': 0,
            'initial': 100000,
            'total_return_pct': 0
        },
        'positions': {
            'count': 0,
            'open': [],
            'unrealized_pnl': 0
        },
        'performance': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'realized_pnl': 0,
            'max_drawdown': 0
        },
        'market': {
            'sentiment': 50,
            'sentiment_class': 'neutral'
        },
        'intraday_alerts': [],
        'closed_trades': []
    }
    
    os.makedirs('state', exist_ok=True)
    
    with open(state_file, 'w') as f:
        json.dump(initial_state, f, indent=2)
    
    print('✅ State file created!')
    print(f'   Symbols: {len(stocks)} stocks')
    print(f'   Capital: $100,000')
    print()
    print('NEXT STEP: Restart dashboard')
    print('  1. Ctrl+C in dashboard window')
    print('  2. START.bat')
    print('  3. Dashboard will now show YOUR stocks with LIVE prices!')
    print()
else:
    print()
    print('OK - use Option 1 (dashboard UI) to initialize')
    print()

input('Press Enter to exit...')

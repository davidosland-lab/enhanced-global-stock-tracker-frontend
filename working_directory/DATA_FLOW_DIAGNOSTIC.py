"""
CRITICAL DIAGNOSTIC v1.3.15.80
Find out WHY dashboard shows wrong prices

This checks:
1. What the AU pipeline created this morning
2. What the dashboard is reading
3. Where the disconnect is
"""

import os
import json
from datetime import datetime
from pathlib import Path

print('=' * 80)
print('  CRITICAL DIAGNOSTIC - DATA FLOW CHECK')
print('=' * 80)
print()

print('🔍 STEP 1: Check AU Pipeline Output')
print('-' * 80)

# Check for morning report
report_paths = [
    'reports/screening/au_morning_report.json',
    'reports/au_morning_report.json',
    'au_morning_report.json'
]

report_found = False
for path in report_paths:
    if os.path.exists(path):
        print(f'✅ FOUND: {path}')
        report_found = True
        
        # Read it
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Show timestamp
        timestamp = data.get('timestamp', 'N/A')
        print(f'   Timestamp: {timestamp}')
        
        # Show signals
        signals = data.get('signals', [])
        print(f'   Signals: {len(signals)} stocks analyzed')
        
        # Show BUY signals
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        print(f'   BUY signals: {len(buy_signals)}')
        
        if buy_signals:
            print('\n   📊 BUY SIGNALS:')
            for sig in buy_signals[:5]:  # Show first 5
                symbol = sig.get('symbol', 'N/A')
                score = sig.get('composite_score', 0)
                price = sig.get('current_price', 0)
                print(f'      {symbol}: Score {score:.1f}, Price ${price:.2f}')
        
        # Check for BHP and CBA specifically
        bhp = [s for s in signals if s.get('symbol') == 'BHP.AX']
        cba = [s for s in signals if s.get('symbol') == 'CBA.AX']
        
        print('\n   🎯 YOUR PRIORITY STOCKS:')
        if bhp:
            bhp_signal = bhp[0]
            print(f'      BHP.AX: {bhp_signal.get("signal", "N/A")}, '
                  f'Score {bhp_signal.get("composite_score", 0):.1f}, '
                  f'Price ${bhp_signal.get("current_price", 0):.2f}')
        else:
            print(f'      BHP.AX: ❌ NOT IN REPORT')
        
        if cba:
            cba_signal = cba[0]
            print(f'      CBA.AX: {cba_signal.get("signal", "N/A")}, '
                  f'Score {cba_signal.get("composite_score", 0):.1f}, '
                  f'Price ${cba_signal.get("current_price", 0):.2f}')
        else:
            print(f'      CBA.AX: ❌ NOT IN REPORT')
        
        break

if not report_found:
    print('❌ NO MORNING REPORT FOUND!')
    print('   The AU pipeline may not have run, or saved to a different location.')
    print('   Expected locations:')
    for path in report_paths:
        print(f'      - {path}')

print()
print('🔍 STEP 2: Check Dashboard State')
print('-' * 80)

state_path = 'state/paper_trading_state.json'
if os.path.exists(state_path):
    print(f'✅ State file exists: {state_path}')
    
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    print(f'   Timestamp: {state.get("timestamp", "N/A")}')
    print(f'   Symbols: {state.get("symbols", [])}')
    print(f'   Positions: {state.get("positions", {}).get("count", 0)}')
    
    # Check capital
    capital = state.get('capital', {})
    print(f'   Total Capital: ${capital.get("total", 0):,.2f}')
    print(f'   Cash: ${capital.get("cash", 0):,.2f}')
    
    # Show open positions
    positions = state.get('positions', {}).get('open', [])
    if positions:
        print(f'\n   📊 OPEN POSITIONS:')
        for pos in positions:
            symbol = pos.get('symbol', 'N/A')
            qty = pos.get('quantity', 0)
            entry = pos.get('entry_price', 0)
            current = pos.get('current_price', 0)
            pnl_pct = pos.get('unrealized_pnl_pct', 0)
            print(f'      {symbol}: {qty} shares @ ${entry:.2f}, '
                  f'Now ${current:.2f} ({pnl_pct:+.2f}%)')
else:
    print(f'❌ State file NOT FOUND: {state_path}')
    print('   Dashboard has no saved trading state.')

print()
print('🔍 STEP 3: Real-Time Price Check')
print('-' * 80)

try:
    import yfinance as yf
    
    test_stocks = ['BHP.AX', 'CBA.AX']
    print('Fetching current prices...\n')
    
    for symbol in test_stocks:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info.get('currentPrice', info.get('regularMarketPrice', 0))
        prev_close = info.get('previousClose', 0)
        
        if current and prev_close:
            change_pct = ((current - prev_close) / prev_close) * 100
            print(f'{symbol:10} Current: ${current:.2f}  Prev: ${prev_close:.2f}  '
                  f'Change: {change_pct:+.2f}%')
        else:
            print(f'{symbol:10} ❌ Could not fetch price')
except Exception as e:
    print(f'❌ Error fetching prices: {e}')

print()
print('=' * 80)
print('  DIAGNOSIS')
print('=' * 80)
print()

if not report_found:
    print('🚨 PROBLEM: AU Pipeline output not found')
    print('   SOLUTION: Re-run the pipeline:')
    print('   python run_au_pipeline_v1.3.13.py --symbols BHP.AX,CBA.AX,RIO.AX,DRO.AX,BGA.AX,REH.AX,DTL.AX')
    print()

if not os.path.exists(state_path) or os.path.getsize(state_path) < 100:
    print('🚨 PROBLEM: Dashboard state is empty')
    print('   The dashboard is showing data but not saving/loading positions')
    print('   SOLUTION: Use the "Start Trading" button in the dashboard')
    print('   This will initialize the paper trading system')
    print()

print('📋 NEXT STEPS:')
print('1. If morning report exists → Dashboard should load those signals')
print('2. If state is empty → Click "Start Trading" in dashboard')
print('3. If prices are still wrong → Restart dashboard (Ctrl+C, then START.bat)')
print()

input('Press Enter to exit...')

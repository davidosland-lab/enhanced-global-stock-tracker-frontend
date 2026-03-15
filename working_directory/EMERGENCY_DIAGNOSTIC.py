"""
EMERGENCY DIAGNOSTIC v1.3.15.79
Checks real-time prices and fixes data staleness issue

Run this to see what's actually happening with your stocks
"""
import yfinance as yf
from datetime import datetime
import pytz

print('=' * 80)
print('  EMERGENCY PRICE DIAGNOSTIC')
print('=' * 80)
print()

# Your stocks
stocks = [
    'AAPL', 'MSFT', 'CBA.AX', 'BHP.AX', 'HSBA.L', 'BARC.L', 
    'LGEN.L', 'STAN.L', 'PHNX.L', 'BHP.L', 'RIO.L', 'USB', 
    'TFC', 'FITB', 'DRO.AX', 'BGA.AX', 'REH.AX', 'DTL.AX'
]

# Focus on problem stocks
priority_stocks = ['BHP.AX', 'CBA.AX', '^AORD']

print('🚨 PRIORITY CHECK: BHP.AX, CBA.AX, AORD')
print('=' * 80)
print()

gmt = pytz.timezone('GMT')
aest = pytz.timezone('Australia/Sydney')
now_gmt = datetime.now(gmt)
now_aest = datetime.now(aest)

print(f'Current Time:')
print(f'  GMT:  {now_gmt.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'  AEST: {now_aest.strftime("%Y-%m-%d %H:%M:%S")}')
print()

for symbol in priority_stocks:
    print(f'\n📊 {symbol}')
    print('-' * 60)
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current info
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        prev_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
        
        if current_price and prev_close:
            change_pct = ((current_price - prev_close) / prev_close) * 100
            print(f'  Current Price:   ${current_price:.2f}')
            print(f'  Previous Close:  ${prev_close:.2f}')
            print(f'  Change:          {change_pct:+.2f}%')
            
            if change_pct > 1.0:
                print(f'  ✅ STRONG UP - Should be BUY signal!')
            elif change_pct > 0.5:
                print(f'  ✅ Up - Consider BUY')
            elif change_pct < -0.5:
                print(f'  ❌ Down - NO BUY')
        else:
            print(f'  ⚠️  Could not get current price')
        
        # Check latest data timestamp
        hist = ticker.history(period='1d', interval='1m')
        if len(hist) > 0:
            latest_time = hist.index[-1]
            latest_price = hist['Close'].iloc[-1]
            print(f'  Latest Data:     {latest_time.strftime("%Y-%m-%d %H:%M:%S")} ({latest_price:.2f})')
            
            # Time since last update
            time_diff = now_gmt.replace(tzinfo=None) - latest_time.replace(tzinfo=None)
            minutes_ago = time_diff.total_seconds() / 60
            print(f'  Data Age:        {minutes_ago:.0f} minutes ago')
            
            if minutes_ago > 15:
                print(f'  ⚠️  WARNING: Data is STALE!')
        else:
            print(f'  ❌ NO recent data available')
            
    except Exception as e:
        print(f'  ❌ ERROR: {e}')

print()
print('=' * 80)
print('  ALL STOCKS QUICK CHECK')
print('=' * 80)
print()

for symbol in stocks:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        prev_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
        
        if current_price and prev_close:
            change_pct = ((current_price - prev_close) / prev_close) * 100
            status = '✅ UP' if change_pct > 0.5 else '❌ DOWN' if change_pct < -0.5 else '➖ FLAT'
            print(f'{symbol:12} {current_price:8.2f}  {change_pct:+6.2f}%  {status}')
        else:
            print(f'{symbol:12} {"N/A":8}  {"N/A":6}  ⚠️  NO DATA')
    except:
        print(f'{symbol:12} {"ERROR":8}  {"ERROR":6}  ❌')

print()
print('=' * 80)
print('  DIAGNOSIS')
print('=' * 80)
print()

print('If you see:')
print('  1. BHP.AX showing DOWN when market is UP → Dashboard using OLD data')
print('  2. CBA.AX showing UP but NO BUY signal → ML pipeline not running')
print('  3. Data Age > 15 minutes → Real-time feed broken')
print()
print('SOLUTIONS:')
print('  Issue 1: Restart dashboard (stops using cached data)')
print('  Issue 2: Run AU pipeline: python run_au_pipeline_v1.3.13.py')
print('  Issue 3: Check internet connection / yfinance working')
print()

input('Press Enter to exit...')

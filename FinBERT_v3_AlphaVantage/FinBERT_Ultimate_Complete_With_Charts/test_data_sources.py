import os
import yfinance as yf
import requests
import json

# Disable cache
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

print("="*60)
print("TESTING ALL DATA SOURCES")
print("="*60)

# Your Alpha Vantage Key
ALPHA_VANTAGE_KEY = '68ZFANK047DL0KSR'

print("\n1. TESTING YAHOO FINANCE:")
print("-" * 40)
symbols = ['AAPL', 'CBA.AX']
for symbol in symbols:
    print(f"\nTesting {symbol}:")
    try:
        data = yf.download(symbol, period='5d', progress=False)
        if not data.empty:
            print(f"  ✓ SUCCESS: Got {len(data)} days of data")
            print(f"  Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"  ✗ FAILED: Empty data returned")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print("\n2. TESTING ALPHA VANTAGE:")
print("-" * 40)
for symbol in ['AAPL', 'CBA.AX']:
    print(f"\nTesting {symbol}:")
    try:
        # For Australian stocks, remove .AX for Alpha Vantage
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': av_symbol,
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        print(f"  URL: {url}")
        print(f"  Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for various response types
            if 'Error Message' in data:
                print(f"  ✗ API Error: {data['Error Message']}")
            elif 'Note' in data:
                print(f"  ✗ Rate limit: {data['Note']}")
            elif 'Time Series (Daily)' in data:
                ts = data['Time Series (Daily)']
                dates = list(ts.keys())[:5]
                print(f"  ✓ SUCCESS: Got {len(ts)} days of data")
                if dates:
                    latest = ts[dates[0]]
                    print(f"  Latest close: ${float(latest['4. close']):.2f}")
            else:
                print(f"  ✗ Unexpected response structure")
                print(f"  Keys in response: {list(data.keys())}")
        else:
            print(f"  ✗ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print("\n3. TESTING DIRECT YAHOO FINANCE API:")
print("-" * 40)
try:
    import urllib.request
    
    url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    
    if 'chart' in data and 'result' in data['chart']:
        result = data['chart']['result'][0]
        if 'meta' in result:
            price = result['meta'].get('regularMarketPrice', 0)
            print(f"  ✓ Direct API works: AAPL price ${price:.2f}")
    else:
        print(f"  ✗ Unexpected response")
        
except Exception as e:
    print(f"  ✗ ERROR: {e}")

print("\n" + "="*60)
input("Press Enter to exit...")
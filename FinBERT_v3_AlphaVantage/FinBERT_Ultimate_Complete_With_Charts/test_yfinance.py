import os
import yfinance as yf

# Disable cache
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

print("Testing yfinance data fetching...")
print("-" * 50)

# Test symbols
symbols = ['AAPL', 'MSFT', 'CBA.AX']

for symbol in symbols:
    print(f"\nTesting {symbol}:")
    try:
        # Method 1: Using download
        print(f"  Using yf.download()...")
        data = yf.download(symbol, period='1d', progress=False)
        if not data.empty:
            print(f"    ✓ Got {len(data)} rows")
            print(f"    Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"    ✗ No data returned")
            
        # Method 2: Using Ticker
        print(f"  Using yf.Ticker()...")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            print(f"    ✓ Got {len(hist)} rows")
            print(f"    Latest close: ${hist['Close'].iloc[-1]:.2f}")
        else:
            print(f"    ✗ No data returned")
            
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "-" * 50)
input("Press Enter to exit...")
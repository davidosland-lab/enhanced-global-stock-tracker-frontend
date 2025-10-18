#!/usr/bin/env python3
"""
Fix Yahoo Finance connection issues
"""

import subprocess
import sys

def fix_yfinance():
    """Try multiple fixes for yfinance"""
    
    print("=" * 60)
    print("Fixing Yahoo Finance Connection")
    print("=" * 60)
    print()
    
    fixes = [
        # Fix 1: Upgrade yfinance
        {
            'name': 'Upgrading yfinance to latest version',
            'command': [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yfinance']
        },
        # Fix 2: Install development version
        {
            'name': 'Installing yfinance development version',
            'command': [sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'git+https://github.com/ranaroussi/yfinance.git']
        },
        # Fix 3: Clear yfinance cache
        {
            'name': 'Clearing yfinance cache',
            'command': [sys.executable, '-c', 'import yfinance as yf; yf.utils.clear_cache()']
        },
        # Fix 4: Install with dependencies
        {
            'name': 'Reinstalling with all dependencies',
            'command': [sys.executable, '-m', 'pip', 'install', '--upgrade', 'requests', 'lxml', 'html5lib', 'beautifulsoup4', 'yfinance']
        }
    ]
    
    for fix in fixes:
        print(f"\nTrying: {fix['name']}...")
        try:
            result = subprocess.run(fix['command'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {fix['name']} - Success")
            else:
                print(f"⚠️ {fix['name']} - Failed")
                print(f"Error: {result.stderr[:200]}")
        except Exception as e:
            print(f"❌ {fix['name']} - Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Yahoo Finance after fixes...")
    print("=" * 60)
    
    # Test if it works now
    try:
        import yfinance as yf
        print("\nTesting with different methods...")
        
        # Method 1: Using download
        print("\n1. Testing yf.download()...")
        data = yf.download("AAPL", period="5d", progress=False, threads=False)
        if not data.empty:
            print(f"✅ SUCCESS! Got {len(data)} days of AAPL data")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
            return True
        
        # Method 2: Using Ticker
        print("\n2. Testing yf.Ticker()...")
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        if not hist.empty:
            print(f"✅ SUCCESS! Got {len(hist)} days of data")
            return True
            
    except Exception as e:
        print(f"\n❌ Still not working: {e}")
    
    print("\n" + "=" * 60)
    print("Alternative: Use a different package")
    print("=" * 60)
    print("""
    If yfinance still doesn't work, you can:
    
    1. Use yfinance-cache (works offline):
       pip install yfinance-cache
    
    2. Use pandas-datareader:
       pip install pandas-datareader
       
    3. Use Alpha Vantage (need free API key):
       pip install alpha-vantage
       
    4. Check if you're behind a proxy/firewall
    """)
    
    return False

if __name__ == "__main__":
    success = fix_yfinance()
    if success:
        print("\n🎉 Yahoo Finance is working now!")
        print("You can use the real system without any fallback data.")
    else:
        print("\n⚠️ Yahoo Finance still has issues.")
        print("This might be a network/firewall problem.")
        print("Try on a different network or with a VPN.")
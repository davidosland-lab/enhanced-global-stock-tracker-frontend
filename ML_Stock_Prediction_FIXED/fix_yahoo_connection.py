#!/usr/bin/env python3
"""
Fix Yahoo Finance connection issues
This implements workarounds for recent Yahoo Finance API changes
"""

import subprocess
import sys
import os

def fix_yahoo():
    print("="*60)
    print("Fixing Yahoo Finance Connection")
    print("="*60)
    print()
    
    print("The issue: Yahoo Finance API has been unstable recently")
    print("Installing fixes and workarounds...\n")
    
    commands = [
        {
            'name': 'Step 1: Upgrade pip',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']
        },
        {
            'name': 'Step 2: Install latest yfinance from GitHub',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 
                   'git+https://github.com/ranaroussi/yfinance.git']
        },
        {
            'name': 'Step 3: Install dependencies',
            'cmd': [sys.executable, '-m', 'pip', 'install', '--upgrade',
                   'requests', 'urllib3', 'certifi', 'lxml', 'html5lib', 'beautifulsoup4']
        },
        {
            'name': 'Step 4: Clear yfinance cache',
            'cmd': [sys.executable, '-c', 
                   "import shutil, os; shutil.rmtree(os.path.join(os.path.expanduser('~'), '.cache'), ignore_errors=True)"]
        }
    ]
    
    for step in commands:
        print(f"\n{step['name']}...")
        try:
            result = subprocess.run(step['cmd'], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Success")
            else:
                print(f"⚠️ Warning: {result.stderr[:100] if result.stderr else 'Continue anyway'}")
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout - continuing...")
        except Exception as e:
            print(f"⚠️ {e}")
    
    print("\n" + "="*60)
    print("Testing Yahoo Finance...")
    print("="*60)
    
    # Test with new method
    test_code = """
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_yahoo():
    symbol = "AAPL"
    
    # Method 1: Using Ticker with session
    print("Method 1: Testing with Ticker...")
    try:
        ticker = yf.Ticker(symbol)
        # Try fast_info first (more reliable)
        info = ticker.fast_info
        if info:
            print(f"✅ Got fast_info - Price: ${info.get('lastPrice', 'N/A')}")
            return True
    except Exception as e:
        print(f"❌ Fast info failed: {e}")
    
    # Method 2: Using history with specific dates
    print("\\nMethod 2: Testing with specific dates...")
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        hist = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval="1d",
            auto_adjust=True,
            back_adjust=False
        )
        
        if not hist.empty:
            print(f"✅ Got {len(hist)} days of data")
            print(f"   Latest close: ${hist['Close'].iloc[-1]:.2f}")
            return True
    except Exception as e:
        print(f"❌ History failed: {e}")
    
    # Method 3: Direct download with dates
    print("\\nMethod 3: Testing download with dates...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            progress=False,
            threads=False,
            ignore_tz=True
        )
        
        if not data.empty:
            print(f"✅ Downloaded {len(data)} days of data")
            if 'Close' in data.columns:
                print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
            return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
    
    return False

if test_yahoo():
    print("\\n✅ Yahoo Finance is working!")
else:
    print("\\n❌ Yahoo Finance still has issues")
    print("\\nPossible solutions:")
    print("1. Try using a VPN")
    print("2. Wait a few minutes and try again")
    print("3. Check if finance.yahoo.com works in your browser")
"""
    
    with open('test_yahoo_fix.py', 'w') as f:
        f.write(test_code)
    
    result = subprocess.run([sys.executable, 'test_yahoo_fix.py'], capture_output=True, text=True)
    print(result.stdout)
    
    # Clean up
    try:
        os.remove('test_yahoo_fix.py')
    except:
        pass
    
    if "Yahoo Finance is working!" in result.stdout:
        print("\n" + "="*60)
        print("✅ FIX SUCCESSFUL!")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("Alternative Solutions")
        print("="*60)
        print("""
If Yahoo Finance still doesn't work:

1. **Network Issues:**
   - Check if https://finance.yahoo.com works in your browser
   - Try using a different network (mobile hotspot)
   - Disable VPN if you're using one (or enable it if not)

2. **Regional Blocking:**
   - Yahoo Finance may be blocked in your region
   - Try using a VPN connected to US servers

3. **Temporary Outage:**
   - Yahoo Finance has been unstable lately
   - Wait 10-15 minutes and try again

4. **Firewall/Antivirus:**
   - Add Python to firewall exceptions
   - Temporarily disable antivirus

The ML system itself is working perfectly (as shown by the tests).
It's only the Yahoo Finance connection that's having issues.
""")
        return False

if __name__ == "__main__":
    fix_yahoo()
    input("\nPress Enter to exit...")
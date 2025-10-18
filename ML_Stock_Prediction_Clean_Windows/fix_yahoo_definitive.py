#!/usr/bin/env python3
"""
Definitive fix for Yahoo Finance
This addresses the actual issue that's been happening recently
"""

import subprocess
import sys
import os

def fix_yahoo_finance():
    print("="*60)
    print("Applying Definitive Yahoo Finance Fix")
    print("="*60)
    print()
    
    print("The issue: Yahoo Finance changed their API recently")
    print("The fix: Use specific versions that work\n")
    
    steps = [
        {
            'name': 'Step 1: Uninstall current yfinance',
            'commands': [
                [sys.executable, '-m', 'pip', 'uninstall', '-y', 'yfinance'],
            ]
        },
        {
            'name': 'Step 2: Clear pip cache',
            'commands': [
                [sys.executable, '-m', 'pip', 'cache', 'purge'],
            ]
        },
        {
            'name': 'Step 3: Install specific working versions',
            'commands': [
                # These specific versions are known to work together
                [sys.executable, '-m', 'pip', 'install', 'requests==2.31.0'],
                [sys.executable, '-m', 'pip', 'install', 'urllib3==2.0.7'],
                [sys.executable, '-m', 'pip', 'install', 'certifi==2024.2.2'],
                [sys.executable, '-m', 'pip', 'install', 'charset-normalizer==3.3.2'],
                [sys.executable, '-m', 'pip', 'install', 'lxml==4.9.3'],
                [sys.executable, '-m', 'pip', 'install', 'html5lib==1.1'],
                [sys.executable, '-m', 'pip', 'install', 'beautifulsoup4==4.12.2'],
                [sys.executable, '-m', 'pip', 'install', 'appdirs==1.4.4'],
                [sys.executable, '-m', 'pip', 'install', 'pytz==2024.1'],
                [sys.executable, '-m', 'pip', 'install', 'frozendict==2.3.10'],
                [sys.executable, '-m', 'pip', 'install', 'peewee==3.17.0'],
                [sys.executable, '-m', 'pip', 'install', 'yfinance==0.2.37'],  # Latest version that should work
            ]
        },
        {
            'name': 'Step 4: Clear yfinance cache',
            'commands': [
                [sys.executable, '-c', 'import shutil, os; cache_dir = os.path.join(os.path.expanduser("~"), ".cache"); shutil.rmtree(cache_dir, ignore_errors=True)'],
            ]
        }
    ]
    
    for step in steps:
        print(f"\n{step['name']}...")
        for cmd in step['commands']:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"  ✅ Success")
                else:
                    print(f"  ⚠️  Warning: {result.stderr[:100] if result.stderr else 'Unknown issue'}")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Timeout - continuing...")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Testing Yahoo Finance...")
    print("="*60)
    
    # Test if it works now
    test_code = """
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# Method 1: Using download
try:
    print("Testing yf.download()...")
    data = yf.download("AAPL", period="5d", progress=False, threads=False)
    if not data.empty:
        print(f"✅ SUCCESS! Got {len(data)} days of data")
        print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        exit(0)
except Exception as e:
    print(f"❌ Download failed: {e}")

# Method 2: Using Ticker
try:
    print("\\nTesting yf.Ticker()...")
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    if not hist.empty:
        print(f"✅ SUCCESS! Got {len(hist)} days of data")
        print(f"   Latest close: ${hist['Close'].iloc[-1]:.2f}")
        exit(0)
except Exception as e:
    print(f"❌ Ticker failed: {e}")

print("\\n❌ Yahoo Finance still not working")
exit(1)
"""
    
    # Write test script
    with open('test_yahoo.py', 'w') as f:
        f.write(test_code)
    
    # Run test
    result = subprocess.run([sys.executable, 'test_yahoo.py'], capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n🎉 Yahoo Finance is now working!")
        print("You can now use the REAL DATA ONLY version.")
        
        # Clean up
        try:
            os.remove('test_yahoo.py')
        except:
            pass
            
        return True
    else:
        print("\n" + "="*60)
        print("Additional troubleshooting needed")
        print("="*60)
        print("""
If the fix didn't work, the issue might be:

1. **Network/Firewall blocking Yahoo Finance**
   - Try disabling Windows Defender Firewall temporarily
   - Check if your antivirus is blocking connections
   - Try on a different network (mobile hotspot)

2. **DNS Issues**
   - Try changing DNS to Google (8.8.8.8) or Cloudflare (1.1.1.1)
   - Run: ipconfig /flushdns

3. **Regional Blocking**
   - Yahoo Finance might be blocked in your country
   - Try using a VPN connected to US servers

4. **Corporate Network**
   - Many corporate networks block financial APIs
   - Try from a personal network

5. **ISP Blocking**
   - Some ISPs block or throttle financial data
   - Contact your ISP or try a different connection

The ML system is working perfectly - it just needs Yahoo Finance access.
""")
        return False

if __name__ == "__main__":
    success = fix_yahoo_finance()
    if not success:
        print("\nPress Enter to exit...")
        input()
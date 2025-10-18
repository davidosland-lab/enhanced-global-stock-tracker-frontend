#!/usr/bin/env python3
"""
Diagnose the REAL Yahoo Finance issue
NO FALLBACK - Just find and fix the problem
"""

import sys
import subprocess
import json
import requests

def check_yfinance_version():
    """Check current yfinance version"""
    print("Checking yfinance version...")
    try:
        import yfinance as yf
        print(f"Current version: {yf.__version__}")
        
        # Check for known broken versions
        if yf.__version__ in ['0.2.28', '0.2.29', '0.2.30']:
            print("❌ This version has known issues!")
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_direct_yahoo_api():
    """Test direct access to Yahoo Finance API"""
    print("\nTesting direct Yahoo Finance API access...")
    
    # Test URLs that yfinance uses
    test_urls = [
        ("Yahoo Finance main", "https://finance.yahoo.com"),
        ("Query1 API", "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"),
        ("Query2 API", "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    working_urls = []
    for name, url in test_urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Working (Status {response.status_code})")
                working_urls.append(url)
                
                # Check if we got JSON data
                if 'query' in url:
                    try:
                        data = response.json()
                        if 'chart' in data:
                            print(f"   Got valid data structure")
                    except:
                        print(f"   Warning: Response is not valid JSON")
            else:
                print(f"❌ {name}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: {str(e)[:50]}")
    
    return len(working_urls) > 0

def check_ssl_certificates():
    """Check SSL certificate issues"""
    print("\nChecking SSL certificates...")
    try:
        import ssl
        import certifi
        print(f"SSL version: {ssl.OPENSSL_VERSION}")
        print(f"Certifi location: {certifi.where()}")
        return True
    except Exception as e:
        print(f"SSL issue: {e}")
        return False

def test_with_different_settings():
    """Test yfinance with different settings"""
    print("\nTesting yfinance with different configurations...")
    
    import yfinance as yf
    
    # Test different approaches
    tests = [
        {
            'name': 'Standard download',
            'func': lambda: yf.download("AAPL", period="5d", progress=False)
        },
        {
            'name': 'Download with threads=False',
            'func': lambda: yf.download("AAPL", period="5d", progress=False, threads=False)
        },
        {
            'name': 'Download with group_by=None',
            'func': lambda: yf.download("AAPL", period="5d", progress=False, group_by=None)
        },
        {
            'name': 'Ticker with proxy',
            'func': lambda: yf.Ticker("AAPL").history(period="5d", proxy=None)
        }
    ]
    
    for test in tests:
        print(f"\nTrying: {test['name']}...")
        try:
            result = test['func']()
            if result is not None and not result.empty:
                print(f"✅ SUCCESS! Got {len(result)} days of data")
                return True
            else:
                print(f"⚠️  No data returned")
        except Exception as e:
            error_msg = str(e)
            if "Expecting value" in error_msg:
                print(f"❌ JSON decode error - Yahoo might be returning HTML instead of JSON")
            else:
                print(f"❌ Error: {error_msg[:100]}")
    
    return False

def apply_fix():
    """Apply the most likely fix"""
    print("\n" + "="*60)
    print("Applying fixes...")
    print("="*60)
    
    fixes_applied = []
    
    # Fix 1: Downgrade to known working version
    print("\n1. Installing known working version (0.2.18)...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "yfinance==0.2.18"], 
                      capture_output=True, check=True)
        print("✅ Installed yfinance 0.2.18")
        fixes_applied.append("Downgraded to stable version")
    except:
        print("❌ Could not install 0.2.18")
    
    # Fix 2: Clear cache
    print("\n2. Clearing yfinance cache...")
    try:
        import yfinance as yf
        # Try to clear cache
        import shutil
        import os
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "py-yfinance")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("✅ Cache cleared")
            fixes_applied.append("Cache cleared")
    except:
        pass
    
    # Fix 3: Set proper headers
    print("\n3. Setting proper request headers...")
    try:
        # Create a session with proper headers
        import yfinance as yf
        from requests import Session
        
        session = Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        ticker = yf.Ticker("AAPL", session=session)
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print("✅ Headers fix worked!")
            fixes_applied.append("Headers configured")
            return True
    except Exception as e:
        print(f"❌ Headers fix failed: {e}")
    
    return fixes_applied

def main():
    print("="*60)
    print("Yahoo Finance Diagnostic - NO FALLBACK VERSION")
    print("="*60)
    print()
    
    # Run diagnostics
    version_ok = check_yfinance_version()
    api_ok = test_direct_yahoo_api()
    ssl_ok = check_ssl_certificates()
    
    if not api_ok:
        print("\n❌ PROBLEM IDENTIFIED: Cannot reach Yahoo Finance API")
        print("This could be:")
        print("1. Firewall/Proxy blocking")
        print("2. DNS issues")
        print("3. Regional blocking")
        print("\nTry:")
        print("- Using a VPN")
        print("- Different network")
        print("- Check firewall settings")
        return
    
    # Try different settings
    works = test_with_different_settings()
    
    if not works:
        print("\n❌ PROBLEM IDENTIFIED: yfinance parsing issue")
        print("Yahoo probably changed their API response format")
        
        # Apply fixes
        fixes = apply_fix()
        
        if fixes:
            print(f"\n✅ Applied fixes: {', '.join(fixes)}")
            print("\nNow test again with: python quick_test.py")
    else:
        print("\n✅ yfinance is working!")

if __name__ == "__main__":
    main()
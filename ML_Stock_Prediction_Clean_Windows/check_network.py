#!/usr/bin/env python3
"""
Check if the issue is network-related
"""

import socket
import requests
import json

def check_network():
    print("="*60)
    print("Network Connectivity Check")
    print("="*60)
    print()
    
    # Check basic internet
    print("1. Checking basic internet connectivity...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("   ✅ Internet connection: OK")
    except:
        print("   ❌ No internet connection")
        return False
    
    # Check DNS resolution
    print("\n2. Checking DNS resolution...")
    domains = [
        "finance.yahoo.com",
        "query1.finance.yahoo.com",
        "query2.finance.yahoo.com"
    ]
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"   ✅ {domain}: {ip}")
        except:
            print(f"   ❌ {domain}: Cannot resolve")
    
    # Check HTTP access
    print("\n3. Testing HTTP access to Yahoo Finance...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    urls = [
        "https://finance.yahoo.com",
        "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?period1=0&period2=9999999999&interval=1d",
    ]
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"   ✅ {url[:50]}... : Status {response.status_code}")
            
            if "v8/finance/chart" in url and response.status_code == 200:
                try:
                    data = response.json()
                    if 'chart' in data and 'result' in data['chart']:
                        print("      ✅ Valid JSON data received")
                    else:
                        print("      ⚠️  Unexpected JSON structure")
                except:
                    print("      ❌ Response is not JSON - might be blocked")
                    # Print first 200 chars to see what we're getting
                    print(f"      Response: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {url[:50]}... : {str(e)[:50]}")
    
    # Check for proxy
    print("\n4. Checking for proxy settings...")
    import os
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ⚠️  {var} = {value}")
            proxy_found = True
    
    if not proxy_found:
        print("   ✅ No proxy detected")
    else:
        print("   ⚠️  Proxy detected - this might interfere with Yahoo Finance")
    
    # Windows specific checks
    print("\n5. Windows-specific checks...")
    try:
        import platform
        if platform.system() == "Windows":
            # Check Windows Defender Firewall
            import subprocess
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'currentprofile'], 
                                  capture_output=True, text=True)
            if 'State                                 ON' in result.stdout:
                print("   ⚠️  Windows Firewall is ON - might be blocking")
            else:
                print("   ✅ Windows Firewall is OFF")
    except:
        pass
    
    print("\n" + "="*60)
    print("Network Check Complete")
    print("="*60)

if __name__ == "__main__":
    check_network()
    print("\nPress Enter to exit...")
    input()
#!/usr/bin/env python3
"""
Diagnostic Tool for ML Stock Predictor
Checks system configuration and troubleshoots issues on Windows 11
"""

import os
import sys
import json
import platform
import subprocess
import socket
from datetime import datetime

print("="*70)
print("   ML STOCK PREDICTOR - DIAGNOSTIC TOOL")
print("="*70)

# System Information
print("\n📊 SYSTEM INFORMATION:")
print("-"*50)
print(f"Operating System: {platform.system()} {platform.release()}")
print(f"Platform: {platform.platform()}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")

# Check Python packages
print("\n📦 PACKAGE STATUS:")
print("-"*50)

packages_to_check = [
    ('yfinance', 'Yahoo Finance data fetching'),
    ('flask', 'Web server framework'),
    ('flask-cors', 'CORS support for Flask'),
    ('pandas', 'Data manipulation'),
    ('numpy', 'Numerical operations'),
    ('requests', 'HTTP requests (Alpha Vantage)'),
    ('scikit-learn', 'Machine learning'),
    ('xgboost', 'XGBoost models')
]

missing_packages = []
installed_packages = []

for package, description in packages_to_check:
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {package:15} - {description}")
        installed_packages.append(package)
    except ImportError:
        print(f"❌ {package:15} - {description} [NOT INSTALLED]")
        missing_packages.append(package)

# Network checks
print("\n🌐 NETWORK TESTS:")
print("-"*50)

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

# Check port 8000
if check_port(8000):
    print(f"⚠️  Port 8000 is IN USE - Server may already be running")
    print("   Run 'netstat -an | findstr :8000' to check what's using it")
else:
    print(f"✅ Port 8000 is AVAILABLE")

# Test localhost connectivity
try:
    socket.gethostbyname('localhost')
    print("✅ Localhost resolution working")
except:
    print("❌ Localhost resolution failed")

# Check for firewall (Windows specific)
if platform.system() == 'Windows':
    print("\n🔒 WINDOWS FIREWALL:")
    print("-"*50)
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'show', 'currentprofile'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if 'State' in result.stdout and 'ON' in result.stdout:
            print("⚠️  Windows Firewall is ON - May block connections")
            print("   You may need to allow Python through the firewall")
        else:
            print("✅ Windows Firewall appears to be OFF")
    except:
        print("⚠️  Could not check Windows Firewall status")

# Test Yahoo Finance
print("\n📈 YAHOO FINANCE TEST:")
print("-"*50)

try:
    import yfinance as yf
    print("Testing Yahoo Finance connection...")
    
    # Test with a known stock
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    
    if info and 'regularMarketPrice' in info:
        print(f"✅ Yahoo Finance is WORKING")
        print(f"   Test stock (AAPL): ${info.get('regularMarketPrice', 'N/A')}")
    else:
        print("⚠️  Yahoo Finance connected but returned limited data")
        
    # Test Australian stock
    print("\nTesting Australian stock (CBA.AX)...")
    aus_ticker = yf.Ticker("CBA.AX")
    aus_info = aus_ticker.info
    
    if aus_info and 'regularMarketPrice' in aus_info:
        print(f"✅ Australian stocks WORKING")
        print(f"   CBA.AX: AUD ${aus_info.get('regularMarketPrice', 'N/A')}")
    else:
        print("⚠️  Australian stock data limited")
        
except ImportError:
    print("❌ yfinance not installed - Cannot test Yahoo Finance")
except Exception as e:
    print(f"❌ Yahoo Finance test failed: {e}")

# Test Alpha Vantage
print("\n💹 ALPHA VANTAGE TEST:")
print("-"*50)

ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
print(f"API Key configured: {ALPHA_VANTAGE_API_KEY[:8]}...")

try:
    import requests
    print("Testing Alpha Vantage connection...")
    
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': 'AAPL',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if 'Global Quote' in data:
        print(f"✅ Alpha Vantage is WORKING")
        quote = data['Global Quote']
        print(f"   AAPL: ${quote.get('05. price', 'N/A')}")
    elif 'Note' in data:
        print(f"⚠️  Alpha Vantage rate limit reached")
        print(f"   Message: {data['Note'][:50]}...")
    elif 'Error Message' in data:
        print(f"❌ Alpha Vantage error: {data['Error Message']}")
    else:
        print(f"⚠️  Unexpected Alpha Vantage response")
        
except ImportError:
    print("❌ requests not installed - Cannot test Alpha Vantage")
except Exception as e:
    print(f"❌ Alpha Vantage test failed: {e}")

# Create diagnostic report
print("\n📋 DIAGNOSTIC SUMMARY:")
print("-"*50)

issues_found = []
recommendations = []

if missing_packages:
    issues_found.append(f"{len(missing_packages)} required packages missing")
    recommendations.append(f"Run: pip install {' '.join(missing_packages)}")

if check_port(8000):
    issues_found.append("Port 8000 is already in use")
    recommendations.append("Kill existing process or use a different port")

if platform.system() == 'Windows':
    recommendations.append("Ensure Python is allowed through Windows Firewall")
    recommendations.append("Run Command Prompt as Administrator if issues persist")

if not issues_found:
    print("✅ No major issues detected!")
    print("   System appears ready to run the ML Stock Predictor")
else:
    print(f"⚠️  {len(issues_found)} issue(s) found:")
    for issue in issues_found:
        print(f"   - {issue}")
    
    print(f"\n📌 RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"   • {rec}")

# Save diagnostic report
report_filename = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
print(f"\n💾 Saving detailed report to: {report_filename}")

with open(report_filename, 'w') as f:
    f.write("ML STOCK PREDICTOR - DIAGNOSTIC REPORT\n")
    f.write(f"Generated: {datetime.now()}\n")
    f.write("="*70 + "\n\n")
    
    f.write("SYSTEM INFORMATION:\n")
    f.write(f"  OS: {platform.system()} {platform.release()}\n")
    f.write(f"  Platform: {platform.platform()}\n")
    f.write(f"  Python: {sys.version}\n")
    f.write(f"  Current Dir: {os.getcwd()}\n\n")
    
    f.write("PACKAGE STATUS:\n")
    f.write(f"  Installed: {', '.join(installed_packages) if installed_packages else 'None'}\n")
    f.write(f"  Missing: {', '.join(missing_packages) if missing_packages else 'None'}\n\n")
    
    f.write("NETWORK STATUS:\n")
    f.write(f"  Port 8000: {'IN USE' if check_port(8000) else 'AVAILABLE'}\n\n")
    
    f.write("ISSUES FOUND:\n")
    if issues_found:
        for issue in issues_found:
            f.write(f"  - {issue}\n")
    else:
        f.write("  None\n")
    
    f.write("\nRECOMMENDATIONS:\n")
    for rec in recommendations:
        f.write(f"  • {rec}\n")

print("\n" + "="*70)
print("Diagnostic complete! Press Enter to exit...")
input()
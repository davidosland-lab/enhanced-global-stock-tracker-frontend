#!/usr/bin/env python3
"""
GSMT Ver 8.1.3 - CBA Module Test Suite
Tests Commonwealth Bank of Australia tracking functionality
"""

import requests
import json
import time
from datetime import datetime
import sys

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header():
    """Print test header"""
    print("=" * 70)
    print(" " * 20 + "GSMT Ver 8.1.3 - CBA MODULE TEST")
    print(" " * 15 + "Commonwealth Bank of Australia Tracker")
    print("=" * 70)
    print()

def test_server_status():
    """Test if servers are running"""
    print(f"{BLUE}Testing Server Connectivity...{RESET}")
    
    servers = [
        ("Market Data Server", "http://localhost:8000/health"),
        ("CBA Specialist Server", "http://localhost:8001/")
    ]
    
    all_ok = True
    for name, url in servers:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  {GREEN}✓{RESET} {name}: Online")
            else:
                print(f"  {RED}✗{RESET} {name}: Error (Status {response.status_code})")
                all_ok = False
        except Exception as e:
            print(f"  {RED}✗{RESET} {name}: Not responding")
            all_ok = False
    
    return all_ok

def test_cba_endpoints():
    """Test all CBA specialist endpoints"""
    print(f"\n{BLUE}Testing CBA Module Endpoints...{RESET}")
    
    base_url = "http://localhost:8001"
    endpoints = [
        {
            "name": "CBA Stock Price",
            "url": "/api/cba/price",
            "check": lambda r: "CBA.AX" in str(r) and "price" in r
        },
        {
            "name": "CBA History",
            "url": "/api/cba/history?period=1d",
            "check": lambda r: "prices" in r and len(r["prices"]) > 0
        },
        {
            "name": "CBA Predictions",
            "url": "/api/cba/prediction",
            "check": lambda r: "predictions" in r and "models" in r
        },
        {
            "name": "CBA Publications",
            "url": "/api/cba/publications",
            "check": lambda r: "publications" in r
        },
        {
            "name": "Market Sentiment",
            "url": "/api/cba/sentiment",
            "check": lambda r: "sentiment" in r and "news" in r
        },
        {
            "name": "Banking Sector",
            "url": "/api/cba/banking-sector",
            "check": lambda r: "peers" in r and "CBA.AX" in str(r)
        }
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint['url']}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if endpoint["check"](data):
                    print(f"  {GREEN}✓{RESET} {endpoint['name']}: Working")
                    results.append(True)
                    
                    # Print sample data for key endpoints
                    if "price" in endpoint["url"]:
                        print(f"    - Symbol: {data.get('symbol', 'N/A')}")
                        print(f"    - Price: ${data.get('price', 'N/A')}")
                        print(f"    - Change: {data.get('changePercent', 'N/A')}%")
                    elif "prediction" in endpoint["url"]:
                        if "predictions" in data:
                            pred = data["predictions"].get("1_day", {})
                            print(f"    - 1 Day Prediction: ${pred.get('predicted', 'N/A')}")
                            print(f"    - Confidence: {pred.get('confidence', 'N/A')}%")
                    elif "sentiment" in endpoint["url"]:
                        sent = data.get("sentiment", {})
                        print(f"    - Overall Sentiment: {sent.get('trend', 'N/A')}")
                        print(f"    - Score: {sent.get('overall', 'N/A')}")
                else:
                    print(f"  {YELLOW}⚠{RESET} {endpoint['name']}: Unexpected response format")
                    results.append(False)
            else:
                print(f"  {RED}✗{RESET} {endpoint['name']}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  {RED}✗{RESET} {endpoint['name']}: {str(e)}")
            results.append(False)
    
    return all(results)

def test_market_data():
    """Test market data server"""
    print(f"\n{BLUE}Testing Market Data Integration...{RESET}")
    
    try:
        # Test ASX indices
        response = requests.get("http://localhost:8000/api/indices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            indices = data.get("indices", {})
            
            # Check for ASX
            if "^AXJO" in indices:
                asx = indices["^AXJO"]
                print(f"  {GREEN}✓{RESET} ASX 200: ${asx.get('price', 'N/A')} ({asx.get('changePercent', 'N/A')}%)")
            else:
                print(f"  {YELLOW}⚠{RESET} ASX 200 not found in indices")
            
            # Check total markets
            print(f"  {GREEN}✓{RESET} Total markets tracked: {len(indices)}")
            return True
    except Exception as e:
        print(f"  {RED}✗{RESET} Market data error: {str(e)}")
        return False

def test_frontend_files():
    """Check if frontend files exist"""
    print(f"\n{BLUE}Checking Frontend Files...{RESET}")
    
    import os
    frontend_dir = "frontend"
    required_files = [
        "comprehensive_dashboard.html",
        "cba_market_tracker.html",
        "indices_tracker.html",
        "single_stock_tracker.html",
        "technical_analysis.html",
        "prediction_center.html",
        "config.js"
    ]
    
    all_present = True
    for file in required_files:
        filepath = os.path.join(frontend_dir, file)
        if os.path.exists(filepath):
            print(f"  {GREEN}✓{RESET} {file}")
        else:
            print(f"  {RED}✗{RESET} {file} - Missing")
            all_present = False
    
    return all_present

def validate_cba_data():
    """Validate CBA specific data accuracy"""
    print(f"\n{BLUE}Validating CBA Data Accuracy...{RESET}")
    
    try:
        response = requests.get("http://localhost:8001/api/cba/price", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            validations = [
                ("Symbol", data.get("symbol") == "CBA.AX", data.get("symbol")),
                ("Name", "Commonwealth Bank" in data.get("name", ""), data.get("name")),
                ("Market Cap", data.get("marketCap", 0) > 100000000000, f"${data.get('marketCap', 0)/1e9:.1f}B"),
                ("P/E Ratio", 10 < data.get("peRatio", 0) < 30, data.get("peRatio")),
                ("Dividend Yield", 2 < data.get("dividendYield", 0) < 6, f"{data.get('dividendYield', 0)}%")
            ]
            
            all_valid = True
            for check_name, is_valid, value in validations:
                if is_valid:
                    print(f"  {GREEN}✓{RESET} {check_name}: {value}")
                else:
                    print(f"  {RED}✗{RESET} {check_name}: {value} (Invalid)")
                    all_valid = False
            
            return all_valid
    except Exception as e:
        print(f"  {RED}✗{RESET} Validation error: {str(e)}")
        return False

def test_banking_peers():
    """Test banking sector comparison"""
    print(f"\n{BLUE}Testing Banking Sector Comparison...{RESET}")
    
    try:
        response = requests.get("http://localhost:8001/api/cba/banking-sector", timeout=10)
        if response.status_code == 200:
            data = response.json()
            peers = data.get("peers", [])
            
            # Check for Big 4 banks
            big4 = ["CBA.AX", "WBC.AX", "ANZ.AX", "NAB.AX"]
            found = []
            
            for peer in peers:
                symbol = peer.get("symbol", "")
                if symbol in big4:
                    found.append(symbol)
                    print(f"  {GREEN}✓{RESET} {peer.get('name', symbol)}: ${peer.get('price', 'N/A')}")
            
            missing = set(big4) - set(found)
            if missing:
                for symbol in missing:
                    print(f"  {YELLOW}⚠{RESET} {symbol}: Not found")
            
            return len(found) >= 3  # At least 3 of Big 4
    except Exception as e:
        print(f"  {RED}✗{RESET} Banking sector error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header()
    
    # Check if servers should be started
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--start-servers":
        print(f"{YELLOW}Starting servers...{RESET}\n")
        import subprocess
        import os
        
        # Start servers
        try:
            # Start market data server
            subprocess.Popen(
                ["python", "backend/market_data_server.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  {GREEN}✓{RESET} Market Data Server started")
            
            time.sleep(2)
            
            # Start CBA specialist server
            subprocess.Popen(
                ["python", "backend/cba_specialist_server.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  {GREEN}✓{RESET} CBA Specialist Server started")
            
            print(f"\n{YELLOW}Waiting for servers to initialize...{RESET}")
            time.sleep(5)
        except Exception as e:
            print(f"  {RED}✗{RESET} Failed to start servers: {e}")
            sys.exit(1)
    
    # Run tests
    test_results = []
    
    # Test 1: Server Status
    if test_server_status():
        test_results.append(("Server Connectivity", True))
    else:
        test_results.append(("Server Connectivity", False))
        print(f"\n{RED}Servers are not running!{RESET}")
        print(f"Run: python {sys.argv[0]} --start-servers")
        sys.exit(1)
    
    # Test 2: CBA Endpoints
    test_results.append(("CBA Endpoints", test_cba_endpoints()))
    
    # Test 3: Market Data
    test_results.append(("Market Data", test_market_data()))
    
    # Test 4: Frontend Files
    test_results.append(("Frontend Files", test_frontend_files()))
    
    # Test 5: CBA Data Validation
    test_results.append(("CBA Data Validation", validate_cba_data()))
    
    # Test 6: Banking Peers
    test_results.append(("Banking Peers", test_banking_peers()))
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 25 + "TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    print("\n" + "-" * 70)
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{total}){RESET}")
        print(f"\n{GREEN}CBA Module is working correctly!{RESET}")
        print("Commonwealth Bank of Australia tracking is fully operational.")
    else:
        print(f"{YELLOW}⚠ PARTIAL SUCCESS ({passed}/{total}){RESET}")
        print(f"\nSome tests failed. Please check the output above.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
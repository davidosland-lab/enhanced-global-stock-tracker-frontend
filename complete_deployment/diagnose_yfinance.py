#!/usr/bin/env python3
"""
FinBERT v4.4.4 - yfinance Diagnostic Tool

Comprehensive diagnostic to identify why yfinance is failing with:
"Expecting value: line 1 column 1 (char 0)"

This script tests:
1. Network connectivity to Yahoo Finance
2. yfinance library functionality
3. curl_cffi installation and browser impersonation
4. Different yfinance API methods
5. Direct HTTP requests to Yahoo Finance endpoints
6. DNS resolution and proxy settings

Author: Claude AI Assistant
Date: 2025-11-10
"""

import sys
import os
import time
import json
import platform
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class YFinanceDiagnostic:
    """Comprehensive yfinance diagnostic tool"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.platform(),
            'python_version': sys.version,
            'tests': []
        }
        self.test_tickers = [
            'CBA.AX',  # ASX - Commonwealth Bank
            '^AXJO',   # ASX 200 Index
            'AAPL',    # NASDAQ - Apple
            '^GSPC',   # S&P 500 Index
        ]
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    def print_test(self, test_name: str, status: str, message: str = "", details: Any = None):
        """Print test result with formatting"""
        status_colors = {
            'PASS': Colors.OKGREEN,
            'FAIL': Colors.FAIL,
            'WARN': Colors.WARNING,
            'INFO': Colors.OKCYAN
        }
        color = status_colors.get(status, '')
        symbol = {'PASS': '✓', 'FAIL': '✗', 'WARN': '⚠', 'INFO': 'ℹ'}.get(status, '•')
        
        print(f"{color}{symbol} {test_name}: {status}{Colors.ENDC}")
        if message:
            print(f"  {message}")
        if details:
            print(f"  Details: {details}")
        
        # Store result
        self.results['tests'].append({
            'name': test_name,
            'status': status,
            'message': message,
            'details': str(details) if details else None
        })
    
    def test_basic_imports(self) -> bool:
        """Test 1: Check if required libraries can be imported"""
        self.print_header("TEST 1: Basic Library Imports")
        
        all_passed = True
        
        # Test yfinance
        try:
            import yfinance as yf
            version = yf.__version__ if hasattr(yf, '__version__') else 'unknown'
            self.print_test("yfinance import", "PASS", f"Version: {version}")
        except Exception as e:
            self.print_test("yfinance import", "FAIL", str(e))
            all_passed = False
        
        # Test curl_cffi (critical for yfinance 0.2.x+)
        try:
            import curl_cffi
            version = curl_cffi.__version__ if hasattr(curl_cffi, '__version__') else 'unknown'
            self.print_test("curl_cffi import", "PASS", f"Version: {version}")
        except Exception as e:
            self.print_test("curl_cffi import", "FAIL", "curl_cffi not found - CRITICAL for yfinance 0.2.x+", str(e))
            all_passed = False
        
        # Test requests
        try:
            import requests
            self.print_test("requests import", "PASS", f"Version: {requests.__version__}")
        except Exception as e:
            self.print_test("requests import", "FAIL", str(e))
            all_passed = False
        
        # Test pandas
        try:
            import pandas as pd
            self.print_test("pandas import", "PASS", f"Version: {pd.__version__}")
        except Exception as e:
            self.print_test("pandas import", "FAIL", str(e))
            all_passed = False
        
        return all_passed
    
    def test_network_connectivity(self) -> bool:
        """Test 2: Check network connectivity to Yahoo Finance"""
        self.print_header("TEST 2: Network Connectivity")
        
        import requests
        
        endpoints = [
            ('Yahoo Finance Homepage', 'https://finance.yahoo.com'),
            ('Yahoo Finance API v8', 'https://query2.finance.yahoo.com/v8/finance/chart/AAPL'),
            ('Yahoo Finance API v7', 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL'),
        ]
        
        all_passed = True
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    self.print_test(f"Connect to {name}", "PASS", f"Status: {response.status_code}, Size: {len(response.content)} bytes")
                else:
                    self.print_test(f"Connect to {name}", "WARN", f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.print_test(f"Connect to {name}", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def test_yfinance_ticker_creation(self) -> bool:
        """Test 3: Test yfinance Ticker object creation"""
        self.print_header("TEST 3: yfinance Ticker Object Creation")
        
        import yfinance as yf
        
        all_passed = True
        for ticker_symbol in self.test_tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)
                self.print_test(f"Create Ticker({ticker_symbol})", "PASS", f"Object created: {type(ticker)}")
            except Exception as e:
                self.print_test(f"Create Ticker({ticker_symbol})", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def test_yfinance_fast_info(self) -> bool:
        """Test 4: Test yfinance fast_info (lightweight API)"""
        self.print_header("TEST 4: yfinance fast_info Method")
        
        import yfinance as yf
        
        all_passed = True
        for ticker_symbol in self.test_tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.fast_info
                
                # Try to access common attributes
                attrs = ['last_price', 'currency', 'exchange', 'market_cap']
                found_attrs = {attr: getattr(info, attr, None) for attr in attrs if hasattr(info, attr)}
                
                if found_attrs:
                    self.print_test(f"fast_info({ticker_symbol})", "PASS", f"Attributes: {list(found_attrs.keys())}", found_attrs)
                else:
                    self.print_test(f"fast_info({ticker_symbol})", "FAIL", "No attributes accessible")
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"fast_info({ticker_symbol})", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def test_yfinance_history(self) -> bool:
        """Test 5: Test yfinance history method"""
        self.print_header("TEST 5: yfinance history Method")
        
        import yfinance as yf
        
        all_passed = True
        for ticker_symbol in self.test_tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period='5d')
                
                if not hist.empty:
                    self.print_test(f"history({ticker_symbol})", "PASS", 
                                  f"Rows: {len(hist)}, Columns: {list(hist.columns)[:3]}...",
                                  f"Latest close: {hist['Close'].iloc[-1]:.2f}")
                else:
                    self.print_test(f"history({ticker_symbol})", "FAIL", "Empty DataFrame returned")
                    all_passed = False
                    
            except Exception as e:
                self.print_test(f"history({ticker_symbol})", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def test_yfinance_info(self) -> bool:
        """Test 6: Test yfinance info method (heavy API call)"""
        self.print_header("TEST 6: yfinance info Method (Comprehensive)")
        
        import yfinance as yf
        
        all_passed = True
        # Only test one ticker for info (slow)
        ticker_symbol = 'CBA.AX'
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if info and isinstance(info, dict) and len(info) > 0:
                key_fields = ['shortName', 'regularMarketPrice', 'currency', 'exchange']
                found_fields = {k: info.get(k) for k in key_fields if k in info}
                
                self.print_test(f"info({ticker_symbol})", "PASS", 
                              f"Fields: {len(info)}, Key data: {list(found_fields.keys())}",
                              found_fields)
            else:
                self.print_test(f"info({ticker_symbol})", "FAIL", "Empty or invalid info dict returned")
                all_passed = False
                
        except Exception as e:
            self.print_test(f"info({ticker_symbol})", "FAIL", str(e))
            all_passed = False
        
        return all_passed
    
    def test_curl_cffi_browser_impersonation(self) -> bool:
        """Test 7: Test curl_cffi browser impersonation"""
        self.print_header("TEST 7: curl_cffi Browser Impersonation")
        
        try:
            from curl_cffi import requests as curl_requests
            
            url = 'https://query2.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=5d'
            
            # Test with Chrome impersonation
            try:
                response = curl_requests.get(url, impersonate="chrome")
                if response.status_code == 200:
                    data = response.json()
                    self.print_test("curl_cffi Chrome impersonation", "PASS", 
                                  f"Status: {response.status_code}, JSON valid",
                                  f"Response size: {len(response.content)} bytes")
                else:
                    self.print_test("curl_cffi Chrome impersonation", "WARN", 
                                  f"Non-200 status: {response.status_code}")
            except Exception as e:
                self.print_test("curl_cffi Chrome impersonation", "FAIL", str(e))
                return False
            
            return True
            
        except ImportError:
            self.print_test("curl_cffi browser impersonation", "FAIL", 
                          "curl_cffi not installed - CRITICAL for yfinance 0.2.x+")
            return False
        except Exception as e:
            self.print_test("curl_cffi browser impersonation", "FAIL", str(e))
            return False
    
    def test_direct_yahoo_api(self) -> bool:
        """Test 8: Test direct Yahoo Finance API calls"""
        self.print_header("TEST 8: Direct Yahoo Finance API Calls")
        
        import requests
        
        # Test quote endpoint
        try:
            url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=CBA.AX'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                        quotes = data['quoteResponse']['result']
                        if quotes:
                            quote = quotes[0]
                            self.print_test("Direct Yahoo API (quote)", "PASS",
                                          f"Symbol: {quote.get('symbol')}, Price: {quote.get('regularMarketPrice')}",
                                          f"Exchange: {quote.get('exchange')}")
                        else:
                            self.print_test("Direct Yahoo API (quote)", "FAIL", "Empty result array")
                            return False
                    else:
                        self.print_test("Direct Yahoo API (quote)", "FAIL", "Unexpected JSON structure", data)
                        return False
                except json.JSONDecodeError as e:
                    self.print_test("Direct Yahoo API (quote)", "FAIL", 
                                  f"JSON parse error: {str(e)}", 
                                  f"Response: {response.text[:200]}...")
                    return False
            else:
                self.print_test("Direct Yahoo API (quote)", "FAIL", 
                              f"HTTP {response.status_code}", 
                              response.text[:200])
                return False
                
        except Exception as e:
            self.print_test("Direct Yahoo API (quote)", "FAIL", str(e))
            return False
        
        return True
    
    def test_environment_variables(self) -> bool:
        """Test 9: Check environment variables that might affect connectivity"""
        self.print_header("TEST 9: Environment Variables")
        
        env_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'REQUESTS_CA_BUNDLE']
        
        found_vars = {}
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                found_vars[var] = value
                self.print_test(f"Environment variable {var}", "INFO", f"Value: {value}")
        
        if not found_vars:
            self.print_test("Proxy/SSL environment variables", "PASS", "None set (expected)")
        
        return True
    
    def test_dns_resolution(self) -> bool:
        """Test 10: Test DNS resolution for Yahoo Finance domains"""
        self.print_header("TEST 10: DNS Resolution")
        
        import socket
        
        domains = [
            'finance.yahoo.com',
            'query1.finance.yahoo.com',
            'query2.finance.yahoo.com'
        ]
        
        all_passed = True
        for domain in domains:
            try:
                ip = socket.gethostbyname(domain)
                self.print_test(f"DNS resolve {domain}", "PASS", f"IP: {ip}")
            except socket.gaierror as e:
                self.print_test(f"DNS resolve {domain}", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def generate_diagnosis(self):
        """Generate final diagnosis and recommendations"""
        self.print_header("DIAGNOSTIC SUMMARY")
        
        passed = sum(1 for t in self.results['tests'] if t['status'] == 'PASS')
        failed = sum(1 for t in self.results['tests'] if t['status'] == 'FAIL')
        warnings = sum(1 for t in self.results['tests'] if t['status'] == 'WARN')
        
        print(f"\nTotal Tests Run: {len(self.results['tests'])}")
        print(f"{Colors.OKGREEN}✓ Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}✗ Failed: {failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠ Warnings: {warnings}{Colors.ENDC}")
        
        # Analyze failures and provide recommendations
        print(f"\n{Colors.BOLD}DIAGNOSIS:{Colors.ENDC}")
        
        # Check for curl_cffi issues
        curl_cffi_tests = [t for t in self.results['tests'] if 'curl_cffi' in t['name']]
        if any(t['status'] == 'FAIL' for t in curl_cffi_tests):
            print(f"\n{Colors.FAIL}🔴 CRITICAL: curl_cffi NOT WORKING{Colors.ENDC}")
            print("   This is the most likely cause of your issues.")
            print("   yfinance 0.2.x+ REQUIRES curl_cffi for browser impersonation.")
            print(f"\n   {Colors.BOLD}SOLUTION:{Colors.ENDC}")
            print("   1. Install curl_cffi: pip install curl_cffi")
            print("   2. If already installed, reinstall: pip uninstall curl_cffi && pip install curl_cffi")
            print("   3. If still failing, try: pip install curl_cffi --force-reinstall")
        
        # Check for network issues
        network_tests = [t for t in self.results['tests'] if 'Connect to' in t['name'] or 'DNS' in t['name']]
        network_failed = [t for t in network_tests if t['status'] == 'FAIL']
        if network_failed:
            print(f"\n{Colors.FAIL}🔴 NETWORK CONNECTIVITY ISSUES{Colors.ENDC}")
            print("   Cannot reach Yahoo Finance servers.")
            print(f"\n   {Colors.BOLD}POSSIBLE CAUSES:{Colors.ENDC}")
            print("   - Firewall blocking access")
            print("   - Corporate proxy/VPN interfering")
            print("   - ISP-level blocking")
            print("   - Yahoo Finance blocking your IP/region")
        
        # Check yfinance method failures
        yf_tests = [t for t in self.results['tests'] if 'fast_info' in t['name'] or 'history' in t['name']]
        yf_failed = [t for t in yf_tests if t['status'] == 'FAIL']
        if yf_failed and not any(t['status'] == 'FAIL' for t in curl_cffi_tests):
            print(f"\n{Colors.WARNING}⚠ YFINANCE API FAILURES{Colors.ENDC}")
            print("   yfinance methods failing despite curl_cffi working.")
            print(f"\n   {Colors.BOLD}POSSIBLE CAUSES:{Colors.ENDC}")
            print("   - Yahoo Finance API rate limiting")
            print("   - Yahoo Finance blocking automated requests")
            print("   - yfinance version incompatibility")
            print(f"\n   {Colors.BOLD}SOLUTIONS:{Colors.ENDC}")
            print("   1. Wait 5-10 minutes (rate limit cooldown)")
            print("   2. Update yfinance: pip install --upgrade yfinance")
            print("   3. Check yfinance GitHub issues for known problems")
            print("   4. Try using VPN to change IP address")
        
        # If everything passed but original system failed
        if failed == 0 and warnings == 0:
            print(f"\n{Colors.OKGREEN}✓ ALL DIAGNOSTICS PASSED{Colors.ENDC}")
            print("   The yfinance library appears to be working correctly in isolation.")
            print(f"\n   {Colors.BOLD}POSSIBLE CAUSES OF YOUR ORIGINAL FAILURE:{Colors.ENDC}")
            print("   1. Timing issue - Yahoo may have been temporarily blocking")
            print("   2. Session pollution - old requests.Session() interfering")
            print("   3. Concurrent requests triggering rate limits")
            print("   4. System-specific environment issue")
            print(f"\n   {Colors.BOLD}RECOMMENDATIONS:{Colors.ENDC}")
            print("   1. Try running your screener again (issue may be resolved)")
            print("   2. Add delays between yfinance calls (0.5-1 second)")
            print("   3. Reduce parallel workers to avoid rate limiting")
            print("   4. Enable yfinance debug logging: yf.enable_debug_mode()")
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    def save_results(self, filename: str = 'yfinance_diagnostic_results.json'):
        """Save diagnostic results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n{Colors.OKGREEN}✓ Results saved to: {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ Failed to save results: {e}{Colors.ENDC}")
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("="*80)
        print("FinBERT v4.4.4 - yfinance Diagnostic Tool".center(80))
        print("="*80)
        print(f"{Colors.ENDC}")
        print(f"Platform: {platform.platform()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        tests = [
            self.test_basic_imports,
            self.test_network_connectivity,
            self.test_dns_resolution,
            self.test_environment_variables,
            self.test_curl_cffi_browser_impersonation,
            self.test_direct_yahoo_api,
            self.test_yfinance_ticker_creation,
            self.test_yfinance_fast_info,
            self.test_yfinance_history,
            self.test_yfinance_info,
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"{Colors.FAIL}✗ Test failed with exception: {e}{Colors.ENDC}")
        
        # Generate diagnosis
        self.generate_diagnosis()
        
        # Save results
        self.save_results()


def main():
    """Main entry point"""
    diagnostic = YFinanceDiagnostic()
    diagnostic.run_all_tests()
    
    print("\n" + "="*80)
    print("Diagnostic complete!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

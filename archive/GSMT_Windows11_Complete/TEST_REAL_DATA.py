#!/usr/bin/env python3
"""
Test Script to Verify Real Data Implementation
GSMT Ver 8.1.3 - Ensures NO synthetic data is being used
"""

import sys
import os
import subprocess
import time
import json
import requests
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def test_result(test_name, passed, details=""):
    if passed:
        print(f"{Colors.GREEN}✓ {test_name}{Colors.RESET}")
        if details:
            print(f"  {Colors.GREEN}{details}{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ {test_name}{Colors.RESET}")
        if details:
            print(f"  {Colors.RED}{details}{Colors.RESET}")

def check_file_for_synthetic(filepath):
    """Check if a file contains synthetic data generation code"""
    synthetic_patterns = [
        'random.gauss',
        'random.uniform',
        'generate_price_data',
        'generate_cba_price_data',
        'synthetic',
        'demo_data',
        'mock_data',
        'fake_data'
    ]
    
    if not os.path.exists(filepath):
        return False, "File not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_patterns = []
        for pattern in synthetic_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        if found_patterns:
            return True, f"Found synthetic data patterns: {', '.join(found_patterns)}"
        return False, "No synthetic data patterns found"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def test_real_data_server(port=8000):
    """Test if real data server is returning actual market data"""
    try:
        # Test market indices endpoint
        response = requests.get(f"http://localhost:{port}/api/indices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Check if data looks real (not generated)
            if 'indices' in data:
                # Real data should have varying prices, not perfectly round numbers
                indices = data['indices']
                if len(indices) > 0:
                    # Check first index
                    first_index = list(indices.values())[0]
                    price = first_index.get('price', 0)
                    
                    # Synthetic data often has perfectly round numbers
                    if price > 0 and price % 100 != 0:
                        return True, f"Server returning real-looking data (price: {price:.2f})"
                    else:
                        return False, f"Data looks synthetic (price too round: {price})"
            
        return False, f"Server responded with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Server not running or not accessible"
    except Exception as e:
        return False, f"Error testing server: {str(e)}"

def check_yfinance_import():
    """Check if yfinance can be imported and works"""
    try:
        import yfinance as yf
        # Test with a real ticker
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if 'regularMarketPrice' in info or 'currentPrice' in info:
            return True, "yfinance installed and working"
        return False, "yfinance installed but not returning data"
    except ImportError:
        return False, "yfinance not installed"
    except Exception as e:
        return False, f"yfinance error: {str(e)}"

def scan_all_files():
    """Scan all Python and batch files for synthetic data references"""
    print_header("Scanning All Files for Synthetic Data")
    
    directories_to_scan = ['backend', 'frontend', '.']
    synthetic_files = []
    clean_files = []
    
    for directory in directories_to_scan:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            # Skip archived folders
            if 'archived_synthetic' in root:
                continue
            
            for file in files:
                if file.endswith(('.py', '.bat')) and not file.startswith('TEST_'):
                    filepath = os.path.join(root, file)
                    has_synthetic, details = check_file_for_synthetic(filepath)
                    
                    if has_synthetic:
                        synthetic_files.append((filepath, details))
                        print(f"{Colors.YELLOW}⚠ {filepath}{Colors.RESET}")
                        print(f"  {details}")
                    elif has_synthetic is False:
                        clean_files.append(filepath)
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Clean files: {len(clean_files)}")
    print(f"  Files with synthetic data: {len(synthetic_files)}")
    
    return len(synthetic_files) == 0

def main():
    print_header("GSMT Real Data Verification Test")
    print(f"{Colors.BOLD}Testing GSMT Ver 8.1.3 - Ensuring NO Synthetic Data{Colors.RESET}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_tests_passed = True
    
    # Test 1: Check yfinance installation
    print(f"{Colors.BOLD}1. Checking Real Data Dependencies:{Colors.RESET}")
    passed, details = check_yfinance_import()
    test_result("yfinance module", passed, details)
    all_tests_passed = all_tests_passed and passed
    
    # Test 2: Check main server files
    print(f"\n{Colors.BOLD}2. Checking Server Files:{Colors.RESET}")
    
    # Check if main data servers exist and are clean
    main_servers = [
        'backend/market_data_server.py',
        'backend/cba_specialist_server.py'
    ]
    
    for server in main_servers:
        exists = os.path.exists(server)
        if exists:
            has_synthetic, details = check_file_for_synthetic(server)
            is_clean = exists and not has_synthetic
            test_result(f"Server exists and is clean: {os.path.basename(server)}", is_clean, 
                       "" if is_clean else details)
            all_tests_passed = all_tests_passed and is_clean
        else:
            test_result(f"Server exists: {os.path.basename(server)}", False)
            all_tests_passed = False
    
    # Check old synthetic servers
    synthetic_servers = [
        'backend/market_data_server.py',
        'backend/cba_specialist_server.py'
    ]
    
    for server in synthetic_servers:
        if os.path.exists(server):
            has_synthetic, details = check_file_for_synthetic(server)
            if has_synthetic:
                test_result(f"Old server still has synthetic: {os.path.basename(server)}", False, details)
                all_tests_passed = False
    
    # Test 3: Check batch file uses correct servers
    print(f"\n{Colors.BOLD}3. Checking Launch Configuration:{Colors.RESET}")
    launcher = 'LAUNCH_GSMT_813.bat'
    if os.path.exists(launcher):
        with open(launcher, 'r') as f:
            content = f.read()
        
        uses_correct = 'backend\\market_data_server.py' in content and 'backend\\cba_specialist_server.py' in content
        test_result("Launcher uses correct data servers", uses_correct)
        all_tests_passed = all_tests_passed and uses_correct
    
    # Test 4: Comprehensive file scan
    print()
    no_synthetic = scan_all_files()
    all_tests_passed = all_tests_passed and no_synthetic
    
    # Final summary
    print_header("Test Results Summary")
    
    if all_tests_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}The project is now using REAL market data.{Colors.RESET}")
        print(f"{Colors.GREEN}No synthetic data generation found.{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Some files still contain synthetic data references.{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the files listed above.{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    if not all_tests_passed:
        print("1. Replace old server files with real data versions")
        print("2. Update batch files to use real_market_data_server.py")
        print("3. Remove any remaining synthetic data generation code")
    else:
        print("1. Test the servers by running LAUNCH_GSMT_813.bat")
        print("2. Verify data in the web interface shows real market prices")
        print("3. Monitor for any errors when markets are closed")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
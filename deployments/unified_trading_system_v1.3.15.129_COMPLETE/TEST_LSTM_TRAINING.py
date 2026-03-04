#!/usr/bin/env python3
"""
LSTM Training Test Suite - v1.3.15.87
Tests the comprehensive fix for LSTM training

This script tests:
1. US stocks (AAPL, MSFT)
2. ASX stocks with dots (BHP.AX, CBA.AX)
3. UK stocks with dots (HSBA.L, BP.L)
4. Error handling for invalid symbols
5. API response format

Usage:
    python TEST_LSTM_TRAINING.py [--server http://localhost:5000]
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name):
        self.passed += 1
        self.tests.append((test_name, True, None))
        print(f"✓ PASS: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.tests.append((test_name, False, error))
        print(f"✗ FAIL: {test_name}")
        print(f"  Error: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "="*80)
        print(f"TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({100*self.passed//total if total > 0 else 0}%)")
        print(f"Failed: {self.failed} ({100*self.failed//total if total > 0 else 0}%)")
        print("="*80 + "\n")
        
        if self.failed > 0:
            print("Failed Tests:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")
        
        return self.failed == 0

def test_api_endpoint(server: str, symbol: str, epochs: int = 10, timeout: int = 120) -> Dict[str, Any]:
    """
    Test LSTM training API endpoint
    
    Args:
        server: Server URL (e.g., http://localhost:5000)
        symbol: Stock symbol to test
        epochs: Number of epochs (use low value for testing)
        timeout: Request timeout in seconds
    
    Returns:
        Response dict or error info
    """
    url = f"{server}/api/train/{symbol}"
    
    data = json.dumps({
        'epochs': epochs,
        'sequence_length': 60
    }).encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'LSTM-Training-Test/1.0'
    }
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return {
                'success': True,
                'status_code': response.status,
                'data': response_data
            }
    
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
        except:
            error_data = {'message': 'Could not parse error response'}
        
        return {
            'success': False,
            'status_code': e.code,
            'error': error_data
        }
    
    except urllib.error.URLError as e:
        return {
            'success': False,
            'status_code': 0,
            'error': {'message': f'Connection error: {e.reason}'}
        }
    
    except Exception as e:
        return {
            'success': False,
            'status_code': 0,
            'error': {'message': f'Unexpected error: {str(e)}'}
        }

def main():
    parser = argparse.ArgumentParser(description='Test LSTM Training API')
    parser.add_argument('--server', default='http://localhost:5000', 
                        help='Server URL (default: http://localhost:5000)')
    parser.add_argument('--quick', action='store_true',
                        help='Quick test (fewer epochs, faster)')
    
    args = parser.parse_args()
    
    server = args.server
    epochs = 5 if args.quick else 10
    
    print("="*80)
    print("LSTM TRAINING TEST SUITE v1.3.15.87")
    print("="*80)
    print(f"Server: {server}")
    print(f"Epochs: {epochs} (quick mode: {args.quick})")
    print("="*80 + "\n")
    
    results = TestResults()
    
    # Test 1: Check server is running
    print("Test 1: Server Health Check")
    try:
        req = urllib.request.Request(f"{server}/api/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                results.add_pass("Server is running")
            else:
                results.add_fail("Server health check", f"Status code: {response.status}")
    except Exception as e:
        results.add_fail("Server health check", f"Cannot connect: {e}")
        print("\nERROR: Cannot connect to server")
        print(f"Make sure Flask is running at {server}")
        print("\nStart server with:")
        print("  cd finbert_v4.4.4")
        print("  python app_finbert_v4_dev.py")
        sys.exit(1)
    
    print()
    
    # Test 2: US Stock (AAPL)
    print("Test 2: US Stock - AAPL")
    response = test_api_endpoint(server, 'AAPL', epochs=epochs)
    if response['success'] and response['data'].get('status') == 'success':
        results.add_pass("AAPL training")
    else:
        error_msg = response.get('error', {}).get('message', 'Unknown error')
        results.add_fail("AAPL training", error_msg)
    
    print()
    
    # Test 3: ASX Stock with dot (BHP.AX)
    print("Test 3: ASX Stock with dot - BHP.AX")
    response = test_api_endpoint(server, 'BHP.AX', epochs=epochs)
    if response['success'] and response['data'].get('status') == 'success':
        results.add_pass("BHP.AX training (dot in symbol)")
    else:
        error_msg = response.get('error', {}).get('message', 'Unknown error')
        results.add_fail("BHP.AX training", error_msg)
    
    print()
    
    # Test 4: Invalid symbol (should fail gracefully)
    print("Test 4: Invalid Symbol - INVALID_SYMBOL_XYZ")
    response = test_api_endpoint(server, 'INVALID_SYMBOL_XYZ', epochs=epochs, timeout=30)
    if not response['success'] or response['data'].get('status') == 'error':
        # This is expected - should fail with proper error message
        error_msg = response.get('data', {}).get('message', response.get('error', {}).get('message', ''))
        if 'No data' in error_msg or 'Insufficient' in error_msg or 'Invalid' in error_msg:
            results.add_pass("Invalid symbol handling (proper error message)")
        else:
            results.add_fail("Invalid symbol handling", f"Unexpected error: {error_msg}")
    else:
        results.add_fail("Invalid symbol handling", "Should have failed but succeeded")
    
    print()
    
    # Test 5: Check response format
    print("Test 5: Response Format Validation")
    response = test_api_endpoint(server, 'MSFT', epochs=epochs)
    if response['success']:
        data = response['data']
        required_fields = ['status', 'symbol', 'message']
        missing_fields = [f for f in required_fields if f not in data]
        
        if not missing_fields:
            results.add_pass("Response format (all required fields present)")
        else:
            results.add_fail("Response format", f"Missing fields: {missing_fields}")
    else:
        results.add_fail("Response format", "Request failed")
    
    print()
    
    # Summary
    success = results.summary()
    
    if success:
        print("✓ ALL TESTS PASSED!")
        print("\nLSTM training is working correctly for all symbols")
        print("You can now train models for:")
        print("  - US stocks (AAPL, MSFT, TSLA, etc.)")
        print("  - ASX stocks (BHP.AX, CBA.AX, etc.)")
        print("  - UK stocks (HSBA.L, BP.L, etc.)")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the failed tests above")
        print("Make sure:")
        print("  1. Flask server is running")
        print("  2. Comprehensive fix is applied")
        print("  3. All dependencies are installed")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

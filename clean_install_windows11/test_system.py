#!/usr/bin/env python3
"""
System Test Script - Verify all components are working
"""

import sys
import os
import subprocess
import time
import requests
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

def print_header(title):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}{title}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def test_python_version():
    """Test Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"{Fore.GREEN}✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"{Fore.RED}✗ Python {version.major}.{version.minor}.{version.micro} - Requires 3.8+")
        return False

def test_imports():
    """Test critical imports"""
    print_header("Import Test")
    
    imports = [
        ('fastapi', 'FastAPI Backend'),
        ('uvicorn', 'ASGI Server'),
        ('yfinance', 'Yahoo Finance API'),
        ('pandas', 'Data Processing'),
        ('numpy', 'Numerical Computing'),
        ('tensorflow', 'ML Training'),
        ('sklearn', 'Machine Learning'),
        ('cachetools', 'Caching')
    ]
    
    all_ok = True
    for module, description in imports:
        try:
            __import__(module)
            print(f"{Fore.GREEN}✓ {module:<15} - {description}")
        except ImportError as e:
            print(f"{Fore.RED}✗ {module:<15} - {description} (Error: {e})")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Test file structure"""
    print_header("File Structure Check")
    
    required_files = [
        'backend.py',
        'ml_training_backend.py',
        'historical_data_manager.py',
        'index.html',
        'WORKING_PREDICTION_MODULE.html',
        'modules/ml_training_centre.html',
        'requirements_ml.txt',
        'LAUNCH_ALL_SERVICES.bat'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"{Fore.GREEN}✓ {file}")
        else:
            print(f"{Fore.RED}✗ {file} - Missing")
            all_ok = False
    
    return all_ok

def test_backend_connection():
    """Test backend connection"""
    print_header("Backend Connection Test")
    
    try:
        response = requests.get('http://localhost:8002/', timeout=2)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Main Backend (port 8002) - Online")
            return True
        else:
            print(f"{Fore.YELLOW}⚠ Main Backend (port 8002) - Responding but not ready")
            return False
    except:
        print(f"{Fore.RED}✗ Main Backend (port 8002) - Offline")
        print(f"{Fore.YELLOW}  Run: python backend.py")
        return False

def test_ml_backend_connection():
    """Test ML backend connection"""
    print_header("ML Backend Connection Test")
    
    try:
        response = requests.get('http://localhost:8003/health', timeout=2)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ ML Backend (port 8003) - Online")
            return True
        else:
            print(f"{Fore.YELLOW}⚠ ML Backend (port 8003) - Responding but not ready")
            return False
    except:
        print(f"{Fore.RED}✗ ML Backend (port 8003) - Offline")
        print(f"{Fore.YELLOW}  Run: python ml_training_backend.py")
        return False

def test_yahoo_finance():
    """Test Yahoo Finance connection"""
    print_header("Yahoo Finance API Test")
    
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if 'regularMarketPrice' in info or 'currentPrice' in info:
            price = info.get('regularMarketPrice', info.get('currentPrice', 'N/A'))
            print(f"{Fore.GREEN}✓ Yahoo Finance API - Working")
            print(f"  AAPL Current Price: ${price}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠ Yahoo Finance API - Limited data")
            return True
    except Exception as e:
        print(f"{Fore.RED}✗ Yahoo Finance API - Error: {e}")
        return False

def test_sqlite_database():
    """Test SQLite database"""
    print_header("SQLite Database Test")
    
    try:
        from historical_data_manager import HistoricalDataManager
        hdm = HistoricalDataManager()
        print(f"{Fore.GREEN}✓ SQLite Database - Initialized")
        print(f"  Database: historical_data/stocks.db")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ SQLite Database - Error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Stock Tracker System Test")
    print(f"{Fore.CYAN}{'='*60}")
    
    results = []
    
    # Run tests
    results.append(('Python Version', test_python_version()))
    results.append(('Import Test', test_imports()))
    results.append(('File Structure', test_file_structure()))
    results.append(('Yahoo Finance', test_yahoo_finance()))
    results.append(('SQLite Database', test_sqlite_database()))
    results.append(('Main Backend', test_backend_connection()))
    results.append(('ML Backend', test_ml_backend_connection()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Fore.GREEN}✓ PASS" if result else f"{Fore.RED}✗ FAIL"
        print(f"{status:<20} {name}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{Fore.GREEN}✅ System is ready to use!")
        print(f"\n{Fore.YELLOW}To start the system:")
        print(f"  1. Run: LAUNCH_ALL_SERVICES.bat")
        print(f"  2. Open: http://localhost:8000")
    else:
        print(f"{Fore.YELLOW}⚠️ Some components need attention")
        print(f"\n{Fore.YELLOW}Quick fixes:")
        print(f"  1. Install missing packages: pip install -r requirements_ml.txt")
        print(f"  2. Start backend: python backend.py")
        print(f"  3. Start ML backend: python ml_training_backend.py")

if __name__ == "__main__":
    main()
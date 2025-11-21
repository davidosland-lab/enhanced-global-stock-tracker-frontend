#!/usr/bin/env python3
"""
Dual Market Screening System - Verification Script
Tests all components to ensure proper installation
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def test_python_version():
    """Test Python version"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def test_imports():
    """Test critical imports"""
    print_info("Testing Python package imports...")
    
    packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'yahooquery': 'yahooquery',
        'sklearn': 'scikit-learn',
        'hmmlearn': 'hmmlearn (optional for regime detection)'
    }
    
    all_ok = True
    for package, display_name in packages.items():
        try:
            __import__(package)
            print_success(f"{display_name}")
        except ImportError:
            if package == 'hmmlearn':
                print_warning(f"{display_name} - Will use fallback mode")
            else:
                print_error(f"{display_name} - REQUIRED")
                all_ok = False
    
    return all_ok

def test_directory_structure():
    """Test directory structure"""
    print_info("Checking directory structure...")
    
    required_dirs = [
        'models/config',
        'models/screening',
        'logs/screening/us/errors',
        'reports/us',
        'data/us'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}")
        else:
            print_error(f"{dir_path} - MISSING")
            all_ok = False
    
    return all_ok

def test_configuration_files():
    """Test configuration files"""
    print_info("Checking configuration files...")
    
    config_files = [
        'models/config/asx_sectors.json',
        'models/config/us_sectors.json',
        'models/config/us_market_config.py',
        'requirements.txt',
        'run_screening.py'
    ]
    
    all_ok = True
    for file_path in config_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - MISSING")
            all_ok = False
    
    return all_ok

def test_asx_components():
    """Test ASX pipeline components"""
    print_info("Testing ASX pipeline components...")
    
    all_ok = True
    
    # Test ASX Scanner
    try:
        from models.screening.stock_scanner import StockScanner
        scanner = StockScanner()
        print_success("ASX Stock Scanner")
    except Exception as e:
        print_error(f"ASX Stock Scanner: {e}")
        all_ok = False
    
    # Test SPI Monitor
    try:
        from models.screening.spi_monitor import SPIMonitor
        monitor = SPIMonitor()
        print_success("SPI Monitor (ASX sentiment)")
    except Exception as e:
        print_error(f"SPI Monitor: {e}")
        all_ok = False
    
    # Test ASX Regime Engine
    try:
        from models.screening.market_regime_engine import MarketRegimeEngine
        engine = MarketRegimeEngine()
        print_success("ASX Market Regime Engine")
    except Exception as e:
        print_error(f"ASX Market Regime Engine: {e}")
        all_ok = False
    
    return all_ok

def test_us_components():
    """Test US pipeline components"""
    print_info("Testing US pipeline components...")
    
    all_ok = True
    
    # Test US Scanner
    try:
        from models.screening.us_stock_scanner import USStockScanner
        scanner = USStockScanner()
        print_success("US Stock Scanner")
    except Exception as e:
        print_error(f"US Stock Scanner: {e}")
        all_ok = False
    
    # Test US Market Monitor
    try:
        from models.screening.us_market_monitor import USMarketMonitor
        monitor = USMarketMonitor()
        print_success("US Market Monitor (S&P 500, VIX)")
    except Exception as e:
        print_error(f"US Market Monitor: {e}")
        all_ok = False
    
    # Test US Regime Engine
    try:
        from models.screening.us_market_regime_engine import USMarketRegimeEngine
        engine = USMarketRegimeEngine()
        print_success("US Market Regime Engine")
    except Exception as e:
        print_error(f"US Market Regime Engine: {e}")
        all_ok = False
    
    return all_ok

def test_shared_components():
    """Test shared components"""
    print_info("Testing shared components...")
    
    all_ok = True
    
    # Test Batch Predictor
    try:
        from models.screening.batch_predictor import BatchPredictor
        predictor = BatchPredictor()
        print_success("Batch Predictor")
    except Exception as e:
        print_warning(f"Batch Predictor: {e} (optional)")
    
    # Test Opportunity Scorer
    try:
        from models.screening.opportunity_scorer import OpportunityScorer
        scorer = OpportunityScorer()
        print_success("Opportunity Scorer")
    except Exception as e:
        print_error(f"Opportunity Scorer: {e}")
        all_ok = False
    
    # Test Report Generator
    try:
        from models.screening.report_generator import ReportGenerator
        reporter = ReportGenerator()
        print_success("Report Generator")
    except Exception as e:
        print_error(f"Report Generator: {e}")
        all_ok = False
    
    return all_ok

def test_live_data_fetch():
    """Test live data fetching"""
    print_info("Testing live data connectivity...")
    
    all_ok = True
    
    try:
        from yahooquery import Ticker
        
        # Test S&P 500
        ticker = Ticker("^GSPC")
        hist = ticker.history(period="1d")
        if hist is not None and not hist.empty:
            print_success("S&P 500 data fetch (^GSPC)")
        else:
            print_error("S&P 500 data fetch - No data returned")
            all_ok = False
        
        # Test VIX
        ticker = Ticker("^VIX")
        hist = ticker.history(period="1d")
        if hist is not None and not hist.empty:
            print_success("VIX data fetch (^VIX)")
        else:
            print_warning("VIX data fetch - No data returned")
        
        # Test US stock
        ticker = Ticker("AAPL")
        hist = ticker.history(period="1d")
        if hist is not None and not hist.empty:
            print_success("US stock data fetch (AAPL)")
        else:
            print_error("US stock data fetch - No data returned")
            all_ok = False
            
    except Exception as e:
        print_error(f"Data fetch failed: {e}")
        all_ok = False
    
    return all_ok

def main():
    """Run all verification tests"""
    print_header("DUAL MARKET SCREENING SYSTEM - VERIFICATION")
    
    results = []
    
    # Run all tests
    print_header("1. SYSTEM REQUIREMENTS")
    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    
    print_header("2. DIRECTORY STRUCTURE")
    results.append(("Directories", test_directory_structure()))
    results.append(("Configuration Files", test_configuration_files()))
    
    print_header("3. ASX PIPELINE COMPONENTS")
    results.append(("ASX Components", test_asx_components()))
    
    print_header("4. US PIPELINE COMPONENTS")
    results.append(("US Components", test_us_components()))
    
    print_header("5. SHARED COMPONENTS")
    results.append(("Shared Components", test_shared_components()))
    
    print_header("6. DATA CONNECTIVITY")
    results.append(("Live Data Fetch", test_live_data_fetch()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print()
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
        print()
        print_info("System is ready for use!")
        print()
        print("Next steps:")
        print("  python run_screening.py --market us --stocks 5")
        print()
        return 0
    else:
        print_error(f"SOME TESTS FAILED ({passed}/{total} passed)")
        print()
        print_warning("Please address the failed tests before using the system.")
        print()
        print("Common fixes:")
        print("  pip install -r requirements.txt")
        print("  mkdir -p logs/screening/us/errors reports/us data/us")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

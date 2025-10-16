"""
Diagnostic tool for StockTracker V10
Checks all services and dependencies
"""

import sys
import subprocess
import importlib
import requests
import time
from typing import Dict, List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check Python version"""
    version = sys.version
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 8:
        return True, f"Python {version.split()[0]} ✓"
    return False, f"Python {version.split()[0]} - Requires 3.8+"

def check_package(package_name: str) -> Tuple[bool, str]:
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True, f"{package_name} ✓"
    except ImportError:
        return False, f"{package_name} ✗ (not installed)"

def check_service(port: int, name: str) -> Tuple[bool, str]:
    """Check if a service is running"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            return True, f"{name} (port {port}) ✓"
    except:
        pass
    return False, f"{name} (port {port}) ✗ (not running)"

def test_yfinance() -> Tuple[bool, str]:
    """Test Yahoo Finance data retrieval"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        if not hist.empty:
            return True, "Yahoo Finance API ✓"
        return False, "Yahoo Finance API ✗ (no data)"
    except Exception as e:
        return False, f"Yahoo Finance API ✗ ({str(e)})"

def run_diagnostics():
    """Run complete diagnostics"""
    print("="*60)
    print("StockTracker V10 - System Diagnostics")
    print("="*60)
    print()
    
    # Check Python
    print("Python Environment:")
    success, message = check_python_version()
    print(f"  {message}")
    print()
    
    # Check required packages
    print("Required Packages:")
    packages = [
        "fastapi", "uvicorn", "pandas", "numpy", 
        "yfinance", "sklearn", "requests", "joblib"
    ]
    all_installed = True
    for package in packages:
        # Special handling for sklearn
        if package == "sklearn":
            success, message = check_package("sklearn")
        else:
            success, message = check_package(package)
        print(f"  {message}")
        if not success:
            all_installed = False
    print()
    
    # Check optional packages
    print("Optional Packages:")
    optional = ["transformers", "torch"]
    for package in optional:
        success, message = check_package(package)
        print(f"  {message}")
    print()
    
    # Test Yahoo Finance
    print("Data Source:")
    success, message = test_yfinance()
    print(f"  {message}")
    print()
    
    # Check services
    print("Services Status:")
    services = [
        (8000, "Main Backend"),
        (8002, "ML Backend"),
        (8003, "FinBERT Backend"),
        (8004, "Historical Backend"),
        (8005, "Backtesting Backend")
    ]
    for port, name in services:
        success, message = check_service(port, name)
        print(f"  {message}")
    print()
    
    # Summary
    print("="*60)
    if all_installed:
        print("✓ All required packages are installed")
    else:
        print("✗ Some required packages are missing")
        print("  Run INSTALL.bat to install missing packages")
    print("="*60)

if __name__ == "__main__":
    run_diagnostics()
    input("\nPress Enter to continue...")
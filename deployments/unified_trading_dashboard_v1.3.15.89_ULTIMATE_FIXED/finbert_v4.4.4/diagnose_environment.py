#!/usr/bin/env python3
"""
FinBERT v4.4 - Environment Diagnostic Tool
Checks all required packages and their versions
"""

import sys
from typing import Dict, List, Tuple

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed and get its version."""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, 'NOT INSTALLED'

def main():
    """Run diagnostic checks."""
    print("=" * 60)
    print("  FinBERT v4.4 - Environment Diagnostic")
    print("=" * 60)
    print()
    
    # Core packages (required)
    core_packages = [
        ('flask', 'flask'),
        ('flask-cors', 'flask_cors'),
        ('yfinance', 'yfinance'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('ta', 'ta'),
    ]
    
    # Optional packages
    optional_packages = [
        ('tensorflow', 'tensorflow'),
        ('keras', 'keras'),
        ('scikit-learn', 'sklearn'),
        ('transformers', 'transformers'),
        ('torch', 'torch'),
        ('APScheduler', 'apscheduler'),
        ('python-dateutil', 'dateutil'),
        ('pytz', 'pytz'),
    ]
    
    print("Core Packages (Required):")
    print("-" * 60)
    core_ok = True
    for package_name, import_name in core_packages:
        installed, version = check_package(package_name, import_name)
        status = "[OK]" if installed else "[FAIL]"
        print(f"  {status} {package_name:20s} {version}")
        if not installed:
            core_ok = False
    
    print()
    print("Optional Packages (Features may be limited if missing):")
    print("-" * 60)
    for package_name, import_name in optional_packages:
        installed, version = check_package(package_name, import_name)
        status = "[OK]" if installed else "[SKIP]"
        print(f"  {status} {package_name:20s} {version}")
    
    print()
    print("=" * 60)
    
    if core_ok:
        print("✓ All core packages installed - System ready!")
        return 0
    else:
        print("✗ Some core packages missing - Run INSTALL.bat")
        return 1

if __name__ == '__main__':
    sys.exit(main())

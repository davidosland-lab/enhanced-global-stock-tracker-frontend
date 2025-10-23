#!/usr/bin/env python3
"""
Comprehensive Diagnostic Tool for StockTracker V10
Performs all diagnostic checks and generates detailed report
"""

import sys
import os
import platform
import subprocess
import socket
import json
import traceback
from datetime import datetime
from pathlib import Path
import importlib.util

# Color codes for terminal output (Windows compatible)
try:
    import colorama
    colorama.init()
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
except:
    GREEN = RED = YELLOW = BLUE = RESET = ""

class DiagnosticTool:
    def __init__(self):
        self.report = []
        self.issues_found = []
        self.recommendations = []
        
    def print_and_log(self, message, color=""):
        """Print to console and add to report"""
        print(f"{color}{message}{RESET}")
        self.report.append(message)
    
    def section_header(self, title):
        """Print section header"""
        separator = "=" * 60
        self.print_and_log(f"\n{separator}", BLUE)
        self.print_and_log(f"{title}", BLUE)
        self.print_and_log(separator, BLUE)
    
    def check_system_info(self):
        """Check system information"""
        self.section_header("1. SYSTEM INFORMATION")
        
        info = {
            "Platform": platform.system(),
            "Platform Version": platform.version(),
            "Architecture": platform.machine(),
            "Python Version": sys.version,
            "Python Executable": sys.executable,
            "Current Directory": os.getcwd(),
            "User Home": os.path.expanduser("~")
        }
        
        for key, value in info.items():
            self.print_and_log(f"  {key}: {value}")
        
        # Check if running Windows
        if platform.system() != "Windows":
            self.issues_found.append("Not running on Windows - some features may not work")
    
    def check_python_environment(self):
        """Check Python environment and virtual environment"""
        self.section_header("2. PYTHON ENVIRONMENT")
        
        # Check Python version
        python_version = sys.version_info
        self.print_and_log(f"  Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.issues_found.append(f"Python version {python_version.major}.{python_version.minor} is too old - need 3.8+")
            self.recommendations.append("Install Python 3.8 or higher from python.org")
        else:
            self.print_and_log(f"  ✓ Python version OK", GREEN)
        
        # Check if in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if in_venv:
            self.print_and_log(f"  ✓ Running in virtual environment", GREEN)
            self.print_and_log(f"    Venv path: {sys.prefix}")
        else:
            self.print_and_log(f"  ⚠ Not running in virtual environment", YELLOW)
            self.recommendations.append("Run this diagnostic from within the virtual environment (activate venv first)")
        
        # Check pip
        try:
            import pip
            self.print_and_log(f"  ✓ pip is available", GREEN)
        except ImportError:
            self.issues_found.append("pip is not available")
            self.recommendations.append("Reinstall Python with pip included")
    
    def check_required_packages(self):
        """Check all required Python packages"""
        self.section_header("3. REQUIRED PACKAGES")
        
        required_packages = {
            'fastapi': 'FastAPI web framework',
            'uvicorn': 'ASGI server',
            'pandas': 'Data analysis',
            'numpy': 'Numerical computing',
            'yfinance': 'Yahoo Finance API',
            'sklearn': 'Machine learning',
            'requests': 'HTTP requests',
            'joblib': 'Model persistence',
            'scipy': 'Scientific computing',
            'ta': 'Technical analysis',
            'certifi': 'SSL certificates'
        }
        
        optional_packages = {
            'transformers': 'FinBERT sentiment analysis',
            'torch': 'PyTorch for FinBERT',
            'sqlite3': 'Database (built-in)'
        }
        
        self.print_and_log("  Required packages:")
        missing_required = []
        for package, description in required_packages.items():
            try:
                if package == 'sklearn':
                    importlib.import_module('sklearn')
                else:
                    importlib.import_module(package)
                self.print_and_log(f"    ✓ {package:<20} - {description}", GREEN)
            except ImportError as e:
                self.print_and_log(f"    ✗ {package:<20} - {description} (MISSING)", RED)
                missing_required.append(package)
                self.issues_found.append(f"Required package '{package}' is not installed")
        
        self.print_and_log("\n  Optional packages:")
        for package, description in optional_packages.items():
            try:
                importlib.import_module(package)
                self.print_and_log(f"    ✓ {package:<20} - {description}", GREEN)
            except ImportError:
                self.print_and_log(f"    ⚠ {package:<20} - {description} (not installed)", YELLOW)
        
        if missing_required:
            self.recommendations.append(f"Install missing packages: pip install {' '.join(missing_required)}")
    
    def check_service_files(self):
        """Check if all service files exist and can be imported"""
        self.section_header("4. SERVICE FILES")
        
        services = [
            ('main_backend.py', 'Main API service'),
            ('ml_backend.py', 'Machine learning service'),
            ('finbert_backend.py', 'Sentiment analysis service'),
            ('historical_backend.py', 'Historical data service'),
            ('backtesting_backend.py', 'Backtesting service'),
            ('index.html', 'Main dashboard'),
            ('prediction_center.html', 'ML interface')
        ]
        
        for filename, description in services:
            if os.path.exists(filename):
                self.print_and_log(f"  ✓ {filename:<30} - {description}", GREEN)
                
                # Try to import Python files
                if filename.endswith('.py'):
                    module_name = filename[:-3]
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, filename)
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute, just check if it can be loaded
                        self.print_and_log(f"    └─ Can be imported successfully", GREEN)
                    except Exception as e:
                        self.print_and_log(f"    └─ Import error: {str(e)[:50]}...", RED)
                        self.issues_found.append(f"Cannot import {filename}: {str(e)[:100]}")
            else:
                self.print_and_log(f"  ✗ {filename:<30} - {description} (MISSING)", RED)
                self.issues_found.append(f"Service file '{filename}' is missing")
    
    def check_ports(self):
        """Check if required ports are available"""
        self.section_header("5. PORT AVAILABILITY")
        
        ports = [
            (8000, "Main Backend"),
            (8002, "ML Backend"),
            (8003, "FinBERT Backend"),
            (8004, "Historical Backend"),
            (8005, "Backtesting Backend")
        ]
        
        for port, service in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                self.print_and_log(f"  Port {port} ({service}): IN USE", YELLOW)
                # Check what's using the port
                try:
                    if platform.system() == "Windows":
                        cmd = f"netstat -ano | findstr :{port}"
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.stdout:
                            self.print_and_log(f"    └─ Process info: {result.stdout.strip()[:100]}")
                except:
                    pass
            else:
                self.print_and_log(f"  Port {port} ({service}): Available", GREEN)
    
    def check_yahoo_finance(self):
        """Test Yahoo Finance connectivity"""
        self.section_header("6. YAHOO FINANCE API")
        
        try:
            import yfinance as yf
            self.print_and_log("  Testing Yahoo Finance connection...")
            
            ticker = yf.Ticker("AAPL")
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                self.print_and_log(f"  ✓ Yahoo Finance API is working", GREEN)
                self.print_and_log(f"    └─ Retrieved data for AAPL: {len(hist)} records")
            else:
                self.print_and_log(f"  ⚠ Yahoo Finance returned no data", YELLOW)
                self.issues_found.append("Yahoo Finance returned empty data")
        except ImportError:
            self.print_and_log(f"  ✗ yfinance package not installed", RED)
            self.issues_found.append("Cannot test Yahoo Finance - yfinance not installed")
        except Exception as e:
            self.print_and_log(f"  ✗ Yahoo Finance test failed: {str(e)}", RED)
            self.issues_found.append(f"Yahoo Finance error: {str(e)}")
            self.recommendations.append("Check internet connection and firewall settings")
    
    def check_ssl_certificates(self):
        """Check SSL certificate configuration"""
        self.section_header("7. SSL CERTIFICATES")
        
        ssl_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
        
        for var in ssl_vars:
            value = os.environ.get(var, "Not set")
            if value and value != "Not set":
                self.print_and_log(f"  {var}: {value}", YELLOW)
                self.recommendations.append(f"Consider unsetting {var} if having SSL issues")
            else:
                self.print_and_log(f"  {var}: Not set (OK)", GREEN)
        
        # Check certifi
        try:
            import certifi
            cert_path = certifi.where()
            self.print_and_log(f"  ✓ Certifi certificates found: {cert_path}", GREEN)
            if os.path.exists(cert_path):
                self.print_and_log(f"    └─ Certificate file exists", GREEN)
            else:
                self.print_and_log(f"    └─ Certificate file missing!", RED)
                self.issues_found.append("Certifi certificate file missing")
        except ImportError:
            self.print_and_log(f"  ⚠ Certifi not installed", YELLOW)
    
    def check_database(self):
        """Check SQLite database functionality"""
        self.section_header("8. DATABASE CHECK")
        
        try:
            import sqlite3
            
            # Test in-memory database
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO test VALUES (1)")
            cursor.execute("SELECT * FROM test")
            result = cursor.fetchone()
            conn.close()
            
            if result == (1,):
                self.print_and_log(f"  ✓ SQLite database working", GREEN)
            else:
                self.print_and_log(f"  ⚠ SQLite test returned unexpected result", YELLOW)
                
            # Check for existing database files
            db_files = ['ml_models.db', 'historical_cache.db', 'backtest_results.db']
            for db_file in db_files:
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file) / 1024  # KB
                    self.print_and_log(f"    └─ {db_file}: {size:.2f} KB", GREEN)
                else:
                    self.print_and_log(f"    └─ {db_file}: Not created yet", YELLOW)
                    
        except Exception as e:
            self.print_and_log(f"  ✗ SQLite test failed: {str(e)}", RED)
            self.issues_found.append(f"SQLite error: {str(e)}")
    
    def check_permissions(self):
        """Check file system permissions"""
        self.section_header("9. FILE PERMISSIONS")
        
        # Test write permission
        test_file = "test_write_permission.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            self.print_and_log(f"  ✓ Write permission OK in current directory", GREEN)
        except Exception as e:
            self.print_and_log(f"  ✗ Cannot write to current directory: {str(e)}", RED)
            self.issues_found.append("No write permission in current directory")
            self.recommendations.append("Run as Administrator or check folder permissions")
        
        # Check if running as admin (Windows)
        if platform.system() == "Windows":
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                self.print_and_log(f"  ✓ Running as Administrator", GREEN)
            else:
                self.print_and_log(f"  ⚠ Not running as Administrator", YELLOW)
                self.recommendations.append("Consider running as Administrator if having permission issues")
    
    def test_service_startup(self):
        """Test if services can be started"""
        self.section_header("10. SERVICE STARTUP TEST")
        
        services = [
            ('main_backend.py', 8000),
            ('ml_backend.py', 8002),
            ('finbert_backend.py', 8003),
            ('historical_backend.py', 8004),
            ('backtesting_backend.py', 8005)
        ]
        
        self.print_and_log("  Testing if services can be imported and initialized...")
        
        for service_file, port in services:
            if not os.path.exists(service_file):
                self.print_and_log(f"  ✗ {service_file}: File not found", RED)
                continue
                
            try:
                # Try to import the service module
                module_name = service_file[:-3]
                spec = importlib.util.spec_from_file_location(module_name, service_file)
                module = importlib.util.module_from_spec(spec)
                
                # Check if FastAPI app exists
                self.print_and_log(f"  ✓ {service_file}: Can be loaded", GREEN)
                
            except Exception as e:
                self.print_and_log(f"  ✗ {service_file}: {str(e)[:100]}", RED)
                self.issues_found.append(f"Service {service_file} cannot be loaded: {str(e)[:100]}")
    
    def generate_summary(self):
        """Generate diagnostic summary"""
        self.section_header("DIAGNOSTIC SUMMARY")
        
        if not self.issues_found:
            self.print_and_log("\n  ✓ NO ISSUES FOUND - System appears ready!", GREEN)
        else:
            self.print_and_log(f"\n  ⚠ {len(self.issues_found)} ISSUE(S) FOUND:", YELLOW)
            for i, issue in enumerate(self.issues_found, 1):
                self.print_and_log(f"    {i}. {issue}", RED)
        
        if self.recommendations:
            self.print_and_log(f"\n  RECOMMENDATIONS:", BLUE)
            for i, rec in enumerate(self.recommendations, 1):
                self.print_and_log(f"    {i}. {rec}")
        
        self.print_and_log(f"\n  Diagnostic completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def save_report(self, filename=None):
        """Save diagnostic report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report))
            print(f"\n{GREEN}Report saved to: {filename}{RESET}")
            return filename
        except Exception as e:
            print(f"\n{RED}Failed to save report: {str(e)}{RESET}")
            return None
    
    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}StockTracker V10 - Comprehensive Diagnostic Tool{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        try:
            self.check_system_info()
            self.check_python_environment()
            self.check_required_packages()
            self.check_service_files()
            self.check_ports()
            self.check_yahoo_finance()
            self.check_ssl_certificates()
            self.check_database()
            self.check_permissions()
            self.test_service_startup()
            self.generate_summary()
            
        except Exception as e:
            self.print_and_log(f"\n{RED}Diagnostic error: {str(e)}{RESET}")
            self.print_and_log(traceback.format_exc())
        
        return self.issues_found, self.recommendations

def main():
    """Main entry point"""
    diagnostic = DiagnosticTool()
    issues, recommendations = diagnostic.run_full_diagnostic()
    
    # Return exit code based on issues found
    if issues:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
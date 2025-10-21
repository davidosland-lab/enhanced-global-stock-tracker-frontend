#!/usr/bin/env python3
"""
Server Diagnostic Tool - Find and fix server startup issues
"""

import os
import sys
import socket
import subprocess
import json
import traceback
from datetime import datetime

print("="*70)
print("   SERVER DIAGNOSTIC TOOL")
print("="*70)
print(f"Time: {datetime.now()}")
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
print()

# Test results storage
results = {
    'timestamp': datetime.now().isoformat(),
    'python_version': sys.version,
    'platform': sys.platform,
    'errors': [],
    'warnings': [],
    'success': []
}

def test_step(name, critical=True):
    """Decorator for test steps"""
    def decorator(func):
        def wrapper():
            print(f"\n{'='*50}")
            print(f"Testing: {name}")
            print('-'*50)
            try:
                result = func()
                if result:
                    print(f"✅ {name}: PASSED")
                    results['success'].append(name)
                else:
                    print(f"❌ {name}: FAILED")
                    if critical:
                        results['errors'].append(f"{name} failed")
                    else:
                        results['warnings'].append(f"{name} failed")
                return result
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
                print(f"Traceback: {traceback.format_exc()}")
                results['errors'].append(f"{name}: {str(e)}")
                return False
        return wrapper
    return decorator

@test_step("Python Version Check")
def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("⚠️ Python 3.7+ required")
        return False
    
    print("Python version is compatible")
    return True

@test_step("Required Modules Import")
def check_imports():
    """Test importing required modules"""
    required_modules = [
        ('flask', 'Flask web framework'),
        ('flask_cors', 'CORS support'),
        ('yfinance', 'Yahoo Finance data'),
        ('pandas', 'Data manipulation'),
        ('numpy', 'Numerical operations'),
        ('requests', 'HTTP requests')
    ]
    
    all_good = True
    for module_name, description in required_modules:
        try:
            if module_name == 'flask_cors':
                import flask_cors
                version = getattr(flask_cors, '__version__', 'unknown')
            else:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'unknown')
            print(f"✅ {module_name:15} v{version:10} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:15} MISSING     - {description}")
            print(f"   Error: {e}")
            results['errors'].append(f"Missing module: {module_name}")
            all_good = False
        except Exception as e:
            print(f"⚠️ {module_name:15} ERROR       - {e}")
            results['warnings'].append(f"Module error: {module_name} - {str(e)}")
            all_good = False
    
    return all_good

@test_step("NumPy Compatibility Check")
def check_numpy_compatibility():
    """Check NumPy version and compatibility"""
    try:
        import numpy as np
        print(f"NumPy version: {np.__version__}")
        
        # Check if version is 2.x
        major_version = int(np.__version__.split('.')[0])
        if major_version >= 2:
            print("⚠️ NumPy 2.x detected - may have compatibility issues with some ML libraries")
            
            # Try importing sklearn
            try:
                import sklearn
                print("✅ scikit-learn works with current NumPy")
            except ImportError:
                print("ℹ️ scikit-learn not installed (optional)")
            except Exception as e:
                print(f"⚠️ scikit-learn compatibility issue: {e}")
                results['warnings'].append(f"NumPy 2.x may cause issues with ML libraries")
        else:
            print("✅ NumPy 1.x - good compatibility")
        
        # Test basic NumPy operations
        test_array = np.array([1, 2, 3])
        test_result = np.mean(test_array)
        print(f"NumPy basic operations: OK (mean of [1,2,3] = {test_result})")
        return True
        
    except Exception as e:
        print(f"NumPy error: {e}")
        return False

@test_step("Port Availability Check")
def check_port():
    """Check if port 8000 is available"""
    port = 8000
    
    # Method 1: Try binding
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.bind(('127.0.0.1', port))
        sock.close()
        print(f"✅ Port {port} is AVAILABLE")
        return True
    except OSError as e:
        print(f"❌ Port {port} is IN USE or BLOCKED")
        print(f"   Error: {e}")
        
        # Try to find what's using the port
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['netstat', '-ano'], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':8000' in line and 'LISTENING' in line:
                        print(f"   Found: {line.strip()}")
                        # Extract PID
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            print(f"   Process ID using port: {pid}")
                            print(f"   To kill: taskkill /F /PID {pid}")
            except:
                pass
        
        results['errors'].append(f"Port {port} is not available")
        return False

@test_step("Flask Application Test")
def test_flask_app():
    """Test creating a minimal Flask application"""
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/test')
        def test():
            return {'status': 'ok'}
        
        # Test if app can be created
        with app.test_client() as client:
            response = client.get('/test')
            if response.status_code == 200:
                print("✅ Flask app creation and routing works")
                return True
            else:
                print(f"❌ Flask test failed with status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"Flask test error: {e}")
        results['errors'].append(f"Flask app test failed: {str(e)}")
        return False

@test_step("Yahoo Finance Connection Test", critical=False)
def test_yahoo_finance():
    """Test Yahoo Finance connectivity"""
    try:
        import yfinance as yf
        
        print(f"yfinance version: {yf.__version__}")
        
        # Try to fetch data
        print("Testing Yahoo Finance with AAPL...")
        ticker = yf.Ticker("AAPL")
        
        # Method 1: Using download
        try:
            df = yf.download("AAPL", period="5d", progress=False, threads=False)
            if not df.empty:
                latest_price = df['Close'].iloc[-1]
                print(f"✅ Method 1 (download): Success - AAPL: ${latest_price:.2f}")
                return True
        except Exception as e:
            print(f"⚠️ Method 1 failed: {e}")
        
        # Method 2: Using Ticker.history
        try:
            hist = ticker.history(period="5d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                print(f"✅ Method 2 (history): Success - AAPL: ${latest_price:.2f}")
                return True
        except Exception as e:
            print(f"⚠️ Method 2 failed: {e}")
        
        # Method 3: Using info
        try:
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                print(f"✅ Method 3 (info): Success - AAPL: ${info['regularMarketPrice']}")
                return True
        except Exception as e:
            print(f"⚠️ Method 3 failed: {e}")
        
        print("⚠️ All Yahoo Finance methods failed - may need to update yfinance")
        results['warnings'].append("Yahoo Finance connectivity issues")
        return False
        
    except ImportError:
        print("yfinance not installed")
        return False
    except Exception as e:
        print(f"Yahoo Finance test error: {e}")
        return False

@test_step("Server File Check")
def check_server_files():
    """Check if server files exist and are readable"""
    server_files = [
        'unified_production_server.py',
        'server_minimal.py',
        'server_fixed_crumb.py',
        'server.py'
    ]
    
    found_files = []
    for file in server_files:
        if os.path.exists(file):
            try:
                size = os.path.getsize(file)
                print(f"✅ Found: {file} ({size:,} bytes)")
                
                # Try to compile the file
                with open(file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, file, 'exec')
                    print(f"   Syntax check: OK")
                    found_files.append(file)
                    
            except SyntaxError as e:
                print(f"❌ Syntax error in {file}: {e}")
                results['errors'].append(f"Syntax error in {file}: Line {e.lineno}")
            except Exception as e:
                print(f"⚠️ Error checking {file}: {e}")
        else:
            print(f"❌ Not found: {file}")
    
    if not found_files:
        results['errors'].append("No server files found")
        return False
    
    print(f"\nFound {len(found_files)} server file(s)")
    return True

@test_step("Test Import Server Modules")
def test_import_servers():
    """Try importing each server module to check for errors"""
    servers = [
        ('server_minimal', 'Minimal Server'),
        ('unified_production_server', 'Production Server'),
        ('server_fixed_crumb', 'Fixed Crumb Server'),
        ('server', 'Basic Server')
    ]
    
    for module_name, description in servers:
        if os.path.exists(f"{module_name}.py"):
            print(f"\nTesting import of {description}...")
            try:
                # Try to import the module
                spec = __import__(module_name)
                print(f"✅ {description} imports successfully")
                
                # Check if main components exist
                if hasattr(spec, 'app'):
                    print(f"   Flask app found")
                if hasattr(spec, 'main'):
                    print(f"   Main function found")
                    
            except ImportError as e:
                print(f"❌ Import error: {e}")
                missing = str(e).replace("No module named ", "")
                if missing:
                    print(f"   Missing module: {missing}")
                    print(f"   Install with: pip install {missing}")
            except SyntaxError as e:
                print(f"❌ Syntax error at line {e.lineno}: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    return True

@test_step("Windows Firewall Check", critical=False)
def check_windows_firewall():
    """Check Windows firewall settings"""
    if sys.platform != 'win32':
        print("Not Windows - skipping")
        return True
    
    try:
        # Check if Python is allowed through firewall
        result = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        python_allowed = False
        if 'python' in result.stdout.lower():
            python_allowed = True
            print("✅ Python appears in firewall rules")
        else:
            print("⚠️ Python not found in firewall rules")
            print("   You may need to allow Python through Windows Firewall")
            
        return True
        
    except Exception as e:
        print(f"Could not check firewall: {e}")
        return True

@test_step("Database Test", critical=False)
def test_database():
    """Test SQLite database functionality"""
    try:
        import sqlite3
        
        # Try to create a test database
        test_db = 'test_diagnostic.db'
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test (value) VALUES ('test')")
        conn.commit()
        
        # Read back
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        
        conn.close()
        
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ SQLite database operations work")
        return True
        
    except Exception as e:
        print(f"Database test error: {e}")
        return False

# Generate diagnostic summary
def generate_summary():
    """Generate a summary of all tests"""
    print("\n" + "="*70)
    print("   DIAGNOSTIC SUMMARY")
    print("="*70)
    
    if results['errors']:
        print(f"\n❌ {len(results['errors'])} CRITICAL ERROR(S):")
        for error in results['errors']:
            print(f"   • {error}")
    
    if results['warnings']:
        print(f"\n⚠️ {len(results['warnings'])} WARNING(S):")
        for warning in results['warnings']:
            print(f"   • {warning}")
    
    if results['success']:
        print(f"\n✅ {len(results['success'])} TEST(S) PASSED:")
        for success in results['success']:
            print(f"   • {success}")
    
    # Recommendations
    print("\n" + "="*70)
    print("   RECOMMENDED FIXES")
    print("="*70)
    
    if any('Port' in e for e in results['errors']):
        print("\n1. FIX PORT ISSUE:")
        print("   Run: netstat -ano | findstr :8000")
        print("   Then: taskkill /F /PID [process_id]")
    
    if any('Missing module' in e for e in results['errors']):
        print("\n2. INSTALL MISSING MODULES:")
        missing = [e.replace('Missing module: ', '') for e in results['errors'] if 'Missing module' in e]
        for module in missing:
            print(f"   pip install {module}")
    
    if any('NumPy' in w for w in results['warnings']):
        print("\n3. FIX NUMPY COMPATIBILITY:")
        print("   Option A: Use server_minimal.py (works with NumPy 2.x)")
        print("   Option B: Downgrade NumPy: pip install 'numpy<2'")
    
    if any('Syntax error' in e for e in results['errors']):
        print("\n4. FIX SYNTAX ERRORS:")
        print("   Check the line numbers mentioned above")
        print("   Common issues: indentation, missing colons, unclosed quotes")
    
    if not results['errors']:
        print("\n✅ NO CRITICAL ERRORS FOUND!")
        print("\nYou should be able to start the server.")
        print("Try running one of these:")
        print("   python server_minimal.py")
        print("   python unified_production_server.py")
    
    # Save report
    report_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed report saved to: {report_file}")

# Run all tests
def main():
    print("\nStarting comprehensive diagnostics...\n")
    
    # Run tests in order
    check_python_version()
    check_imports()
    check_numpy_compatibility()
    check_port()
    test_flask_app()
    test_yahoo_finance()
    check_server_files()
    test_import_servers()
    check_windows_firewall()
    test_database()
    
    # Generate summary
    generate_summary()
    
    print("\n" + "="*70)
    print("Diagnostic complete!")
    
    if not results['errors']:
        print("✅ Your system appears ready to run the server!")
    else:
        print(f"❌ Found {len(results['errors'])} issue(s) that need fixing")
    
    print("="*70)

if __name__ == '__main__':
    main()
    print("\nPress Enter to exit...")
    input()
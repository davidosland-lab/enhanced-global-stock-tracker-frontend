#!/usr/bin/env python3
"""
ML Core Enhanced - Comprehensive Diagnostic Tool
Diagnoses and fixes common issues with the ML system
"""

import sys
import os
import subprocess
import socket
import time
import json
import psutil
import platform
from datetime import datetime

class MLCoreDiagnostic:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.system_info = {
            'os': platform.system(),
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat()
        }
        
    def print_header(self):
        """Print diagnostic header"""
        print("=" * 70)
        print("ML CORE ENHANCED - DIAGNOSTIC TOOL v2.0")
        print("=" * 70)
        print(f"OS: {self.system_info['os']}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("\n1. Checking Python Version...")
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            self.issues_found.append("Python version too old")
            print(f"   ❌ Python {version.major}.{version.minor} - Need 3.9+")
            return False
        elif version.major == 3 and version.minor == 12:
            print(f"   ⚠️  Python 3.12 - May have scipy compatibility issues")
            self.issues_found.append("Python 3.12 scipy compatibility")
            return True
        else:
            print(f"   ✅ Python {version.major}.{version.minor} - Compatible")
            return True
            
    def check_port_availability(self, port=8000):
        """Check if port is available or in use"""
        print(f"\n2. Checking Port {port}...")
        
        # Method 1: Try to bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            print(f"   ✅ Port {port} is available")
            return True
        except OSError:
            print(f"   ❌ Port {port} is in use")
            
            # Try to find what's using it
            if self.system_info['os'] == 'Windows':
                try:
                    result = subprocess.run(['netstat', '-ano'], 
                                          capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if parts:
                                pid = parts[-1]
                                print(f"   📍 Process ID {pid} is using port {port}")
                                
                                # Try to get process name
                                try:
                                    for proc in psutil.process_iter(['pid', 'name']):
                                        if proc.info['pid'] == int(pid):
                                            print(f"   📍 Process: {proc.info['name']}")
                                            break
                                except:
                                    pass
                except:
                    pass
                    
            self.issues_found.append(f"Port {port} in use")
            return False
            
    def kill_port_process(self, port=8000):
        """Kill process using specified port"""
        print(f"\n   Attempting to free port {port}...")
        
        if self.system_info['os'] == 'Windows':
            try:
                # Find PID using the port
                result = subprocess.run(['netstat', '-ano'], 
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            # Kill the process
                            subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                         capture_output=True)
                            print(f"   ✅ Killed process {pid}")
                            self.fixes_applied.append(f"Freed port {port}")
                            return True
            except Exception as e:
                print(f"   ❌ Could not kill process: {e}")
        return False
        
    def check_dependencies(self):
        """Check if required packages are installed"""
        print("\n3. Checking Dependencies...")
        
        required = {
            'numpy': None,
            'pandas': None,
            'scipy': None,
            'sklearn': 'scikit-learn',
            'fastapi': None,
            'uvicorn': None,
            'yfinance': None,
            'requests': None
        }
        
        missing = []
        issues = []
        
        for module, pip_name in required.items():
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError:
                missing.append(pip_name or module)
                print(f"   ❌ {module} - NOT INSTALLED")
        
        # Check for problematic scipy on Python 3.12
        if sys.version_info.minor == 12:
            try:
                import scipy
                import numpy
                # Try to actually use scipy to see if it works
                from scipy import stats
                print(f"   ✅ scipy working on Python 3.12")
            except Exception as e:
                issues.append("scipy compatibility issue")
                print(f"   ⚠️  scipy has issues: {str(e)[:50]}")
                
        if missing:
            self.issues_found.append(f"Missing packages: {', '.join(missing)}")
            
        if issues:
            self.issues_found.extend(issues)
            
        return len(missing) == 0 and len(issues) == 0
        
    def check_sentiment_analyzer(self):
        """Check if sentiment analyzer is causing issues"""
        print("\n4. Checking Sentiment Analyzer...")
        
        # Check if the file exists
        if not os.path.exists('comprehensive_sentiment_analyzer.py'):
            print("   ⚠️  Sentiment analyzer not found (will use neutral sentiment)")
            return True
            
        try:
            # Try to import it
            from comprehensive_sentiment_analyzer import sentiment_analyzer
            print("   ✅ Sentiment analyzer found")
            
            # Check for transformer dependencies
            try:
                import transformers
                print("   ✅ Transformers library available")
            except ImportError:
                print("   ⚠️  Transformers not installed (sentiment will be limited)")
                print("      To enable full sentiment: pip install transformers torch")
                
            return True
            
        except ImportError as e:
            print(f"   ⚠️  Sentiment analyzer import issue: {e}")
            self.issues_found.append("Sentiment analyzer import failed")
            return False
        except Exception as e:
            print(f"   ❌ Sentiment analyzer error: {e}")
            self.issues_found.append(f"Sentiment error: {e}")
            return False
            
    def test_server_startup(self):
        """Test if server can start"""
        print("\n5. Testing Server Startup...")
        
        try:
            # Try to import and check syntax
            with open('ml_core_enhanced_production.py', 'r') as f:
                code = f.read()
            compile(code, 'ml_core_enhanced_production.py', 'exec')
            print("   ✅ Code syntax valid")
            return True
        except SyntaxError as e:
            print(f"   ❌ Syntax error: {e}")
            self.issues_found.append(f"Syntax error in main file")
            return False
        except FileNotFoundError:
            print("   ❌ ml_core_enhanced_production.py not found")
            self.issues_found.append("Main file missing")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
            
    def check_memory(self):
        """Check available memory"""
        print("\n6. Checking System Resources...")
        
        try:
            import psutil
            
            # Memory
            mem = psutil.virtual_memory()
            print(f"   RAM: {mem.available / (1024**3):.1f} GB available of {mem.total / (1024**3):.1f} GB")
            
            if mem.available < 2 * (1024**3):  # Less than 2GB
                print("   ⚠️  Low memory - may affect ML training")
                self.issues_found.append("Low memory")
                
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   CPU: {cpu_percent}% usage")
            
            # Disk
            disk = psutil.disk_usage('.')
            print(f"   Disk: {disk.free / (1024**3):.1f} GB free")
            
            if disk.free < 1 * (1024**3):  # Less than 1GB
                print("   ⚠️  Low disk space")
                self.issues_found.append("Low disk space")
                
            return True
            
        except ImportError:
            print("   ℹ️  psutil not installed - can't check resources")
            print("      Install with: pip install psutil")
            return True
            
    def test_api_endpoint(self):
        """Test if API is responding"""
        print("\n7. Testing API Connection...")
        
        try:
            import requests
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API responding: {data.get('system', 'Unknown')}")
                print(f"      Version: {data.get('version', 'Unknown')}")
                print(f"      Features: {data.get('features', {}).get('features_count', 'Unknown')}")
                return True
            else:
                print(f"   ❌ API returned status {response.status_code}")
                return False
        except requests.ConnectionError:
            print("   ℹ️  Server not running (normal if not started yet)")
            return True
        except requests.Timeout:
            print("   ⚠️  Server timeout")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
            
    def generate_fix_script(self):
        """Generate a script to fix found issues"""
        print("\n8. Generating Fix Script...")
        
        fixes = []
        
        # Add header
        fixes.append("@echo off")
        fixes.append("echo Fixing ML Core Issues...")
        fixes.append("")
        
        # Port fix
        if any("Port" in issue for issue in self.issues_found):
            fixes.append("echo Freeing port 8000...")
            fixes.append('for /f "tokens=5" %%a in (\'netstat -ano ^| findstr :8000\') do (')
            fixes.append('    taskkill /PID %%a /F 2>nul')
            fixes.append(')')
            fixes.append("")
            
        # Dependency fix
        if any("Missing packages" in issue for issue in self.issues_found):
            fixes.append("echo Installing missing packages...")
            fixes.append("pip install numpy pandas scipy scikit-learn yfinance fastapi uvicorn requests")
            fixes.append("")
            
        # Scipy fix for Python 3.12
        if any("scipy" in issue.lower() for issue in self.issues_found):
            fixes.append("echo Fixing scipy for Python 3.12...")
            fixes.append("pip uninstall scipy -y")
            fixes.append("pip install scipy==1.11.4")
            fixes.append("")
            
        # Memory warning
        if any("memory" in issue.lower() for issue in self.issues_found):
            fixes.append("echo WARNING: Low memory detected")
            fixes.append("echo Close other applications before running ML training")
            fixes.append("")
            
        # Save fix script
        with open('fix_issues.bat', 'w') as f:
            f.write('\n'.join(fixes))
            f.write('\necho Fixes applied! Try running ML Core again.\n')
            f.write('pause\n')
            
        print("   ✅ Created fix_issues.bat")
        
    def run_diagnostics(self):
        """Run all diagnostic checks"""
        self.print_header()
        
        # Run checks
        self.check_python_version()
        port_ok = self.check_port_availability()
        
        # Offer to fix port if needed
        if not port_ok:
            response = input("\n   Fix port issue? (y/n): ").lower()
            if response == 'y':
                if self.kill_port_process():
                    self.check_port_availability()
                    
        self.check_dependencies()
        self.check_sentiment_analyzer()
        self.test_server_startup()
        self.check_memory()
        self.test_api_endpoint()
        
        # Generate fix script if issues found
        if self.issues_found:
            self.generate_fix_script()
            
        # Summary
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        if self.issues_found:
            print("\n⚠️  Issues Found:")
            for issue in self.issues_found:
                print(f"   • {issue}")
                
            print("\n📝 Recommended Actions:")
            print("   1. Run fix_issues.bat to apply automatic fixes")
            print("   2. Restart your computer if port issues persist")
            print("   3. Install missing dependencies manually if needed")
            
        else:
            print("\n✅ No critical issues found!")
            print("   System should be ready to run.")
            
        if self.fixes_applied:
            print("\n✅ Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
                
        print("\n" + "=" * 70)
        
        # Save diagnostic report
        report = {
            'timestamp': self.system_info['timestamp'],
            'system': self.system_info,
            'issues': self.issues_found,
            'fixes_applied': self.fixes_applied
        }
        
        with open('diagnostic_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("\n📄 Full report saved to diagnostic_report.json")
        
        return len(self.issues_found) == 0

if __name__ == "__main__":
    diagnostic = MLCoreDiagnostic()
    success = diagnostic.run_diagnostics()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ SYSTEM READY - You can run: python ml_core_enhanced_production.py")
    else:
        print("⚠️  ISSUES DETECTED - Run fix_issues.bat then try again")
    print("=" * 70)
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
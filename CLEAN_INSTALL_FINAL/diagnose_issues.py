#!/usr/bin/env python3
"""
Diagnostic Tool - Identifies and fixes issues
"""

import os
import sys
import socket
import subprocess
import platform
import json
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_ports():
    """Check if required ports are free"""
    print_header("Port Availability Check")
    
    ports = {
        8000: "Frontend Server",
        8002: "Main Backend API",
        8003: "ML Training Backend"
    }
    
    issues = []
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} ({service}) - IN USE")
            issues.append(port)
        else:
            print(f"✅ Port {port} ({service}) - Available")
    
    return issues

def check_packages():
    """Check if required packages are installed"""
    print_header("Package Installation Check")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'yfinance',
        'pandas',
        'numpy',
        'tensorflow',
        'scikit-learn'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    return missing

def check_files():
    """Check if required files exist"""
    print_header("File Structure Check")
    
    required_files = [
        'backend.py',
        'index.html',
        'REAL_WORKING_PREDICTOR.html',
        'modules/ml_training_centre.html'
    ]
    
    missing = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            missing.append(file)
    
    return missing

def test_backend_connection():
    """Test backend connectivity"""
    print_header("Backend Connection Test")
    
    import requests
    
    try:
        response = requests.get('http://localhost:8002/', timeout=2)
        if response.status_code == 200:
            print("✅ Main Backend (8002) - Connected")
            return True
    except:
        print("❌ Main Backend (8002) - Not responding")
        print("   Fix: Run 'python backend.py' in a separate window")
        return False
    
    return False

def generate_fix_script():
    """Generate a fix script based on issues found"""
    print_header("Generating Fix Script")
    
    fixes = []
    
    # Check for port issues
    port_issues = check_ports()
    if port_issues:
        fixes.append("# Kill processes on conflicting ports")
        for port in port_issues:
            if platform.system() == "Windows":
                fixes.append(f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port}\') do taskkill /F /PID %a')
            else:
                fixes.append(f"lsof -ti:{port} | xargs kill -9")
    
    # Check for missing packages
    missing_packages = check_packages()
    if missing_packages:
        fixes.append("\n# Install missing packages")
        fixes.append("python -m pip install --upgrade pip")
        fixes.append(f"python -m pip install {' '.join(missing_packages)}")
    
    # Create launch commands
    fixes.append("\n# Launch services")
    fixes.append("# Run each in a separate terminal:")
    fixes.append("python backend.py")
    fixes.append("python -m http.server 8000")
    
    # Save fix script
    if platform.system() == "Windows":
        fix_file = "auto_fix.bat"
        with open(fix_file, 'w') as f:
            f.write("@echo off\n")
            f.write("\n".join(fixes).replace('%', '%%'))
    else:
        fix_file = "auto_fix.sh"
        with open(fix_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("\n".join(fixes))
        os.chmod(fix_file, 0o755)
    
    print(f"✅ Fix script created: {fix_file}")
    return fix_file

def main():
    print("\n" + "🔍 STOCK TRACKER DIAGNOSTIC TOOL 🔍".center(60))
    print("="*60)
    
    # Run all checks
    python_ok = check_python_version()
    port_issues = check_ports()
    missing_packages = check_packages()
    missing_files = check_files()
    backend_ok = test_backend_connection()
    
    # Summary
    print_header("Diagnostic Summary")
    
    total_issues = len(port_issues) + len(missing_packages) + len(missing_files)
    
    if total_issues == 0 and python_ok and backend_ok:
        print("✅ All systems operational!")
        print("\nYou can now access the application at:")
        print("http://localhost:8000")
    else:
        print(f"⚠️  Found {total_issues} issue(s) to fix")
        
        if port_issues:
            print(f"\nPort conflicts: {port_issues}")
            print("Fix: Kill processes or use different ports")
        
        if missing_packages:
            print(f"\nMissing packages: {missing_packages}")
            print("Fix: Run 'pip install -r requirements_ml.txt'")
        
        if missing_files:
            print(f"\nMissing files: {missing_files}")
            print("Fix: Re-extract the installation package")
        
        if not backend_ok:
            print("\nBackend not running")
            print("Fix: Run 'python backend.py' in a new terminal")
        
        # Generate fix script
        fix_script = generate_fix_script()
        print(f"\n💡 Run '{fix_script}' to auto-fix issues")
    
    print("\n" + "="*60)
    print("For ML Training Centre issues:")
    print("1. The ML backend is optional")
    print("2. If needed, run: python ml_training_backend_fixed.py")
    print("3. It will find an available port automatically")
    print("="*60)

if __name__ == "__main__":
    main()
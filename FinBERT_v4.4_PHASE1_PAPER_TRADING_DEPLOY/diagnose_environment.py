#!/usr/bin/env python3
"""
FinBERT v4.4 - Environment Diagnostic Tool

This script checks your Python environment and diagnoses common issues.
Run this BEFORE starting the server to verify everything is set up correctly.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    """Print a section header"""
    print(f"\n{'─' * 80}")
    print(f"📋 {text}")
    print('─' * 80)

def check_python_version():
    """Check Python version"""
    print_section("Python Version Check")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Full Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_virtual_environment():
    """Check if running in virtual environment"""
    print_section("Virtual Environment Check")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✅ Running in virtual environment")
        print(f"   Virtual Env: {sys.prefix}")
        print(f"   Base Python: {sys.base_prefix}")
    else:
        print("⚠️  NOT running in virtual environment")
        print("   Using system Python (this is OK, but venv is recommended)")
    
    return True

def check_required_packages():
    """Check if required packages are installed"""
    print_section("Required Package Check")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'yfinance': 'yfinance',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
    }
    
    optional_packages = {
        'ta': 'ta (Technical Analysis)',
        'tensorflow': 'TensorFlow',
        'transformers': 'Transformers (FinBERT)',
        'torch': 'PyTorch',
    }
    
    all_ok = True
    
    # Check required packages
    print("\n🔴 REQUIRED PACKAGES:")
    for module_name, display_name in required_packages.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {display_name:20s} v{version}")
        except ImportError:
            print(f"  ❌ {display_name:20s} NOT INSTALLED")
            all_ok = False
    
    # Check optional packages
    print("\n🟡 OPTIONAL PACKAGES:")
    for module_name, display_name in optional_packages.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {display_name:30s} v{version}")
        except ImportError:
            print(f"  ⚠️  {display_name:30s} Not installed (optional)")
    
    return all_ok

def check_file_structure():
    """Check if required files exist"""
    print_section("File Structure Check")
    
    required_files = [
        'app_finbert_v4_dev.py',
        'requirements.txt',
        'templates/finbert_v4_enhanced_ui.html',
    ]
    
    optional_files = [
        'START_FINBERT.bat',
        'train_lstm_batch.py',
        'README.md',
        'INSTALL.txt',
    ]
    
    required_dirs = [
        'models',
        'templates',
        'static',
    ]
    
    all_ok = True
    
    print("\n🔴 REQUIRED FILES:")
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"  ✅ {file_path:40s} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path:40s} MISSING")
            all_ok = False
    
    print("\n🔴 REQUIRED DIRECTORIES:")
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            file_count = len(list(Path(dir_path).rglob('*')))
            print(f"  ✅ {dir_path:40s} ({file_count} files)")
        else:
            print(f"  ❌ {dir_path:40s} MISSING")
            all_ok = False
    
    print("\n🟡 OPTIONAL FILES:")
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} (optional)")
    
    return all_ok

def check_requirements_file():
    """Check requirements.txt content"""
    print_section("Requirements.txt Check")
    
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    content = req_file.read_text()
    
    critical_packages = ['flask-cors', 'flask', 'yfinance', 'pandas', 'numpy']
    
    print("\nChecking for critical packages in requirements.txt:")
    all_ok = True
    for package in critical_packages:
        if package.lower() in content.lower():
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package} NOT FOUND")
            all_ok = False
    
    return all_ok

def provide_recommendations(checks):
    """Provide recommendations based on check results"""
    print_section("Recommendations")
    
    if all(checks.values()):
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nYour environment is properly configured.")
        print("\nYou can now start the server with:")
        print("  python app_finbert_v4_dev.py")
        print("\nOr double-click: START_FINBERT.bat")
    else:
        print("\n⚠️  ISSUES DETECTED\n")
        
        if not checks['packages']:
            print("🔧 TO FIX MISSING PACKAGES:")
            print("   pip install -r requirements.txt")
            print("\n   Or install flask-cors specifically:")
            print("   pip install flask-cors")
        
        if not checks['files']:
            print("\n🔧 TO FIX MISSING FILES:")
            print("   Re-extract the FinBERT ZIP file")
            print("   Make sure all files are extracted to the same directory")
        
        if not checks['requirements']:
            print("\n🔧 TO FIX requirements.txt:")
            print("   Download the latest version from GitHub")
            print("   Or manually add: flask-cors>=4.0.0")

def main():
    """Main diagnostic function"""
    print_header("FinBERT v4.4 - Environment Diagnostic Tool")
    print("\nThis tool will check your Python environment and identify issues.")
    print("Please wait while we run the diagnostics...")
    
    checks = {
        'python': check_python_version(),
        'venv': check_virtual_environment(),
        'packages': check_required_packages(),
        'files': check_file_structure(),
        'requirements': check_requirements_file(),
    }
    
    provide_recommendations(checks)
    
    print("\n" + "=" * 80)
    print("  Diagnostic Complete")
    print("=" * 80)
    print("\nIf you're still experiencing issues, please report:")
    print("  1. The output of this diagnostic")
    print("  2. The error message you're seeing")
    print("  3. Your operating system and Python version")
    
    return 0 if all(checks.values()) else 1

if __name__ == '__main__':
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

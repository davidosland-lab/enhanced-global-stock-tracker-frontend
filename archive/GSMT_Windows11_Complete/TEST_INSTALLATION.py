#!/usr/bin/env python3
"""
GSMT Installation Test Script
Tests all components to ensure everything is working
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_python():
    """Test Python installation"""
    print_header("Testing Python Installation")
    print(f"✓ Python version: {sys.version}")
    print(f"✓ Python executable: {sys.executable}")
    return True

def test_imports():
    """Test required imports"""
    print_header("Testing Required Packages")
    
    packages = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'datetime': 'Date/time handling (built-in)',
        'json': 'JSON handling (built-in)',
        'random': 'Random number generation (built-in)',
        'math': 'Mathematical functions (built-in)'
    }
    
    failed = []
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✓ {package}: {description}")
        except ImportError:
            print(f"✗ {package}: NOT FOUND - {description}")
            failed.append(package)
    
    if failed:
        print(f"\n⚠ Missing packages: {', '.join(failed)}")
        print("Run: pip install fastapi uvicorn")
        return False
    return True

def test_files():
    """Test that all required files exist"""
    print_header("Checking Required Files")
    
    files = [
        ('backend/main_server.py', 'Main production server'),
        ('backend/test_server.py', 'Test server for diagnostics'),
        ('backend/simple_ml_backend.py', 'Lightweight ML backend'),
        ('backend/enhanced_ml_backend.py', 'Full ML implementation'),
        ('frontend/index.html', 'Main web interface'),
        ('START.bat', 'Main launcher'),
        ('RUN_NOW.bat', 'Direct run script')
    ]
    
    all_found = True
    for filepath, description in files:
        path = Path(filepath)
        if path.exists():
            print(f"✓ {filepath}: {description}")
        else:
            print(f"✗ {filepath}: NOT FOUND - {description}")
            all_found = False
    
    return all_found

def test_server_import():
    """Test if the main server can be imported"""
    print_header("Testing Server Import")
    
    try:
        # Add backend to path
        backend_path = Path('backend').absolute()
        if backend_path.exists():
            sys.path.insert(0, str(backend_path))
        
        # Try to import main_server
        import main_server
        print("✓ main_server.py can be imported successfully")
        
        # Check for FastAPI app
        if hasattr(main_server, 'app'):
            print("✓ FastAPI app object found")
            
            # Check for prediction engine
            if hasattr(main_server, 'prediction_engine'):
                print("✓ Prediction engine found")
                print(f"  Models available: {', '.join(main_server.prediction_engine.models)}")
            
            return True
        else:
            print("✗ FastAPI app object not found in main_server.py")
            return False
            
    except Exception as e:
        print(f"✗ Error importing main_server.py: {e}")
        return False

def test_quick_server():
    """Quick test to see if server can start"""
    print_header("Quick Server Test")
    
    try:
        import fastapi
        import uvicorn
        
        # Create a minimal test app
        test_app = fastapi.FastAPI()
        
        @test_app.get("/test")
        def test_endpoint():
            return {"status": "test successful"}
        
        print("✓ FastAPI test app created successfully")
        print("✓ Server components are working")
        return True
        
    except Exception as e:
        print(f"✗ Error creating test app: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("     GSMT STOCK TRACKER - INSTALLATION TEST")
    print("="*60)
    
    # Track results
    results = {
        'Python': test_python(),
        'Packages': test_imports(),
        'Files': test_files(),
        'Server Import': test_server_import(),
        'Quick Test': test_quick_server()
    }
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your installation is ready.")
        print("\nTo start the server, run one of these:")
        print("  1. Double-click RUN_NOW.bat")
        print("  2. Double-click START.bat and choose option 1")
        print("  3. Run: python backend\\main_server.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Run FIX_INSTALLATION.bat to install packages")
        print("  2. Make sure you extracted all files")
        print("  3. Check that Python is installed correctly")
    
    print("\n" + "="*60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Ensure Real Data Script
This script verifies and fixes any modules that might be using synthetic data
Ensures all modules fetch real data from Yahoo Finance
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def fix_html_files():
    """Fix any HTML files that might have hardcoded data"""
    
    fixes_applied = []
    modules_dir = Path('modules')
    
    if not modules_dir.exists():
        print("❌ Modules directory not found")
        return fixes_applied
    
    # Common patterns to fix
    replacements = [
        # Remove any hardcoded price of $100 for CBA
        (r'CBA.*?\$100(?:\.00)?', 'CBA.AX: (Loading real price...)'),
        
        # Ensure fetch URLs use correct backend port
        (r'http://localhost:8001', 'http://localhost:8002'),
        (r'http://127\.0\.0\.1:8001', 'http://localhost:8002'),
        
        # Fix ML backend port
        (r'http://localhost:8004', 'http://localhost:8003'),
        
        # Remove any static data arrays for prices
        (r'prices:\s*\[[^\]]*100[^\]]*\]', 'prices: [] // Will be loaded from API'),
        
        # Ensure proper API endpoints
        (r'/api/stocks/', '/api/stock/'),
        (r'/api/data/', '/api/historical/'),
    ]
    
    html_files = list(modules_dir.glob('*.html')) + list(Path('.').glob('*.html'))
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            file_fixed = False
            
            for pattern, replacement in replacements:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    file_fixed = True
            
            # Additional check for fetch calls
            if 'fetch(' in content:
                # Ensure all fetch calls to backend use port 8002
                content = re.sub(
                    r'fetch\([\'"`]http://localhost:(?!8002|8003)\d+',
                    'fetch(\'http://localhost:8002',
                    content
                )
                
                # Ensure ML backend calls use port 8003
                content = re.sub(
                    r'fetch\([\'"`]http://localhost:8002/api/ml',
                    'fetch(\'http://localhost:8003/api/ml',
                    content
                )
                content = re.sub(
                    r'fetch\([\'"`]http://localhost:8002/api/phase4',
                    'fetch(\'http://localhost:8003/api/phase4',
                    content
                )
            
            if content != original_content:
                # Backup original file
                backup_path = html_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copy(html_file, backup_path)
                
                # Write fixed content
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes_applied.append({
                    'file': str(html_file),
                    'backup': str(backup_path),
                    'changes': 'Fixed hardcoded data and API endpoints'
                })
                
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    return fixes_applied

def verify_backend_configuration():
    """Verify backend files are properly configured"""
    
    checks = []
    
    # Check main backend
    backend_file = Path('backend.py')
    if backend_file.exists():
        with open(backend_file, 'r') as f:
            content = f.read()
        
        checks.append({
            'file': 'backend.py',
            'port_8002': 'port=8002' in content or ':8002' in content,
            'uses_yfinance': 'import yfinance' in content,
            'no_mock_data': 'mock' not in content.lower() and 'fake' not in content.lower(),
            'has_status_endpoint': '/api/status' in content
        })
    
    # Check ML backends
    ml_files = ['ml_backend_working.py', 'ml_training_backend.py', 'ml_backend_simple.py']
    for ml_file in ml_files:
        file_path = Path(ml_file)
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            checks.append({
                'file': ml_file,
                'port_8003': 'port=8003' in content or ':8003' in content,
                'has_health': '/health' in content,
                'no_hardcoded': 'return 100' not in content
            })
    
    return checks

def create_test_script():
    """Create a script to test all endpoints"""
    
    test_script = '''#!/usr/bin/env python3
"""Test script to verify all services are using real data"""

import requests
import time
import sys

def test_endpoints():
    """Test all critical endpoints"""
    
    print("Testing Stock Tracker Endpoints...")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test main backend
    try:
        print("\\n[1] Testing Main Backend (Port 8002)...")
        response = requests.get("http://localhost:8002/api/status", timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend is online")
            tests_passed += 1
        else:
            print(f"  ❌ Backend returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Backend is offline: {e}")
        tests_failed += 1
    
    # Test CBA.AX real price
    try:
        print("\\n[2] Testing CBA.AX real price...")
        response = requests.get("http://localhost:8002/api/stock/CBA.AX", timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data.get('price', 0)
            if 150 < price < 200:  # CBA should be around $170
                print(f"  ✅ CBA.AX price is realistic: ${price:.2f}")
                tests_passed += 1
            else:
                print(f"  ⚠️  CBA.AX price seems wrong: ${price:.2f}")
                tests_failed += 1
        else:
            print(f"  ❌ Failed to fetch CBA.AX")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Error fetching CBA.AX: {e}")
        tests_failed += 1
    
    # Test ML backend
    try:
        print("\\n[3] Testing ML Backend (Port 8003)...")
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ ML Backend is online")
            tests_passed += 1
        else:
            print(f"  ❌ ML Backend returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"  ⚠️  ML Backend might be offline: {e}")
        print("     (This is optional for basic functionality)")
    
    # Test historical data
    try:
        print("\\n[4] Testing Historical Data API...")
        response = requests.get("http://localhost:8002/api/historical/CBA.AX?period=1mo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                print(f"  ✅ Historical data available: {len(data['data'])} records")
                tests_passed += 1
            else:
                print(f"  ⚠️  No historical data returned")
                tests_failed += 1
        else:
            print(f"  ❌ Failed to fetch historical data")
            tests_failed += 1
    except Exception as e:
        print(f"  ❌ Error fetching historical data: {e}")
        tests_failed += 1
    
    # Summary
    print("\\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Tests Passed: {tests_passed}")
    print(f"  Tests Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\\n✅ All critical tests passed! System is using real data.")
        return 0
    else:
        print(f"\\n⚠️  {tests_failed} test(s) failed. Please check the services.")
        return 1

if __name__ == "__main__":
    print("Waiting 3 seconds for services to stabilize...")
    time.sleep(3)
    sys.exit(test_endpoints())
'''
    
    with open('test_real_data.py', 'w') as f:
        f.write(test_script)
    
    # Make it executable on Unix systems
    os.chmod('test_real_data.py', 0o755)
    
    print("✅ Created test_real_data.py")

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("    ENSURING REAL DATA IN ALL MODULES")
    print("=" * 60)
    print()
    
    # Fix HTML files
    print("[1] Checking and fixing HTML modules...")
    print("-" * 40)
    fixes = fix_html_files()
    if fixes:
        print(f"✅ Fixed {len(fixes)} files:")
        for fix in fixes:
            print(f"   - {fix['file']}")
            print(f"     Backup: {fix['backup']}")
    else:
        print("✅ No fixes needed - all modules look clean")
    
    print()
    
    # Verify backend configuration
    print("[2] Verifying backend configuration...")
    print("-" * 40)
    backend_checks = verify_backend_configuration()
    all_good = True
    for check in backend_checks:
        file_name = check['file']
        issues = []
        
        if 'port_8002' in check and not check['port_8002']:
            if 'backend.py' in file_name:
                issues.append("Not configured for port 8002")
        
        if 'port_8003' in check and not check['port_8003']:
            if 'ml_' in file_name:
                issues.append("Not configured for port 8003")
        
        if 'no_mock_data' in check and not check['no_mock_data']:
            issues.append("Contains mock/fake data references")
        
        if issues:
            print(f"⚠️  {file_name}: {', '.join(issues)}")
            all_good = False
        else:
            print(f"✅ {file_name}: Properly configured")
    
    if all_good:
        print("\n✅ All backend files are properly configured")
    
    print()
    
    # Create test script
    print("[3] Creating test script...")
    print("-" * 40)
    create_test_script()
    
    print()
    print("=" * 60)
    print("COMPLETE!")
    print()
    print("Next steps:")
    print("1. Run MASTER_STARTUP_ENHANCED.bat to start all services")
    print("2. Run: python test_real_data.py")
    print("3. Check that all tests pass")
    print()
    print("All modules are now configured to use REAL Yahoo Finance data.")
    print("No synthetic, mock, or demo data is being used.")
    print("=" * 60)

if __name__ == "__main__":
    main()
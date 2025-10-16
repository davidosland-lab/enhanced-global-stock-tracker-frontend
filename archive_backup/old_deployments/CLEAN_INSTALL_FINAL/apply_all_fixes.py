#!/usr/bin/env python3
"""
Apply all fixes for broken modules
Fixes:
1. Historical Data Manager 404 errors
2. Document Analyser broken link
3. Prediction Centre broken link
4. ML Training incorrect CBA.AX prices
"""

import os
import shutil
import re
from pathlib import Path

def backup_files():
    """Create backups of files before modifying"""
    files_to_backup = ['backend.py', 'index.html']
    for file in files_to_backup:
        if os.path.exists(file):
            backup_name = f"{file}.backup_fixed"
            shutil.copy(file, backup_name)
            print(f"✅ Backed up {file} to {backup_name}")

def fix_backend():
    """Replace backend with complete fixed version"""
    if os.path.exists('backend_complete_fixed.py'):
        shutil.copy('backend_complete_fixed.py', 'backend.py')
        print("✅ Backend replaced with complete fixed version")
        print("   - Added /api/historical/batch-download endpoint")
        print("   - Added /api/historical/download endpoint")
        print("   - Fixed CBA.AX price fetching")
        return True
    else:
        print("❌ backend_complete_fixed.py not found")
        return False

def fix_index_links():
    """Fix module links in index.html"""
    if not os.path.exists('index.html'):
        print("❌ index.html not found")
        return False
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the modules object
    pattern = r"const modules = \{[^}]+\};"
    replacement = """const modules = {
            'cba': 'modules/cba_enhanced.html',
            'indices': 'modules/indices_tracker.html',
            'tracker': 'modules/stock_tracker.html',
            'predictor': 'modules/prediction_centre_phase4.html',
            'documents': 'modules/document_uploader.html',
            'historical': 'modules/historical_data_manager_fixed.html',
            'performance': 'modules/prediction_performance_dashboard.html',
            'mltraining': 'modules/ml_training_centre.html',
            'technical': 'modules/technical_analysis_fixed.html'
        };"""
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed module links in index.html")
    print("   - Prediction Centre: modules/prediction_centre_phase4.html")
    print("   - Document Uploader: modules/document_uploader.html")  
    print("   - Historical Data: modules/historical_data_manager_fixed.html")
    return True

def fix_ml_training():
    """Fix ML Training module to prevent caching"""
    ml_path = Path('modules/ml_training_centre.html')
    
    if not ml_path.exists():
        print("⚠️  ML Training module not found at modules/ml_training_centre.html")
        return False
    
    with open(ml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add cache-busting to fetch calls
    if '&t=${Date.now()}' not in content:
        # Find fetch calls and add timestamp
        content = re.sub(
            r"fetch\(`\$\{API_BASE\}/api/historical/([^`]+)`\)",
            r"fetch(`${API_BASE}/api/historical/\1${(\1).includes('?') ? '&' : '?'}t=${Date.now()}`)",
            content
        )
        
        with open(ml_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed ML Training module")
        print("   - Added cache-busting to ensure fresh CBA.AX prices")
        return True
    else:
        print("ℹ️  ML Training module already has cache-busting")
        return True

def verify_files():
    """Verify all required files exist"""
    print("\n📁 Verifying module files...")
    
    required_modules = [
        'modules/cba_enhanced.html',
        'modules/indices_tracker.html',
        'modules/document_uploader.html',
        'modules/ml_training_centre.html',
        'modules/historical_data_manager_fixed.html',
        'modules/technical_analysis_fixed.html',
        'modules/prediction_centre_phase4.html'
    ]
    
    all_exist = True
    for module in required_modules:
        if os.path.exists(module):
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module} - NOT FOUND")
            all_exist = False
    
    return all_exist

def create_test_script():
    """Create a test script to verify fixes"""
    test_script = '''import requests
import time

print("Testing Fixed Endpoints...")
print("=" * 50)

# Test backend status
try:
    resp = requests.get("http://localhost:8002/api/status")
    if resp.status_code == 200:
        print("✅ Backend status: ONLINE")
    else:
        print("❌ Backend status: ERROR")
except:
    print("❌ Backend not running on port 8002")

# Test batch download endpoint
try:
    resp = requests.post("http://localhost:8002/api/historical/batch-download")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Batch download: {data.get('count', 0)} symbols")
    else:
        print(f"❌ Batch download: Status {resp.status_code}")
except:
    print("❌ Batch download endpoint not working")

# Test CBA.AX price
try:
    resp = requests.get("http://localhost:8002/api/stock/CBA.AX")
    if resp.status_code == 200:
        data = resp.json()
        price = data.get('price', 0)
        if 150 < price < 200:
            print(f"✅ CBA.AX price: ${price:.2f} (realistic)")
        else:
            print(f"⚠️  CBA.AX price: ${price:.2f} (seems wrong)")
    else:
        print("❌ Cannot fetch CBA.AX")
except:
    print("❌ Error fetching CBA.AX")

print("\\nTest complete!")
'''
    
    with open('test_fixes.py', 'w') as f:
        f.write(test_script)
    
    print("\n✅ Created test_fixes.py")
    print("   Run it after starting services to verify fixes")

def main():
    print("=" * 60)
    print("         APPLYING ALL MODULE FIXES")
    print("=" * 60)
    print()
    
    # Step 1: Backup
    print("📁 Creating backups...")
    backup_files()
    print()
    
    # Step 2: Fix backend
    print("🔧 Fixing backend...")
    backend_fixed = fix_backend()
    print()
    
    # Step 3: Fix index links
    print("🔗 Fixing module links...")
    links_fixed = fix_index_links()
    print()
    
    # Step 4: Fix ML training
    print("🤖 Fixing ML Training module...")
    ml_fixed = fix_ml_training()
    print()
    
    # Step 5: Verify files
    files_ok = verify_files()
    print()
    
    # Step 6: Create test script
    create_test_script()
    print()
    
    # Summary
    print("=" * 60)
    print("                    SUMMARY")
    print("=" * 60)
    
    if backend_fixed and links_fixed and files_ok:
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Stop all Python processes: taskkill /F /IM python.exe")
        print("2. Run: COMPLETE_FIX_SCRIPT.bat")
        print("   OR")
        print("   Run: MASTER_STARTUP_ENHANCED.bat")
        print("3. Clear browser cache (Ctrl+Shift+Delete)")
        print("4. Test with: python test_fixes.py")
    else:
        print("⚠️  Some fixes could not be applied")
        print("Please check the error messages above")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Fix Script for Windows 11 Stock Tracker Modules
Replaces broken endpoints with working ones
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of original file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"Backed up: {filepath} -> {backup_path}")
    return backup_path

def fix_endpoints_in_file(filepath, fixes):
    """Apply endpoint fixes to a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for old_pattern, new_pattern in fixes.items():
        content = re.sub(old_pattern, new_pattern, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = "/home/user/webapp/clean_install_windows11"
    
    # Define endpoint fixes
    endpoint_fixes = {
        # Fix status endpoint calls
        r'/api/status': '/api/status',  # Keep this as backend now has it
        r'\$\{ML_BACKEND_URL\}/api/predict': '${BACKEND_URL}/api/predict',
        r'http://localhost:8004': 'http://localhost:8002',
        r'const ML_BACKEND_URL = .*?;': 'const ML_BACKEND_URL = "http://localhost:8002";',
        r'const BACKEND_URL = .*?;': 'const BACKEND_URL = "http://localhost:8002";',
        # Fix phase 4 endpoints
        r'/api/phase4/predict': '/api/phase4/predict',  # Keep as backend now has it
        r'/api/phase4/backtest': '/api/phase4/backtest',  # Keep as backend now has it
    }
    
    # Files to fix
    files_to_fix = [
        "index.html",
        "modules/analysis/cba_analysis_enhanced.html",
        "modules/market-tracking/market_tracker_final.html",
        "modules/predictions/prediction_centre_real_ml.html",
        "modules/technical_analysis_enhanced.html"
    ]
    
    print("Starting module fix process...")
    print("=" * 50)
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"\n📄 Processing: {file_path}")
        
        # Backup original
        backup_file(full_path)
        
        # Apply fixes
        if fix_endpoints_in_file(full_path, endpoint_fixes):
            print(f"✅ Fixed endpoints in {file_path}")
            fixed_count += 1
        else:
            print(f"ℹ️  No changes needed for {file_path}")
    
    # Copy the new backend
    print("\n" + "=" * 50)
    print("📦 Deploying new backend...")
    
    new_backend_src = "/home/user/webapp/backend_fixed_complete.py"
    new_backend_dst = os.path.join(base_dir, "backend.py")
    
    if os.path.exists(new_backend_dst):
        backup_file(new_backend_dst)
    
    shutil.copy2(new_backend_src, new_backend_dst)
    print(f"✅ Deployed new backend to {new_backend_dst}")
    
    # Copy document uploader
    print("\n📄 Adding Document Uploader module...")
    doc_uploader_src = "/home/user/webapp/document_uploader_finbert.html"
    doc_uploader_dst = os.path.join(base_dir, "modules", "document_uploader.html")
    
    shutil.copy2(doc_uploader_src, doc_uploader_dst)
    print(f"✅ Added Document Uploader to {doc_uploader_dst}")
    
    # Create launch script
    launch_script = """#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def main():
    print("=" * 50)
    print("Windows 11 Stock Tracker Launcher")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\\n📦 Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", 
                   "yfinance", "fastapi", "uvicorn", "pandas", "numpy", 
                   "cachetools", "pytz", "python-multipart"])
    
    print("\\n🚀 Starting backend on http://localhost:8002")
    print("Access the application at: http://localhost:8002")
    print("\\nPress Ctrl+C to stop the server")
    
    # Run the backend
    subprocess.run([sys.executable, "backend.py"])

if __name__ == "__main__":
    main()
"""
    
    launch_path = os.path.join(base_dir, "launch.py")
    with open(launch_path, 'w') as f:
        f.write(launch_script)
    os.chmod(launch_path, 0o755)
    print(f"\n✅ Created launch script: {launch_path}")
    
    # Update index.html to include document uploader
    index_path = os.path.join(base_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        # Check if document uploader is already in the modules
        if 'document_uploader.html' not in index_content:
            print("\n📝 Updating index.html to include Document Uploader...")
            
            # Find the module cards section and add document uploader
            module_section_pattern = r'(<!-- Module Cards -->.*?)<div class="module-card">'
            
            doc_uploader_card = '''
                <div class="module-card">
                    <div class="module-icon">📄</div>
                    <h3>Document Analyzer</h3>
                    <p>Upload financial documents for FinBERT sentiment analysis</p>
                    <a href="modules/document_uploader.html" class="module-link">Open Module</a>
                </div>
'''
            
            # Try to insert the card
            if '<div class="module-grid">' in index_content:
                index_content = index_content.replace(
                    '<div class="module-grid">',
                    '<div class="module-grid">\n' + doc_uploader_card
                )
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(index_content)
                print("✅ Added Document Uploader to index.html")
    
    print("\n" + "=" * 50)
    print(f"✅ Fix process complete!")
    print(f"📊 Fixed {fixed_count} modules")
    print("\n📌 Next steps:")
    print("1. Run the backend: python launch.py")
    print("2. Open browser to: http://localhost:8002")
    print("3. All modules should now connect properly")
    print("\n⚠️  Important: The backend must be running for modules to work!")

if __name__ == "__main__":
    main()